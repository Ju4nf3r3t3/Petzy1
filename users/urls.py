from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UsuarioListView, register_view
from . import views
from .views import CustomLoginView, CustomLogoutView

app_name = "users"

urlpatterns = [
    path("", UsuarioListView.as_view(), name="list"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
]
