import streamlit as st
import pandas as pd
import yfinance as yf  # Exemplo de biblioteca para dados financeiros

# Função para pegar dados (exemplo com yfinance)
def get_ibov_data():
    # Substitua por uma lista real de tickers do Ibovespa
    tickers = ["BHIA3.SA", "TRAD3.SA", "MGLU3.SA", "RCSL3.SA", "ASAI3.SA", 
               "IFCM3.SA", "FHER3.SA", "PDGR3.SA", "AERI3.SA", "TPIS3.SA"]
    data = yf.download(tickers, period="1d")["Adj Close"]
    variacao = data.pct_change().iloc[-1] * 100  # Variação em %
    return pd.DataFrame({"Ação": [t[:-3] for t in tickers], "Variação (%)": variacao})

# Carregando dados
df = get_ibov_data()

# Filtrando altas e baixas
maiores_altas = df.nlargest(5, "Variação (%)")
maiores_baixas = df.nsmallest(5, "Variação (%)")

# Interface com Streamlit
st.title("Maiores Altas e Baixas do Ibovespa")
st.write("Data: 11 de Março de 2025")

st.subheader("5 Maiores Altas do Dia")
st.dataframe(maiores_altas)

st.subheader("5 Maiores Baixas do Dia")
st.dataframe(maiores_baixas)