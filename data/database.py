import sqlite3
import os

def salvar_pedido(pedido_data):
    db_path = 'delivery.db'
    # Remove o arquivo se não for um banco válido
    if os.path.exists(db_path):
        try:
            sqlite3.connect(db_path).execute("SELECT 1")
        except sqlite3.DatabaseError:
            os.remove(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pedidos
                 (cliente_nome TEXT, cliente_telefone TEXT, produto_nome TEXT, produto_preco REAL, quantidade INTEGER, endereco TEXT)''')
    
    cliente_nome = pedido_data['cliente']['nome']
    cliente_telefone = pedido_data['cliente']['telefone']
    produto_nome = pedido_data['produto']['nome']
    produto_preco = pedido_data['produto']['preco']
    quantidade = pedido_data['quantidade']
    endereco = pedido_data['endereco']
    
    c.execute("INSERT INTO pedidos VALUES (?, ?, ?, ?, ?, ?)", (
        cliente_nome, cliente_telefone, produto_nome, produto_preco, quantidade, endereco
    ))
    conn.commit()
    conn.close()

def listar_pedidos():
    try:
        conn = sqlite3.connect('delivery.db')
        c = conn.cursor()
        c.execute("SELECT * FROM pedidos")
        return c.fetchall()
    except sqlite3.Error:
        return []
    finally:
        conn.close()