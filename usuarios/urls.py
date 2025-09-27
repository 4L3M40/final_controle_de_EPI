from django.urls import path
from .views import ColaboradorCreateView, ColaboradorListView
from .views import UsuarioLoginView
from .views import UsuarioLogoutView

app_name = "usuarios"

urlpatterns = [
    path('login/', UsuarioLoginView.as_view(), name='login'),
    path('logout/', UsuarioLogoutView.as_view(), name='logout'),
    path("login/", UsuarioLoginView.as_view(), name="login"),
    path("logout/", UsuarioLogoutView.as_view(), name="logout"),
    path("", ColaboradorListView.as_view(), name="list"),
    path("novo/", ColaboradorCreateView.as_view(), name="create"),
]
