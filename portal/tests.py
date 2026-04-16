from django.test import TestCase
from django.urls import reverse

from .content import get_document, get_document_sections, get_sources_payload
from .models import DemoRequest


class PortalViewsTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse("portal:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Legal Checks RF")
        self.assertContains(response, "Официальные источники")
        self.assertContains(response, "Тарифы")

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

    def test_marketing_pages_render(self):
        page_expectations = [
            ("portal:demo-request", "Запросить демо"),
            ("portal:tariffs", "Пакеты для демо"),
            ("portal:privacy-policy", "Политика"),
            ("portal:personal-data-consent", "Согласие"),
            ("portal:contacts", "Связаться"),
        ]

        for route_name, expected_text in page_expectations:
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_text)

    def test_demo_request_submission_creates_record(self):
        response = self.client.post(
            reverse("portal:demo-request"),
            data={
                "name": "Иван Петров",
                "email": "ivan@example.com",
                "phone": "+7 (900) 123-45-67",
                "company": "ООО Ромашка",
                "role": "Юрист",
                "message": "Нужна демонстрация тарифов и demo-flow.",
                "agree": "on",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заявка сохранена")
        self.assertEqual(DemoRequest.objects.count(), 1)

        demo_request = DemoRequest.objects.get()
        self.assertEqual(demo_request.contact_name, "Иван Петров")
        self.assertEqual(demo_request.email, "ivan@example.com")
        self.assertEqual(demo_request.role, "Юрист")
        self.assertTrue(demo_request.agreed_to_personal_data)


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
