from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['rol'] = user.rol
        token['tenant_id'] = user.tenant_id
        token['nombre'] = user.nombre_completo
        return token


class UserSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.ReadOnlyField()
    is_super_admin = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'nombre_completo',
                  'rol', 'tenant', 'is_active', 'is_super_admin', 'cedula_profesional')
        read_only_fields = ('id', 'nombre_completo', 'rol', 'tenant', 'is_super_admin')


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'rol', 'tenant', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contrasena actual es incorrecta.')
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('La nueva contrasena debe tener al menos 8 caracteres.')
        return value
