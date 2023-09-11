"""
URL configuration for rezerwacja_nip project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib.auth.views import LogoutView
from django.urls import path
from rezerwacja_nip_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('register_nip/', views.register_nip, name='register_nip'),
    path('user_nip_list/', views.user_nip_list, name='user_nip_list'),
    path('admin-nip-list/', views.admin_nip_list, name='admin_nip_list'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('import_records/', views.import_records, name='import_records'),
    path('export_records/', views.export_records, name='export_records'),
]
