from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='list'),
    path('crear/', views.ProductoCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProductoDetailView.as_view(), name='detail'),
    path('<int:producto_id>/crear-review/', views.CrearReviewView.as_view(), name='crear_review'),
    path('top/vendidos/', views.TopProductosListView.as_view(), name='top_vendidos'),
    path('top/comentados/', views.MasComentadosListView.as_view(), name='top_comentados'),
    path('top/calificados/', views.MejorCalificadosListView.as_view(), name='top_calificados'),
    path('api/available/', views.productos_disponibles_api, name='api_available'),
]