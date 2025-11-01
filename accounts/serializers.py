from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Admin, Role, Seller, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'role', 'email', 'first_name', 'last_name', 'phone_number', 
            'avatar_url', 'registered_at', 'updated_at'
        ]


class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Admin
        fields = '__all__'


class SellerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Seller
        fields = '__all__'


class OTPRegisterSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    temp_token = serializers.UUIDField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'otp', 'temp_token']

class TempRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password']

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone_field = 'phone_number'

    def validate(self, attrs):
        phone = attrs.get(self.phone_field)
        password = attrs.get('password')

        if phone and password:
            user = authenticate(request=self.context.get('request'), phone_number=phone, password=password)
            if not user:
                raise serializers.ValidationError("Invalid username or password")
        else:
            raise serializers.ValidationError("Empty phone or password")

        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'phone_number': user.phone_number,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
        }
        return data
