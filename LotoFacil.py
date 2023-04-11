# Importando bibliotecas necessárias
import random
import collections
import openpyxl
import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk

# Função para carregar dados dos sorteios anteriores do arquivo Excel
def carregar_dados_sorteios(caminho_arquivo):
    sorteios_anteriores = []

    wb = openpyxl.load_workbook(caminho_arquivo)
    ws = wb.active

    for i, row in enumerate(ws.iter_rows()):
        if i == 0:  # Pular a primeira linha (cabeçalho)
            continue
        sorteio = [int(cell.value) for cell in row[2:]]  # Ler apenas as colunas das bolas (números)
        sorteios_anteriores.append(sorteio)

    return sorteios_anteriores

# Função para calcular a frequência dos números nos sorteios anteriores
def calcular_frequencias(sorteios_anteriores):
    frequencias = collections.defaultdict(int)
    for sorteio in sorteios_anteriores:
        for numero in sorteio:
            frequencias[numero] += 1
    return frequencias
# Função para gerar uma aposta única
def gerar_aposta(frequencias):
    numeros_ordenados = sorted(frequencias.keys(), key=lambda x: -frequencias[x])
    numeros_selecionados = set()

    while len(numeros_selecionados) < 15:
        numero = random.choice(numeros_ordenados[:20])  # Escolhe um dos 15 números mais frequentes
        numeros_selecionados.add(numero)

    return sorted(numeros_selecionados)

# Função para gerar várias apostas
def gerar_apostas(frequencias, quantidade_apostas):
    apostas = []
    for _ in range(quantidade_apostas):
        aposta = gerar_aposta(frequencias)
        apostas.append(aposta)
    return apostas

# Função para selecionar o arquivo Excel com os dados dos sorteios
def selecionar_arquivo():
    caminho_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos Excel", "*.xlsx")])
    return caminho_arquivo
caminho_arquivo = ""
frequencias = {}

def selecionar_arquivo_interface():
    global caminho_arquivo
    global frequencias
    caminho_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos Excel", "*.xlsx")])
    
    if caminho_arquivo:
        sorteios_anteriores = carregar_dados_sorteios(caminho_arquivo)
        frequencias = calcular_frequencias(sorteios_anteriores)
        label_arquivo_selecionado.config(text=f"Arquivo selecionado: {os.path.basename(caminho_arquivo)}")
    else:
        label_arquivo_selecionado.config(text="Nenhum arquivo selecionado")

def atualizar_progresso(value):
    progresso['value'] = value
    app.update_idletasks()

def gerar_apostas_thread():
    if not frequencias:
        return

    try:
        quantidade_apostas = int(entry_quantidade.get())
    except ValueError:
        output.delete(1.0, tk.END)
        output.insert(tk.END, "Por favor, insira um número válido na quantidade de apostas.")
        return

    apostas = gerar_apostas(frequencias, quantidade_apostas)
    output.delete(1.0, tk.END)
    for i, aposta in enumerate(apostas):
        output.insert(tk.END, f"{aposta}\n")
        atualizar_progresso((i+1)/quantidade_apostas*100)
def gerar_apostas_interface():
    t = threading.Thread(target=gerar_apostas_thread)
    t.start()
    
def limpar_tudo():
    global caminho_arquivo
    caminho_arquivo = ""
    entry_quantidade.delete(0, tk.END)
    output.delete(1.0, tk.END)
    atualizar_progresso(0)

if __name__ == "__main__":
    app = tk.Tk()
    app.title("Gerador de Apostas Lotofácil")
    app.configure(bg="#F0F0F0")

    label_quantidade = tk.Label(app, text="Quantidade de apostas:", font=("Helvetica", 12), bg="#F0F0F0")
    label_quantidade.pack(pady=(10, 0))

    entry_quantidade = tk.Entry(app, font=("Helvetica", 12))
    entry_quantidade.pack(pady=(5, 10))

    botao_selecionar_arquivo = tk.Button(app, text="Selecionar arquivo XLSX", font=("Helvetica", 12), command=selecionar_arquivo_interface)
    botao_selecionar_arquivo.pack(pady=(5, 5))

    label_arquivo_selecionado = tk.Label(app, text="Nenhum arquivo selecionado", font=("Helvetica", 12), bg="#F0F0F0")
    label_arquivo_selecionado.pack(pady=(5, 10))

    botao_gerar = tk.Button(app, text="Gerar Apostas", font=("Helvetica", 12), command=gerar_apostas_interface)
    botao_gerar.pack(pady=(5, 5))

    botao_limpar = tk.Button(app, text="Limpar tudo", font=("Helvetica", 12), command=limpar_tudo)
    botao_limpar.pack(pady=(5, 5))

    progresso = ttk.Progressbar(app, orient="horizontal", length=200, mode="determinate")
    progresso.pack(pady=(10, 0))

    output = tk.Text(app, wrap=tk.WORD, padx=5, pady=5, width=50, height=10, font=("Helvetica", 12))
    output.pack(pady=(10, 10))

    app.mainloop()