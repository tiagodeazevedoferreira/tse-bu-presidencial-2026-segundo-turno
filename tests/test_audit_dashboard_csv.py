import contextlib
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.audit_dashboard_csv import detect_delimiter, main, normalize, parse_integer


class AuditHelpersTests(unittest.TestCase):
    def test_normalize_header_with_accents_and_symbols(self):
        self.assertEqual(normalize("Flávio 1º turno"), "flavio1turno")
        self.assertEqual(normalize("\ufeffSeção eleitoral"), "secaoeleitoral")

    def test_parse_integer_distinguishes_blank_invalid_and_negative(self):
        self.assertEqual(parse_integer(""), (None, None))
        self.assertEqual(parse_integer("1.234"), (1234, None))
        self.assertEqual(parse_integer("0"), (0, None))
        self.assertEqual(parse_integer("-2"), (-2, "negative"))
        self.assertEqual(parse_integer("12,5"), (None, "invalid_integer"))

    def test_detect_semicolon_delimiter(self):
        self.assertEqual(detect_delimiter("uf;municipio;votos\nSC;Teste;10\n"), ";")


class AuditIntegrationTests(unittest.TestCase):
    def test_audit_reports_duplicate_missing_partial_and_invalid_values(self):
        headers = [
            "uf", "municipio", "zona", "secao", "local",
            "flavio1turno", "flavio2turno", "lula1turno", "lula2turno",
        ]
        rows = [
            ["SC", "Teste", "1", "1", "Escola", "10", "20", "5", "15"],
            ["SC", "Teste", "1", "2", "Escola", "", "30", "5", "10"],
            ["SC", "Teste", "1", "2", "Escola", "0", "30", "5", "10"],
            ["SC", "Teste", "1", "3", "Escola", "-1", "0", "2", "3"],
            ["SC", "Teste", "1", "4", "Escola", "abc", "0", "2", "3"],
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            csv_path = root / "sample.csv"
            report_path = root / "report.json"
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter=";")
                writer.writerow(headers)
                writer.writerows(rows)

            stdout = io.StringIO()
            with patch.object(sys, "argv", ["audit_dashboard_csv.py", str(csv_path), "--output", str(report_path)]):
                with contextlib.redirect_stdout(stdout):
                    result = main()

            self.assertEqual(result, 0)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            summary = report["resumo"]
            self.assertEqual(summary["linhas_de_dados"], 5)
            self.assertEqual(summary["linhas_com_chave_de_secao_duplicada"], 1)
            self.assertEqual(summary["linhas_com_voto_negativo"], 1)
            self.assertEqual(summary["linhas_com_valor_numerico_invalido"], 2)
            self.assertEqual(summary["linhas_com_votos_parciais_no_1_turno"], 1)
            self.assertEqual(summary["chaves_de_secao_unicas"], 4)


if __name__ == "__main__":
    unittest.main()
