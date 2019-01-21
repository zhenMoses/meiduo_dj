from rest_framework import serializers
import re
from django_redis import get_redis_connection
from rest_framework.settings import api_settings

from .models import User
from rest_framework.response import Response
class UserSerializer(serializers.ModelSerializer):
    """用户注册,创建用户的序列化器"""
    password2 = serializers.CharField(label='确认密码',write_only=True)
    sms_code = serializers.CharField(label='短信验证码',write_only=True)
    allow = serializers.CharField(label='同意协议',write_only=True)
    token = serializers.CharField(label='状态保持token',read_only=True)  # 增减token字段,以完成状态保持

    class Meta:
        model=User
        # 将来序列化器中需要的所有字段:'id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow'
        # 模型中已存在的字段: id', 'username', 'password', 'mobile'
        # 输出:  'id', 'username', 'mobile'
        # 输入: 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow'
        fields=['id','username','password','password2','mobile','sms_code','allow']

        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$',value):
            raise serializers.ValidationError('手机格式错误')
        return value

    def validate_allow(self,value):
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断用户短信验证码
        # 连接redis数据库
        redis_conn=get_redis_connection('verify_codes')
        mobile=data['mobile']
        real_sms_code=redis_conn.get('sms_%s' % mobile)

        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')

        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return data

    def create(self, validated_data):
        """重写create方法"""
        #  validated_data: 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow'
        # 需要存储到mysql中的字段: username  password mobile
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        user=User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        # 手动生成token

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 加载生成载荷函数
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 加载生成token函数

        payload = jwt_payload_handler(user)  # 生成载荷
        token = jwt_encode_handler(payload)  # 根据载荷生成token
        user.token =token
        return user