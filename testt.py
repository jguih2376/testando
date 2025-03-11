import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Configuração da página com tema escuro
st.set_page_config(page_title="Panorama de Mercado", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    .main-title {
        font-size: 36px;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .subheader {
        color: #FFFFFF;
        font-size: 24px;
        margin-bottom: 15px;
        margin-top: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .timestamp {
        color: #A9A9A9;
        font-size: 14px;
        text-align: right;
        margin-bottom: 20px;
    }
    .card-container {
        display: flex;
        flex-wrap: nowrap; /* Impede quebra de linha */
        gap: 15px;
        padding: 10px;
        overflow-x: auto; /* Adiciona rolagem horizontal */
        justify-content: flex-start; /* Alinha à esquerda */
        scrollbar-width: thin; /* Para navegadores que suportam */
        scrollbar-color: #555555 #2E2E2E; /* Cor da barra de rolagem */
    }
    .card-container::-webkit-scrollbar {
        height: 8px; /* Altura da barra de rolagem */
    }
    .card-container::-webkit-scrollbar-track {
        background: #2E2E2E; /* Cor do fundo da barra */
    }
    .card-container::-webkit-scrollbar-thumb {
        background: #555555; /* Cor do polegar da barra */
        border-radius: 4px;
    }
    .card-container::-webkit-scrollbar-thumb:hover {
        background: #777777; /* Cor ao passar o mouse */
    }
    .card {
        background-color: #2E2E2E;
        border-radius: 10px;
        padding: 15px;
        width: 200px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        text-align: center;
        transition: transform 0.2s;
        flex: 0 0 auto; /* Impede que o cartão encolha */
    }
    .card:hover {
        transform: scale(1.05);
        background-color: #3E3E3E;
    }
    .card-title {
        font-size: 16px;
        color: #FFFFFF;
        margin-bottom: 5px;
        font-weight: bold;
    }
    .card-value {
        font-size: 18px;
        margin-top: 5px;
    }
    .card-variation {
        font-size: 14px;
        margin-top: 5px;
    }
    .positive {
        color: #32CD32; /* Verde */
    }
    .negative {
        color: #FF4500; /* Vermelho */
    }
    body, .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# Título
st.markdown('<p class="main-title">Panorama de Mercado</p>', unsafe_allow_html=True)

# Atualização automática a cada 30 segundos
st_autorefresh(interval=30000, key="marketrefresh")

# Timestamp
st.markdown(f'<p class="timestamp">Última atualização: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>', unsafe_allow_html=True)

# Funções de dados (com cache)
@st.cache_data(ttl=30)
def get_currency_rates():
    try:
        # Substitua YOUR_API_KEY pela sua chave da ExchangeRate-API
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()
        rates = {
            "USD/BRL": data["rates"]["BRL"],
            "EUR/USD": 1 / data["rates"]["EUR"],  # Invertido para EUR/USD
            "USD/JPY": data["rates"]["JPY"],
            "USD/GBP": data["rates"]["GBP"],
            "USD/CAD": data["rates"]["CAD"],
            "USD/SEK": data["rates"]["SEK"],
            "USD/CHF": data["rates"]["CHF"]
        }
        return pd.DataFrame(rates.items(), columns=["Par", "Cotação"])
    except Exception as e:
        st.error(f"Erro ao carregar moedas: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=30)
def get_commodities():
    symbols = {
        "Petróleo (WTI)": "CL=F",
        "Ouro": "GC=F",
        "Prata": "SI=F"
    }
    data = {}
    for name, symbol in symbols.items():
        try:
            commodity = yf.Ticker(symbol)
            hist = commodity.history(period="2d")  # 2 dias para calcular variação
            if len(hist) >= 2:
                current_price = hist["Close"].iloc[-1]
                prev_price = hist["Close"].iloc[-2]
                variation = ((current_price - prev_price) / prev_price) * 100
                data[name] = {"Preço": round(current_price, 2), "Variação (%)": round(variation, 2)}
            else:
                data[name] = {"Preço": "N/A", "Variação (%)": "N/A"}
        except Exception as e:
            data[name] = {"Preço": f"N/A (Erro: {e})", "Variação (%)": "N/A"}
    return pd.DataFrame([(k, v["Preço"], v["Variação (%)"]) for k, v in data.items()],
                        columns=["Commodity", "Preço", "Variação (%)"])

@st.cache_data(ttl=30)
def get_stocks():
    symbols = {
        "Apple": "AAPL",
        "Ibovespa": "^BVSP",
        "Tesla": "TSLA"
    }
    data = {}
    for name, symbol in symbols.items():
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2d")  # 2 dias para calcular variação
            if len(hist) >= 2:
                current_price = hist["Close"].iloc[-1]
                prev_price = hist["Close"].iloc[-2]
                variation = ((current_price - prev_price) / prev_price) * 100
                data[name] = {"Preço": round(current_price, 2), "Variação (%)": round(variation, 2)}
            else:
                data[name] = {"Preço": "N/A", "Variação (%)": "N/A"}
        except Exception as e:
            data[name] = {"Preço": f"N/A (Erro: {e})", "Variação (%)": "N/A"}
    return pd.DataFrame([(k, v["Preço"], v["Variação (%)"]) for k, v in data.items()],
                        columns=["Ação", "Preço", "Variação (%)"])

# Moedas
st.markdown('<p class="subheader">💱 Moedas</p>', unsafe_allow_html=True)
currency_data = get_currency_rates()
if not currency_data.empty:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    for index, row in currency_data.iterrows():
        # Variação fictícia (para valores reais, use uma API com histórico, como Alpha Vantage)
        variation = [0.5, -0.3, 1.2, -0.8, 0.9, -0.2, 0.4][index % 7]  # Exemplo fictício
        var_class = "positive" if variation >= 0 else "negative"
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">{row['Par']}</div>
                <div class="card-value">{row['Cotação']:.4f}</div>
                <div class="card-variation {var_class}">{variation:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Commodities
st.markdown('<p class="subheader">⛽ Commodities</p>', unsafe_allow_html=True)
commodities_data = get_commodities()
if not commodities_data.empty:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    for index, row in commodities_data.iterrows():
        var_class = "positive" if float(str(row["Variação (%)"]).replace("N/A", "0")) >= 0 else "negative"
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">{row['Commodity']}</div>
                <div class="card-value">{row['Preço']}</div>
                <div class="card-variation {var_class}">{row['Variação (%)']}%</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Ações
st.markdown('<p class="subheader">📈 Ações</p>', unsafe_allow_html=True)
stocks_data = get_stocks()
if not stocks_data.empty:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    for index, row in stocks_data.iterrows():
        var_class = "positive" if float(str(row["Variação (%)"]).replace("N/A", "0")) >= 0 else "negative"
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">{row['Ação']}</div>
                <div class="card-value">{row['Preço']}</div>
                <div class="card-variation {var_class}">{row['Variação (%)']}%</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Rodapé
st.markdown("""
<div style="text-align: center; font-size: 12px; color: #A9A9A9; margin-top: 20px;">
    <strong>Fonte:</strong> Moedas: ExchangeRate-API | Commodities e Ações: Yahoo Finance<br>
    <strong>Nota:</strong> Atualização automática a cada 30 segundos. Dados para fins informativos.
</div>
""", unsafe_allow_html=True)