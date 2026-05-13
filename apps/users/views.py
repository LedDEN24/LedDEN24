from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.donations.models import Donation
from apps.donations.serializers import DonationSerializer
from .models import EmailVerificationToken, SavedPaymentMethod
from .serializers import EmailVerificationSerializer, RegisterSerializer, SavedPaymentMethodSerializer, UserProfileSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "login"


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class SavedPaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = SavedPaymentMethodSerializer

    def get_queryset(self):
        return SavedPaymentMethod.objects.filter(user=self.request.user)


class DonationHistoryView(generics.ListAPIView):
    serializer_class = DonationSerializer

    def get_queryset(self):
        return Donation.objects.filter(donor=self.request.user).select_related("project")


class EmailVerificationView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"detail": "Email verified.", "email": user.email})


@login_required
def account_dashboard(request):
    donations = Donation.objects.filter(donor=request.user).select_related("project")[:10]
    return render(request, "account/dashboard.html", {"donations": donations, "now": timezone.now()})
