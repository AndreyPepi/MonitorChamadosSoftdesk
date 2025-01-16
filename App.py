from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter import StringVar, PhotoImage
import time
import threading
from win10toast import ToastNotifier  # Para exibir notificações

# Configurações do navegador
options = Options()
options.add_argument("--headless")  # Modo sem GUI
driver = webdriver.Firefox(options=options)

# Inicializa o ToastNotifier para notificações
toaster = ToastNotifier()

# Credenciais e URL
URL_LOGIN = "https://grupomassa.soft4.com.br/login"
USUARIO = "USER"
SENHA = "SENHA"

# Variáveis para armazenar os últimos valores de chamados
ultimo_sem_atendente = None
ultimo_sem_categoria = None

# Função para exibir uma notificação
def exibir_notificacao(titulo, mensagem):
    toaster.show_toast(titulo, mensagem, duration=5)

# Função para verificar chamados
def verificar_chamados():
    global driver, ultimo_sem_atendente, ultimo_sem_categoria
    try:
        # Acessa a página de login
        driver.get(URL_LOGIN)

        # Insere o usuário
        driver.find_element(By.XPATH, "//*[@id='auth-login']/div[1]/input").send_keys(USUARIO)

        # Insere a senha
        driver.find_element(By.XPATH, "//*[@id='auth-login']/div[2]/input").send_keys(SENHA)

        # Clica no botão de login
        driver.find_element(By.XPATH, "//*[@id='auth-login']/div[3]/button[2]/span[3]").click()

        # Aguarda a página principal carregar
        time.sleep(5)  # Ajuste conforme necessário

        # Localiza a quantidade de chamados "Sem atendente"
        sem_atendente_element = driver.find_element(By.XPATH, "//*[@id='modulo-chamado']/div[2]/div[1]/aside/div[2]/ul/li[3]/ul/li[1]/div/span/div/span[2]")
        qtd_sem_atendente = sem_atendente_element.text

        # Localiza a quantidade de chamados "Sem categoria"
        sem_categoria_element = driver.find_element(By.XPATH, "//*[@id='modulo-chamado']/div[2]/div[1]/aside/div[2]/ul/li[3]/ul/li[2]/div/span/div/span[2]")
        qtd_sem_categoria = sem_categoria_element.text

        # Verifica mudanças nos valores para notificar
        if qtd_sem_atendente != ultimo_sem_atendente:
            exibir_notificacao("Alteração em Chamados", f"Chamados Sem atendente: {qtd_sem_atendente}")  # Notificação
            ultimo_sem_atendente = qtd_sem_atendente

        if qtd_sem_categoria != ultimo_sem_categoria:
            exibir_notificacao("Alteração em Chamados", f"Chamados Sem categoria: {qtd_sem_categoria}")  # Notificação
            ultimo_sem_categoria = qtd_sem_categoria

        # Atualiza os valores na GUI
        chamados_sem_atendente.set(qtd_sem_atendente)
        chamados_sem_categoria.set(qtd_sem_categoria)

    except Exception as e:
        chamados_sem_atendente.set("Erro ao obter dados")
        chamados_sem_categoria.set(str(e))

# Função para rodar a verificação em loop
def atualizar_chamados():
    global driver
    while True:
        try:
            verificar_chamados()
            time.sleep(10)  # Intervalo de execução
        except Exception as e:
            print(f"Erro inesperado no loop: {e}")
        finally:
            # Fecha e reinicia o navegador para evitar problemas de sessão
            driver.quit()
            driver = webdriver.Firefox(options=options)

# Interface gráfica
root = tk.Tk()
root.title("Monitor de Chamados")
root.geometry("600x400")

# Carrega a imagem de fundo para o Canvas
canvas = tk.Canvas(root, width=600, height=400, highlightthickness=0)
canvas.pack(fill="both", expand=True)

bg_image = PhotoImage(file="C:/TESTES/bkd.png")
canvas.create_image(0, 0, image=bg_image, anchor="nw")

# Variáveis para os textos
chamados_sem_atendente = StringVar()
chamados_sem_categoria = StringVar()

# Configurando os valores iniciais
chamados_sem_atendente.set("Carregando...")
chamados_sem_categoria.set("Carregando...")

# Adicionando os textos ao Canvas
text_id1 = canvas.create_text(300, 150, text="Chamados Sem atendente: Carregando...", font=("Lato", 20), fill="white", anchor="center")
text_id2 = canvas.create_text(300, 200, text="Chamados Sem categoria: Carregando...", font=("Lato", 20), fill="white", anchor="center")

# Atualizando os textos com valores dinâmicos
def atualizar_textos():
    while True:
        canvas.itemconfig(text_id1, text=f"Chamados Sem atendente: {chamados_sem_atendente.get()}")
        canvas.itemconfig(text_id2, text=f"Chamados Sem categoria: {chamados_sem_categoria.get()}")
        time.sleep(1)

# Thread para evitar travamento da interface
thread_chamados = threading.Thread(target=atualizar_chamados, daemon=True)
thread_chamados.start()

thread_textos = threading.Thread(target=atualizar_textos, daemon=True)
thread_textos.start()

# Loop da interface gráfica
root.mainloop()
