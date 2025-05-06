import streamlit as st
from typing import List, Dict, Tuple
import plotly.express as px


class Knapsack:
    def __init__(self, products: List[Dict[str, int]]):
        self.products = products

    def otimize(self, budget: int) -> Tuple[Dict[str, int], int]:
        expanded_items = []

        # Decomposição binária dos produtos com limite
        for i, prod in enumerate(self.products):
            units = prod['max_units']
            power = 1
            while units > 0:
                take = min(power, units)
                expanded_items.append({
                    'index': i,
                    'name': prod['name'],
                    'cost': take * prod['cost'],
                    'value': take * prod['value'],
                    'units': take
                })
                units -= take
                power *= 2

        dp = [0] * (budget + 1)
        trace = [None] * (budget + 1)

        for item in expanded_items:
            for b in range(budget, item['cost'] - 1, -1):
                if dp[b - item['cost']] + item['value'] > dp[b]:
                    dp[b] = dp[b - item['cost']] + item['value']
                    trace[b] = item

        # Reconstrução respeitando os limites
        to_produce = {prod['name']: 0 for prod in self.products}
        used_units = [0] * len(self.products)
        b = budget

        while b > 0:
            item = trace[b]
            if item is None:
                b -= 1
                continue
            idx = item['index']
            if used_units[idx] + item['units'] <= self.products[idx]['max_units']:
                to_produce[item['name']] += item['units']
                used_units[idx] += item['units']
                b -= item['cost']
            else:
                b -= 1

        return to_produce, dp[budget]


# Interface Streamlit
st.set_page_config(page_title="Otimizador de Produção", layout="centered")

st.title("Otimizador de Produção com Budget Limitado")
st.markdown("Otimize a produção de produtos com custo, lucro e limite de unidades usando programação dinâmica.")

st.subheader("Defina seu orçamento")
budget = st.number_input("Orçamento disponível", min_value=100, step=100, value=10000)

st.subheader("Lista de Produtos")

if "products" not in st.session_state:
    st.session_state.products = []

def add_product(name, cost, value, max_units):
    st.session_state.products.append({
        "name": name,
        "cost": cost,
        "value": value,
        "max_units": max_units
    })

col1, col2, col3, col4 = st.columns(4)
with col1:
    name = st.text_input("Nome do produto", value="Produto X")
with col2:
    cost = st.number_input("Custo", min_value=1, step=1, value=10)
with col3:
    value = st.number_input("Lucro (valor)", min_value=1, step=1, value=20)
with col4:
    max_units = st.number_input("Máx. unidades", min_value=1, step=1, value=3)

if st.button("Adicionar produto"):
    add_product(name, cost, value, max_units)

if st.button("📂 Carregar exemplo"):
    st.session_state.products = [
        {'name': 'Notebook', 'cost': 2500, 'value': 5000, 'max_units': 3},
        {'name': 'Smartphone', 'cost': 1500, 'value': 3000, 'max_units': 2},
        {'name': 'Tablet', 'cost': 1000, 'value': 2000, 'max_units': 2}
    ]

if st.session_state.products:
    st.write("### Produtos atuais")
    st.table(st.session_state.products)

    if st.button("Otimizar produção"):
        knapsack = Knapsack(st.session_state.products)
        result, total_profit = knapsack.otimize(budget)
        
        cost_total = sum(
            next(prod for prod in st.session_state.products if prod["name"] == name)["cost"] * qty
            for name, qty in result.items()
        )

        st.success("Produção ótima encontrada!")
        st.write("### Quantidade por produto")
        
        data = [
            {"Produto": name, "Quantidade": qty}
            for name, qty in result.items()
        ]

        fig = px.bar(data, x="Produto", y="Quantidade", title="Quantidade de produtos a serem produzidos")
        st.plotly_chart(fig, use_container_width=True)

        # Métricas
        st.subheader("Métricas de desempenho")
        col1, col2, col3 = st.columns(3)
        col1.metric("Lucro total", f"{total_profit}")
        col2.metric("Custo total usado", f"{cost_total}")
        col3.metric("% orçamento usado", f"{(cost_total / budget * 100):.1f}%")

        col4, col5 = st.columns(2)
        col4.metric("Eficiência do orçamento", f"{(total_profit / budget * 100):.1f}%")
        col5.metric("Lucro por real investido", f"{(total_profit / cost_total):.2f}")
else:
    st.info("Adicione produtos ou carregue um exemplo para começar.")