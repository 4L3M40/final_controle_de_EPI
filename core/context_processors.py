
def user_profile(request):
    perfis_validos = {"ADMIN","TECNICO_SST","ALMOXARIFE","COLABORADOR"}
    perfil = request.GET.get("perfil")
    if perfil and perfil in perfis_validos:
        request.session["user_perfil"] = perfil
    atual = request.session.get("user_perfil", "ADMIN")
    return {"user_perfil": atual}
