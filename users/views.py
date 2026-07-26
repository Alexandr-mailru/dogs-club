from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View,
    TemplateView,
    FormView,
    CreateView,
    ListView,
    DetailView,
    UpdateView,
)
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CustomUserUpdateForm,
    ReviewForm,
)
from .models import Review, CustomUser
from .utils import generate_random_password


# Домашняя страница
class HomeView(TemplateView):
    template_name = 'users/home.html'


# Регистрация нового пользователя
class UserCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        send_mail(
            "Регистрация в клубе собак",
            f"Здравствуйте, {user.username}! Аккаунт создан. Входите с паролем, указанным при регистрации.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
        messages.success(
            self.request,
            "Регистрация успешна! Теперь можно войти с вашим паролем.",
        )
        return redirect(self.success_url)


# Вход пользователя
class UserLoginView(FormView):
    """
    Представление для входа пользователя в систему
    """
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        """
        Обрабатывает успешную отправку формы
        """
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        # Аутентификация пользователя
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)

            messages.info(self.request, f"Добро пожаловать, {username}!")

            if hasattr(user, 'slug') and user.slug:
                # Перенаправление на страницу профиля с slug
                return redirect('profile', slug=user.slug)
            else:
                messages.warning(self.request, "Slug пользователя не найден.")
                return redirect('home')  # Замените 'home' на нужный маршрут
        else:
            messages.error(self.request, "Неверное имя пользователя или пароль.")
            return redirect('login')


# Профиль пользователя
class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/profile.html"
    context_object_name = "profile_user"
    slug_field = "slug"
    slug_url_kwarg = "slug"


# Обновление данных профиля
class UpdateProfileView(LoginRequiredMixin, FormView):
    """
    Представление для обновления данных профиля пользователя
    """
    form_class = CustomUserUpdateForm
    template_name = 'users/update_profile.html'

    def get_form_kwargs(self):
        """
        Передает текущего пользователя в форму как instance
        """
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Обрабатывает успешную отправку формы
        """
        form.save()
        messages.success(self.request, "Данные успешно обновлены!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Обрабатывает ошибки в форме.
        """
        messages.error(self.request, "Ошибка в форме. Проверьте введенные данные.")
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Генерирует URL для перенаправления после успешного обновления профиля
        """
        user = self.request.user
        return reverse('profile', kwargs={'slug': user.slug})


# Смена пароля
class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = PasswordChangeForm
    template_name = "users/change_password.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Пароль успешно изменён!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка в форме. Проверьте введенные данные.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("profile", kwargs={"slug": self.request.user.slug})


# Выход из аккаунта
class UserLogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "Вы успешно вышли из аккаунта.")
        return redirect('login')


# Генерация временного пароля
class GenerateTempPasswordView(View):
    template_name = 'users/generate_temp_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        User = get_user_model()
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Пользователь с таким email не найден.")
            return redirect('generate_temp_password')

        temp_password = generate_random_password()
        user.set_password(temp_password)
        user.save()

        subject = 'Ваш временный пароль'
        html_message = render_to_string(
            'emails/temp_password_email.html', {'temp_password': temp_password}
        )
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True,
        )

        messages.success(request, "Если SMTP настроен — временный пароль отправлен на email. Иначе смотрите консоль сервера.")
        return redirect('login')


# Список собак пользователя
class MyDogsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/my_dogs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['dogs'] = user.dogs.all()
        return context


# Список пользователей
class UserListView(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff and not self.request.user.groups.filter(name='moderators').exists():
            queryset = queryset.exclude(is_staff=True).exclude(groups__name='moderators')
        return queryset


# Подробный просмотр пользователя
class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'users/user_detail.html'
    context_object_name = 'target_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(target_user=self.object)
        return context


# Создание отзыва
class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = get_object_or_404(get_user_model(), id=self.kwargs['user_id'])
        return context

    def form_valid(self, form):
        target_user_id = self.kwargs['user_id']
        target_user = get_object_or_404(get_user_model(), id=target_user_id)

        if self.request.user == target_user:
            messages.error(self.request, "Вы не можете оставить отзыв самому себе.")
            return super().form_invalid(form)

        form.instance.author = self.request.user
        form.instance.target_user = target_user
        form.instance.status = 'pending'  # Устанавливаем статус "На рассмотрении"
        messages.success(self.request, "Отзыв успешно отправлен на модерацию!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home')  # Перенаправляем на главную страницу


# Модерация отзывов
class ReviewModerationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Review
    template_name = 'reviews/moderation_list.html'
    context_object_name = 'reviews'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(name='moderators').exists()

    def get_queryset(self):
        return Review.objects.filter(status='pending')


class ReviewModerationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    fields = ['status']
    template_name = 'reviews/moderation_update.html'
    success_url = reverse_lazy('review-moderation-list')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(name='moderators').exists()

    def form_valid(self, form):
        review = form.save(commit=False)
        if review.status == 'approved':
            review.approve()
            messages.success(self.request, f"Отзыв пользователя {review.author.username} одобрен.")
        elif review.status == 'rejected':
            review.reject()
            messages.info(self.request, f"Отзыв пользователя {review.author.username} отклонён.")
        return super().form_valid(form)
