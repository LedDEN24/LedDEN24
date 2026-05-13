from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import EmailVerificationToken, SavedPaymentMethod


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "first_name", "last_name", "phone", "country", "city"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone",
            "country",
            "city",
            "avatar",
            "role",
            "email_verified",
            "marketing_consent",
        ]
        read_only_fields = ["role", "email_verified"]


class SavedPaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPaymentMethod
        fields = ["id", "method", "title", "masked_details", "metadata", "is_default", "created_at"]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        return SavedPaymentMethod.objects.create(user=self.context["request"].user, **validated_data)


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate_token(self, token):
        try:
            record = EmailVerificationToken.objects.select_related("user").get(token=token)
        except EmailVerificationToken.DoesNotExist as exc:
            raise serializers.ValidationError("Invalid verification token.") from exc
        if not record.is_valid:
            raise serializers.ValidationError("Verification token expired or already used.")
        return record

    def save(self, **kwargs):
        record = self.validated_data["token"]
        record.user.email_verified = True
        record.user.save(update_fields=["email_verified"])
        record.used_at = timezone.now()
        record.save(update_fields=["used_at"])
        return record.user
