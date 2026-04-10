from django.db import models

class SiteProfile(models.Model):
    """Единая карточка магазина (контакты/адрес/соцсети)."""
    name = models.CharField(max_length=200, default="Цветочный Atrium")
    subtitle = models.CharField(max_length=300, blank=True, default="Магазин цветов, товары для праздника, доставка букетов")
    description = models.TextField(blank=True, default="")

    phone = models.CharField(max_length=50, blank=True, default="+7 (982) 726-84-00")
    address = models.CharField(max_length=300, blank=True, default="Свердловская область, Екатеринбург, ул. Краснолесья, 10/3")
    # ...поменяй на свой username/ссылку
    tg_url = models.URLField(blank=True, default="https://t.me/CHANGE_ME")
    vk_url = models.URLField(blank=True, default="https://vk.com/public211403983")
    maps_url = models.URLField(blank=True, default="https://yandex.ru/profile/7437735476?lang=ru&no-distribution=1&view-state=mini&source=wizbiz_new_map_single")

    work_hours = models.CharField(max_length=100, blank=True, default="Пн–Вс 09:00–21:00")
    yandex_rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.6)
    yandex_reviews_count = models.PositiveIntegerField(default=22)

    def __str__(self):
        return self.name

class Review(models.Model):
    author = models.CharField(max_length=120)
    stars = models.PositiveSmallIntegerField(default=5)
    text = models.TextField()
    created_at = models.DateField()

    def __str__(self):
        return f"{self.author} ({self.stars})"

class GalleryPhoto(models.Model):
    image = models.ImageField(upload_to="gallery/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo #{self.pk}"
