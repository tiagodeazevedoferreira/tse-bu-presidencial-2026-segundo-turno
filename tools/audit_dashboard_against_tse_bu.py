
#!/usr/bin/env python3
"""Compara votos do dashboard com o BU oficial do segundo turno de uma UF."""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


SOURCE_URL = (
    "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/"
    "buweb/bweb_2t_RR_261020260742.zip"
)
HASH_URL = SOURCE_URL + ".sha512"

BU_REQUIRED_COLUMNS = {
    "NR_TURNO",
    "DS_CARGO_PERGUNTA",
    "SG_UF",
    "NM_MUNICIPIO",
    "NR_ZONA",
    "NR_SECAO",
    "DS_TIPO_VOTAVEL",
    "NR_VOTAVEL",
    "QT_VOTOS",
}


def norm(value):
    """Normaliza texto para comparação de cabeçalhos e nomes geográficos."""
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(
        char for char in value
        if not unicodedata.combining(char)
    )
    return re.sub(r"[^a-zA-Z0-9]", "", value).upper()


def parse_votes(value):
    """Converte votos inteiros não negativos; vazio é distinto de zero."""
    value = str(value or "").strip()

    if not value:
        return None

    if not re.fullmatch(r"\d+", value):
        raise ValueError(f"Valor de votos inválido: {value!r}")

    return int(value)


def sha512_file(path):
    """Calcula SHA-512 sem carregar o arquivo inteiro na memória."""
    digest = hashlib.sha512()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def find_column(headers, aliases, label):
    """Localiza uma coluna usando nomes alternativos normalizados."""
    normalized = [norm(header) for header in headers]

    for index, name in enumerate(normalized):
        if name in aliases:
            return index

    raise ValueError(
        f"Coluna obrigatória não encontrada: {label}. "
        f"Cabeçalhos: {headers!r}"
    )


