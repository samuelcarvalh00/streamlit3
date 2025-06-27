import sqlite3
import os

# Função para inicializar ou verificar o banco de dados
def init_db():
    db_path = 'delivery.db'
    # Remove o arquivo corrompido, se existir
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Arquivo corrompido {db_path} removido.")

    try:
        # Conectar ou criar o banco de dados
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # Criar tabela se não existir
        c.execute('''CREATE TABLE IF NOT EXISTS pedidos
                     (cliente_nome TEXT, cliente_telefone TEXT, produto_nome TEXT, produto_preco REAL, quantidade INTEGER, endereco TEXT, data TEXT)''')
        conn.commit()
        conn.close()
        print("Banco de dados 'delivery.db' criado ou verificado com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao criar o banco de dados: {e}")

if __name__ == "__main__":
    init_db()