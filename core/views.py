from rest_framework.views import APIView
from core import serializers
from rest_framework.response import Response
from core.models import (
    CustomUser, 
    AccountVerification, 
    PasswordChange, 
    UserProfile, 
    StaticData
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, status
from django.conf import settings
import jwt, random, string, requests, ast, json, threading


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.CustomTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def send_verification_mail(self, data):
        requests.post(settings.MAIL_SERVER + "verificationmail/", data)

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
        profile_obj = UserProfile(email = user_ins.email)
        profile_obj.save()
        if user_ins.is_verified:
            return Response(data = {"message" : "Account already Verified ✔️"})
        setattr(user_ins, "is_verified", True)
        user_ins.save()
        v_obj.delete()
        return Response(data = {"message" : "Verification Successful ✔️"})


class ChangePasswordMail(APIView):
    permission_classes = (permissions.AllowAny, )

    def send_password_mail(self, data):
        requests.post(settings.MAIL_SERVER + "sendpassmail/", data)

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

class UpdateUserProfile(APIView):
    permission_classes = (permissions.AllowAny,)

    def convert_to_list(self, data):
        try:
            return_data = ast.literal_eval(data)
        except:
            qery_list = json.dumps(data)
            return_data = ast.literal_eval(qery_list)
        return return_data
    
    def post(self, request):
        request_data = request.data
        date = request_data["date_time"].split(" ")[0]
        obj = UserProfile.objects.get(email = request_data["email"])
        setattr(obj, "score", obj.score + int(request_data["inc"]))

        if request_data["type"] == "H":
            setattr(obj, "hard_solved", obj.hard_solved + 1)
        elif request_data["type"] == "M":
            setattr(obj, "medium_solved", obj.medium_solved + 1)
        elif request_data["type"] == "E":
            setattr(obj, "easy_solved", obj.easy_solved + 1)
        
        if obj.submissions == "":   
            data = {
                    date : [int(request_data["problem_id"])]
                }
            setattr(obj, "submissions", str(data))
        else:
            list_data = self.convert_to_list(obj.submissions)
            if not list_data.get(date):
                list_data[date] = [int(request_data["problem_id"])]
            else:
                list_data[date].append(int(request_data["problem_id"]))
            setattr(obj, "submissions", str(list_data))
        obj.save()
        return Response(status = status.HTTP_200_OK)


class SetFixedData(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        request_data = request.data
        obj = StaticData.objects.all()[0]
        if request_data["type"] == "increase":
            if request_data["field"] == "easy":
                setattr(obj, "easy", obj.easy + 1)
            elif request_data["field"] == "medium":
                setattr(obj, "medium", obj.medium + 1)
            elif request_data["field"] == "hard":
                setattr(obj, "hard", obj.hard + 1)
        if request_data["type"] == "decrease":
            if request_data["field"] == "easy":
                setattr(obj, "easy", obj.easy - 1)
            elif request_data["field"] == "medium":
                setattr(obj, "medium", obj.medium - 1)
            elif request_data["field"] == "hard":
                setattr(obj, "hard", obj.hard - 1)
        obj.save()
        return Response(status = status.HTTP_200_OK)



class GetUserProfile(APIView):
    def get(self, request):
        obj = UserProfile.objects.get(email = request.user.email)
        data = serializers.UserProfileSerializer(obj)
        return Response(data = data.data, status = status.HTTP_200_OK)


class GetStaticData(APIView):
    def get(self, request):
        obj = StaticData.objects.all()[0]
        data = serializers.StaticDataSerializer(obj)
        return Response(data = data.data, status = status.HTTP_200_OK)
