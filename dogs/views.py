from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django import forms

from .models import Dog, Pedigree
from .forms import DogForm, PedigreeForm
from .services import get_dog_from_cache, clear_dog_cache, clear_all_cache
from .utils import send_email


class DogListView(ListView):
    """
    Отображение списка собак с возможностью:
    Поиска по имени,
    Поиска по породе,
    Сортировки по имени, породе или дате рождения,
    Переключения между активными и деактивированными собаками.
    """
    model = Dog
    template_name = 'dogs/dog_list.html'
    context_object_name = 'dogs'
    paginate_by = 6

    def get_queryset(self):
        status = self.request.GET.get('status', 'active')
        breed_search = self.request.GET.get('breed_search', '')
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort_by', 'name')

        queryset = Dog.objects.select_related('owner', 'breed')

        user = self.request.user
        is_staff_role = (
            user.is_authenticated
            and getattr(user, 'role', None) in ['admin', 'moderator']
        )

        if is_staff_role:
            if status == 'inactive':
                queryset = queryset.filter(is_active=False)
            else:
                queryset = queryset.filter(is_active=True)
        else:
            queryset = queryset.filter(is_active=True)

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        if breed_search:
            queryset = queryset.filter(breed__name__icontains=breed_search)

        if sort_by in ['name', 'breed', 'birth_date']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['current_status'] = self.request.GET.get('status', 'active')
        context['allowed_roles'] = ['admin', 'moderator']

        context['breed_search'] = self.request.GET.get('breed_search', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'name')

        return context


class DogDetailView(DetailView):
    """
    Отображает детальную информацию о собаке с использованием кэширования.
    Увеличивает счетчик просмотров, если пользователь не является владельцем собаки.
    """
    model = Dog
    template_name = 'dogs/dog_detail.html'
    context_object_name = 'dog'

    def get_object(self, queryset=None):
        """
        Получает объект собаки из кэша или базы данных.
        Проверяет активность собаки и права доступа пользователя.
        """
        from django.http import Http404

        slug = self.kwargs.get('slug')
        pk = self.kwargs.get('pk')

        if not slug and not pk:
            raise Http404("Не указан slug или pk.")

        dog = get_dog_from_cache(slug=slug, pk=pk)

        if not dog:
            if slug:
                dog = get_object_or_404(Dog, slug=slug)
            else:
                dog = get_object_or_404(Dog, pk=pk)

        user = self.request.user
        is_staff_role = (
            user.is_authenticated
            and getattr(user, 'role', None) in ['admin', 'moderator']
        )
        if not dog.is_active and not is_staff_role:
            raise Http404("Собака не найдена.")

        if user.is_authenticated and user != dog.owner:
            Dog.objects.filter(pk=dog.pk).update(views_count=models.F('views_count') + 1)
            dog.refresh_from_db(fields=['views_count'])
        elif not user.is_authenticated:
            Dog.objects.filter(pk=dog.pk).update(views_count=models.F('views_count') + 1)
            dog.refresh_from_db(fields=['views_count'])

        return dog


class DogCreateView(LoginRequiredMixin, CreateView):
    """
    Обрабатывает создание новой собаки и её родословной
    """
    model = Dog
    form_class = DogForm
    template_name = 'dogs/dog_form.html'
    success_url = reverse_lazy('dog_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        PedigreeFormSet = inlineformset_factory(
            Dog, Pedigree, form=PedigreeForm, extra=1, can_delete=False, fk_name='dog'
        )
        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST)
        else:
            context['pedigree_formset'] = PedigreeFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        pedigree_formset = context["pedigree_formset"]

        if not pedigree_formset.is_valid():
            messages.error(self.request, "Ошибка в форме. Проверьте введенные данные.")
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()

        pedigree_formset.instance = self.object
        pedigree_formset.save()

        send_email(
            "Новая собака зарегистрирована",
            f"Вы успешно зарегистрировали собаку: {self.object.name}.",
            [self.request.user.email],
        )
        messages.success(self.request, "Собака успешно добавлена!")
        return redirect(self.get_success_url())


class DogFullForm(forms.ModelForm):
    """
    Форма для полного редактирования данных о собаке.
    Включает все поля модели Dog.
    """

    class Meta:
        model = Dog
        fields = '__all__'


class DogLimitedForm(forms.ModelForm):
    """
    Форма с ограниченным набором полей
    """

    class Meta:
        model = Dog
        exclude = ('is_active', 'owner', 'views_count')


class DogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Обрабатывает обновление информации о собаке
    Владелец, администратор или модератор могут редактировать собаку
    """
    model = Dog
    template_name = 'dogs/dog_form.html'
    success_url = reverse_lazy('dog_list')

    def get_form_class(self):
        """
        Возвращает форму в зависимости от уровня доступа пользователя
        """
        if self.request.user.is_superuser or self.request.user == self.object.owner:
            return DogFullForm
        else:
            return DogLimitedForm

    def get_context_data(self, **kwargs):
        """
        Добавляет inline formset для родословной в контекст шаблона
        """
        context = super().get_context_data(**kwargs)

        PedigreeFormSet = inlineformset_factory(
            Dog, Pedigree, form=PedigreeForm, extra=1, can_delete=False, fk_name='dog'
        )

        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST, instance=self.object)
        else:
            context['pedigree_formset'] = PedigreeFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        """
        Проверяет валидность основной формы и inline formset
        """
        context = self.get_context_data()
        pedigree_formset = context['pedigree_formset']

        if pedigree_formset.is_valid():
            response = super().form_valid(form)
            pedigree_formset.save()
            messages.success(self.request, "Информация о собаке успешно обновлена!")
            return response
        else:
            messages.error(self.request, "Ошибка в форме. Проверьте введенные данные.")
            return self.form_invalid(form)

    def test_func(self):
        """
        Проверяет права доступа пользователя для редактирования собаки
        """
        dog = self.get_object()
        user = self.request.user

        return (
            dog.owner == user or user.is_superuser or getattr(user, 'role', None) in ['admin', 'moderator']
        )


class DogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Обрабатывает удаление собаки
    Владелец, администратор или модератор могут удалить собаку
    """
    model = Dog
    template_name = 'dogs/dog_confirm_delete.html'
    success_url = reverse_lazy('dog_list')

    def test_func(self):
        dog = self.get_object()
        return (
            dog.owner == self.request.user or self.request.user.role in ['admin', 'moderator']
        )

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Собака успешно удалена!")
        return super().delete(request, *args, **kwargs)


class ClearDogCacheView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Очищает кэш для конкретной собаки (только staff/модератор)."""

    def test_func(self):
        user = self.request.user
        return user.is_staff or getattr(user, "role", None) in ("admin", "moderator")

    def get(self, request, pk):
        clear_dog_cache(pk=pk)
        return JsonResponse({"message": f"Кэш для собаки с ID {pk} очищен."})


class ClearAllCacheView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Очищает весь кэш (только staff/модератор)."""

    def test_func(self):
        user = self.request.user
        return user.is_staff or getattr(user, "role", None) in ("admin", "moderator")

    def get(self, request):
        clear_all_cache()
        return JsonResponse({"message": "Весь кэш очищен."})


class ToggleDogStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Класс для изменения статуса активности собаки
    Доступ разрешен только администраторам и модераторам
    """

    def test_func(self):
        return self.request.user.role in ['admin', 'moderator']

    def get(self, request, pk):
        # Получаем объект собаки по ID
        dog = get_object_or_404(Dog, pk=pk)

        dog.is_active = not dog.is_active
        dog.save()

        messages.success(request, f'Статус собаки "{dog.name}" изменен.')

        return redirect('dog_list')
