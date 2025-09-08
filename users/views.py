# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView

from .forms import CustomUserCreationForm   # 👈 usamos el form custom

User = get_user_model()

class UsuarioListView(ListView):
    model = User
    template_name = "users/users_list.html"
    context_object_name = "usuarios"
    paginate_by = 20

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # login automático
            return redirect("home:index")  # ajusta según tu app home
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')