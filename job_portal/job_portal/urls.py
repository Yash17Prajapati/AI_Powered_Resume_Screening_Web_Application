"""
URL configuration for job_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.signup,name='signup'),
    path('send-otp/',views.send_otp),
    path('login/',views.loginpag,name='login'),
    path('admin/', admin.site.urls),
    path('system/admin/login/',views.adminlogin,name='adminlogin'),
    path('user/', include('user.urls')),
    path('recruiter/', include('recruiter.urls')),
    # path('user/user_dashboard/', views.user_dashboard, name='user_dashboard'),
    # path('recruiter/recruiter_dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('system/admin/dashboard/',views.admindashboard,name='admindashboard'),
    path('system/admin/candidate_table_details',views.candidate_details,name='candidate_details'),
    # path('start-ai-screening/', views.start_ai_screening, name='start_ai_screening')
]
