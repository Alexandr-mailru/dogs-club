from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .legal_views import privacy

urlpatterns = [
    path("admin/", admin.site.urls),
    path("privacy/", privacy, name="privacy"),
    path("", include("users.urls")),
    path("dogs/", include("dogs.urls")),
]

# Добавляем обработку медиафайлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
