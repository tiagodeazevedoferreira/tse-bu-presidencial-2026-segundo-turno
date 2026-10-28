#!/usr/bin/env python3
"""Audita a estrutura e a consistência do CSV usado pelo dashboard.

Usa apenas a biblioteca padrão do Python, lê o arquivo em streaming e não altera
nem regrava a fonte. O relatório é exploratório: não determina fraude ou erro
eleitoral; apenas aponta problemas de qualidade e situações para conferência.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

ALIASES = {
    "uf": {"uf", "siglauf", "unidadefederacao"},
    "municipio": {"municipio", "municipionome", "municpio", "nomemunicipio"},
    "zona": {"zona", "zonaeleitoral", "numerozona"},
    "secao": {"secao", "secaoeleitoral", "seo", "numerosecao"},
    "local": {"local", "localdevotacao", "localdevotao", "nomelocal"},
    "flavio1": {"flavio1turno", "flavio1oturno", "flvio1turno", "votosflavio1turno"},
    "flavio2": {"flavio2turno", "flavio2oturno", "flvio2turno", "votosflavio2turno"},
    "lula1": {"lula1turno", "lula1oturno", "votoslula1turno"},
    "lula2": {"lula2turno", "lula2oturno", "votoslula2turno"},
}
NUMERIC_FIELDS = ("flavio1", "flavio2", "lula1", "lula2")


def normalize(value: str) -> str:
    value = value.lstrip("\ufeff").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", value)


def detect_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,\t|").delimiter
    except csv.Error:
        counts = {d: sample.count(d) for d in (";", ",", "\t", "|")}
        return max(counts, key=counts.get)


def parse_integer(raw: str) -> tuple[int | None, str | None]:
    value = raw.strip()
    if not value:
        return None, None
    value = value.replace("\u00a0", "").replace(" ", "")
    if re.fullmatch(r"\d+", value):
        return int(value), None
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", value):
        return int(value.replace(".", "")), None
    if re.fullmatch(r"-\d+", value):
        return int(value), "negative"
    return None, "invalid_integer"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", help="Caminho do CSV atual do dashboard")
    parser.add_argument(
        "--output",
        default="reports/auditoria_csv_dashboard.json",
        help="Caminho do relatório JSON (padrão: reports/auditoria_csv_dashboard.json)",
    )
    parser.add_argument(
        "--examples",
        type=int,
        default=20,
        help="Máximo de exemplos por categoria no relatório (padrão: 20)",
    )
    args = parser.parse_args()

    source = Path(args.csv_path)
    if not source.is_file():
        print(f"ERRO: arquivo não encontrado: {source}", file=sys.stderr)
        return 2

    counters: Counter[str] = Counter()
    numeric_stats: dict[str, dict[str, Any]] = {
        name: {"present": 0, "blank": 0, "invalid": 0, "negative": 0, "zero": 0,
               "positive": 0, "sum": 0, "max": None, "max_row": None}
        for name in NUMERIC_FIELDS
    }
    examples: dict[str, list[dict[str, Any]]] = {
        "duplicate_keys": [], "invalid_numeric": [], "negative_votes": [],
        "missing_location": [], "partial_turn": [],
    }
    headers: list[str] = []
    mapping: dict[str, int] = {}
    delimiter = ";"
    duplicate_count = 0
    duplicate_db = tempfile.NamedTemporaryFile(prefix="tse-audit-", suffix=".sqlite3", delete=False)
    duplicate_db_path = Path(duplicate_db.name)
    duplicate_db.close()

    def add_example(category: str, item: dict[str, Any]) -> None:
        if len(examples[category]) < max(0, args.examples):
            examples[category].append(item)

    try:
        with source.open("r", encoding="utf-8-sig", newline="") as f:
            sample = f.read(65536)
            delimiter = detect_delimiter(sample)
            f.seek(0)
            reader = csv.reader(f, delimiter=delimiter)
            try:
                raw_headers = next(reader)
            except StopIteration:
                print("ERRO: CSV vazio.", file=sys.stderr)
                return 2

            headers = [h.strip() for h in raw_headers]
            normalized = [normalize(h) for h in headers]
            for logical_name, aliases in ALIASES.items():
                for i, header in enumerate(normalized):
                    if header in aliases:
                        mapping[logical_name] = i
                        break

            required = ("uf", "municipio", "zona", "secao", *NUMERIC_FIELDS)
            missing_columns = [name for name in required if name not in mapping]
            if missing_columns:
                report = {
                    "arquivo": str(source),
                    "tamanho_bytes": source.stat().st_size,
                    "delimitador_detectado": repr(delimiter),
                    "cabecalhos": headers,
                    "colunas_mapeadas": mapping,
                    "colunas_obrigatorias_ausentes": missing_columns,
                    "status": "schema_incompativel",
                    "nota": "O arquivo não foi alterado. Revise os nomes reais das colunas e ajuste os aliases antes de interpretar os resultados.",
                }
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
                print(json.dumps(report, ensure_ascii=False, indent=2))
                return 1

            conn = sqlite3.connect(str(duplicate_db_path))
            conn.execute("CREATE TABLE seen (section_key TEXT PRIMARY KEY)")
            conn.commit()

            for row_number, row in enumerate(reader, start=2):
                if not row or not any(cell.strip() for cell in row):
                    counters["blank_rows"] += 1
                    continue
                counters["data_rows"] += 1
                if len(row) != len(headers):
                    counters["wrong_column_count"] += 1
                    if counters["wrong_column_count"] <= args.examples:
                        add_example("invalid_numeric", {
                            "linha": row_number, "tipo": "quantidade_colunas",
                            "esperado": len(headers), "encontrado": len(row)
                        })

                def get(name: str) -> str:
                    idx = mapping.get(name)
                    return row[idx].strip() if idx is not None and idx < len(row) else ""

                uf, municipality, zone, section = (get(x) for x in ("uf", "municipio", "zona", "secao"))
                if not all((uf, municipality, zone, section)):
                    counters["missing_location_rows"] += 1
                    add_example("missing_location", {
                        "linha": row_number, "uf": uf, "municipio": municipality,
                        "zona": zone, "secao": section
                    })
                else:
                    key = json.dumps([uf, municipality, zone, section], ensure_ascii=False, separators=(",", ":"))
                    cursor = conn.execute("INSERT OR IGNORE INTO seen(section_key) VALUES (?)", (key,))
                    if cursor.rowcount == 0:
                        duplicate_count += 1
                        counters["duplicate_rows"] += 1
                        add_example("duplicate_keys", {
                            "linha": row_number, "uf": uf, "municipio": municipality,
                            "zona": zone, "secao": section
                        })

                values: dict[str, int | None] = {}
                raw_values: dict[str, str] = {}
                for name in NUMERIC_FIELDS:
                    raw = get(name)
                    raw_values[name] = raw
                    parsed, error = parse_integer(raw)
                    values[name] = parsed
                    stats = numeric_stats[name]
                    if not raw:
                        stats["blank"] += 1
                    elif error:
                        stats["invalid"] += 1
                        if error == "negative":
                            stats["negative"] += 1
                            counters["negative_votes"] += 1
                            counters["invalid_numeric"] += 1
                            add_example("negative_votes", {
                                "linha": row_number, "campo": name, "valor": raw,
                                "uf": uf, "municipio": municipality, "zona": zone, "secao": section
                            })
                        else:
                            counters["invalid_numeric"] += 1
                            add_example("invalid_numeric", {
                                "linha": row_number, "campo": name, "valor": raw,
                                "uf": uf, "municipio": municipality, "zona": zone, "secao": section
                            })
                    else:
                        stats["present"] += 1
                        stats["sum"] += parsed
                        if parsed == 0:
                            stats["zero"] += 1
                        else:
                            stats["positive"] += 1
                        if stats["max"] is None or parsed > stats["max"]:
                            stats["max"] = parsed
                            stats["max_row"] = row_number

                for turn, a, b in (("1", "flavio1", "lula1"), ("2", "flavio2", "lula2")):
                    if (not raw_values[a]) != (not raw_values[b]):
                        counters[f"partial_turn_{turn}"] += 1
                        add_example("partial_turn", {
                            "linha": row_number, "turno": turn,
                            "campo_ausente": a if values[a] is None else b,
                            "uf": uf, "municipio": municipality, "zona": zone, "secao": section
                        })

            conn.commit()
            unique_sections = conn.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
            conn.close()

        report = {
            "arquivo": str(source),
            "tamanho_bytes": source.stat().st_size,
            "delimitador_detectado": repr(delimiter),
            "cabecalhos": headers,
            "colunas_mapeadas": mapping,
            "status": "concluido",
            "resumo": {
                "linhas_de_dados": counters["data_rows"],
                "linhas_vazias": counters["blank_rows"],
                "linhas_com_quantidade_de_colunas_incorreta": counters["wrong_column_count"],
                "linhas_com_chave_geografica_incompleta": counters["missing_location_rows"],
                "chaves_de_secao_unicas": unique_sections,
                "linhas_com_chave_de_secao_duplicada": duplicate_count,
                "linhas_com_voto_negativo": counters["negative_votes"],
                "linhas_com_valor_numerico_invalido": counters["invalid_numeric"],
                "linhas_com_votos_parciais_no_1_turno": counters["partial_turn_1"],
                "linhas_com_votos_parciais_no_2_turno": counters["partial_turn_2"],
            },
            "estatisticas_numericas": numeric_stats,
            "exemplos": examples,
            "interpretacao": [
                "Campos vazios são contabilizados como ausentes, não convertidos em zero.",
                "Uma chave duplicada é um alerta para revisão; não é removida nem prova, isoladamente, de erro.",
                "A auditoria não verifica a veracidade eleitoral contra o TSE; compara apenas estrutura e consistência interna do CSV.",
                "A soma de votos e os máximos são estatísticas descritivas, não limites oficiais de plausibilidade.",
            ],
        }
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": report["status"], "relatorio": str(output), **report["resumo"]},
                         ensure_ascii=False, indent=2))
        return 0
    finally:
        try:
            duplicate_db_path.unlink(missing_ok=True)
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
