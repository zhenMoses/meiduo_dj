from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView,RetrieveAPIView
from rest_framework.permissions import IsAuthenticated


from .models import User
from .serializers import UserSerializer, UserDetailSerializer


# Create your views here.

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]  # 指定权限,必须是通过认证的用户才能访问此接口(就是当前本网站的登录用户)
    # serializer_class = '详情的序列化器'


    def get_object(self,request):
        user = request.user  # 获取本次请求的用户对象
        serializer = UserDetailSerializer  # 指定序列化器
        return  Response(serializer.data)


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