def write_report(path, report):
    """Grava e imprime o relatório JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nRelatório salvo em: {path.resolve()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    pasta_temp = Path(
        os.environ.get(
            "TEMP",
            str(Path.home() / "AppData" / "Local" / "Temp"),
        )
    )
    pasta_piloto = pasta_temp / "tse_bu_piloto_rr"

    parser.add_argument(
        "--bu-zip",
        default=str(
            pasta_piloto / "bweb_2t_RR_261020260742.zip"
        ),
    )
    parser.add_argument(
        "--sha512",
        default=str(
            pasta_piloto / "bweb_2t_RR_261020260742.zip.sha512"
        ),
    )
    parser.add_argument(
        "--dashboard",
        default="data/NovoArquivoDashboard.csv",
    )
    parser.add_argument(
        "--output",
        default="reports/auditoria_bu_dashboard_RR.json",
    )

    args = parser.parse_args()

    zip_path = Path(args.bu_zip)
    hash_path = Path(args.sha512)
    dashboard_path = Path(args.dashboard)
    output_path = Path(args.output)

    for path in (zip_path, hash_path, dashboard_path):
        if not path.is_file():
            raise SystemExit(f"ERRO: arquivo não encontrado: {path}")

    # Confere o arquivo local contra o SHA-512 publicado pelo TSE.
    try:
        hash_text = hash_path.read_text(encoding="ascii").strip()
        match = re.search(r"\b([0-9a-fA-F]{128})\b", hash_text)

        if not match:
            raise ValueError("Arquivo SHA-512 sem digest válido.")

        expected_hash = match.group(1).lower()
        actual_hash = sha512_file(zip_path)
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f"ERRO ao validar o SHA-512: {exc}")

    hash_ok = actual_hash == expected_hash

    report = {
        "auditoria": "BU oficial do segundo turno versus dashboard",
        "executado_em_utc": datetime.now(timezone.utc).isoformat(),
        "uf": "RR",
        "turno": 2,
        "fonte_bu": SOURCE_URL,
        "fonte_hash": HASH_URL,
        "arquivo_bu": zip_path.name,
        "arquivo_hash": hash_path.name,
        "sha512_publicado": expected_hash,
        "sha512_calculado": actual_hash,
        "sha512_confere": hash_ok,
        "arquivo_dashboard": str(dashboard_path),
        "interpretacao": (
            "A ausência de registro nominal de um candidato no BU é "
            "tratada como zero somente para a comparação dos votos "
            "nominais por seção neste teste. Isso não preenche nem "
            "altera o arquivo original."
        ),
    }

    if not hash_ok:
        report["status"] = "falha_hash"
        write_report(output_path, report)
        raise SystemExit(
            "ERRO: SHA-512 não confere; auditoria interrompida."
        )

    # Estruturas para acumular votos e detectar duplicidades no BU.
    bu_votes = defaultdict(lambda: {"13": 0, "22": 0})
    bu_candidate_rows = Counter()
    bu_duplicate_nominal_rows = []
    bu_sections = set()
    csv_member = None

    try:
        with zipfile.ZipFile(zip_path) as archive:
            corrupt_member = archive.testzip()

            if corrupt_member:
                raise ValueError(
                    f"Membro corrompido no ZIP: {corrupt_member}"
                )

            candidates = [
                name for name in archive.namelist()
                if name.lower().endswith(".csv")
                and "bweb_2t_rr_" in name.lower()
            ]

            if len(candidates) != 1:
                raise ValueError(
                    "Esperado um CSV de BU de RR; "
                    f"encontrados: {candidates}"
                )

            csv_member = candidates[0]

            with archive.open(csv_member) as raw:
                text = io.TextIOWrapper(
                    raw,
                    encoding="cp1252",
                    newline="",
                )
                reader = csv.DictReader(text, delimiter=";")

                missing_columns = (
                    BU_REQUIRED_COLUMNS
                    - set(reader.fieldnames or [])
                )

                if missing_columns:
                    raise ValueError(
                        "Colunas obrigatórias ausentes no BU: "
                        + ", ".join(sorted(missing_columns))
                    )

                for row_number, row in enumerate(reader, start=2):
                    if (
                        None in row
                        or any(
                            row.get(column) is None
                            for column in BU_REQUIRED_COLUMNS
                        )
                    ):
                        raise ValueError(
                            "Registro incompleto no CSV do BU, "
                            f"linha {row_number}."
                        )

                    if (
                        row["NR_TURNO"].strip() != "2"
                        or row["DS_CARGO_PERGUNTA"].strip()
                        != "Presidente"
                    ):
                        continue

                    key = (
                        row["SG_UF"].strip().upper(),
                        norm(row["NM_MUNICIPIO"]),
                        row["NR_ZONA"].strip(),
                        row["NR_SECAO"].strip(),
                    )

                    if key[0] != "RR":
                        continue

                    bu_sections.add(key)

                    if (
                        row["DS_TIPO_VOTAVEL"].strip() != "Nominal"
                        or row["NR_VOTAVEL"].strip() not in ("13", "22")
                    ):
                        continue

                    code = row["NR_VOTAVEL"].strip()

                    try:
                        vote_count = parse_votes(row["QT_VOTOS"])
                        if vote_count is None:
                            raise ValueError("quantidade de votos vazia")
                    except ValueError as exc:
                        raise ValueError(
                            "Quantidade de votos inválida no BU, "
                            f"linha {row_number}: {exc}"
                        ) from exc

                    bu_candidate_rows[(key, code)] += 1

                    if bu_candidate_rows[(key, code)] > 1:
                        bu_duplicate_nominal_rows.append({
                            "chave": key,
                            "candidato": code,
                            "linha": row_number,
                        })

                    bu_votes[key][code] += vote_count

    except (OSError, UnicodeError, csv.Error, zipfile.BadZipFile, ValueError) as exc:
        report.update({
            "status": "erro_estrutura_bu",
            "erro": str(exc),
            "arquivo_csv_interno_do_bu": csv_member,
        })
        write_report(output_path, report)
        raise SystemExit(f"ERRO na estrutura do BU: {exc}")

    # Mapeia os campos do dashboard pelos cabeçalhos normalizados.
    dashboard = {}
    dashboard_duplicates = []
    invalid_dashboard_values = []
    dashboard_rows = 0

    aliases = {
        "uf": {"UF", "SIGLAUF"},
        "municipio": {"MUNICIPIO", "MUNICPIO", "NOMEMUNICIPIO"},
        "zona": {"ZONA", "ZONAELEITORAL"},
        "secao": {"SECAO", "SECAOELEITORAL", "SEO"},
        "flavio2": {
            "FLAVIO2TURNO",
            "FLVIO2TURNO",
            "FLAVIO2OTURNO",
            "VOTOSFLAVIO2TURNO",
        },
        "lula2": {
            "LULA2TURNO",
            "LULA2OTURNO",
            "VOTOSLULA2TURNO",
        },
    }

    try:
        with dashboard_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.reader(file, delimiter=";")
            headers = next(reader, None)

            if not headers:
                raise ValueError("CSV do dashboard vazio ou sem cabeçalho.")

            columns = {
                name: find_column(headers, accepted, name)
                for name, accepted in aliases.items()
            }

            for line_number, row in enumerate(reader, start=2):
                if not row or not any(cell.strip() for cell in row):
                    continue

                if len(row) != len(headers):
                    invalid_dashboard_values.append({
                        "linha": line_number,
                        "erro": (
                            "quantidade de colunas incompatível: "
                            f"esperado {len(headers)}, recebido {len(row)}"
                        ),
                    })
                    continue

                uf = row[columns["uf"]].strip().upper()

                if uf != "RR":
                    continue

                dashboard_rows += 1

                key = (
                    uf,
                    norm(row[columns["municipio"]]),
                    row[columns["zona"]].strip(),
                    row[columns["secao"]].strip(),
                )

                if not key[1] or not key[2] or not key[3]:
                    invalid_dashboard_values.append({
                        "linha": line_number,
                        "chave": key,
                        "erro": "chave geográfica incompleta",
                    })
                    continue

                try:
                    values = {
                        "13": parse_votes(row[columns["lula2"]]),
                        "22": parse_votes(row[columns["flavio2"]]),
                    }
                except ValueError as exc:
                    invalid_dashboard_values.append({
                        "linha": line_number,
                        "chave": key,
                        "erro": str(exc),
                    })
                    continue

                if key in dashboard:
                    dashboard_duplicates.append(key)
                else:
                    dashboard[key] = values

    except (OSError, UnicodeError, csv.Error, ValueError, StopIteration) as exc:
        report.update({
            "status": "erro_estrutura_dashboard",
            "erro": str(exc),
        })
        write_report(output_path, report)
        raise SystemExit(
            f"ERRO na estrutura do dashboard: {exc}"
        )

    dashboard_keys = set(dashboard)
    common = dashboard_keys & bu_sections
    dashboard_only = dashboard_keys - bu_sections
    bu_only = bu_sections - dashboard_keys

    differences = {"lula": [], "flavio": []}
    missing_nominal_rows = {"lula": 0, "flavio": 0}

    for key in sorted(common):
        for code, name in (("13", "lula"), ("22", "flavio")):
            bu_value = bu_votes[key][code]
            dashboard_value = dashboard[key][code]

            if bu_candidate_rows[(key, code)] == 0:
                missing_nominal_rows[name] += 1

            # Ausência no dashboard continua distinta de zero.
            if dashboard_value is None or dashboard_value != bu_value:
                differences[name].append({
                    "chave": key,
                    "dashboard": dashboard_value,
                    "bu": bu_value,
                })

    report.update({
        "arquivo_csv_interno_do_bu": csv_member,
        "linhas_dashboard_rr": dashboard_rows,
        "chaves_dashboard": len(dashboard_keys),
        "chaves_bu": len(bu_sections),
        "chaves_em_comum": len(common),
        "somente_dashboard": sorted(dashboard_only),
        "somente_bu": sorted(bu_only),
        "duplicadas_dashboard": dashboard_duplicates,
        "registros_nominais_duplicados_bu": bu_duplicate_nominal_rows,
        "valores_dashboard_invalidos": invalid_dashboard_values,
        "secoes_sem_registro_nominal_bu": missing_nominal_rows,
        "divergencias": differences,
        "quantidade_divergencias": {
            name: len(items)
            for name, items in differences.items()
        },
    })

    passed = (
        hash_ok
        and not dashboard_only
        and not bu_only
        and not dashboard_duplicates
        and not bu_duplicate_nominal_rows
        and not invalid_dashboard_values
        and not differences["lula"]
        and not differences["flavio"]
    )

    report["status"] = (
        "concluido_sem_divergencias"
        if passed
        else "revisao_necessaria"
    )

    write_report(output_path, report)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
