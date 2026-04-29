from .models import SiteProfile

def site_profile(request):
    profile = SiteProfile.objects.first()
    return {"site_profile": profile}
