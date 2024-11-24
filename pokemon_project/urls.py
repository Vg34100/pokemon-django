# pokemon_project/urls.py
from django.contrib import admin
from django.urls import path
from pokemon import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register_user, name='register'),  # Removed 'api/'
    path('login/', views.login_user, name='login'),          # Removed 'api/'
    path('logout/', views.logout_user, name='logout'),       # Removed 'api/'
]