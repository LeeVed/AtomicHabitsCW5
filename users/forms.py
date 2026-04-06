from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания и валидации нового пользователя"""

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите ваш email"}
        ),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Повторите пароль"}
        ),
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        label="Номер телефона",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите номер вашего телефона",
            }
        ),
    )
    country = forms.CharField(
        max_length=50,
        required=False,
        label="Страна",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Укажите название вашей страны",
            }
        ),
    )
    avatar = forms.ImageField(
        required=False,
        label="Аватар",
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем атрибут для сообщения об успехе
        self.success_message = None
        if "username" in self.fields:
            del self.fields["username"]

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "phone_number",
            "country",
            "avatar",
            "password1",
            "password2",
        )

    def clean_email(self):
        """Проверка уникальности email"""

        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def save(self, commit=True):
        """Сохраняет пользователя и устанавливает сообщение об успехе"""

        user = super().save(commit=False)

        if commit:
            user.save()
            self.success_message = f"Пользователь {user.email} успешно зарегистрирован!"

        return user
