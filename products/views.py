from django.views.generic import ListView, DetailView, CreateView
from .models import Producto
from django.urls import reverse_lazy

class ProductoListView(ListView):
    model = Producto
    template_name = "products/products_list.html"
    context_object_name = "productos"


class ProductoDetailView(DetailView):
    model = Producto
    template_name = "products/products_detail.html"
    context_object_name = "producto"

class ProductoCreateView(CreateView):
    model = Producto
    template_name = "products/product_form.html"
    fields = ["nombre", "descripcion", "precio", "stock", "categoria"]  # campos editables
    success_url = reverse_lazy("products:list")  # redirige a la lista al guardar

    def form_valid(self, form):
        # asignar vendedor automáticamente al usuario logueado
        form.instance.vendedor = self.request.user
        return super().form_valid(form)