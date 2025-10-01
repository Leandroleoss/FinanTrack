import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from database.database import conectar, inserir_transacao, listar_transacoes
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import json
import os
import subprocess

# Inicializa o banco de dados
conectar()

# Categorias por tipo
categorias_receita = ["Salário", "Pagamento", "Reembolso", "Investimentos"]
categorias_despesa = ["Alimentação", "Transporte", "Lazer", "Saúde", "Moradia"]

# Variável global para abrir último arquivo
ultimo_arquivo_exportado = ""

# Carrega filtros salvos
def carregar_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    return {}

def escolher_e_abrir_arquivo():
    caminho = filedialog.askopenfilename(
        title="Escolher arquivo para abrir",
        filetypes=[("Arquivos PDF e Excel", "*.pdf *.xlsx")]
    )
    if caminho:
        subprocess.Popen(['start', '', caminho], shell=True)
        status_label.config(text=f"Abrindo: {os.path.basename(caminho)}", foreground="blue")
    else:
        status_label.config(text="Nenhum arquivo selecionado.", foreground="red")
        
def escolher_e_visualizar_excel():
    caminho = filedialog.askopenfilename(
            title="Escolher arquivo Excel",
            filetypes=[("Planilhas Excel", "*.xlsx")]
    )
        
    if caminho:
        try:
            df = pd.read_excel(caminho)
            janela_excel = tk.Toplevel(root)
            janela_excel.title(f"Visualizando: {os.path.basename(caminho)}")
            frame_excel = ttk.Frame(janela_excel)
            frame_excel.pack(fill="both", expand=True)

            tabela_excel = ttk.Treeview(frame_excel, show="headings")
            tabela_excel.pack(fill="both", expand=True)

            tabela_excel["columns"] = list(df.columns)
            for col in df.columns:
                tabela_excel.heading(col, text=col)
                tabela_excel.column(col, width=100)

            for _, row in df.iterrows():
                tabela_excel.insert("", "end", values=list(row))

            status_label.config(text=f"Visualizando: {os.path.basename(caminho)}", foreground="blue")
        except Exception as e:
            status_label.config(text=f"Erro ao abrir Excel: {e}", foreground="red")
    else:
        status_label.config(text="Nenhum arquivo selecionado.", foreground="red")

def salvar_config():
    config = {
        "tipo": filtro_tipo.get(),
        "categoria": filtro_categoria.get(),
        "data_inicio": filtro_data_inicio.get(),
        "data_fim": filtro_data_fim.get()
    }
    with open("config.json", "w") as f:
        json.dump(config, f)

# Janela principal
root = tk.Tk()
root.title("FinanTrack - Controle de Gastos")
root.geometry("950x600")

# Frames
frame_topo = ttk.Frame(root)
frame_topo.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

frame_filtros = ttk.LabelFrame(root, text="Filtros")
frame_filtros.grid(row=1, column=0, sticky="ew", padx=10)

frame_tabela = ttk.Frame(root)
frame_tabela.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

frame_botoes = ttk.Frame(root)
frame_botoes.grid(row=3, column=0, sticky="ew", padx=10)

root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# Variáveis
tipo_var = tk.StringVar()
categoria_var = tk.StringVar()
valor_var = tk.StringVar()
data_var = tk.StringVar()
descricao_var = tk.StringVar()

filtro_tipo = tk.StringVar()
filtro_categoria = tk.StringVar()
filtro_data_inicio = tk.StringVar()
filtro_data_fim = tk.StringVar()

# Campos de entrada
ttk.Label(frame_topo, text="Tipo:").grid(row=0, column=0)
tipo_menu = ttk.Combobox(frame_topo, textvariable=tipo_var, values=["Despesa", "Receita"])
tipo_menu.grid(row=0, column=1)

ttk.Label(frame_topo, text="Categoria:").grid(row=0, column=2)
categoria_menu = ttk.Combobox(frame_topo, textvariable=categoria_var)
categoria_menu.grid(row=0, column=3)

