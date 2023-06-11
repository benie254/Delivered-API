from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.renderers import JSONRenderer
from deliver_app.models import MyUser as User 
from deliver_app.serializers_auth import ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetSerializer, UpdateUserSerializer, UserSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAdminUser
from django.http import Http404
import sendgrid
from sendgrid.helpers.mail import *
from decouple import config 
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from django.contrib.auth.models import update_last_login
from deliver_app.tokens import account_activation_token
from knox.models import AuthToken
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
import jwt
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string

# auth views 
@permission_classes([IsAdminUser,])
class AllAdmins(APIView):
    def get_admins(self):
        try:
            return User.objects.all().filter(is_staff=True)
        except User.DoesNotExist:
            return Http404
    
    def get(self, request, format=None):
        admins = User.objects.all().fitler(is_staff=True)
        serializers = UserSerializer(admins,many=True)
        return Response(serializers.data)
    
@permission_classes([IsAdminUser,])
class UserProfiles(APIView):
    def get_users(self):
        try:
            return User.objects.all()
        except User.DoesNotExist:
            return Http404
    
    def get(self, request, format=None):
        users = User.objects.all()
        serializers = UserSerializer(users,many=True)
        return Response(serializers.data)
    
@permission_classes([AllowAny,])
class Register(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            receiver = serializer.validated_data['email']
            user = serializer.save()
            user.refresh_from_db()
            sg = sendgrid.SendGridAPIClient(api_key=config('SENDGRID_API_KEY'))
            msg = render_to_string('auth/user-welcome.html', {
                'user': username,
                'email': receiver,
            })
            message = Mail(
                from_email = Email("davinci.monalissa@gmail.com"),
                to_emails = receiver,
                subject = "You're in!",
                html_content = msg
            )
            try:
                sendgrid_client = sendgrid.SendGridAPIClient(config('SENDGRID_API_KEY'))
                response = sendgrid_client.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)
            status_code = status.HTTP_201_CREATED
            token = AuthToken.objects.create(user)
            response = {
                'success' : 'True',
                'status code' : status_code,
                'message': 'User registered  successfully',
                "token": token[1]
                }
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([AllowAny,])
class Login(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        
        try:
            token = AuthToken.objects.create(user)[1]
            update_last_login(None, user)
        except User.DoesNotExist:
            raise serializers.ValidationError('User with the given email and password does not exist!')
        response = Response()
        response.set_cookie(key='knox',value=token,httponly=True)
        response.data = {
            'token': token,
            'email': user.email,
            'username': user.username,
            'id': user.id,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        return response 
    
@permission_classes([IsAuthenticated,])
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
@permission_classes([IsAuthenticated,])
class Logout(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('knox')
        response.data = {
            'message': 'success'
        }
        return response 
    
class ChangePassword(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,IsAdminUser,)
    serializer_class = ChangePasswordSerializer

@permission_classes([AllowAny,])
class PasswordResetRequest(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            receiver = request.data['email']
            username = request.data['username']
            user = User.objects.filter(email=receiver,username=username).first()
            if user is None:
                raise AuthenticationFailed('User not found!')
                
            serializer.save()
            user_id = user.id
            current_site = get_current_site(request)
            msg = render_to_string('auth/user-pass-reset-request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user_id)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            sg = sendgrid.SendGridAPIClient(api_key=config('SENDGRID_API_KEY'))
            message = Mail(
                from_email = Email("davinci.monalissa@gmail.com"),
                to_emails = receiver,
                subject = "Password Reset Request",
                html_content= msg
            )
            try:
                sendgrid_client = sendgrid.SendGridAPIClient(config('SENDGRID_API_KEY'))
                response = sendgrid_client.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)

            status_code = status.HTTP_201_CREATED
            response = {
                'success' : 'True',
                'status code' : status_code,
                'message': 'Password reset link sent successfully. Please check your email.',
                }
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
@renderer_classes((JSONRenderer,))
@permission_classes([AllowAny,])
def activate(request, uidb64, token):
        permission_classes = (AllowAny,)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            print("found user with id:", uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            uid = force_str(urlsafe_base64_decode(uidb64))
            print("uid decoded:",uid)
            user = None 
            print("no user")
        if user is not None and account_activation_token.check_token(user, token):
            print("success")
            response = Response()
            successMsg = 'Confirmed! Activation link is valid.'
            response.data = {
                'success':successMsg,
            }
            # return response 
            return redirect('http://delivered.web.app/auth/confirmed/password/reset' + uid)
        else:
            Http404
            print("failure")
            response = Response()
            errorMsg = 'Sorry, activation link is invalid.'
            response.data = {
                'error':errorMsg,
            }
            return response
        
@permission_classes([AllowAny,IsAdminUser,])
class ResetPassword(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = PasswordResetSerializer

@permission_classes([IsAdminUser,])
class UpdateUser(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer