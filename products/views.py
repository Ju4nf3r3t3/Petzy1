from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView

from .models import Producto, Review


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
        context['breadcrumbs'] = [
            {"label": _("Inicio"), "url": reverse_lazy("home:index")},
            {"label": _("Productos"), "url": ""},
        ]
        return context


class ProductoDetailView(DetailView):
    model = Producto
    template_name = "products/product_detail.html"
    context_object_name = "producto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto = context.get("producto")
        context['breadcrumbs'] = [
            {"label": _("Inicio"), "url": reverse_lazy("home:index")},
            {"label": _("Productos"), "url": reverse_lazy("products:list")},
            {"label": producto.nombre if producto else _("Detalle"), "url": ""},
        ]
        return context


class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    template_name = "products/product_form.html"
    fields = ["nombre", "descripcion", "precio", "stock", "categoria", "imagen"]
    success_url = reverse_lazy("products:list")

    def form_valid(self, form):
        form.instance.vendedor = self.request.user
        messages.success(self.request, _("¡Producto creado exitosamente!"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {"label": _("Inicio"), "url": reverse_lazy("home:index")},
            {"label": _("Productos"), "url": reverse_lazy("products:list")},
            {"label": _("Crear producto"), "url": ""},
        ]
        return context


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
        context['titulo'] = _("Productos Más Vendidos")
        context['breadcrumbs'] = [
            {"label": _("Inicio"), "url": reverse_lazy("home:index")},
            {"label": _("Productos"), "url": reverse_lazy("products:list")},
            {"label": context['titulo'], "url": ""},
        ]
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
        context['titulo'] = _("Productos Más Comentados")
        context['breadcrumbs'] = [
            {"label": _("Inicio"), "url": reverse_lazy("home:index")},
            {"label": _("Productos"), "url": reverse_lazy("products:list")},
            {"label": context['titulo'], "url": ""},
        ]
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
        context['titulo'] = _("Productos Mejor Calificados")
        context['breadcrumbs'] = [
            {"label": _("Inicio"), "url": reverse_lazy("home:index")},
            {"label": _("Productos"), "url": reverse_lazy("products:list")},
            {"label": context['titulo'], "url": ""},
        ]
        return context


class CrearReviewView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['rating', 'comentario']
    template_name = 'products/crear_review.html'

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'pk': self.kwargs['producto_id']})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        base_classes = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        form.fields['rating'].widget.attrs.update({'class': base_classes})
        form.fields['comentario'].widget.attrs.update({
            'class': base_classes,
            'placeholder': _("Escribe tu experiencia con este producto..."),
            'rows': 4,
        })
        return form

    def form_valid(self, form):
        producto = get_object_or_404(Producto, pk=self.kwargs['producto_id'])
        # Verificar si el usuario ya ha reseñado este producto
        if Review.objects.filter(producto=producto, usuario=self.request.user).exists():
            messages.error(self.request, _("Ya has reseñado este producto."))
            return redirect('products:detail', pk=producto.pk)

        form.instance.producto = producto
        form.instance.usuario = self.request.user
        messages.success(self.request, _("¡Reseña agregada exitosamente!"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = get_object_or_404(Producto, pk=self.kwargs['producto_id'])
        context['breadcrumbs'] = [
            {"label": _("Inicio"), "url": reverse_lazy("home:index")},
            {"label": _("Productos"), "url": reverse_lazy("products:list")},
            {"label": context['producto'].nombre, "url": context['producto'].get_absolute_url()},
            {"label": _("Crear reseña"), "url": ""},
        ]
        return context


def productos_disponibles_api(request):
    """Servicio web que expone la lista de productos disponibles."""

    productos = Producto.objects.filter(stock__gt=0).order_by("nombre")
    results = [
        {
            "id": producto.pk,
            "name": producto.nombre,
            "category": producto.categoria,
            "price": float(producto.precio),
            "stock": producto.stock,
            "detail_url": request.build_absolute_uri(producto.get_absolute_url()),
            "image": request.build_absolute_uri(producto.imagen.url) if producto.imagen else None,
        }
        for producto in productos
    ]
    return JsonResponse({
        "count": len(results),
        "results": results,
    })