from django.urls import path
from .views import (
    HomeView,
    UserCreateView,
    UserLoginView,
    ProfileView,
    MyDogsView,
    UpdateProfileView,
    ChangePasswordView,
    UserLogoutView,
    GenerateTempPasswordView,
    UserListView,
    UserDetailView,
    ReviewCreateView,
    ReviewModerationListView,
    ReviewModerationUpdateView,
)

urlpatterns = [
    # Домашняя страница
    path('', HomeView.as_view(), name='home'),

    # Регистрация нового пользователя
    path('register/', UserCreateView.as_view(), name='register'),

    # Вход в аккаунт
    path('login/', UserLoginView.as_view(), name='login'),

    # Просмотр профиля
    path('profile/<slug:slug>/', ProfileView.as_view(), name='profile'),

    # Список собак пользователя
    path('my-dogs/', MyDogsView.as_view(), name='my_dogs'),

    # Изменение данных аккаунта
    path('update-profile/<int:pk>/', UpdateProfileView.as_view(), name='update_profile'),

    # Смена пароля
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Выход из аккаунта
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # Генерация временного пароля (восстановление доступа)
    path('generate-temp-password/', GenerateTempPasswordView.as_view(), name='generate_temp_password'),

    # Список всех пользователей (доступно только модераторам/админам)
    path('users/', UserListView.as_view(), name='user-list'),

    # Подробный просмотр профиля пользователя (доступно только модераторам/админам)
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Создание отзыва о пользователе (доступно всем авторизованным пользователям)
    path('users/<int:user_id>/review/', ReviewCreateView.as_view(), name='review-create'),

    # Модерация отзывов (список отзывов на рассмотрении)
    path('reviews/moderation/', ReviewModerationListView.as_view(), name='review-moderation-list'),

    # Модерация отзыва (одобрение/отклонение)
    path('reviews/moderation/<int:pk>/', ReviewModerationUpdateView.as_view(), name='review-moderation-update'),
]
