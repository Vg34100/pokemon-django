# pokemon_project/urls.py
from django.contrib import admin
from django.urls import path
from pokemon import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register_user, name='register'),  # Removed 'api/'
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),       # Removed 'api/'
    
    path('check-session/', views.check_session, name='check_session'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    
    path('caught-pokemon/', views.catch_pokemon, name='catch_pokemon'),
    path('caught-pokemon/<int:pokemon_id>/<int:version_group_id>/', 
         views.uncatch_pokemon, name='uncatch_pokemon'),
    path('caught-pokemon/game/<int:version_group_id>/', 
         views.get_caught_pokemon, name='get_caught_pokemon'),
    path('caught-pokemon/check/<int:pokemon_id>/<int:version_group_id>/', 
         views.check_pokemon_caught, name='check_pokemon_caught'),
]