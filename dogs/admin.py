from django.contrib import admin
from .models import Breed, Dog


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Breed.
    """
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Dog.
    """
    list_display = ('name', 'breed', 'owner', 'birth_date', 'slug')
    readonly_fields = ('slug',)
    list_filter = ('breed', 'owner')
    search_fields = ('name', 'owner__username')

    def get_queryset(self, request):
        """
        Переопределяем QuerySet для оптимизации запросов.
        """
        return super().get_queryset(request).select_related('breed', 'owner')
