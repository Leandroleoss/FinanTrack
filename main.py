import tkinter as tk
from tkcalendar import DateEntry
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from database.database import (
    conectar,
    inserir_transacao,
    listar_transacoes,
    excluir_transacao,
    atualizar_transacao as atualizar_transacao_db,
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
    atualizar_transacao_db(
        id_transacao,
        tipo_entry.get(),
        categoria_entry.get(),
        float(valor_entry.get()),
        data_entry.get(),
        descricao_entry.get()
    )
    janela.destroy()
    atualizar_tabela()



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
        try:
            atualizar_transacao_db(
                id_transacao,
                tipo_entry.get(),
                categoria_entry.get(),
                float(valor_entry.get()),
                data_entry.get(),
                descricao_entry.get()
            )
            status_label.config(text="Transação atualizada com sucesso!", foreground="green")
            atualizar_tabela()
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar: {e}")


    # Botão Salvar
    btn_salvar = tk.Button(janela, text="Salvar", command=salvar_edicao)
    btn_salvar.grid(row=5, column=1, pady=10, sticky="e")




def salvar_config():
    config = {
        "mes": filtro_mes.get(),
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

def calcular_saldo():
    linhas_visiveis = tabela.get_children()
    if not linhas_visiveis:
        messagebox.showinfo("Saldo", "Nenhuma transação está sendo exibida.")
        return

    total_receita = 0
    total_despesa = 0

    for linha in linhas_visiveis:
        valores = tabela.item(linha)["values"]
        tipo = valores[1]
        valor = float(valores[3])

        if tipo == "Receita":
            total_receita += valor
        elif tipo == "Despesa":
            total_despesa += valor

    saldo = total_receita - total_despesa
    cor = "green" if saldo >= 0 else "red"
    saldo_label.config(text=f"Saldo atual: R${saldo:.2f}", foreground=cor)
    messagebox.showinfo("Saldo Atual", f"Receitas: R${total_receita:.2f}\nDespesas: R${total_despesa:.2f}\n\nSaldo: R${saldo:.2f}")


# Janela principal
root = tk.Tk()
root.title("FinanTrack - Controle de Gastos")
root.geometry("950x600")

# Frames
frame_topo = ttk.Frame(root)
frame_topo.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

frame_filtros = ttk.LabelFrame(root, text="Filtros")
frame_filtros.grid(row=1, column=0, sticky="ew", padx=10)

filtro_mes = tk.StringVar()

ttk.Label(frame_filtros, text="Mês (MM/YYYY):").grid(row=2, column=0)
ttk.Entry(frame_filtros, textvariable=filtro_mes).grid(row=2, column=1)


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
DateEntry(frame_topo, textvariable=data_var, date_pattern="dd/mm/yyyy", locale="pt_BR").grid(row=1, column=3)

ttk.Label(frame_topo, text="Descrição:").grid(row=2, column=0)
ttk.Entry(frame_topo, textvariable=descricao_var, width=50).grid(row=2, column=1, columnspan=3)



# Labels de status e saldo
status_label = ttk.Label(frame_topo, text="")
status_label.grid(row=4, column=0, columnspan=4)

saldo_label = ttk.Label(frame_topo, text="Saldo atual: R$0.00", font=("Arial", 12, "bold"))
saldo_label.grid(row=5, column=0, columnspan=4, pady=5)


# Atualiza categorias
def atualizar_categorias(*args):
    tipo = tipo_var.get()
    if tipo == "Receita":
        categoria_menu['values'] = categorias_receita
    else:
        categoria_menu['values'] = categorias_despesa
    categoria_var.set("")

tipo_var.trace_add("write", lambda *args: atualizar_categorias())


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
tabela = ttk.Treeview(frame_tabela, columns=("id", "Tipo", "Categoria", "Valor", "Data", "Descrição"), show="headings")
for col in ("Tipo", "Categoria", "Valor", "Data", "Descrição"):
    tabela.heading(col, text=col)
tabela.grid(row=0, column=0, sticky="nsew")

frame_tabela.grid_rowconfigure(0, weight=1)
frame_tabela.grid_columnconfigure(0, weight=1)

tabela.tag_configure("verde", background="#d0f0c0")
tabela.tag_configure("vermelho", background="#f0d0d0")

#Botões
frame_botoes = tk.Frame(root)
frame_botoes.grid(row=1, column=0, pady=20)



btn_atualizar = tk.Button(frame_botoes, text="Atualizar", command=atualizar_transacao)
btn_atualizar.grid(row=0, column=1, padx=5)

btn_excluir = tk.Button(frame_botoes, text="Excluir", command=excluir_transacao_ui)
btn_excluir.grid(row=0, column=2, padx=5)


btn_saldo = tk.Button(frame_botoes, text="Calcular Saldo", command=calcular_saldo)
btn_saldo.grid(row=0, column=4, padx=5)




# Atualiza tabela
def atualizar_tabela():
    salvar_config()

    mes_filtro = filtro_mes.get().strip()
    if not mes_filtro:
        messagebox.showwarning("Filtro necessário", "Por favor, informe o mês (MM/YYYY) para visualizar as transações.")
        return

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
            mes_transacao = data_obj.strftime("%m/%Y")
            if mes_transacao != mes_filtro:
                continue
        except:
            continue

        cor = "verde" if tipo == "Receita" else "vermelho"
        tabela.insert("", "end", values=(id_transacao, tipo, categoria, valor, data, descricao), tags=(cor,))



btn_mostrar = tk.Button(frame_botoes, text="Mostrar Transações", command=atualizar_tabela)
btn_mostrar.grid(row=0, column=0, padx=5)

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

# Botão Cadastrar dentro do frame_topo
btn_cadastrar = tk.Button(frame_topo, text="Cadastrar", command=cadastrar_transacao)
btn_cadastrar.grid(row=3, column=3, sticky="e", pady=10)

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
    caminho = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Arquivo CSV", "*.csv")],
        title="Salvar como"
    )
    if caminho:
        exportar_para_csv(caminho)
        messagebox.showinfo("Exportação", f"Transações exportadas com sucesso para:\n{os.path.basename(caminho)}")
        status_label.config(text=f"Exportado para CSV: {os.path.basename(caminho)}", foreground="green")
    else:
        status_label.config(text="Exportação cancelada.", foreground="red")

btn_exportar = tk.Button(frame_botoes, text="Exportar CSV", command=exportar_csv)
btn_exportar.grid(row=0, column=3, padx=5)

def aplicar_filtro():
    tipo = filtro_tipo.get()
    categoria = filtro_categoria.get()
    data_inicio = filtro_data_inicio.get()
    data_fim = filtro_data_fim.get()

    transacoes = listar_transacoes()
    filtradas = []

    for transacao in transacoes:
        id_transacao, tipo_t, categoria_t, valor, data, descricao = transacao

        if tipo and tipo_t != tipo:
            continue
        if categoria and categoria.lower() not in categoria_t.lower():
            continue
        try:
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            if data_inicio:
                ini_obj = datetime.strptime(data_inicio, "%d/%m/%Y")
                if data_obj < ini_obj:
                    continue
            if data_fim:
                fim_obj = datetime.strptime(data_fim, "%d/%m/%Y")
                if data_obj > fim_obj:
                    continue
        except:
            continue

        filtradas.append(transacao)

    # Atualiza a tabela com os dados filtrados
    for linha in tabela.get_children():
        tabela.delete(linha)

    for transacao in filtradas:
        id_transacao, tipo, categoria, valor, data, descricao = transacao
        cor = "verde" if tipo == "Receita" else "vermelho"
        tabela.insert("", "end", values=(id_transacao, tipo, categoria, valor, data, descricao), tags=(cor,))

    status_label.config(text="Filtro aplicado com sucesso!", foreground="blue")






# Carrega filtros salvos e atualiza tabela
config = carregar_config()
filtro_tipo.set(config.get("tipo", ""))
filtro_categoria.set(config.get("categoria", ""))
filtro_data_inicio.set(config.get("data_inicio", ""))
filtro_data_fim.set(config.get("data_fim", ""))
filtro_mes.set(config.get("mes", ""))
#atualizar_tabela()

# Inicia interface
root.mainloop()
