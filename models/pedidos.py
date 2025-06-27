from models.clientes import Cliente
from models.produtos import Produto

class Pedido:
    def __init__(self, cliente, produto, quantidade, endereco):
        self.cliente = cliente
        self.produto = produto
        self.quantidade = quantidade
        self.endereco = endereco

    def to_dict(self):
        return {
            "cliente": self.cliente.to_dict(),
            "produto": self.produto.to_dict(),
            "quantidade": self.quantidade,
            "endereco": self.endereco
        }