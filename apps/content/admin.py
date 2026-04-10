from django.contrib import admin
from .models import SiteProfile, Review, GalleryPhoto

@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author","stars","created_at")
    list_filter = ("stars",)
    search_fields = ("author","text")

@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    pass
