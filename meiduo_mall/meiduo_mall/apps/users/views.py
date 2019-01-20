from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from .models import User

from .serializers import UserSerializer
# Create your views here.
class UserView(CreateAPIView):
    # 指定序列化器
    serializer_class = UserSerializer

class UsernameCountView(APIView):
    """用户是否存在"""
    def get(self,request,username):
        # 查询用户是否存在
        count = User.objects.filter(username=username).count()
        # 构造响应数据
        data={
            'username':username,
            'count':count
        }

        return Response(data)



class MobileCountView(APIView):
    """"验证手机号是否已存在"""
    def get(self,request,mobile):
        # 根据前端传来的手机号,查询这个手机号的数量,1代表已存在,0代表无
        count=User.objects.filter(mobile=mobile).count()

        data={
            'count':count,
            'mobile':mobile
        }
        return Response(data)



