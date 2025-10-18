import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.django_db
def test_cadastrar_colaborador_local():
    driver = webdriver.Edge() 
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
        # Garante que chegou no dashboard
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        # 2) Abre a página de novo colaborador
        driver.get("http://127.0.0.1:8000/colaboradores/novo/")
        wait.until(EC.presence_of_element_located((By.NAME, "matricula")))

        # 3) Preenche campos (nomes corretos, CPF sem máscara)
        driver.find_element(By.NAME, "matricula").clear()
        driver.find_element(By.NAME, "matricula").send_keys("511338")

        driver.find_element(By.NAME, "nome").clear()
        driver.find_element(By.NAME, "nome").send_keys("Manu Souza")

        # CPF: **apenas 11 dígitos**
        driver.find_element(By.NAME, "cpf").clear()
        driver.find_element(By.NAME, "cpf").send_keys("10247878965")

        # 4) Submete
        driver.find_element(By.CSS_SELECTOR, "form button[type=submit]").click()

        # 5) Tenta encontrar o alerta de sucesso; se não achar, tenta identificar erros de formulário
        try:
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-success")))
            assert "sucesso" in driver.page_source.lower()
            assert "/colaboradores/novo/" in driver.current_url  # a view retorna para a mesma página
        except Exception:
            # Não apareceu alerta de sucesso — vamos ver se renderizou erros (ul.errorlist do Django)
            error_lists = driver.find_elements(By.CSS_SELECTOR, "ul.errorlist")
            if error_lists:
                all_errors = " | ".join(el.text for el in error_lists)
                pytest.fail(f"Formulário inválido. Erros: {all_errors}")
            else:
                # Último recurso: falha com trecho da página para análise
                page_snippet = driver.page_source[:1000].replace("\n", " ")
                pytest.fail(f"Nenhum alerta de sucesso e sem errorlist. Trecho da página: {page_snippet}")

    finally:
        driver.quit()
