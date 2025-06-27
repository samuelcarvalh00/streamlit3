import streamlit as st
import sys
import os
import json
from datetime import datetime
import sqlite3
import re
from whatsapp_api import enviar_pedido, verificar_conexao_twilio
from cep_service import buscar_cep

# Modelos
class Cliente:
    def __init__(self, nome, telefone):
        self.nome = nome
        self.telefone = telefone

class Produto:
    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco

class Pedido:
    def __init__(self, cliente, produto, quantidade, endereco):
        self.cliente = cliente
        self.produto = produto
        self.quantidade = quantidade
        self.endereco = endereco

    def to_dict(self):
        return {
            "cliente": self.cliente.nome,
            "telefone": self.cliente.telefone,
            "produto": self.produto.nome,
            "quantidade": self.quantidade,
            "preco": self.produto.preco,
            "total": self.produto.preco * self.quantidade,
            "endereco": self.endereco,
            "data": datetime.now().strftime('%d/%m/%Y %H:%M')
        }

# Funções de validação
def validar_telefone(telefone):
    """Valida e formata número de telefone brasileiro"""
    # Remove todos os caracteres não numéricos
    telefone_limpo = re.sub(r'\D', '', telefone)
    
    # Verifica se tem 10 ou 11 dígitos (sem código do país)
    if len(telefone_limpo) == 11:  # Com 9º dígito
        return f"+55{telefone_limpo}"
    elif len(telefone_limpo) == 10:  # Sem 9º dígito
        return f"+55{telefone_limpo}"
    elif len(telefone_limpo) == 13 and telefone_limpo.startswith('55'):  # Com código do país
        return f"+{telefone_limpo}"
    else:
        return None

def validar_cep(cep):
    """Valida formato do CEP"""
    cep_limpo = re.sub(r'\D', '', cep)
    return len(cep_limpo) == 8

# Funções de banco de dados
def init_db():
    try:
        if os.path.exists('delivery.db') and os.path.getsize('delivery.db') == 0:
            os.remove('delivery.db')
            st.warning("Arquivo corrompido 'delivery.db' removido.")
        
        conn = sqlite3.connect('delivery.db')
        c = conn.cursor()
        
        # Verificar se a tabela existe e tem todas as colunas necessárias
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pedidos'")
        table_exists = c.fetchone()
        
        if not table_exists:
            # Criar nova tabela com estrutura completa
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
            # Verificar e adicionar colunas que faltam
            c.execute("PRAGMA table_info(pedidos)")
            columns = [column[1] for column in c.fetchall()]
            
            if 'sid' not in columns:
                c.execute("ALTER TABLE pedidos ADD COLUMN sid TEXT")
            
            if 'status' not in columns:
                c.execute("ALTER TABLE pedidos ADD COLUMN status TEXT DEFAULT 'Pendente'")
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"Erro ao inicializar o banco de dados: {e}")
        return False

