import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from database.database import (
    conectar,
    inserir_transacao,
    listar_transacoes,
    excluir_transacao,
    atualizar_transacao,
    exportar_para_csv
)
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

def abrir_janela_edicao(id_transacao, tipo, categoria, valor, data, descricao):
    janela = tk.Toplevel()
    janela.title("Editar Transação")

    tk.Label(janela, text="Tipo:").grid(row=0, column=0)
    tipo_entry = ttk.Combobox(janela, values=["Receita", "Despesa"])
    tipo_entry.set(tipo)
    tipo_entry.grid(row=0, column=1)

    tk.Label(janela, text="Categoria:").grid(row=1, column=0)
    categoria_entry = tk.Entry(janela)
    categoria_entry.insert(0, categoria)
    categoria_entry.grid(row=1, column=1)

    tk.Label(janela, text="Valor:").grid(row=2, column=0)
    valor_entry = tk.Entry(janela)
    valor_entry.insert(0, valor)
    valor_entry.grid(row=2, column=1)

    tk.Label(janela, text="Data (YYYY-MM-DD):").grid(row=3, column=0)
    data_entry = tk.Entry(janela)
    data_entry.insert(0, data)
    data_entry.grid(row=3, column=1)

    tk.Label(janela, text="Descrição:").grid(row=4, column=0)
    descricao_entry = tk.Entry(janela)
    descricao_entry.insert(0, descricao)
    descricao_entry.grid(row=4, column=1)

    def salvar_edicao():
        database.atualizar_transacao(
            id_transacao,
            tipo_entry.get(),
            categoria_entry.get(),
            float(valor_entry.get()),
            data_entry.get(),
            descricao_entry.get()
        )
        janela.destroy()
        atualizar_tabela()

    


def salvar_config():
    config = {
        "tipo": filtro_tipo.get(),
        "categoria": filtro_categoria.get(),
        "data_inicio": filtro_data_inicio.get(),
        "data_fim": filtro_data_fim.get()
    }
    with open("config.json", "w") as f:
        json.dump(config, f)

def atualizar_transacao():
    selecionado = tabela.focus()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione uma transação para editar.")
        return
    valores = tabela.item(selecionado, "values")
    id_transacao = int(valores[0])
    abrir_janela_edicao(*valores)

    # Aqui você pode abrir uma nova janela para editar os campos
    # ou preencher os campos existentes com os dados e salvar

def excluir_transacao_ui():
    selecionado = tabela.focus()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione uma transação para excluir.")
        return
    valores = tabela.item(selecionado, "values")
    id_transacao = valores[0]
    if messagebox.askyesno("Confirmação", "Deseja realmente excluir esta transação?"):
        excluir_transacao(id_transacao)  # Essa é a função importada do database


        atualizar_tabela()


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



btn_atualizar = tk.Button(frame_botoes, text="Atualizar", command=atualizar_transacao)
btn_atualizar.pack(side=tk.LEFT, padx=5)

btn_excluir = tk.Button(frame_botoes, text="Excluir", command=excluir_transacao_ui)

btn_excluir.pack(side=tk.LEFT, padx=5)


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
        id_transacao, tipo, categoria, valor, data, descricao = transacao

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

def exportar_csv():
    database.exportar_para_csv()
    messagebox.showinfo("Exportação", "Transações exportadas com sucesso!")


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

frame_botoes = tk.Frame(root)
frame_botoes.grid(row=1, column=0, pady=20)

btn_cadastrar = tk.Button(frame_botoes, text="Cadastrar", command=cadastrar_transacao)
btn_cadastrar.grid(row=0, column=0, padx=5)

btn_atualizar = tk.Button(frame_botoes, text="Atualizar", command=atualizar_transacao)
btn_atualizar.grid(row=0, column=1, padx=5)

btn_excluir = tk.Button(frame_botoes, text="Excluir", command=excluir_transacao)
btn_excluir.grid(row=0, column=2, padx=5)

btn_exportar = tk.Button(frame_botoes, text="Exportar CSV", command=exportar_csv)
btn_exportar.grid(row=0, column=3, padx=5)





# Carrega filtros salvos e atualiza tabela
config = carregar_config()
filtro_tipo.set(config.get("tipo", ""))
filtro_categoria.set(config.get("categoria", ""))
filtro_data_inicio.set(config.get("data_inicio", ""))
filtro_data_fim.set(config.get("data_fim", ""))
atualizar_tabela()

# Inicia interface
root.mainloop()
