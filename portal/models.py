from django.db import models


class DemoRequest(models.Model):
    company_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    role = models.CharField(max_length=150, blank=True)
    message = models.TextField(blank=True)
    agreed_to_personal_data = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.company_name} — {self.contact_name}"
