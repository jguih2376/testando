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
        margin-bottom: 10px;
        font-weight: bold;
    }
    .subheader {
        color: #FFFFFF;
        font-size: 24px;
        margin-bottom: 15px;
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
    .stDataFrame {
        background-color: #2E2E2E;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    .dataframe th {
        background: linear-gradient(to right, #3A3A3A, #4A4A4A);
        color: #FFFFFF !important;
        border-bottom: 1px solid #555555;
        font-size: 16px !important;
        padding: 10px;
        text-align: center;
    }
    .dataframe td {
        background-color: #2E2E2E !important;
        color: #FFFFFF !important;
        border-bottom: 1px solid #444444;
        font-size: 14px !important;
        padding: 8px;
        text-align: center;
    }
    .dataframe tr:hover {
        background-color: #3E3E3E !important;
        transition: background-color 0.3s;
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
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()
        rates = {
            "EUR/USD": 1 / data["rates"]["EUR"],
            "USD/BRL": data["rates"]["BRL"],
            "USD/JPY": data["rates"]["JPY"]
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
            price = commodity.history(period="1d")["Close"].iloc[-1]
            data[name] = round(price, 2)
        except Exception as e:
            data[name] = f"N/A (Erro: {e})"
    return pd.DataFrame(data.items(), columns=["Commodity", "Preço"])

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
            price = stock.history(period="1d")["Close"].iloc[-1]
            data[name] = round(price, 2)
        except Exception as e:
            data[name] = f"N/A (Erro: {e})"
    return pd.DataFrame(data.items(), columns=["Ação", "Preço"])

# Layout em colunas
col1, col2, col3 = st.columns(3)

# Moedas
with col1:
    st.markdown('<p class="subheader">💱 Moedas</p>', unsafe_allow_html=True)
    currency_data = get_currency_rates()
    if not currency_data.empty:
        styled_data = currency_data.style.format({"Cotação": "{:.4f}"}).set_properties(**{
            "background-color": "#2E2E2E",
            "color": "#FFFFFF",
            "border": "none",
            "text-align": "center"
        }).set_table_styles([
            {"selector": "th", "props": [("border-bottom", "1px solid #555555")]},
            {"selector": "td", "props": [("border-bottom", "1px solid #444444")]}
        ])
        st.dataframe(styled_data, use_container_width=True)

# Commodities
with col2:
    st.markdown('<p class="subheader">⛽ Commodities</p>', unsafe_allow_html=True)
    commodities_data = get_commodities()
    if not commodities_data.empty:
        styled_data = commodities_data.style.format({"Preço": "{:.2f}"}).set_properties(**{
            "background-color": "#2E2E2E",
            "color": "#FFFFFF",
            "border": "none",
            "text-align": "center"
        }).set_table_styles([
            {"selector": "th", "props": [("border-bottom", "1px solid #555555")]},
            {"selector": "td", "props": [("border-bottom", "1px solid #444444")]}
        ])
        st.dataframe(styled_data, use_container_width=True)

# Ações
with col3:
    st.markdown('<p class="subheader">📈 Ações</p>', unsafe_allow_html=True)
    stocks_data = get_stocks()
    if not stocks_data.empty:
        styled_data = stocks_data.style.format({"Preço": "{:.2f}"}).set_properties(**{
            "background-color": "#2E2E2E",
            "color": "#FFFFFF",
            "border": "none",
            "text-align": "center"
        }).set_table_styles([
            {"selector": "th", "props": [("border-bottom", "1px solid #555555")]},
            {"selector": "td", "props": [("border-bottom", "1px solid #444444")]}
        ])
        st.dataframe(styled_data, use_container_width=True)

# Rodapé
st.markdown("""
<div style="text-align: center; font-size: 12px; color: #A9A9A9; margin-top: 20px;">
    <strong>Fonte:</strong> Moedas: ExchangeRate-API | Commodities e Ações: Yahoo Finance<br>
    <strong>Nota:</strong> Atualização automática a cada 30 segundos. Dados para fins informativos.
</div>
""", unsafe_allow_html=True)