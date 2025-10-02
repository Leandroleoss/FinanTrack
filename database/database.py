import sqlite3
import csv

DB_NAME = "financas.db"

def conectar():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    valor REAL NOT NULL,
                    data TEXT NOT NULL,
                    descricao TEXT
                )
            """)
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco: {e}")

def inserir_transacao(tipo, categoria, valor, data, descricao):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transacoes (tipo, categoria, valor, data, descricao)
                VALUES (?, ?, ?, ?, ?)
            """, (tipo, categoria, valor, data, descricao))
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Erro ao inserir transação: {e}")
        return None

def listar_transacoes():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tipo, categoria, valor, data, descricao FROM transacoes ORDER BY data DESC")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao listar transações: {e}")
        return []

def buscar_por_filtros(tipo=None, categoria=None, data_inicio=None, data_fim=None):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            query = "SELECT id, tipo, categoria, valor, data, descricao FROM transacoes WHERE 1=1"
            params = []

            if tipo:
                query += " AND tipo = ?"
                params.append(tipo)
            if categoria:
                query += " AND categoria = ?"
                params.append(categoria)
            if data_inicio:
                query += " AND data >= ?"
                params.append(data_inicio)
            if data_fim:
                query += " AND data <= ?"
                params.append(data_fim)

            query += " ORDER BY data DESC"
            cursor.execute(query, params)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar por filtros: {e}")
        return []

def atualizar_transacao(id, tipo, categoria, valor, data, descricao):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transacoes
                SET tipo = ?, categoria = ?, valor = ?, data = ?, descricao = ?
                WHERE id = ?
            """, (tipo, categoria, valor, data, descricao, id))
            return cursor.rowcount
    except sqlite3.Error as e:
        print(f"Erro ao atualizar transação: {e}")
        return 0

def excluir_transacao(id):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transacoes WHERE id = ?", (id,))
            return cursor.rowcount
    except sqlite3.Error as e:
        print(f"Erro ao excluir transação: {e}")
        return 0

def exportar_para_csv(nome_arquivo="transacoes_exportadas.csv"):
    try:
        transacoes = listar_transacoes()
        with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Tipo", "Categoria", "Valor", "Data", "Descrição"])
            writer.writerows(transacoes)
        print(f"Exportado com sucesso para {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao exportar para CSV: {e}")
