from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User, Role


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'roles', 'last_login']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']
        
        # Check if user exists and is suspended before authentication
        # Use case-insensitive lookup to match the login view's lowercase conversion
        try:
            user = User.objects.get(username__iexact=username)
            if not user.is_active:
                raise serializers.ValidationError('You have been suspended by the admin')
            # Use the actual username from database for authentication
            actual_username = user.username
        except User.DoesNotExist:
            actual_username = username  # User doesn't exist, let authenticate() handle it
        
        # Proceed with normal authentication using the actual username from database
        user = authenticate(username=actual_username, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        
        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    roles = serializers.ListField(child=serializers.ChoiceField(choices=Role.choices))

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'roles']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

