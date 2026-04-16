from django.test import TestCase
from django.urls import reverse

from .content import get_document, get_document_sections, get_sources_payload


class PortalViewsTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse("portal:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Legal Checks RF")
        self.assertContains(response, "Официальные источники")

    def test_document_page_renders(self):
        slug = "self-check"
        document = get_document(slug)

        response = self.client.get(reverse("portal:document-detail", kwargs={"slug": slug}))

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(document)
        self.assertContains(response, document["meta"].title)

    def test_sources_page_renders_rules(self):
        response = self.client.get(reverse("portal:sources"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Правила использования")

    def test_sources_api_returns_json(self):
        response = self.client.get(reverse("portal:sources-api"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json()["project"], "Legal Checks RF")


class ContentLoaderTests(TestCase):
    def test_document_sections_include_expected_slugs(self):
        slugs = {
            document.slug
            for section in get_document_sections()
            for document in section["documents"]
        }

        self.assertIn("self-check", slugs)
        self.assertIn("overview", slugs)
        self.assertIn("credit-report-consent", slugs)

    def test_get_document_returns_expected_title(self):
        document = get_document("third-party-check")

        self.assertIsNotNone(document)
        self.assertEqual(document["meta"].title, "Проверка третьего лица по согласию")

    def test_load_sources_has_expected_source(self):
        sources = get_sources_payload()

        self.assertGreaterEqual(len(sources["sources"]), 5)
        self.assertEqual(sources["sources"][0]["id"], "fssp_ip")
