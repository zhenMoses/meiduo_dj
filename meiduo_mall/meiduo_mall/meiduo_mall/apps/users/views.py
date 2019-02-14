from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.decorators import action

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin,UpdateModelMixin,ListModelMixin
from rest_framework.viewsets import GenericViewSet

from goods.models import SKU
from goods.serializers import SKUSerializer
from users import constants
from .models import User
from .serializers import UserSerializer, UserDetailSerializer, EmailSerializer, UserAddressSerializer, \
    AddressTitleSerializer,UserBrowseHistorySerializer


class UserBrowseHistoryView(CreateAPIView):
    """用户浏览商品记录"""
    serializer_class = UserBrowseHistorySerializer
    permission_classes = [IsAuthenticated]


    def get(self,request):
        """读取用户的浏览记录"""
        # 创建redis连接对象
        redis_conn = get_redis_connection('history')
        # 查询出redis中当前登录用户的浏览记录[b'1', b'2', b'3']
        sku_ids = redis_conn.lrange('hisrory_%d'% request.user.id,0,-1)

        # 把sku_id对应的sku模型取出来
        # skus = SKU.objects.filter(id__in=sku_ids)  # 此查询它会对数据进行排序处理
        # 查询sku列表数据
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)

        # 序列化器
        serializer = SKUSerializer(sku_list, many=True)

        return Response(serializer.data)






class AddressViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user

        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })


    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class EmailVerifyView(APIView):
    """激活邮箱
        为什么要用APIView,因为只有查询get操作,没有用到序列化和反序列化
    """
    def get(self,request):
        # 1.获取前token查询参数
        token=request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'},status=status.HTTP_400_BAD_REQUEST)

        # 对token解密并返回查询到的user
        user  = User.check_verify_email_token(token)
        if not user:
            return Response({'message': '无效token'},status=status.HTTP_400_BAD_REQUEST)

        # 修改user的email_active字段
        user.email_active = True
        user.save()

        return Response({'message': 'ok'})

class EmailView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user


# Create your views here.
# GET   /user/
# class UserDetailView(APIView):
#     """用户中心个人信息视图"""
#     # 指定权限,必须是通过认证的用户才能访问此接口(就是当前本网站的登录用户)
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self,request):
#         user = request.user  # 获取本次请求的用户对象
#         serializer = UserDetailSerializer  # 指定序列化器
#         return  Response(serializer.data)


class UserDetailView(RetrieveAPIView):
    """提供用户个人信息接口"""
    permission_classes = [IsAuthenticated]  # 指定权限,必须是通过认证的用户才能访问此接口(就是当前本网站的登录用户)

    serializer_class = UserDetailSerializer  # 指定序列化器

    # queryset = User.objects.all()
    def get_object(self):  # 返回指定模型对象
        return self.request.user

# POST /users/
class UserView(CreateAPIView):
    # 指定序列化器
    serializer_class = UserSerializer

# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
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

# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
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



