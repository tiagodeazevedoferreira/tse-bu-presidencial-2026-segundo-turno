#!/usr/bin/env python3
"""Executa a auditoria BU-versus-dashboard para as 27 UFs.

Descobre URLs no conjunto oficial CKAN, valida SHA-512, reaproveita ZIPs
válidos em cache e gera relatórios por UF e um resumo nacional.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_URL = "https://dadosabertos.tse.jus.br/api/3/action/package_show"
DATASET_ID = "resultados-2026-boletim-de-urna"
DATASET_PAGE_URL = "https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna"
TIMEOUT_SECONDS = 90
USER_AGENT = "tse-bu-presidencial-2026-segundo-turno/0.2"
UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]


def request_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def sha512_file(path: Path) -> str:
    digest = hashlib.sha512()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_resources(resources: list[dict[str, Any]]) -> dict[str, str]:
    """Retorna UF -> URL ZIP, inclusive quando o CKAN publica só o link SHA-512."""
    found: dict[str, tuple[str, str]] = {}
    pattern = re.compile(r"bweb_2t_([a-z]{2})_(.+)\.zip$", re.IGNORECASE)
    for resource in resources:
        url = str(resource.get("url") or "").strip()
        if not url:
            continue
        filename = urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]
        # Alguns recursos CKAN apontam para o sidecar .zip.sha512, não para o ZIP.
        # O arquivo ZIP oficial correspondente usa a mesma URL sem o sufixo .sha512.
        if filename.lower().endswith(".zip.sha512"):
            filename = filename[:-len(".sha512")]
            url = url[:-len(".sha512")]
        match = pattern.fullmatch(filename)
        if not match:
            continue
        uf = match.group(1).upper()
        if uf not in UFS:
            continue
        version = match.group(2)
        # Se houver mais de uma versão, seleciona o sufixo de data/hora
        # lexicalmente mais recente, sem depender da ordem dos metadados.
        if uf not in found or version > found[uf][0]:
            found[uf] = (version, url)
    return {uf: value[1] for uf, value in found.items()}


def discover_resources_from_page(page_html: str) -> dict[str, str]:
    """Descobre ZIPs oficiais na página pública quando o CKAN omite algum recurso."""
    links = re.findall(r'''href=["']([^"']+)["']''', page_html, flags=re.IGNORECASE)
    resources = []
    for link in links:
        url = urllib.parse.urljoin(DATASET_PAGE_URL, html.unescape(link))
        filename = urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]
        if re.fullmatch(r"bweb_2t_[A-Za-z]{2}_.+\.zip", filename, re.IGNORECASE):
            resources.append({"url": url})
    return discover_resources(resources)


def fetch_metadata() -> dict[str, Any]:
    url = API_URL + "?" + urllib.parse.urlencode({"id": DATASET_ID})
    payload = json.loads(request_bytes(url).decode("utf-8"))
    if payload.get("success") is not True or not isinstance(payload.get("result"), dict):
        raise RuntimeError("A API CKAN não retornou metadados válidos do conjunto de BU.")
    return payload["result"]


def fetch_published_hash(url: str) -> tuple[str, bytes]:
    hash_url = url + ".sha512"
    raw = request_bytes(hash_url)
    match = re.search(rb"\b([0-9a-fA-F]{128})\b", raw)
    if not match:
        raise ValueError("O arquivo publicado não contém um SHA-512 de 128 caracteres.")
    return match.group(1).decode("ascii").lower(), raw


def ensure_download(uf: str, url: str, cache_dir: Path) -> tuple[Path, Path, str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    filename = urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]
    zip_path = cache_dir / filename
    hash_path = cache_dir / (filename + ".sha512")
    expected_hash, hash_bytes = fetch_published_hash(url)

    if zip_path.is_file() and sha512_file(zip_path) == expected_hash:
        hash_path.write_bytes(hash_bytes)
        return zip_path, hash_path, url

    partial_path = zip_path.with_suffix(zip_path.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            with partial_path.open("wb") as destination:
                shutil.copyfileobj(response, destination, length=1024 * 1024)
        actual_hash = sha512_file(partial_path)
        if actual_hash != expected_hash:
            raise ValueError(
                f"SHA-512 divergente para {uf}: publicado={expected_hash}, calculado={actual_hash}"
            )
        with zipfile.ZipFile(partial_path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise ValueError(f"ZIP corrompido ({bad_member})")
        partial_path.replace(zip_path)
        hash_path.write_bytes(hash_bytes)
    finally:
        if partial_path.exists():
            partial_path.unlink()
    return zip_path, hash_path, url


def run_one_uf(
    uf: str,
    url: str,
    dashboard: Path,
    output_dir: Path,
    cache_dir: Path,
    audit_script: Path,
) -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    try:
        zip_path, hash_path, source_url = ensure_download(uf, url, cache_dir)
        report_path = output_dir / f"auditoria_bu_dashboard_{uf}.json"
        command = [
            sys.executable, str(audit_script),
            "--uf", uf,
            "--source-url", source_url,
            "--hash-url", source_url + ".sha512",
            "--bu-zip", str(zip_path),
            "--sha512", str(hash_path),
            "--dashboard", str(dashboard),
            "--output", str(report_path),
        ]
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=False,
        )
        if not report_path.is_file():
            raise RuntimeError(
                f"Auditoria não gerou relatório (código {completed.returncode}): "
                f"{completed.stderr[-1500:]}"
            )
        report = json.loads(report_path.read_text(encoding="utf-8"))
        return {
            "uf": uf,
            "status": report.get("status", "status_ausente"),
            "codigo_saida": completed.returncode,
            "relatorio": str(report_path),
            "chaves_dashboard": report.get("chaves_dashboard"),
            "chaves_bu": report.get("chaves_bu"),
            "chaves_em_comum": report.get("chaves_em_comum"),
            "divergencias_lula": report.get("quantidade_divergencias", {}).get("lula"),
            "divergencias_flavio": report.get("quantidade_divergencias", {}).get("flavio"),
            "erro": report.get("erro"),
            "inicio_utc": started,
            "fim_utc": datetime.now(timezone.utc).isoformat(),
        }
    except (OSError, ValueError, RuntimeError, urllib.error.URLError, zipfile.BadZipFile) as exc:
        return {
            "uf": uf,
            "status": "falha_tecnica",
            "codigo_saida": 2,
            "relatorio": None,
            "erro": str(exc),
            "inicio_utc": started,
            "fim_utc": datetime.now(timezone.utc).isoformat(),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dashboard", default="data/NovoArquivoDashboard.csv")
    parser.add_argument("--output-dir", default="reports/auditoria_nacional_bu")
    parser.add_argument("--summary", default="reports/auditoria_nacional_bu.json")
    parser.add_argument("--cache-dir", default=str(
        Path(os.environ.get("TEMP", str(Path.home() / "AppData" / "Local" / "Temp")))
        / "tse_bu_nacional_2026"
    ))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--ufs", nargs="*", choices=UFS, default=UFS,
                        help="Opcional: auditar somente as UFs informadas.")
    args = parser.parse_args()

    if args.workers < 1 or args.workers > 8:
        parser.error("--workers deve estar entre 1 e 8.")

    dashboard = Path(args.dashboard).resolve()
    output_dir = Path(args.output_dir).resolve()
    summary_path = Path(args.summary).resolve()
    cache_dir = Path(args.cache_dir).resolve()
    audit_script = Path(__file__).with_name("audit_dashboard_against_tse_bu.py")
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    if not dashboard.is_file():
        parser.error(f"CSV do dashboard não encontrado: {dashboard}")
    if not audit_script.is_file():
        parser.error(f"Script de auditoria individual não encontrado: {audit_script}")

    started = datetime.now(timezone.utc).isoformat()
    try:
        dataset = fetch_metadata()
        resources = dataset.get("resources", [])
        urls = discover_resources([r for r in resources if isinstance(r, dict)])
        missing_from_api = [uf for uf in args.ufs if uf not in urls]
        if missing_from_api:
            try:
                page_html = request_bytes(DATASET_PAGE_URL).decode("utf-8", errors="replace")
                page_urls = discover_resources_from_page(page_html)
                urls.update({uf: url for uf, url in page_urls.items() if uf not in urls})
            except (OSError, urllib.error.URLError):
                # Mantém os recursos já descobertos na API; as UFs ausentes serão reportadas.
                pass
    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        summary = {
            "status": "falha_descoberta_recursos",
            "inicio_utc": started,
            "fim_utc": datetime.now(timezone.utc).isoformat(),
            "erro": str(exc),
            "resultados": [],
        }
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 2

    selected = list(args.ufs)
    results: list[dict[str, Any]] = []
    missing = [uf for uf in selected if uf not in urls]
    for uf in missing:
        results.append({
            "uf": uf, "status": "recurso_oficial_nao_encontrado",
            "codigo_saida": 2, "relatorio": None,
            "erro": "Nenhuma URL bweb_2t_<UF>_*.zip foi localizada nos metadados CKAN.",
        })

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(run_one_uf, uf, urls[uf], dashboard, output_dir, cache_dir, audit_script): uf
            for uf in selected if uf in urls
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"[{result['uf']}] {result['status']}")

    results.sort(key=lambda item: UFS.index(item["uf"]))
    complete = len(results) == len(selected) and not missing and all(
        item.get("status") == "concluido_sem_divergencias" for item in results
    )
    summary = {
        "auditoria": "BU oficial do segundo turno versus dashboard",
        "inicio_utc": started,
        "fim_utc": datetime.now(timezone.utc).isoformat(),
        "conjunto_tse": DATASET_ID,
        "dashboard": str(dashboard),
        "ufs_solicitadas": selected,
        "quantidade_ufs_solicitadas": len(selected),
        "quantidade_ufs_com_resultado": len(results),
        "quantidade_concluidas_sem_divergencias": sum(
            item.get("status") == "concluido_sem_divergencias" for item in results
        ),
        "quantidade_com_divergencias_ou_revisao": sum(
            item.get("status") == "revisao_necessaria" for item in results
        ),
        "quantidade_falhas_tecnicas_ou_recursos_ausentes": sum(
            item.get("status") not in ("concluido_sem_divergencias", "revisao_necessaria")
            for item in results
        ),
        "status": "concluido_sem_divergencias_em_todas_as_ufs" if complete else "revisao_ou_cobertura_incompleta",
        "resultados": results,
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Resumo salvo em: {summary_path}")
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
