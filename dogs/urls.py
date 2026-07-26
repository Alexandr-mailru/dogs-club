from django.urls import path
from .views import (
    DogListView,
    DogDetailView,
    DogCreateView,
    DogUpdateView,
    DogDeleteView,
    ClearDogCacheView,
    ClearAllCacheView,
    ToggleDogStatusView,
)

urlpatterns = [
    path('', DogListView.as_view(), name='dog_list'),
    path('dogs/<slug:slug>/', DogDetailView.as_view(), name='dog_detail'),
    path('dog/create/', DogCreateView.as_view(), name='dog_create'),
    path('dog/<int:pk>/update/', DogUpdateView.as_view(), name='dog_update'),
    path('dog/<int:pk>/delete/', DogDeleteView.as_view(), name='dog_delete'),
    path('clear-dog-cache/<int:pk>/', ClearDogCacheView.as_view(), name='clear_dog_cache'),
    path('clear-all-cache/', ClearAllCacheView.as_view(), name='clear_all_cache'),
    path('dog/<int:pk>/toggle-status/', ToggleDogStatusView.as_view(), name='toggle_dog_status'),
]