def salvar_pedido(pedido_dict, sid, status="Enviado"):
    try:
        conn = sqlite3.connect('delivery.db')
        c = conn.cursor()
        c.execute('''INSERT INTO pedidos 
                     (cliente_nome, cliente_telefone, produto_nome, produto_preco, 
                      quantidade, endereco, data, sid, status) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            pedido_dict['cliente'],
            pedido_dict['telefone'],
            pedido_dict['produto'],
            pedido_dict['preco'],
            pedido_dict['quantidade'],
            pedido_dict['endereco'],
            pedido_dict['data'],
            sid,
            status
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"Erro ao salvar pedido no banco: {e}")
        return False

def listar_pedidos():
    try:
        conn = sqlite3.connect('delivery.db')
        c = conn.cursor()
        c.execute('SELECT * FROM pedidos ORDER BY id DESC')
        pedidos = c.fetchall()
        conn.close()
        
        if not pedidos:
            return []
        
        # Converter para lista de dicionários
        colunas = ["id", "cliente", "telefone", "produto", "preco", "quantidade", 
                  "endereco", "data", "sid", "status"]
        return [dict(zip(colunas, pedido)) for pedido in pedidos]
    except sqlite3.Error as e:
        st.error(f"Erro ao listar pedidos: {e}")
        return []

def admin_page():
    st.title("📊 Painel de Administração")
    
    # Botão para testar conexão
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔧 Testar Conexão Twilio"):
            with st.spinner("Testando conexão..."):
                if verificar_conexao_twilio():
                    st.success("✅ Conexão com Twilio OK!")
                else:
                    st.error("❌ Erro na conexão com Twilio!")
    
    with col2:
        if st.button("🔄 Recarregar Pedidos"):
            st.rerun()
    
    # Listar pedidos
    pedidos = listar_pedidos()
    
    if pedidos:
        st.write(f"### 📋 Pedidos Registrados ({len(pedidos)})")
        
        for pedido in pedidos:
            with st.expander(f"Pedido #{pedido['id']} - {pedido['cliente']} - {pedido['data']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Cliente:** {pedido['cliente']}")
                    st.write(f"**Telefone:** {pedido['telefone']}")
                    st.write(f"**Produto:** {pedido['produto']}")
                    st.write(f"**Quantidade:** {pedido['quantidade']}")
                
                with col2:
                    st.write(f"**Preço:** R$ {pedido['preco']:.2f}")
                    st.write(f"**Total:** R$ {pedido['preco'] * pedido['quantidade']:.2f}")
                    st.write(f"**Status:** {pedido['status']}")
                    st.write(f"**SID:** {pedido['sid'] or 'N/A'}")
                
                st.write(f"**Endereço:** {pedido['endereco']}")
    else:
        st.info("📝 Nenhum pedido registrado ainda.")

# Configuração da página
st.set_page_config(
    page_title="Sistema de Delivery", 
    layout="wide",
    page_icon="🍕"
)

# Inicializar banco de dados
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = init_db()

# CSS personalizado
st.markdown(
    """
    <style>
    .stApp { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        text-align: center;
    }
    .card { 
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header principal
st.markdown(
    f"""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🍕 Sistema de Delivery</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">
            📅 {datetime.now().strftime('%d/%m/%Y')} | ⏰ {datetime.now().strftime('%H:%M')}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Navegação
page = st.sidebar.selectbox(
    "📋 Navegação", 
    ["🛒 Fazer Pedido", "👨‍💼 Administração"],
    key="navigation"
)

if page == "🛒 Fazer Pedido":
    # Carregar produtos
    if not os.path.exists("produtos.json"):
        produtos_default = [
            {"nome": "Pizza Margherita", "preco": 35.90},
            {"nome": "Hambúrguer Artesanal", "preco": 25.50},
            {"nome": "Refrigerante 350ml", "preco": 7.00},
            {"nome": "Batata Frita", "preco": 12.00}
        ]
        with open("produtos.json", "w", encoding='utf-8') as f:
            json.dump(produtos_default, f, ensure_ascii=False, indent=2)
    
    try:
        with open("produtos.json", "r", encoding='utf-8') as f:
            produtos_data = json.load(f)
        produtos = [Produto(p["nome"], p["preco"]) for p in produtos_data]
    except (json.JSONDecodeError, FileNotFoundError) as e:
        st.error(f"Erro ao carregar produtos: {e}")
        produtos = []

    if produtos:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Formulário de pedido
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🍽️ Seu Pedido")
            produto_selecionado = st.selectbox(
                "Escolha um produto:", 
                [p.nome for p in produtos],
                key="produto_select"
            )
            
            quantidade = st.number_input(
                "Quantidade:", 
                min_value=1, 
                max_value=10, 
                value=1,
                key="quantidade_input"
            )
            
            # Mostrar preço total
            if produto_selecionado:
                produto_obj = next(p for p in produtos if p.nome == produto_selecionado)
                total = produto_obj.preco * quantidade
                st.success(f"💰 Total: R$ {total:.2f}")
        
        with col2:
            st.subheader("📍 Dados de Entrega")
            
            nome_cliente = st.text_input("Nome completo:", key="nome_input")
            
            telefone_input = st.text_input(
                "Telefone (WhatsApp):", 
                placeholder="(11) 99999-9999",
                key="telefone_input"
            )
            
            cep_input = st.text_input("CEP:", placeholder="12345-678", key="cep_input")
            
            if st.button("🔍 Buscar Endereço", key="buscar_cep"):
                if cep_input and validar_cep(cep_input):
                    with st.spinner("Buscando endereço..."):
                        endereco_encontrado = buscar_cep(cep_input)
                        if endereco_encontrado:
                            st.session_state.endereco_auto = endereco_encontrado
                            st.success("Endereço encontrado!")
                        else:
                            st.error("CEP não encontrado!")
                else:
                    st.error("CEP inválido! Use o formato: 12345-678")
            
            endereco_completo = st.text_area(
                "Endereço completo:", 
                value=st.session_state.get("endereco_auto", ""),
                placeholder="Rua, número, complemento, bairro, cidade - Estado",
                key="endereco_input"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botão de envio
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("📱 Enviar Pedido via WhatsApp", key="enviar_pedido", type="primary"):
            # Validações
            erros = []
            
            if not nome_cliente.strip():
                erros.append("Nome é obrigatório")
            
            if not telefone_input.strip():
                erros.append("Telefone é obrigatório")
            elif not validar_telefone(telefone_input):
                erros.append("Telefone inválido! Use formato: (11) 99999-9999")
            
            if not endereco_completo.strip():
                erros.append("Endereço é obrigatório")
            
            if erros:
                for erro in erros:
                    st.error(f"❌ {erro}")
            else:
                telefone_formatado = validar_telefone(telefone_input)
                
                with st.spinner("📱 Enviando pedido..."):
                    try:
                        cliente = Cliente(nome_cliente.strip(), telefone_formatado)
                        produto = next(p for p in produtos if p.nome == produto_selecionado)
                        pedido = Pedido(cliente, produto, quantidade, endereco_completo.strip())
                        
                        # Tentar enviar
                        resposta = enviar_pedido(pedido, telefone_formatado)
                        
                        if resposta.get("success"):
                            sid = resposta.get("data")
                            
                            # Salvar no banco
                            if salvar_pedido(pedido.to_dict(), sid, "Enviado"):
                                st.success(
                                    f"✅ Pedido enviado com sucesso!\n\n"
                                    f"📱 WhatsApp: {telefone_formatado}\n"
                                    f"🕐 Horário: {datetime.now().strftime('%H:%M')}\n"
                                    f"🆔 ID: {sid[:8]}..."
                                )
                                st.balloons()
                            else:
                                st.warning("⚠️ Pedido enviado, mas houve erro ao salvar no banco.")
                        else:
                            error_msg = resposta.get('data', 'Erro desconhecido')
                            st.error(f"❌ Erro ao enviar pedido: {error_msg}")
                            
                            # Salvar como falhou
                            salvar_pedido(pedido.to_dict(), None, "Falha no envio")
                            
                    except Exception as e:
                        st.error(f"❌ Erro inesperado: {str(e)}")
                        print(f"Erro no pedido: {str(e)}")
    else:
        st.error("❌ Nenhum produto disponível!")

elif page == "👨‍💼 Administração":
    admin_page()