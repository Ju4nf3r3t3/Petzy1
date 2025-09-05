from django.urls import path
from .views import ProductoListView, ProductoDetailView, ProductoCreateView

app_name = "products"

urlpatterns = [
    path("", ProductoListView.as_view(), name="list"),
    path("<int:pk>/", ProductoDetailView.as_view(), name="detail"),
    path("crear/", ProductoCreateView.as_view(), name="create"),
]