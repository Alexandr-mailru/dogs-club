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
    path("", DogListView.as_view(), name="dog_list"),
    path("create/", DogCreateView.as_view(), name="dog_create"),
    path("<slug:slug>/", DogDetailView.as_view(), name="dog_detail"),
    path("<int:pk>/update/", DogUpdateView.as_view(), name="dog_update"),
    path("<int:pk>/delete/", DogDeleteView.as_view(), name="dog_delete"),
    path("<int:pk>/toggle-status/", ToggleDogStatusView.as_view(), name="toggle_dog_status"),
    path("cache/<int:pk>/clear/", ClearDogCacheView.as_view(), name="clear_dog_cache"),
    path("cache/clear-all/", ClearAllCacheView.as_view(), name="clear_all_cache"),
]
