# coding=utf-8
"""webkvmmgr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URL conf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from server import views as servers_views
from instance import views as instances_views
from api import views as api_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', api_views.login_view, name='index'),

    # 宿主机相关
    url(r'^server/list$', servers_views.server_list, name='server_list'),
    url(r'^server/(CAS\d{10})/(\w+)/$', servers_views.server_info),

    # 虚拟机相关
    url(r'^instance/(CAS\d{10})/(\w+)/(\w+)/$', instances_views.instance_info, name='instance'),

    # 接口相关
    url(r'^accounts/login/$', api_views.login_view, name='login'),
    url(r'^accounts/logout/$', api_views.logout_view, name='logout'),

    # 宿主机接口相关
    url(r'^api/server/$', api_views.server_api, name='server_api'),
    url(r'^api/instance/$', api_views.instance_api, name='instance_api'),
    url(r'^api/iostemp/$', api_views.iostemp_api, name='iostemp_api'),
    url(r'^api/vmfile/$', api_views.vmfile_api, name='vmfile_api'),
]
