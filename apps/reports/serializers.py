from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "title", "report_type", "filters", "file", "generated_by", "generated_at"]
        read_only_fields = ["id", "file", "generated_by", "generated_at"]
