from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test


# Функции проверки ролей
def is_admin(user):
    return user.role == 'admin'


def is_moderator(user):
    return user.role in ['admin', 'moderator']


# Представление только для администраторов
@login_required
@user_passes_test(is_admin)
def admin_only_view(request):

    # Логика для страницы, доступной только администраторам
    return render(request, 'admin_only.html')


# Представление для администраторов и модераторов
@login_required
@user_passes_test(is_moderator)
def moderator_only_view(request):
    # Логика для страницы, доступной администраторам и модераторам
    return render(request, 'moderator_only.html')
