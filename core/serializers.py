from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core import github, models, google
from core.register import register_social_user
from rest_framework.exceptions import AuthenticationFailed
from datetime import date

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(CustomTokenObtainPairSerializer, cls).get_token(user)
        token["user_mail"] = user.email
        token["is_verified"] = user.is_verified
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["username"] = user.username
        token["profile_pic"] = user.profile_pic
        user.last_login = date.today()
        user.save()
        return token

class UserSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(read_only = True)
    updated = serializers.DateTimeField(read_only = True)
    password = serializers.CharField(min_length=8, write_only=True)
    class Meta:
        model = models.CustomUser
        fields = ["id", "email", "first_name", "last_name", "username", "password", "created", "updated"]
        read_only_field = ['is_active']
        extra_kwargs = {
            "password" : {'write_only' : True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = [
            'id', 
            'email', 
            'first_name', 
            'last_name', 
            'username', 
            'last_login',
            'score',
            'rank',
        ]

class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()
    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError('The token is invalid or expired. Please login again.')
        if user_data['aud'] != "64402702960-mlmnvge26bhhdf6ghgrt6viqbqhv0610.apps.googleusercontent.com":
            raise AuthenticationFailed('oops, who are you?')
        user_id = user_data['sub']
        email = user_data['email']
        name = user_data['name']
        return register_social_user(provider='google', pic=user_data['picture'], user_id=user_id, email=email, name=name)


class GithubSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()
    def validate_auth_token(self, auth_token):
        user_data = github.Github.validate(auth_token)
        try:
            user_data['email']
        except:
            raise serializers.ValidationError('The token is invalid or expired. Please login again.')
        user_id = user_data['username']
        email = user_data['email']
        name = user_data['name']
        DEFAULT_IMAGE_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEQKASvktw8z6UeZ_lqqo01vP22M7Zca9EIw&usqp=CAU"
        return register_social_user(provider='github', user_id=user_id, email=email, name=name, pic=DEFAULT_IMAGE_URL)
