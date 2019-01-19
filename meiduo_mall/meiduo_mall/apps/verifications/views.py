from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.response import Response
from random import randint
from meiduo_mall.libs.yuntongxun.sms import CCP
import logging
from . import constants
# Create your views here.

logger=logging.getLogger('django')
class SMSCodeView(APIView):
    """发送短信视图"""

    def get(self,request,mobile):
        """
         GET /sms_codes/(?P<mobile>1[3-9]\d{9})/
        :param request:
        :param mobile:
        :return:
        """
        # 连接redis
        redis_conn = get_redis_connection('verify_codes')
        # 生成六位随机验证码
        smc_code='%06d' % randint(0,999999)

        logger.info(smc_code)
        # 把短信验证码缓存到redis  setex(key 过期时间, value)
        redis_conn.setex('sms_%s' % mobile,constants.SMS_CODE_REDIS_EXPIRES,smc_code)
        # 使用容联云通讯去发送短信  send_template_sms(self, to, datas, temp_id)
        CCP().send_template_sms( mobile,[smc_code,constants.SMS_CODE_REDIS_EXPIRES // 60],1)
        # 响应结果
        return Response({'message':'OK'})



        pass