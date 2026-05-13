from rest_framework import serializers

from .models import ReportExport


class ReportExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportExport
        fields = ["id", "kind", "status", "filters", "file", "error", "created_at", "completed_at"]
        read_only_fields = ["status", "file", "error", "created_at", "completed_at"]

    def create(self, validated_data):
        return ReportExport.objects.create(requested_by=self.context["request"].user, **validated_data)
