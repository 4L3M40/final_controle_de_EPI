import pytest
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _uniq_code(prefix="EPI"):
    # Gera um código único para evitar colisão em execuções repetidas
    return f"{prefix}-{int(datetime.now().timestamp())}"


@pytest.mark.django_db
def test_criar_epi_via_ui_local():
    driver = webdriver.Edge()  # ou webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    try:
        # 1) Login
        driver.get("http://127.0.0.1:8000/usuarios/login/")
        wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        driver.find_element(By.ID, "id_username").clear()
        driver.find_element(By.ID, "id_username").send_keys("admin")
        driver.find_element(By.ID, "id_password").clear()
        driver.find_element(By.ID, "id_password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "form button[type=submit]").click()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))  # Dashboard

        # 2) Acessa o formulário de novo EPI
        driver.get("http://127.0.0.1:8000/epis/novo/")
        wait.until(EC.presence_of_element_located((By.ID, "id_codigo")))

        # 3) Preenche o formulário
        codigo = _uniq_code("EPI-CRIAR")
        driver.find_element(By.ID, "id_codigo").send_keys(codigo)
        driver.find_element(By.ID, "id_nome").send_keys("Luva")
        driver.find_element(By.ID, "id_tamanho").send_keys("G")
        driver.find_element(By.ID, "id_ca_numero").send_keys("CA-789")

        # Validade do CA no futuro (obrigatória quando há ca_numero)
        validade = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        driver.find_element(By.ID, "id_ca_validade").send_keys(validade)

        driver.find_element(By.ID, "id_estoque").clear()
        driver.find_element(By.ID, "id_estoque").send_keys("5")

        # 4) Envia
        driver.find_element(By.CSS_SELECTOR, "form button[type=submit]").click()

        # 5) Verifica redirecionamento e presença do item
        wait.until(EC.url_contains("/epis/"))
        page = driver.page_source
        assert "Luva de Segurança" in page or codigo in page

    finally:
        driver.quit()
