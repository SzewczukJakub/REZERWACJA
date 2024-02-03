from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from rezerwacja_nip_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('register_nip/', views.register_nip, name='register_nip'),
    path('user_nip_list/', views.user_nip_list, name='user_nip_list'),
    path('admin-nip-list/', views.admin_nip_list, name='admin_nip_list'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('import_records/', views.import_records, name='import_records'),
    path('export_records/', views.export_records, name='export_records'),
    path('admin/update_expiration_days/<int:record_id>/', views.update_expiration_days, name='update_expiration_days'),


]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
