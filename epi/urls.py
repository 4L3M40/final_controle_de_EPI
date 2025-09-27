
from django.urls import path
from . import views

app_name = "epi"

urlpatterns = [
    path('relatorios/', views.relatorios, name='relatorios'),
    path('epis/csv/', views.epis_csv, name='epis_csv'),
    # EPIs
    path("epis/", views.epi_list, name="list"),
    path("epis/novo/", views.epi_create, name="create"),
    path("epis/<int:pk>/editar/", views.epi_update, name="update"),
    path("epis/<int:pk>/excluir/", views.epi_delete, name="delete"),
    path('emprestimos/csv/', views.emprestimos_csv, name='emprestimos_csv'),
    # Empréstimos
    path("emprestimos/", views.emprestimo_list, name="emprestimo_list"),
    path("emprestimos/novo/", views.emprestimo_create, name="emprestimo_create"),
    path("emprestimos/<int:pk>/editar/", views.emprestimo_edit, name="emprestimo_edit"),
    path('relatorios/colaborador/csv/', views.relatorio_colaborador_csv, name='relatorio_colaborador_csv'),
    # Relatórios
    path("relatorios/colaborador/", views.relatorio_colaborador, name="relatorio_colaborador"),
]
