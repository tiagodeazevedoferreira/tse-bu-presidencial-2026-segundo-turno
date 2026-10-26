#!/usr/bin/env python3
"""Inspect official TSE CKAN resources for the 2026 BU dataset.

This is a discovery utility only: it does not download or process election data.
It prints the live resource metadata so the pipeline can use verified URLs.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any

import requests

API_URL = "https://dadosabertos.tse.jus.br/api/3/action/package_show"
DATASET_ID = "resultados-2026-boletim-de-urna"
TIMEOUT_SECONDS = 30
HEADERS = {"User-Agent": "tse-bu-presidencial-2026-segundo-turno/0.1"}


def fetch_dataset(session: requests.Session) -> dict[str, Any]:
    response = session.get(
        API_URL,
        params={"id": DATASET_ID},
        headers=HEADERS,
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("success") is not True or not isinstance(payload.get("result"), dict):
        raise RuntimeError("A API CKAN não retornou um resultado válido para o conjunto de BU.")
    return payload["result"]


def normalize_resource(resource: dict[str, Any]) -> dict[str, Any]:
    name = str(resource.get("name") or resource.get("description") or "")
    url = resource.get("url")
    return {
        "id": resource.get("id"),
        "name": name,
        "url": url,
        "format": resource.get("format"),
        "mimetype": resource.get("mimetype"),
        "hash": resource.get("hash"),
        "size": resource.get("size"),
        "created": resource.get("created"),
        "last_modified": resource.get("last_modified"),
        "second_turn_candidate": "segundo turno" in name.casefold(),
        "sha2_candidate": "sha2" in name.casefold() or "sha-2" in name.casefold(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Grava o relatório JSON neste caminho; por padrão imprime no terminal.")
    args = parser.parse_args()

    try:
        with requests.Session() as session:
            dataset = fetch_dataset(session)
    except (requests.RequestException, ValueError, RuntimeError) as exc:
        print(f"ERRO ao consultar a API oficial do CKAN: {exc}", file=sys.stderr)
        return 2

    resources = [
        normalize_resource(item)
        for item in dataset.get("resources", [])
        if isinstance(item, dict)
    ]
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": API_URL,
        "dataset_id": dataset.get("name") or DATASET_ID,
        "dataset_title": dataset.get("title"),
        "dataset_metadata_modified": dataset.get("metadata_modified"),
        "resource_count": len(resources),
        "second_turn_candidates": [r for r in resources if r["second_turn_candidate"]],
        "resources": resources,
        "interpretation": (
            "Candidatos são identificados apenas pelo nome do recurso. "
            "Confirme URL, conteúdo e hash antes de usar qualquer arquivo."
        ),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"

    if args.output:
        from pathlib import Path

        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
        print(f"Relatório salvo em: {destination}")
    else:
        print(rendered, end="")

    print(
        f"Recursos encontrados: {len(resources)}; "
        f"candidatos de segundo turno: {len(report['second_turn_candidates'])}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
