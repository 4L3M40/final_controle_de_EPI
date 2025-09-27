
from django.contrib import admin
from django.urls import path, include
from dashboard.dashboard_views import dashboard_view

urlpatterns = [
    path("usuarios/", include("usuarios.urls", namespace="usuarios")),
    path("admin/", admin.site.urls),
    path("", dashboard_view, name="dashboard_home"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("colaboradores/", include("colaboradores.urls", namespace="colaboradores")),
    path("", include("epi.urls", namespace="epi")),
]
