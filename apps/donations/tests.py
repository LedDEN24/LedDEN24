from decimal import Decimal
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.projects.models import Project

from .models import Donation
from .services import approve_donation, register_donation

User = get_user_model()
TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="charity-test-media-")


def tearDownModule():
    shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True, MEDIA_ROOT=TEST_MEDIA_ROOT)
class DonationWorkflowTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Emergency medical care",
            short_description="Urgent care for children",
            description="Funding verified medical interventions.",
            goal_amount=Decimal("1000.00"),
            currency="USD",
            status=Project.Status.ACTIVE,
        )
        self.manager = User.objects.create_user(
            username="finance",
            email="finance@example.org",
            password="StrongPass123!",
            role=User.Role.FINANCIAL_MANAGER,
        )

    def test_register_donation_generates_references_and_transaction(self):
        donation = register_donation(
            project=self.project,
            amount=Decimal("50.00"),
            currency=Donation.Currency.USD,
            method=Donation.Method.VISA,
            donor_email="donor@example.org",
            purpose="Medical support",
        )

        self.assertTrue(donation.public_id.startswith("DN-"))
        self.assertTrue(donation.payment_reference.startswith("PAY-"))
        self.assertEqual(donation.status, Donation.Status.PENDING)
        self.assertEqual(donation.transactions.count(), 1)

    def test_approve_donation_updates_project_and_receipt(self):
        donation = register_donation(
            project=self.project,
            amount=Decimal("125.00"),
            currency=Donation.Currency.USD,
            method=Donation.Method.MASTERCARD,
            donor_email="donor@example.org",
        )

        approve_donation(donation, self.manager)
        donation.refresh_from_db()
        self.project.refresh_from_db()

        self.assertEqual(donation.status, Donation.Status.APPROVED)
        self.assertEqual(donation.approved_by, self.manager)
        self.assertEqual(self.project.raised_amount, Decimal("125.00"))

    def test_public_api_creates_anonymous_donation(self):
        client = APIClient()
        response = client.post(
            "/api/donations/",
            {
                "project": self.project.id,
                "amount": "25.00",
                "currency": "USD",
                "method": "visa",
                "donor_email": "guest@example.org",
                "is_anonymous": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], Donation.Status.PENDING)
        self.assertEqual(Donation.objects.count(), 1)
