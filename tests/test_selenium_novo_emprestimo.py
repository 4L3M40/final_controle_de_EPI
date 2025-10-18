import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.django_db
def test_criar_emprestimo_via_ui_local():
    driver = webdriver.Edge()  # ou webdriver.Chrome()
    wait = WebDriverWait(driver, 12)

    try:
        # 1) Login
        driver.get("http://127.0.0.1:8000/usuarios/login/")
        wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        driver.find_element(By.ID, "id_username").send_keys("admin")
        driver.find_element(By.ID, "id_password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "form button[type=submit]").click()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        # 2) Dados via ORM
        from usuarios.models import Colaborador
        from epi.models import Epi

        colab = Colaborador.objects.create(
            nome="Maria Souza",
            cpf="98765432100",
            matricula="MAT-999",
            perfil="COLABORADOR",
            ativo=True,
        )
        epi = Epi.objects.create(
            codigo=f"EPI-{int(datetime.now().timestamp())}",
            nome="Capacete de Proteção",
            tamanho="M",
            estoque=10,
            ativo=True,
            ca_numero="1234567",
            ca_validade=timezone.now().date() + timedelta(days=365),
        )

        # 3) Abre o formulário
        driver.get("http://127.0.0.1:8000/emprestimos/novo/")
        wait.until(EC.presence_of_element_located((By.NAME, "colaborador")))

        # 4) Seleciona pelo VALUE (PK)
        Select(driver.find_element(By.NAME, "colaborador")).select_by_value(str(colab.pk))

        # 5) Previsão de devolução (datetime-local → ISO)
        prev_iso = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M")
        dt_input = driver.find_element(By.NAME, "previsao_devolucao")
        # seta via JS e dispara eventos (mais robusto)
        driver.execute_script("""
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
        """, dt_input, prev_iso)

        # 6) Item do formset pelo VALUE (PK)
        Select(driver.find_element(By.NAME, "itens-0-epi")).select_by_value(str(epi.pk))
        q = driver.find_element(By.NAME, "itens-0-quantidade")
        q.clear()
        q.send_keys("2")

        # 7) Cadastrar
        driver.find_element(By.CSS_SELECTOR, "form button.btn.btn-primary").click()

        # 8) Espera o REDIRECIONAMENTO correto (volta ao form de criação)
        wait.until(lambda d: d.current_url.rstrip("/").endswith("/emprestimos/novo"))
        # 9) Mensagem de sucesso
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-success")))
        assert "Empréstimo registrado com sucesso." in driver.page_source

    finally:
        driver.quit()
