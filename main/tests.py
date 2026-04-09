from django.test import SimpleTestCase
from django.urls import reverse


class HomePageTests(SimpleTestCase):
    def test_home_page_returns_success(self):
        response = self.client.get(reverse('main:home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/home.html')

    def test_home_page_contains_key_sections(self):
        response = self.client.get(reverse('main:home'))

        self.assertContains(response, 'Готовый сайт на Django')
        self.assertContains(response, 'Корпоративный сайт')
        self.assertContains(response, 'Сайт готов к следующему этапу')
