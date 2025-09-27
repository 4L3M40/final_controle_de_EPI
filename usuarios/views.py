from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from .models import Colaborador
from .forms import ColaboradorForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy



class ColaboradorCreateView(CreateView):
    model = Colaborador
    form_class = ColaboradorForm
    template_name = 'colaborador_form.html'
    success_url = '/usuarios/'

class ColaboradorListView(ListView):
    model = Colaborador
    template_name = 'colaborador_list.html'
    context_object_name = 'colaboradores'


class UsuarioLoginView(LoginView):
    template_name = "usuarios/login_minimal.html"
    redirect_authenticated_user = True


class UsuarioLogoutView(LogoutView):
    next_page = reverse_lazy("usuarios:login")
