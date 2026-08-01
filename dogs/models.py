from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
import random
import string


def generate_random_slug(length=8):
    """
    Генерирует случайный slug заданной длины
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class Breed(models.Model):
    """
    Модель для породы собаки
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("Название породы")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Описание породы")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Порода")
        verbose_name_plural = _("Породы")


class Dog(models.Model):
    """
    Модель для собаки
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("Кличка собаки")
    )
    breed = models.ForeignKey(
        'Breed',
        on_delete=models.CASCADE,
        related_name='dogs',
        verbose_name=_("Порода")
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dogs',
        verbose_name=_("Владелец")
    )
    birth_date = models.DateField(
        verbose_name=_("Дата рождения")
    )
    photo = models.ImageField(
        upload_to='dogs/',
        blank=True,
        null=True,
        verbose_name=_("Фото собаки")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активна")
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Количество просмотров")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Описание")
    )
    slug = models.SlugField(
        unique=True, blank=True, null=True
    )

    def save(self, *args, **kwargs):
        """
        Автоматически генерирует slug, если он не был указан
        """
        if not self.slug:
            while True:
                new_slug = generate_random_slug()
                if not Dog.objects.filter(slug=new_slug).exists():
                    self.slug = new_slug
                    break
        super().save(*args, **kwargs)

    def clean(self):
        """
         Дата рождения не может быть в будущем
        """
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError(_("Дата рождения не может быть в будущем."))

    def age(self):
        """
        Вычисляет возраст собаки в годах на основе даты рождения
        """
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def __str__(self):
        return _("{name} ({breed})").format(name=self.name, breed=self.breed)

    class Meta:
        verbose_name = _("Собака")
        verbose_name_plural = _("Собаки")


class Pedigree(models.Model):
    """
    Модель для родословной собаки.
    """
    dog = models.OneToOneField(
        Dog,
        on_delete=models.CASCADE,
        related_name='pedigree'
    )
    father = models.ForeignKey(
        Dog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='father_of'
    )
    mother = models.ForeignKey(
        Dog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mother_of'
    )
    registration_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Регистрационный номер")
    )
    issued_by = models.CharField(
        max_length=100,
        verbose_name=_("Выдано кем")
    )
    issue_date = models.DateField(
        verbose_name=_("Дата выдачи")
    )

    def clean(self):
        """
        Валидация для родословной:
        1. Собака не может быть своим же отцом или матерью
        2. Отец и мать не могут быть одной и той же собакой
        """
        if self.father == self.dog or self.mother == self.dog:
            raise ValidationError(_("Собака не может быть своим же отцом или матерью."))

        if self.father and self.mother and self.father == self.mother:
            raise ValidationError(_("Отец и мать не могут быть одной и той же собакой."))

    def __str__(self):
        return f"Родословная {self.dog.name} (№{self.registration_number})"

    class Meta:
        verbose_name = _("Родословная")
        verbose_name_plural = _("Родословные")


@receiver(post_save, sender=Dog)
def notify_popular_dog(sender, instance, **kwargs):
    """Письмо владельцу при 100, 200, … просмотрах (не при 0)."""
    if kwargs.get("created"):
        return
    views = instance.views_count or 0
    if views == 0 or views % 100 != 0 or not instance.owner:
        return
    send_mail(
        f"Ваша собака {instance.name} популярна!",
        f"Карточка вашей собаки '{instance.name}' набрала {views} просмотров.",
        settings.DEFAULT_FROM_EMAIL,
        [instance.owner.email],
        fail_silently=True,
    )
