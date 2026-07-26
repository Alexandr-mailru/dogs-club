from django import forms
from django.core.exceptions import ValidationError
from .models import Dog, Pedigree
from datetime import date


class DogForm(forms.ModelForm):
    """
    Форма для создания или редактирования собаки
    """

    class Meta:
        model = Dog
        fields = ['name', 'breed', 'birth_date', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'breed': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.birth_date:
            self.initial['birth_date'] = self.instance.birth_date.strftime('%Y-%m-%d')

    def clean_birth_date(self):
        """
        Валидация даты рождения: проверка, что дата не находится в будущем
        """
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            raise forms.ValidationError("Дата рождения не может быть в будущем.")
        return birth_date

    def clean(self):
        """
        Общая валидация формы
        """
        cleaned_data = super().clean()
        self.instance.clean()
        return cleaned_data


class PedigreeForm(forms.ModelForm):
    class Meta:
        model = Pedigree
        fields = ['father', 'mother', 'registration_number', 'issued_by', 'issue_date']
        labels = {
            'father': 'Отец',
            'mother': 'Мать',
            'registration_number': 'Регистрационный номер',
            'issued_by': 'Кем выдан',
            'issue_date': 'Дата выдачи',
        }
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.dog = kwargs.pop('dog', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.issue_date:
            self.initial['issue_date'] = self.instance.issue_date.strftime('%Y-%m-%d')

        def clean(self):
            cleaned_data = super().clean()
            father = cleaned_data.get('father')
            mother = cleaned_data.get('mother')

            # Собака не может быть своим же отцом или матерью
            if self.dog and (father == self.dog or mother == self.dog):
                raise ValidationError("Собака не может быть своим же отцом или матерью.")

            if father and mother and father == mother:
                raise ValidationError("Отец и мать не могут быть одной и той же собакой.")

            return cleaned_data
