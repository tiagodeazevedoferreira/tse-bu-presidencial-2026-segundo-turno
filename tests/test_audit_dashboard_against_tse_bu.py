
import contextlib
import csv
import hashlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.audit_dashboard_against_tse_bu import main


BU_HEADERS = [
    "NR_TURNO",
    "DS_CARGO_PERGUNTA",
    "SG_UF",
    "NM_MUNICIPIO",
    "NR_ZONA",
    "NR_SECAO",
    "DS_TIPO_VOTAVEL",
    "NR_VOTAVEL",
    "QT_VOTOS",
]


class AuditBuIntegrationTests(unittest.TestCase):
    def criar_arquivos(
        self,
        root,
        hash_correto=True,
        duplicar_registro=False,
        remover_cabecalho=None,
        uf="RR",
    ):
        headers = [
            header for header in BU_HEADERS
            if header != remover_cabecalho
        ]

        registros = [{
            "NR_TURNO": "2",
            "DS_CARGO_PERGUNTA": "Presidente",
            "SG_UF": uf,
            "NM_MUNICIPIO": "CAROEBE",
            "NR_ZONA": "4",
            "NR_SECAO": "141",
            "DS_TIPO_VOTAVEL": "Nominal",
            "NR_VOTAVEL": "13",
            "QT_VOTOS": "100",
        }]

        if duplicar_registro:
            registros.append(registros[0].copy())

        bu_csv = io.StringIO(newline="")
        writer = csv.DictWriter(
            bu_csv,
            fieldnames=headers,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(registros)

        zip_path = root / "bu.zip"
        with zipfile.ZipFile(
            zip_path, "w", zipfile.ZIP_DEFLATED
        ) as archive:
            archive.writestr(
                f"bweb_2t_{uf.lower()}_teste.csv",
                bu_csv.getvalue(),
            )

        digest = hashlib.sha512(zip_path.read_bytes()).hexdigest()
        hash_path = root / "bu.zip.sha512"
        hash_path.write_text(
            digest if hash_correto else "0" * 128,
            encoding="ascii",
        )

        dashboard_path = root / "dashboard.csv"
        with dashboard_path.open(
            "w", encoding="utf-8", newline=""
        ) as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow([
                "UF",
                "Município",
                "Zona",
                "Seção",
                "Flávio - 2º turno",
                "Lula - 2º turno",
            ])
            writer.writerow([
                uf, "CAROEBE", "4", "141", "0", "100"
            ])

        return zip_path, hash_path, dashboard_path

    def executar_auditoria(
        self,
        root,
        hash_correto=True,
        duplicar_registro=False,
        remover_cabecalho=None,
        uf="RR",
    ):
        zip_path, hash_path, dashboard_path = self.criar_arquivos(
            root,
            hash_correto=hash_correto,
            duplicar_registro=duplicar_registro,
            remover_cabecalho=remover_cabecalho,
            uf=uf,
        )

        report_path = root / "report.json"
        args = [
            "audit_dashboard_against_tse_bu.py",
            "--uf", uf,
            "--source-url", f"https://example.test/bweb_2t_{uf}_teste.zip",
            "--hash-url", f"https://example.test/bweb_2t_{uf}_teste.zip.sha512",
            "--bu-zip", str(zip_path),
            "--sha512", str(hash_path),
            "--dashboard", str(dashboard_path),
            "--output", str(report_path),
        ]

        with patch.object(sys, "argv", args):
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as exc:
                    main()

        report = json.loads(
            report_path.read_text(encoding="utf-8")
        )
        return exc.exception.code, report

    def test_compara_votos_e_trata_ausencia_nominal_como_zero(self):
        with tempfile.TemporaryDirectory() as temp:
            code, report = self.executar_auditoria(Path(temp))

        self.assertEqual(code, 0)
        self.assertTrue(report["sha512_confere"])
        self.assertEqual(report["chaves_em_comum"], 1)
        self.assertEqual(
            report["quantidade_divergencias"]["lula"], 0
        )
        self.assertEqual(
            report["quantidade_divergencias"]["flavio"], 0
        )
        self.assertEqual(
            report["secoes_sem_registro_nominal_bu"]["flavio"], 1
        )
        self.assertEqual(
            report["status"], "concluido_sem_divergencias"
        )

    def test_interrompe_auditoria_quando_hash_nao_confere(self):
        with tempfile.TemporaryDirectory() as temp:
            code, report = self.executar_auditoria(
                Path(temp), hash_correto=False
            )

        self.assertNotEqual(code, 0)
        self.assertFalse(report["sha512_confere"])
        self.assertEqual(report["status"], "falha_hash")

    def test_reprova_auditoria_com_registro_nominal_duplicado(self):
        with tempfile.TemporaryDirectory() as temp:
            code, report = self.executar_auditoria(
                Path(temp), duplicar_registro=True
            )

        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "revisao_necessaria")
        self.assertEqual(
            len(report["registros_nominais_duplicados_bu"]), 1
        )

    def test_interrompe_auditoria_quando_falta_cabecalho_do_bu(self):
        with tempfile.TemporaryDirectory() as temp:
            code, report = self.executar_auditoria(
                Path(temp), remover_cabecalho="QT_VOTOS"
            )

        self.assertNotEqual(code, 0)
        self.assertEqual(report["status"], "erro_estrutura_bu")
        self.assertIn("QT_VOTOS", report["erro"])


if __name__ == "__main__":
    unittest.main()
