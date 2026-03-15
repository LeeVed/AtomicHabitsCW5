from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей"""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "country",
            "avatar",
        ]
        read_only_fields = ["id"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации"""

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )  # браузер покажет звёздочки
    password2 = serializers.CharField(
        write_only=True, required=True, label="Подтверждение пароля"
    )

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "phone_number",
            "country",
            "avatar",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        # удаляет лишнее
        validated_data.pop("password2")
        # забирает пароль
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(**validated_data, password=password)
        return user
