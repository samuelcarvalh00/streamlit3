import streamlit as st
from data.database import listar_pedidos

def admin_page():
    st.title("Painel de Administração")
    pedidos = listar_pedidos()
    if pedidos:
        st.write("### Lista de Pedidos")
        for pedido in pedidos:
            st.write(f"Cliente: {pedido[0]}, Telefone: {pedido[1]}, Produto: {pedido[2]}, Preço: R${pedido[3]:.2f}, Quantidade: {pedido[4]}, Endereço: {pedido[5]}")
    else:
        st.write("Nenhum pedido registrado.")