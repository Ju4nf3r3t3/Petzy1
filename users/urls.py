from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UsuarioListView, register_view

app_name = "users"

urlpatterns = [
    path("", UsuarioListView.as_view(), name="list"),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', register_view, name='register'),
]
