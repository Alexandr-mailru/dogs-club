from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Маршрут для админки Django
    path('admin/', admin.site.urls),

    # Маршруты для приложения users (корневой маршрут)
    path('', include('users.urls')),

    # Маршруты для приложения dogs
    path('dogs/', include('dogs.urls')),

    path('admin-only/', views.admin_only_view, name='admin_only'),

    path('moderator-only/', views.moderator_only_view, name='moderator_only'),
]

# Добавляем обработку медиафайлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
