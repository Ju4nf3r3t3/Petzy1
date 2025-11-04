# users/views.py
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import ListView

from .forms import CustomUserCreationForm   # 👈 usamos el form custom

User = get_user_model()

class UsuarioListView(ListView):
    model = User
    template_name = "users/users_list.html"
    context_object_name = "usuarios"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {"label": _("Inicio"), "url": reverse_lazy("home:index")},
            {"label": _("Usuarios"), "url": ""},
        ]
        return context

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # login automático
            return redirect("home:index")  # ajusta según tu app home
    else:
        form = CustomUserCreationForm()
    context = {
        "form": form,
        "breadcrumbs": [
            {"label": _("Inicio"), "url": reverse_lazy("home:index")},
            {"label": _("Registro"), "url": ""},
        ],
    }
    return render(request, "users/register.html", context)

class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {"label": _("Inicio"), "url": reverse_lazy("home:index")},
            {"label": _("Iniciar sesión"), "url": ""},
        ]
        return context

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')