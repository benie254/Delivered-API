from rest_framework import serializers
from django.contrib.auth import authenticate 
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from deliver_app.models import MyUser as User, Password

# serializers here
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ['id','username','email','password',]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
            instance.save()
        return instance 
    
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ('id','username','email','is_staff','is_superuser')

class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,validators=[validate_password])
    password2 = serializers.CharField(write_only=True,required=True)
    old_password = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = User
        fields = ('old_password','password','password2')

    def validate(self,attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password":"Password fields didn't match."})
        return attrs
    
    def update(self,instance,validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance 
    
class PasswordResetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Password 
        fields = ('username','email')

class PasswordResetSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,validators=[validate_password])
    password2 = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = User 
        fields = ('password','password')

    def validate(self,attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password":"Password fields didn't match."})
        return attrs 
    
    def update(self,instance,validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance