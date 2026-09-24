from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from dogs.models import Breed, Dog, Pedigree

User = get_user_model()

BREEDS = [
    ("Лабрадор", "Дружелюбная подружейная порода."),
    ("Корги", "Коротколапая пастушья порода из Уэльса."),
    ("Хаски", "Северная ездовая порода."),
    ("Бигль", "Охотничья гончая с отличным нюхом."),
]

DOGS = [
    ("Барни", "Лабрадор", "Спокойный и контактный, любит апорт.", -1200),
    ("Мила", "Корги", "Любопытная, хорошо учит команды.", -900),
    ("Север", "Хаски", "Энергичный, нуждается в длинных прогулках.", -1500),
    ("Орех", "Бигль", "Ласковый истый нюхач.", -700),
    ("Дина", "Лабрадор", "Отлично ладит с детьми.", -1100),
    ("Пиксель", "Корги", "Маленький и очень общительный.", -500),
]


class Command(BaseCommand):
    help = "Демо-данные: пользователь demo и карточки собак"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "email": "demo@dogs-club.local",
                "role": "user",
            },
        )
        if created or not user.has_usable_password():
            user.set_password("demo12345")
            user.email = user.email or "demo@dogs-club.local"
            user.save()
            self.stdout.write("Создан пользователь demo / demo12345")

        breed_map = {}
        for name, description in BREEDS:
            breed, _ = Breed.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            breed_map[name] = breed

        created_dogs = 0
        for name, breed_name, description, day_offset in DOGS:
            dog, was_created = Dog.objects.update_or_create(
                name=name,
                owner=user,
                defaults={
                    "breed": breed_map[breed_name],
                    "birth_date": date.today() + timedelta(days=day_offset),
                    "description": description,
                    "is_active": True,
                },
            )
            if was_created:
                created_dogs += 1
            Pedigree.objects.get_or_create(
                dog=dog,
                defaults={
                    "registration_number": f"DEMO-{dog.pk:04d}",
                    "issued_by": "Клуб собак (демо)",
                    "issue_date": date.today() - timedelta(days=30),
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: пород {Breed.objects.count()}, "
                f"собак {Dog.objects.filter(is_active=True).count()} "
                f"(новых: {created_dogs}). Вход: demo / demo12345"
            )
        )
