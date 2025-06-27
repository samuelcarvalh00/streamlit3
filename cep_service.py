import requests

def buscar_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    response = requests.get(url)
    if response.status_code == 200 and not response.json().get("erro"):
        data = response.json()
        return f"{data['logradouro']}, {data['bairro']} - {data['localidade']}/{data['uf']}"
    return None