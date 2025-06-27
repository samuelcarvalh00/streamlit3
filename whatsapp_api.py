from twilio.rest import Client
import re
import os

def enviar_pedido(pedido, telefone):
    """Função para enviar pedidos via WhatsApp usando Twilio Client"""
    
    # Suas credenciais
    account_sid = "AC229edcb56ecceca69936b6801cd21098"
    auth_token = "64b3fbc8e88a58b0b51db2cf53bd4256"
    client = Client(account_sid, auth_token)
    
    # Formatear telefone brasileiro
    telefone_formatado = formatar_telefone_brasileiro(telefone)
    if not telefone_formatado:
        return {"success": False, "data": "Número de telefone inválido"}
    
    print(f"📱 Enviando para: {telefone_formatado}")
    
    # Mensagem formatada
    mensagem = criar_mensagem_pedido(pedido)
    
    # Lista de números "From" para tentar
    numeros_from = [
        "+14155238886",  # Sandbox padrão
        "+15551234567",  # Outro possível sandbox
    ]
    
    # Tentar envio com diferentes números
    for from_number in numeros_from:
        resultado = tentar_envio(client, telefone_formatado, from_number, mensagem)
        
        if resultado["success"]:
            print(f"✅ Mensagem enviada com sucesso via {from_number}")
            print(f"🆔 SID: {resultado['data']}")
            return resultado
        else:
            print(f"❌ Falha com {from_number}: {resultado['data']}")
    
    return {
        "success": False,
        "data": "Falha no envio. Verifique se o WhatsApp Sandbox está configurado."
    }

def formatar_telefone_brasileiro(telefone):
    """Formata número de telefone brasileiro para padrão internacional"""
    # Remove todos os caracteres não numéricos
    numeros = re.sub(r'\D', '', telefone)
    
    if numeros.startswith('55') and len(numeros) == 13:
        return f"+{numeros}"
    elif len(numeros) == 11:
        return f"+55{numeros}"
    elif len(numeros) == 10:
        return f"+55{numeros}"
    else:
        print(f"⚠️ Formato de telefone não reconhecido: {telefone}")
        return None

def criar_mensagem_pedido(pedido):
    """Cria a mensagem formatada do pedido"""
    total = pedido.produto.preco * pedido.quantidade
    
    mensagem = f"""🍕 *NOVO PEDIDO CONFIRMADO* 🍕

📋 *DETALHES DO PEDIDO:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🍽️ Produto: {pedido.produto.nome}
📦 Quantidade: {pedido.quantidade}x
💰 Preço unitário: R$ {pedido.produto.preco:.2f}
💵 *TOTAL: R$ {total:.2f}*

📍 *ENDEREÇO DE ENTREGA:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{pedido.endereco}

👤 *DADOS DO CLIENTE:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nome: {pedido.cliente.nome}
Telefone: {pedido.cliente.telefone}

✅ *Pedido confirmado e registrado!*
⏰ Tempo estimado de entrega: 30-45 minutos
📞 Em caso de dúvidas, responda esta mensagem

Obrigado por escolher nosso delivery! 🙏"""
    
    return mensagem

def tentar_envio(client, telefone_para, telefone_de, mensagem):
    """Tenta enviar mensagem usando um número específico com Twilio Client"""
    try:
        print(f"🔄 Tentando envio: {telefone_de} → {telefone_para}")
        
        message = client.messages.create(
            from_=f"whatsapp:{telefone_de}",
            body=mensagem,
            to=f"whatsapp:{telefone_para}"
        )
        
        print(f"📊 Status: {message.status}")
        
        return {
            "success": True,
            "data": message.sid,
            "status": message.status,
            "from": telefone_de
        }
        
    except Exception as e:
        error_code = getattr(e, 'code', None)
        error_message = str(e)
        
        print(f"❌ Erro: {error_message}")
        diagnostico = diagnosticar_erro(error_code, error_message)
        
        return {
            "success": False,
            "data": f"Erro {error_code or 'desconhecido'}: {error_message}",
            "diagnostico": diagnostico
        }

