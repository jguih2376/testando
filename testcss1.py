import streamlit as st
import yfinance as yf

# Obter a cotação da Petrobras (PETR4)
ticker = "PETR4.SA"  # Código da Petrobras na B3
dados = yf.Ticker(ticker)
cotacao_atual = dados.history(period="1d")['Close'][0]

# Exibir o box com a cotação
st.markdown(
    f"""
    <div style="
        background-color: #3498db;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(200, 200, 0, 0.5);
        width: 500px;
        margin: 0 auto;">
        <h3>Meu Box no Streamlit</h3>
        <p>Este é um exemplo de box estilizado com HTML e CSS!</p>
        <p><strong>Cotação da {ticker}:</strong> R$ {cotacao_atual:.2f}</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write('ois')
