from rest_framework import serializers
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