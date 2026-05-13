# Generated for the initial real-estate due-diligence schema.

from __future__ import annotations

import uuid

import apps.checks.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Property",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("address", models.TextField()),
                ("cadastral_number", models.CharField(db_index=True, max_length=64)),
                ("region", models.CharField(blank=True, max_length=128)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
        ),
        migrations.CreateModel(
            name="Check",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("queued", "Queued"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="created",
                        max_length=32,
                    ),
                ),
                ("risk_score", models.PositiveSmallIntegerField(default=0)),
                ("critical_risks_count", models.PositiveSmallIntegerField(default=0)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("error", models.TextField(blank=True)),
                ("ai_summary", models.JSONField(blank=True, default=dict)),
                ("aggregated_data", models.JSONField(blank=True, default=dict)),
                (
                    "property",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="checks", to="checks.property"),
                ),
                (
                    "requested_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="property_checks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("check_created", "Check created"),
                            ("check_queued", "Check queued"),
                            ("parser_started", "Parser started"),
                            ("parser_finished", "Parser finished"),
                            ("report_downloaded", "Report downloaded"),
                        ],
                        max_length=64,
                    ),
                ),
                ("object_id", models.CharField(blank=True, max_length=128)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Owner",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("full_name", apps.checks.fields.EncryptedTextField()),
                ("phone", apps.checks.fields.EncryptedTextField(blank=True)),
                ("email", apps.checks.fields.EncryptedTextField(blank=True)),
                ("inn", apps.checks.fields.EncryptedTextField(blank=True)),
                ("normalized_name_hash", models.CharField(blank=True, db_index=True, max_length=128)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "property",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="owners", to="checks.property"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ParserResult",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("source", models.CharField(db_index=True, max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[("success", "Success"), ("failed", "Failed"), ("skipped", "Skipped")],
                        max_length=16,
                    ),
                ),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("raw_reference", models.CharField(blank=True, max_length=512)),
                ("error", models.TextField(blank=True)),
                ("duration_ms", models.PositiveIntegerField(default=0)),
                (
                    "check",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="parser_results",
                        to="checks.check",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Risk",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.CharField(max_length=64)),
                ("title", models.CharField(max_length=255)),
                (
                    "severity",
                    models.CharField(
                        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
                        max_length=16,
                    ),
                ),
                ("score_impact", models.PositiveSmallIntegerField(default=0)),
                ("explanation", models.TextField()),
                ("evidence", models.JSONField(blank=True, default=dict)),
                ("recommendations", models.JSONField(blank=True, default=list)),
                (
                    "check",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="risks", to="checks.check"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CourtCase",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("case_number", models.CharField(db_index=True, max_length=128)),
                ("court_name", models.CharField(max_length=255)),
                ("role", models.CharField(blank=True, max_length=128)),
                ("status", models.CharField(blank=True, max_length=128)),
                ("amount", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ("filed_at", models.DateField(blank=True, null=True)),
                ("source_url", models.URLField(blank=True, max_length=1000)),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "check",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="court_cases",
                        to="checks.check",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Debt",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("source", models.CharField(max_length=64)),
                ("debtor_name", apps.checks.fields.EncryptedTextField()),
                ("amount", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ("proceeding_number", models.CharField(blank=True, db_index=True, max_length=128)),
                ("status", models.CharField(blank=True, max_length=128)),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "check",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="debts", to="checks.check"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BankruptcyRecord",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("debtor_name", apps.checks.fields.EncryptedTextField()),
                ("case_number", models.CharField(blank=True, db_index=True, max_length=128)),
                ("stage", models.CharField(blank=True, max_length=128)),
                ("published_at", models.DateField(blank=True, null=True)),
                ("source_url", models.URLField(blank=True, max_length=1000)),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "check",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bankruptcy_records",
                        to="checks.check",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ScrapedAd",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("source", models.CharField(max_length=64)),
                ("title", models.CharField(max_length=512)),
                ("url", models.URLField(max_length=1000)),
                ("price", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ("seller_name", apps.checks.fields.EncryptedTextField(blank=True)),
                ("phone", apps.checks.fields.EncryptedTextField(blank=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("is_suspicious", models.BooleanField(default=False)),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "check",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scraped_ads", to="checks.check"),
                ),
            ],
        ),
        migrations.AddIndex(model_name="property", index=models.Index(fields=["cadastral_number"], name="checks_prop_cadas_5fc7f9_idx")),
        migrations.AddIndex(model_name="property", index=models.Index(fields=["region"], name="checks_prop_region_31f3b5_idx")),
        migrations.AddIndex(model_name="check", index=models.Index(fields=["status"], name="checks_chec_status_a91919_idx")),
        migrations.AddIndex(model_name="check", index=models.Index(fields=["created_at"], name="checks_chec_created_5714f7_idx")),
        migrations.AddIndex(model_name="check", index=models.Index(fields=["risk_score"], name="checks_chec_risk_sc_7364fd_idx")),
        migrations.AddIndex(model_name="owner", index=models.Index(fields=["normalized_name_hash"], name="checks_owne_normali_3d1880_idx")),
        migrations.AddIndex(model_name="parserresult", index=models.Index(fields=["source", "status"], name="checks_pars_source_374aa9_idx")),
        migrations.AddConstraint(
            model_name="parserresult",
            constraint=models.UniqueConstraint(fields=("check", "source"), name="unique_parser_source_per_check"),
        ),
        migrations.AddIndex(model_name="risk", index=models.Index(fields=["code"], name="checks_risk_code_69cd99_idx")),
        migrations.AddIndex(model_name="risk", index=models.Index(fields=["severity"], name="checks_risk_severit_59dfd8_idx")),
    ]
