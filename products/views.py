from django.views.generic import ListView, DetailView, CreateView, TemplateView
from .models import Producto, Review
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q, Avg
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages


class ProductoListView(ListView):
    model = Producto
    template_name = "products/product_list.html"
    context_object_name = "productos"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q")
        categoria = self.request.GET.get("categoria")

        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) | Q(descripcion__icontains=q)
            )

        if categoria:
            queryset = queryset.filter(categoria=categoria)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener categorías únicas para el filtro
        context['categorias'] = Producto.objects.values_list('categoria', flat=True).distinct()
        return context


class ProductoDetailView(DetailView):
    model = Producto
    template_name = "products/product_detail.html"
    context_object_name = "producto"


class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    template_name = "products/product_form.html"
    fields = ["nombre", "descripcion", "precio", "stock", "categoria", "imagen"]
    success_url = reverse_lazy("products:list")

    def form_valid(self, form):
        form.instance.vendedor = self.request.user
        messages.success(self.request, "Producto creado exitosamente!")
        return super().form_valid(form)


class TopProductosListView(ListView):
    model = Producto
    template_name = "products/top_products.html"
    context_object_name = "productos"

    def get_queryset(self):
        # Cambia el nombre de la anotación para evitar conflicto con la propiedad
        return Producto.objects.annotate(
            vendidos_total=Sum('orderitem__cantidad', default=0)  # Nombre diferente
        ).order_by("-vendidos_total")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Productos Más Vendidos"
        return context


class MasComentadosListView(ListView):
    model = Producto
    template_name = "products/top_products.html"
    context_object_name = "productos"

    def get_queryset(self):
        return Producto.objects.annotate(
            num_resenas=Count("reviews")
        ).order_by("-num_resenas")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Productos Más Comentados"
        return context


class MejorCalificadosListView(ListView):
    model = Producto
    template_name = "products/top_products.html"
    context_object_name = "productos"

    def get_queryset(self):
        return Producto.objects.annotate(
            promedio_calificacion=Avg("reviews__rating")  # Nombre diferente
        ).filter(promedio_calificacion__isnull=False).order_by("-promedio_calificacion")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Productos Mejor Calificados"
        return context


class CrearReviewView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['rating', 'comentario']
    template_name = 'products/crear_review.html'

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'pk': self.kwargs['producto_id']})

    def form_valid(self, form):
        producto = get_object_or_404(Producto, pk=self.kwargs['producto_id'])
        # Verificar si el usuario ya ha reseñado este producto
        if Review.objects.filter(producto=producto, usuario=self.request.user).exists():
            messages.error(self.request, "Ya has reseñado este producto.")
            return redirect('products:detail', pk=producto.pk)

        form.instance.producto = producto
        form.instance.usuario = self.request.user
        messages.success(self.request, "Reseña agregada exitosamente!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = get_object_or_404(Producto, pk=self.kwargs['producto_id'])
        return context