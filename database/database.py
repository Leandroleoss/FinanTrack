import sqlite3

def conectar():
    conn = sqlite3.connect("financas.db")
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
    conn.commit()
    conn.close()

def inserir_transacao(tipo, categoria, valor, data, descricao):
    conn = sqlite3.connect("financas.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transacoes (tipo, categoria, valor, data, descricao)
        VALUES (?, ?, ?, ?, ?)
    """, (tipo, categoria, valor, data, descricao))
    conn.commit()
    conn.close()
    
def listar_transacoes():
    conn = sqlite3.connect("financas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT tipo, categoria, valor, data, descricao FROM transacoes ORDER BY data DESC")
    dados = cursor.fetchall()
    conn.close()
    return dados