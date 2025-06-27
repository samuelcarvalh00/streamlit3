class Cliente:
    def __init__(self, nome, telefone):
        self.nome = nome
        self.telefone = telefone

    def to_dict(self):
        return {"nome": self.nome, "telefone": self.telefone}