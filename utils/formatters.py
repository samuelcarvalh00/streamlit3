def format_pedido(pedido):
    return f"Pedido: {pedido['quantidade']}x {pedido['produto']['nome']} - R${pedido['produto']['preco']*pedido['quantidade']}"