def diagnosticar_erro(error_code, error_message):
    """Diagnóstica erros comuns e retorna sugestões"""
    diagnosticos = {
        21211: "Número de destino inválido. Verifique o formato do telefone.",
        21408: "Você não tem permissão para enviar para este número. Configure o WhatsApp Sandbox.",
        21610: "Mensagem não pode ser entregue. O número pode não estar no WhatsApp.",
        20003: "Credenciais de autenticação inválidas.",
        21612: "O número não está verificado no WhatsApp Sandbox.",
        21473: "O número de origem não está configurado para WhatsApp."
    }
    
    if error_code:
        return diagnosticos.get(error_code, "Erro não catalogado. Consulte a documentação do Twilio.")
    
    message_lower = error_message.lower()
    if "sandbox" in message_lower:
        return "Problema com WhatsApp Sandbox. Verifique se está configurado corretamente."
    elif "permission" in message_lower:
        return "Problema de permissão. Verifique suas credenciais e configurações."
    elif "phone number" in message_lower:
        return "Problema com número de telefone. Verifique o formato."
    
    return "Erro não identificado automaticamente."

def verificar_conexao_twilio():
    """Testa a conexão com a API do Twilio"""
    account_sid = "AC229edcb56ecceca69936b6801cd21098"
    auth_token = "64b3fbc8e88a58b0b51db2cf53bd4256"
    client = Client(account_sid, auth_token)
    
    try:
        print("🔍 Testando conexão com Twilio...")
        account = client.api.accounts(account_sid).fetch()
        
        print(f"✅ Conexão OK!")
        print(f"📊 Account SID: {account.sid}")
        print(f"📊 Status: {account.status}")
        print(f"📊 Nome: {account.friendly_name}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar conexão: {str(e)}")
        return False

def enviar_mensagem_teste(telefone_destino):
    """Envia uma mensagem de teste para verificar se tudo está funcionando"""
    class ClienteTeste:
        def __init__(self):
            self.nome = "Teste Sistema"
            self.telefone = telefone_destino
    
    class ProdutoTeste:
        def __init__(self):
            self.nome = "Pizza Teste"
            self.preco = 25.99
    
    class PedidoTeste:
        def __init__(self):
            self.cliente = ClienteTeste()
            self.produto = ProdutoTeste()
            self.quantidade = 1
            self.endereco = "Endereço de teste - Teste, 123"
    
    pedido_teste = PedidoTeste()
    
    print("🧪 Enviando mensagem de teste...")
    resultado = enviar_pedido(pedido_teste, telefone_destino)
    
    if resultado["success"]:
        print("✅ Teste realizado com sucesso!")
        print(f"🆔 SID: {resultado['data']}")
        return True
    else:
        print("❌ Falha no teste:")
        print(f"📝 Erro: {resultado['data']}")
        if "diagnostico" in resultado:
            print(f"💡 Diagnóstico: {resultado['diagnostico']}")
        return False

def enviar_status(telefone, mensagem):
    """Envia mensagem de status para o cliente"""
    account_sid = "AC229edcb56ecceca69936b6801cd21098"
    auth_token = "64b3fbc8e88a58b0b51db2cf53bd4256"
    client = Client(account_sid, auth_token)
    
    telefone_formatado = formatar_telefone_brasileiro(telefone)
    if not telefone_formatado:
        return False
    
    try:
        message = client.messages.create(
            from_="whatsapp:+14155238886",
            body=mensagem,
            to=f"whatsapp:{telefone_formatado}"
        )
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar status: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 MODO TESTE - WHATSAPP API")
    print("=" * 40)
    
    numero_teste = "+5585988230252"
    
    print("1. Testando conexão...")
    if verificar_conexao_twilio():
        print("\n2. Enviando mensagem de teste...")
        if enviar_mensagem_teste(numero_teste):
            print("\n🎉 TUDO FUNCIONANDO!")
        else:
            print("\n❌ PROBLEMA NO ENVIO")
            print(obter_instrucoes_sandbox())
    else:
        print("\n❌ PROBLEMA NA CONEXÃO")
        print("Verifique suas credenciais Account SID e Auth Token")