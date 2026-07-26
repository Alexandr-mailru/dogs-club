from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import CustomUser, Review


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Введите пароль"}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Подтвердите пароль"}),
    )
    pdn_consent = forms.BooleanField(
        required=True,
        label="",
        error_messages={"required": "Нужно согласие на обработку персональных данных."},
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "phone_number", "address", "date_of_birth"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя пользователя"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Номер телефона"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Адрес"}),
            "date_of_birth": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "placeholder": "Дата рождения"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        privacy = reverse_lazy("privacy")
        self.fields["pdn_consent"].label = mark_safe(
            format_html(
                'Согласен(на) на <a href="{}" target="_blank" rel="noopener">обработку персональных данных</a> '
                "для создания аккаунта и работы клуба",
                privacy,
            )
        )
        self.fields["pdn_consent"].widget.attrs["class"] = "check-input"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя пользователя"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Пароль"}),
    )


class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "phone_number", "address", "date_of_birth", "avatar"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя пользователя"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Номер телефона"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Адрес"}),
            "date_of_birth": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "placeholder": "Дата рождения"}
            ),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Этот email уже используется другим пользователем.")
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Старый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Старый пароль"}),
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Новый пароль"}),
    )
    new_password2 = forms.CharField(
        label="Подтверждение нового пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Подтвердите новый пароль"}),
    )

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Новые пароли не совпадают.")
        return new_password2


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text", "rating"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4}),
        }

    def save(self, commit=True):
        review = super().save(commit=False)
        if commit:
            review.status = "pending"
            review.save()
        return review