ttk.Label(frame_topo, text="Valor (R$):").grid(row=1, column=0)
ttk.Entry(frame_topo, textvariable=valor_var).grid(row=1, column=1)

ttk.Label(frame_topo, text="Data (dd/mm/aaaa):").grid(row=1, column=2)
ttk.Entry(frame_topo, textvariable=data_var).grid(row=1, column=3)

ttk.Label(frame_topo, text="Descrição:").grid(row=2, column=0)
ttk.Entry(frame_topo, textvariable=descricao_var, width=50).grid(row=2, column=1, columnspan=3)

ttk.Button(frame_botoes, text="Escolher Arquivo", command=escolher_e_abrir_arquivo).grid(row=0, column=6, padx=5, pady=5)

ttk.Button(frame_botoes, text="Visualizar Excel", command=escolher_e_visualizar_excel).grid(row=0, column=7, padx=5, pady=5)

status_label = ttk.Label(frame_topo, text="")
status_label.grid(row=3, column=0, columnspan=4)

# Atualiza categorias
def atualizar_categorias(*args):
    tipo = tipo_var.get()
    if tipo == "Receita":
        categoria_menu['values'] = categorias_receita
    else:
        categoria_menu['values'] = categorias_despesa
    categoria_var.set("")

tipo_var.trace("w", atualizar_categorias)

# Filtros
ttk.Label(frame_filtros, text="Tipo:").grid(row=0, column=0)
ttk.Combobox(frame_filtros, textvariable=filtro_tipo, values=["", "Despesa", "Receita"]).grid(row=0, column=1)

ttk.Label(frame_filtros, text="Categoria:").grid(row=0, column=2)
ttk.Entry(frame_filtros, textvariable=filtro_categoria).grid(row=0, column=3)

ttk.Label(frame_filtros, text="Data Inicial:").grid(row=1, column=0)
ttk.Entry(frame_filtros, textvariable=filtro_data_inicio).grid(row=1, column=1)

ttk.Label(frame_filtros, text="Data Final:").grid(row=1, column=2)
ttk.Entry(frame_filtros, textvariable=filtro_data_fim).grid(row=1, column=3)

# Tabela
tabela = ttk.Treeview(frame_tabela, columns=("Tipo", "Categoria", "Valor", "Data", "Descrição"), show="headings")
for col in ("Tipo", "Categoria", "Valor", "Data", "Descrição"):
    tabela.heading(col, text=col)
tabela.grid(row=0, column=0, sticky="nsew")

frame_tabela.grid_rowconfigure(0, weight=1)
frame_tabela.grid_columnconfigure(0, weight=1)

tabela.tag_configure("verde", background="#d0f0c0")
tabela.tag_configure("vermelho", background="#f0d0d0")

# Atualiza tabela
def atualizar_tabela():
    salvar_config()
    for linha in tabela.get_children():
        tabela.delete(linha)

    transacoes = listar_transacoes()
    tipo_f = filtro_tipo.get()
    cat_f = filtro_categoria.get().lower()
    data_ini = filtro_data_inicio.get()
    data_fim = filtro_data_fim.get()

    for transacao in transacoes:
        tipo, categoria, valor, data, descricao = transacao

        if tipo_f and tipo != tipo_f:
            continue
        if cat_f and cat_f not in categoria.lower():
            continue
        try:
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            if data_ini:
                ini_obj = datetime.strptime(data_ini, "%d/%m/%Y")
                if data_obj < ini_obj:
                    continue
            if data_fim:
                fim_obj = datetime.strptime(data_fim, "%d/%m/%Y")
                if data_obj > fim_obj:
                    continue
        except:
            continue

        cor = "verde" if tipo == "Receita" else "vermelho"
        tabela.insert("", "end", values=transacao, tags=(cor,))

