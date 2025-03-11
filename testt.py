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
        font-size: 22px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: center; /* Centraliza o título dentro da coluna */
        gap: 8px;
    }
    .timestamp {
        color: #A9A9A9;
        font-size: 14px;
        text-align: right;
        margin-bottom: 20px;
    }
    .card-container {
        display: flex;
        flex-wrap: nowrap;
        gap: 8px; /* Espaçamento menor para melhor organização */
        padding: 8px;
        overflow-x: auto;
        justify-content: flex-start;
        scrollbar-width: thin;
        scrollbar-color: #555555 #2E2E2E;
    }
    .card-container::-webkit-scrollbar {
        height: 6px;
    }
    .card-container::-webkit-scrollbar-track {
        background: #2E2E2E;
    }
    .card-container::-webkit-scrollbar-thumb {
        background: #555555;
        border-radius: 3px;
    }
    .card-container::-webkit-scrollbar-thumb:hover {
        background: #777777;
    }
    .card {
        background-color: #2E2E2E;
        border-radius: 8px;
        padding: 10px;
        width: 140px; /* Tamanho ajustado para melhor organização */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        text-align: center;
        transition: transform 0.2s;
        flex: 0 0 auto;
        position: relative;
    }
    .card.positive {
        border: 1px solid #32CD32; /* Borda verde para variação positiva */
    }
    .card.negative {
        border: 1px solid #FF4500; /* Borda vermelha para variação negativa */
    }
    .card:hover {
        transform: scale(1.03);
        background-color: #3E3E3E;
    }
    .card-title {
        font-size: 13px;
        color: #FFFFFF;
        margin-bottom: 4px;
        font-weight: bold;
    }
    .card-value {
        font-size: 15px;
        margin-top: 4px;
        color: #E0E0E0;
    }
    .card-variation {
        font-size: 12px;
        margin-top: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }
    .positive {
        color: #32CD32; /* Verde */
    }
    .negative {
        color: #FF4500; /* Vermelho */
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    body, .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# Título principal
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
            "USD/BRL": data["rates"]["BRL"],
            "EUR/USD": 1 / data["rates"]["EUR"],
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
    # Agrupando commodities por categoria
    symbols = {
        "Metais": {
            'Ouro': 'GC=F', 'Prata': 'SI=F', 'Platinum': 'PL=F', 'Cobre': 'HG=F'
        },
        "Energia": {
            'WTI Oil': 'CL=F', 'Brent Oil': 'BZ=F', 'Gasolina': 'RB=F', 'Gás Natural': 'NG=F'
        },
        "Agrícolas": {
            'Gado Vivo': 'LE=F', 'Porcos Magros': 'HE=F', 'Milho': 'ZC=F', 'Soja': 'ZS=F', 'Cacau': 'CC=F', 'Café': 'KC=F'
        }
    }
    data = {}
    for category, items in symbols.items():
        for name, symbol in items.items():
            try:
                commodity = yf.Ticker(symbol)
                hist = commodity.history(period="2d")
                if len(hist) >= 2:
                    current_price = hist["Close"].iloc[-1]
                    prev_price = hist["Close"].iloc[-2]
                    variation = ((current_price - prev_price) / prev_price) * 100
                    data[f"{name} ({category})"] = {"Preço": round(current_price, 2), "Variação (%)": round(variation, 2)}
                else:
                    data[f"{name} ({category})"] = {"Preço": "N/A", "Variação (%)": "N/A"}
            except Exception as e:
                data[f"{name} ({category})"] = {"Preço": f"N/A (Erro: {e})", "Variação (%)": "N/A"}
    return pd.DataFrame([(k, v["Preço"], v["Variação (%)"]) for k, v in data.items()],
                        columns=["Commodity", "Preço", "Variação (%)"])

@st.cache_data(ttl=30)
def get_stocks():
    symbols = {
        "Apple": "AAPL",
        "Ibovespa": "^BVSP",
        "Tesla": "TSLA",
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "NASDAQ": "^IXIC"
    }
    data = {}
    for name, symbol in symbols.items():
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2d")
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
                        columns=["Índice", "Preço", "Variação (%)"])

# Layout em colunas com proporções ajustadas
col1, col2, col3 = st.columns([1, 2, 1])

# Moedas
with col1:
    st.markdown('<p class="subheader">💱 Moedas</p>', unsafe_allow_html=True)
    currency_data = get_currency_rates()
    if not currency_data.empty:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        for index, row in currency_data.iterrows():
            variation = [0.5, -0.3, 1.2, -0.8, 0.9, -0.2, 0.4][index % 7]  # Exemplo fictício
            var_class = "positive" if variation >= 0 else "negative"
            arrow = "↑" if variation >= 0 else "↓"
            st.markdown(
                f"""
                <div class="card {var_class}">
                    <div class="tooltip">
                        <div class="card-title">{row['Par']}</div>
                        <span class="tooltiptext">Cotação em USD</span>
                    </div>
                    <div class="card-value">{row['Cotação']:.4f}</div>
                    <div class="card-variation {var_class}">{variation:.2f}% {arrow}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Commodities
with col2:
    st.markdown('<p class="subheader">⛽ Commodities</p>', unsafe_allow_html=True)
    commodities_data = get_commodities()
    if not commodities_data.empty:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        for index, row in commodities_data.iterrows():
            var_class = "positive" if float(str(row["Variação (%)"]).replace("N/A", "0")) >= 0 else "negative"
            arrow = "↑" if float(str(row["Variação (%)"]).replace("N/A", "0")) >= 0 else "↓"
            category = row['Commodity'].split('(')[-1].replace(')', '')
            tooltip_text = f"Preço em USD ({category})"
            st.markdown(
                f"""
                <div class="card {var_class}">
                    <div class="tooltip">
                        <div class="card-title">{row['Commodity'].split(' (')[0]}</div>
                        <span class="tooltiptext">{tooltip_text}</span>
                    </div>
                    <div class="card-value">{row['Preço']}</div>
                    <div class="card-variation {var_class}">{row['Variação (%)']}% {arrow}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Índices
with col3:
    st.markdown('<p class="subheader">📈 Índices</p>', unsafe_allow_html=True)
    stocks_data = get_stocks()
    if not stocks_data.empty:
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        for index, row in stocks_data.iterrows():
            var_class = "positive" if float(str(row["Variação (%)"]).replace("N/A", "0")) >= 0 else "negative"
            arrow = "↑" if float(str(row["Variação (%)"]).replace("N/A", "0")) >= 0 else "↓"
            st.markdown(
                f"""
                <div class="card {var_class}">
                    <div class="tooltip">
                        <div class="card-title">{row['Índice']}</div>
                        <span class="tooltiptext">Índice de Mercado</span>
                    </div>
                    <div class="card-value">{row['Preço']}</div>
                    <div class="card-variation {var_class}">{row['Variação (%)']}% {arrow}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Rodapé
st.markdown("""
<div style="text-align: center; font-size: 12px; color: #A9A9A9; margin-top: 20px;">
    <strong>Fonte:</strong> Moedas: ExchangeRate-API | Commodities e Índices: Yahoo Finance<br>
    <strong>Nota:</strong> Atualização automática a cada 30 segundos. Dados para fins informativos.
</div>
""", unsafe_allow_html=True)