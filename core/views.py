from rest_framework.views import APIView
from core import serializers
from rest_framework.response import Response
from core.models import CustomUser, AccountVerification, PasswordChange
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, status
from django.conf import settings
import jwt, random, string, requests
import threading
# from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

MAIL_SERVER = "https://db-mail.herokuapp.com/"
# MAIL_SERVER = "http://mailweb:8000/"


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.CustomTokenObtainPairSerializer

    # def post(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(data=request.data)
    #     try:
    #         serializer.is_valid(raise_exception=True)
    #     except TokenError as e:
    #         raise InvalidToken(e.args[0])
    #     data = serializer.validated_data
    #     return_response = Response(data = {"success" : True}, status=status.HTTP_200_OK)
    #     return_response.set_cookie(key = "refresh", value = data["refresh"], httponly=True)
    #     return_response.set_cookie(key = "access", value = data["access"], httponly=True)
    #     return return_response

class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def send_verification_mail(self, data):
        requests.post(MAIL_SERVER + "verificationmail/", data)

    def post(self, request):
        serializer = serializers.UserSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
                verification_code += str(user.id)    
                ver_obj = AccountVerification(user = user, verification_code = verification_code)
                ver_obj.save()
                data = {
                    "verification_code" : verification_code,
                    "username" : user.username,
                    "email" : user.email
                }
                threading.Thread(target = self.send_verification_mail, args = (data, )).start()
                return Response(json, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class UserNameExisits(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        username = request.data['username']
        obj = CustomUser.objects.filter(username = username)
        if len(obj) > 0 :
            return Response(data = {"message" : "UserName Exists !"})
        return Response(data = {"success" : True, "message" : "UserName Available"}, status = status.HTTP_200_OK)


class EmailExisits(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        email = request.data['email']
        obj = CustomUser.objects.filter(email = email)
        if len(obj) > 0 :
            return Response(data = {"message" : "Email Exists !"})
        return Response(data = {"success" : True, "message" : "Email Available"}, status = status.HTTP_200_OK)


class GetUserData(APIView):
    def get(self, request):
        access_token = request.headers['Authorization'].split(' ')[1]
        data = jwt.decode(access_token, settings.SECRET_KEY , 'HS256')
        user_ins = CustomUser.objects.get(id = data['user_id'])
        user_data = serializers.CustomUserSerializer(user_ins)
        return Response(data = user_data.data , status=status.HTTP_200_OK)


class VerifyUser(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request):
        verification_code = request.data['verification_code']
        v_obj = AccountVerification.objects.filter(verification_code = verification_code)
        if len(v_obj) == 0:
            return Response(data = {"message" : "Wrong Verification Code ❌"})
        v_obj = v_obj.first()
        user_ins = v_obj.user
        if user_ins.is_verified:
            return Response(data = {"message" : "Account already Verified ✔️"})
        setattr(user_ins, "is_verified", True)
        user_ins.save()
        v_obj.delete()
        return Response(data = {"message" : "Verification Successful ✔️"})


class ChangePasswordMail(APIView):
    permission_classes = (permissions.AllowAny, )

    def send_password_mail(self, data):
        requests.post(MAIL_SERVER + "sendpassmail/", data)

    def post(self, request):
        email = request.data['email']
        try:
            user_ins = CustomUser.objects.get(email = email)
            pass_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
            pass_slug += str(user_ins.id)
            filter_data = PasswordChange.objects.filter(user = user_ins)
            if len(filter_data) > 0:
                pass_obj = filter_data.first()
                setattr(pass_obj, "pass_slug", pass_slug)
                pass_obj.save()
            else:
                pass_obj = PasswordChange(user = user_ins, pass_slug = pass_slug)
                pass_obj.save()
            data = {
                "code" : pass_slug,
                "username" : user_ins.username,
                "email" : email
            }
            threading.Thread(target = self.send_password_mail, args = (data, )).start()
            return Response(status = status.HTTP_200_OK)
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)

class GoogleSocialAuthView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        serializer = serializers.GoogleSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data = data, status=status.HTTP_200_OK)


class GithubSocialAuthView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        serializer = serializers.GithubSocialAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return Response(data = data, status = status.HTTP_200_OK)

class HasAccess(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    def post(self, request):
        data = {"success" : True, "email" : request.user.email}
        return Response(data = data, status = status.HTTP_200_OK)

class VerifyAdminStatus(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    def get(self, request):
        if request.user.is_admin:
            data = {"success" : True}
        else:
            data = {"success" : False}
        return Response(data = data, status = status.HTTP_200_OK)