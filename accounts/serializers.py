from datetime import timedelta
from random import randint
from typing import override
import uuid
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.cache import caches
from django.db import transaction

from .models import Admin, Role, Seller, User, Address
from utils.validators import validate_phone_number
from utils import error_messages

auth_cache = caches['auth']

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


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[validate_phone_number])

    def validate(self, attrs):
        phone_number = attrs['phone_number']
        data = auth_cache.get(phone_number)

        if data and data.get('created_at'):
            time_diff = timezone.now() - data['created_at']
            resend_limit = timedelta(minutes=settings.PHONE_NUMBER_RESEND_OTP_MINUTES)
            if time_diff < resend_limit:
                raise serializers.ValidationError({'phone_number': error_messages.ERR_OTP_RATE_LIMIT})

        return super().validate(attrs)

    def create(self, validated_data):
        otp = randint(100000, 999999)
        temp_token = uuid.uuid4()
        phone_number = validated_data['phone_number']

        data = {
            'created_at': timezone.now(),
            'otp': otp,
            'temp_token': str(temp_token),
        }

        auth_cache.set(phone_number, data)
        return data


class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    temp_token = serializers.UUIDField()
    phone_number = serializers.CharField(max_length=20, validators=[validate_phone_number])

    def validate(self, attrs):
        phone_number = attrs['phone_number']
        temp_token = str(attrs['temp_token'])
        otp = attrs['otp']

        # Check if user with this phone number already exists and is verified
        verified_data = auth_cache.get(f'verified_{phone_number}')
        if verified_data:
            raise serializers.ValidationError({'phone_number': error_messages.ERR_USER_ALREADY_VERIFIED})

        data = auth_cache.get(phone_number)

        if not data:
            raise serializers.ValidationError({'phone_number': error_messages.ERR_OTP_EXPIRED})

        if data.get('temp_token') != temp_token:
            raise serializers.ValidationError({'temp_token': error_messages.ERR_INVALID_TEMP_TOKEN})

        if data.get('otp') != otp:
            raise serializers.ValidationError({'otp': error_messages.ERR_INVALID_OTP})

        return super().validate(attrs)

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        temp_token = str(validated_data['temp_token'])
        auth_cache.set(f'verified_{phone_number}', {'temp_token': temp_token})
        return validated_data


class RegisterSerializer(serializers.ModelSerializer):
    temp_token = serializers.UUIDField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'temp_token', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_phone_number(self, value):
        validate_phone_number(value)
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(error_messages.ERR_SHORT_PASSWORD)
        return value

    def validate(self, attrs):
        phone_number = attrs['phone_number']
        temp_token = str(attrs['temp_token'])
        
        data = auth_cache.get(f'verified_{phone_number}')

        if not data:
            raise serializers.ValidationError({'phone_number': error_messages.ERR_PHONE_NUMBER_VALIDATION_REQUIRED})

        if data.get('temp_token') != temp_token:
            raise serializers.ValidationError({'temp_token': error_messages.ERR_INVALID_TOKEN})

        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("temp_token")
        user = User.objects.create_user(password=password, **validated_data)
        
        # Clear verification cache after registration
        phone_number = validated_data['phone_number']
        auth_cache.delete(f'verified_{phone_number}')
        auth_cache.delete(phone_number)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone_field = 'phone_number'

    def validate(self, attrs):
        phone = attrs.get(self.phone_field)
        password = attrs.get('password')

        if not phone:
            raise serializers.ValidationError({"phone_number": error_messages.ERR_REQUIRED_FIELD})
        if not password:
            raise serializers.ValidationError({"password": error_messages.ERR_REQUIRED_FIELD})
            
        user = User.objects.filter(phone_number=phone).first()

        if user is None:
            raise exceptions.AuthenticationFailed(error_messages.ERR_INVALID_PHONE_OR_PASSWORD)
            
        if not user.is_active:
            raise exceptions.AuthenticationFailed(error_messages.ERR_USER_IS_NOT_ACTIVE)

        user = authenticate(request=self.context.get('request'), phone_number=phone, password=password)
        
        if user is None:
            raise exceptions.AuthenticationFailed(error_messages.ERR_INVALID_PHONE_OR_PASSWORD)

        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']

        # Check if the token is already blacklisted first
        if BlacklistedToken.objects.filter(token__token=self.token).exists():
            raise serializers.ValidationError({'refresh': error_messages.ERR_REFRESH_TOKEN_BLACKLISTED})

        try:
            RefreshToken(self.token)
        except TokenError:
            raise serializers.ValidationError({'refresh': error_messages.ERR_INVALID_REFRESH_TOKEN})

        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception:
            # Token might be expired or invalid, which is fine for logout
            pass


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'avatar_url']
        read_only_fields = ['phone_number']

    def validate_first_name(self, value):
        if len(value) < 2 or len(value) > 30:
            raise serializers.ValidationError(error_messages.ERR_INVALID_FIRST_NAME)
        return value

    def validate_last_name(self, value):
        if len(value) < 2 or len(value) > 30:
            raise serializers.ValidationError(error_messages.ERR_INVALID_LAST_NAME)
        return value

    def validate_email(self, value):
        if not value: # This handles the 'empty email' case where the error should be 'This field may not be blank.'
            raise serializers.ValidationError(error_messages.ERR_INVALID_EMAIL) # Raise INVALID_EMAIL for empty email as well as invalid format.
        serializers.EmailField().to_internal_value(value) # DRF's EmailField does more comprehensive validation.
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(error_messages.ERR_WRONG_PASSWORD)
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(error_messages.ERR_SHORT_PASSWORD)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[validate_phone_number])
    temp_token = serializers.UUIDField()
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(error_messages.ERR_SHORT_PASSWORD)
        return value

    def validate(self, attrs):
        phone_number = attrs['phone_number']
        temp_token = str(attrs['temp_token'])
        
        data = auth_cache.get(f'verified_{phone_number}')

        if not data:
            raise serializers.ValidationError({'phone_number': error_messages.ERR_PHONE_NUMBER_VALIDATION_REQUIRED})

        if data.get('temp_token') != temp_token:
            raise serializers.ValidationError({'temp_token': error_messages.ERR_INVALID_TOKEN})
        
        try:
            self.user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError({'phone_number': error_messages.ERR_USER_NOT_FOUND})

        return attrs

    def save(self, **kwargs):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()
        auth_cache.delete(f'verified_{self.user.phone_number}')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'user', 'title', 'full_address', 'postal_code',
            'city', 'latitude', 'longitude', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