# Cadastrar
def cadastrar_transacao():
    try:
        valor = float(valor_var.get())
        datetime.strptime(data_var.get(), "%d/%m/%Y")
        inserir_transacao(tipo_var.get(), categoria_var.get(), valor, data_var.get(), descricao_var.get())
        status_label.config(text="Transação cadastrada com sucesso!", foreground="green")
        atualizar_tabela()
    except:
        status_label.config(text="Erro: valor ou data inválida.", foreground="red")

# Gráfico mensal
def mostrar_grafico_mensal():
    transacoes = listar_transacoes()
    resumo = {}
    for tipo, _, valor, data, _ in transacoes:
        try:
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            chave = f"{tipo} - {data_obj.strftime('%m/%Y')}"
            resumo[chave] = resumo.get(chave, 0) + valor
        except:
            continue

    if resumo:
        plt.figure(figsize=(10,6))
        plt.bar(resumo.keys(), resumo.values(), color="skyblue")
        plt.xticks(rotation=45)
        plt.title("Totais Mensais por Tipo")
        plt.ylabel("Valor (R$)")
        plt.tight_layout()
        plt.show()

# Exportar Excel
def exportar_excel():
    global ultimo_arquivo_exportado
    dados = [tabela.item(i)["values"] for i in tabela.get_children()]
    df = pd.DataFrame(dados, columns=["Tipo", "Categoria", "Valor", "Data", "Descrição"])
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
    nome_arquivo = f"transacoes_filtradas_{timestamp}.xlsx"
    df.to_excel(nome_arquivo, index=False)
    ultimo_arquivo_exportado = nome_arquivo
    status_label.config(text=f"Exportado para Excel: {nome_arquivo}", foreground="green")

# Exportar PDF
def exportar_pdf():
    global ultimo_arquivo_exportado
    dados = [tabela.item(i)["values"] for i in tabela.get_children()]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Transações Filtradas", ln=True, align="C")

    resumo = {}

    for linha in dados:
        tipo, categoria, valor, data, descricao = linha
        try:
            valor_float = float(valor)
            texto = f"{tipo} | {categoria} | R${valor_float:.2f} | {data} | {descricao}"
            pdf.cell(200, 10, txt=texto, ln=True)

            data_obj = datetime.strptime(data, "%d/%m/%Y")
            chave = f"{tipo} - {data_obj.strftime('%m/%Y')}"
            resumo[chave] = resumo.get(chave, 0) + valor_float
        except:
            continue

    pdf.ln(10)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Totais Mensais por Tipo", ln=True)

    for chave, total in resumo.items():
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"{chave}: R${total:.2f}", ln=True)

    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
    nome_arquivo = f"transacoes_filtradas_{timestamp}.pdf"
    pdf.output(nome_arquivo)
    ultimo_arquivo_exportado = nome_arquivo
    status_label.config(text=f"Exportado para PDF: {nome_arquivo}", foreground="green")

# Botões de ação
ttk.Button(frame_botoes, text="Cadastrar", command=cadastrar_transacao).grid(row=0, column=0, padx=5, pady=5)
ttk.Button(frame_botoes, text="Atualizar Tabela", command=atualizar_tabela).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(frame_botoes, text="Gráfico Mensal", command=mostrar_grafico_mensal).grid(row=0, column=2, padx=5, pady=5)
ttk.Button(frame_botoes, text="Exportar Excel", command=exportar_excel).grid(row=0, column=3, padx=5, pady=5)
ttk.Button(frame_botoes, text="Exportar PDF", command=exportar_pdf).grid(row=0, column=4, padx=5, pady=5)

# Carrega filtros salvos e atualiza tabela
config = carregar_config()
filtro_tipo.set(config.get("tipo", ""))
filtro_categoria.set(config.get("categoria", ""))
filtro_data_inicio.set(config.get("data_inicio", ""))
filtro_data_fim.set(config.get("data_fim", ""))
atualizar_tabela()

# Inicia interface
root.mainloop()
