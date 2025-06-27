import sqlite3
import os

def fix_database():
    """Corrige a estrutura do banco de dados adicionando colunas que faltam"""
    
    db_path = 'delivery.db'
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Verificar se a tabela existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pedidos'")
        table_exists = c.fetchone()
        
        if not table_exists:
            print("Tabela não existe. Criando nova estrutura...")
            c.execute('''CREATE TABLE pedidos
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          cliente_nome TEXT, 
                          cliente_telefone TEXT, 
                          produto_nome TEXT, 
                          produto_preco REAL, 
                          quantidade INTEGER, 
                          endereco TEXT, 
                          data TEXT, 
                          sid TEXT,
                          status TEXT DEFAULT 'Pendente')''')
        else:
            print("Tabela existe. Verificando estrutura...")
            
            # Verificar colunas existentes
            c.execute("PRAGMA table_info(pedidos)")
            columns = [column[1] for column in c.fetchall()]
            print(f"Colunas existentes: {columns}")
            
            # Adicionar colunas que faltam
            if 'id' not in columns:
                print("Adicionando coluna 'id'...")
                # Para adicionar PRIMARY KEY AUTOINCREMENT, precisamos recriar a tabela
                recreate_table_with_id(c)
            
            if 'sid' not in columns:
                print("Adicionando coluna 'sid'...")
                c.execute("ALTER TABLE pedidos ADD COLUMN sid TEXT")
            
            if 'status' not in columns:
                print("Adicionando coluna 'status'...")
                c.execute("ALTER TABLE pedidos ADD COLUMN status TEXT DEFAULT 'Pendente'")
        
        conn.commit()
        print("✅ Banco de dados corrigido com sucesso!")
        
        # Verificar estrutura final
        c.execute("PRAGMA table_info(pedidos)")
        columns_final = c.fetchall()
        print("\n📋 Estrutura final da tabela:")
        for col in columns_final:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao corrigir banco: {e}")
        return False

def recreate_table_with_id(cursor):
    """Recria a tabela adicionando a coluna ID como PRIMARY KEY"""
    
    # Criar tabela temporária com nova estrutura
    cursor.execute('''CREATE TABLE pedidos_temp
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      cliente_nome TEXT, 
                      cliente_telefone TEXT, 
                      produto_nome TEXT, 
                      produto_preco REAL, 
                      quantidade INTEGER, 
                      endereco TEXT, 
                      data TEXT, 
                      sid TEXT DEFAULT NULL,
                      status TEXT DEFAULT 'Pendente')''')
    
    # Copiar dados da tabela antiga para a nova
    cursor.execute('''INSERT INTO pedidos_temp 
                      (cliente_nome, cliente_telefone, produto_nome, produto_preco, 
                       quantidade, endereco, data)
                      SELECT cliente_nome, cliente_telefone, produto_nome, produto_preco, 
                             quantidade, endereco, data
                      FROM pedidos''')
    
    # Remover tabela antiga
    cursor.execute("DROP TABLE pedidos")
    
    # Renomear tabela temporária
    cursor.execute("ALTER TABLE pedidos_temp RENAME TO pedidos")
    
    print("✅ Tabela recriada com coluna ID")

def backup_database():
    """Faz backup do banco atual antes das modificações"""
    if os.path.exists('delivery.db'):
        import shutil
        import datetime
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'delivery_backup_{timestamp}.db'
        
        try:
            shutil.copy2('delivery.db', backup_name)
            print(f"✅ Backup criado: {backup_name}")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return False
    return True

def main():
    print("🔧 Corrigindo estrutura do banco de dados...")
    print("=" * 50)
    
    # Fazer backup
    print("1. Criando backup...")
    backup_database()
    
    # Corrigir banco
    print("\n2. Corrigindo estrutura...")
    if fix_database():
        print("\n🎉 Correção concluída com sucesso!")
        print("\nAgora você pode executar o app normalmente:")
        print("streamlit run app.py")
    else:
        print("\n❌ Falha na correção. Verifique os erros acima.")

if __name__ == "__main__":
    main()