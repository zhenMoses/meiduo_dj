from django.conf.urls import url
from . import views

from rest_framework_jwt.views import obtain_jwt_token

urlpatterns=[
    # 注册路由
    url(r'^users/$',views.UserView.as_view()),
    # 判断用户是否存在的路由
    url(r'^usernames/(?P<username>\w{5-20})/count/$',views.UsernameCountView.as_view()),
    #判断手机号是否已存在
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9}/count/$)',views.MobileCountView.as_view()),
    url(r'^authorizations/$',obtain_jwt_token)
]