import unittest

from tools.audit_dashboard_national_bu import discover_resources, discover_resources_from_page


class DiscoverNationalResourcesTests(unittest.TestCase):
    def test_discovers_second_turn_zip_by_uf(self):
        resources = [
            {"name": "Primeiro turno RR", "url": "https://cdn.example/bweb_1t_RR_20261001.zip"},
            {"name": "Recurso BU AC", "url": "https://cdn.example/bweb_2t_AC_261020260742.zip"},
            {"name": "Recurso BU SP", "url": "https://cdn.example/bweb_2t_SP_261020260742.zip"},
            {"name": "Arquivo não relacionado", "url": "https://cdn.example/outro.zip"},
        ]

        found = discover_resources(resources)

        self.assertEqual(
            found,
            {
                "AC": "https://cdn.example/bweb_2t_AC_261020260742.zip",
                "SP": "https://cdn.example/bweb_2t_SP_261020260742.zip",
            },
        )

    def test_prefers_latest_version_if_uf_has_multiple_resources(self):
        resources = [
            {"url": "https://cdn.example/bweb_2t_RR_251020260700.zip"},
            {"url": "https://cdn.example/bweb_2t_RR_261020260742.zip"},
        ]

        self.assertEqual(
            discover_resources(resources),
            {"RR": "https://cdn.example/bweb_2t_RR_261020260742.zip"},
        )

    def test_discovers_rr_from_public_page_when_ckan_omits_it(self):
        page_html = """
        <a href="https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_RR_261020260742.zip">BU RR</a>
        <a href="https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_RR_051020260742.zip">BU RR 1T</a>
        """
        self.assertEqual(
            discover_resources_from_page(page_html),
            {
                "RR": "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_RR_261020260742.zip"
            },
        )

    def test_ignores_non_uf_and_non_zip_resources(self):
        resources = [
            {"url": "https://cdn.example/bweb_2t_XX_261020260742.zip"},
            {"url": "https://cdn.example/bweb_2t_RR_261020260742.csv"},
            {"url": ""},
            {},
        ]

        self.assertEqual(discover_resources(resources), {})


if __name__ == "__main__":
    unittest.main()
