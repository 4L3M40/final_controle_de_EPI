
from django.urls import path
from . import views

app_name = "colaboradores"

urlpatterns = [
    path('csv/', views.colaboradores_csv, name='csv'),
    path("", views.list_colaboradores, name="list"),
    path("novo/", views.create_colaborador, name="create"),
    path("<int:pk>/editar/", views.update_colaborador, name="update"),
    path("<int:pk>/excluir/", views.delete_colaborador, name="delete"),
]
