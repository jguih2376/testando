import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import plotly.graph_objects as go
import streamlit.components.v1 as components
from datetime import datetime
from streamlit_autorefresh import st_autorefresh



st.set_page_config(page_title="Panorama de Mercado", layout="wide", initial_sidebar_state="collapsed")

st.title("🌎 Panorama do Mercado")  
st.write("Visão geral do mercado atual.")


# Criando as abas
tab1, tab2, tab3 = st.tabs(['Panorama', 'TradingView', 'Triple Screen'])

# Aba 1: Panorama
with tab1:


    st.markdown("""
        <style>
        .main-title {
            font-size: 36px;
            color: #FFFFFF;
            text-align: center;
            margin-bottom: 10px;
        }
        .subheader {
            color: #FFFFFF;
            font-size: 24px;
        }
        .timestamp {
            color: #A9A9A9;
            font-size: 14px;
            text-align: right;
        }
        </style>
        """, unsafe_allow_html=True)

    # Forçar tema escuro
    st.markdown("""
        <style>
        body {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        .stApp {
            background-color: #1E1E1E;
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
        except:
            st.error("Erro ao carregar moedas")
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
            except:
                data[name] = "N/A"
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
            except:
                data[name] = "N/A"
        return pd.DataFrame(data.items(), columns=["Ação", "Preço"])

    # Layout em colunas
    col1, col2, col3 = st.columns(3)

    # Moedas
    with col1:
        st.markdown('<p class="subheader">Moedas</p>', unsafe_allow_html=True)
        currency_data = get_currency_rates()
        if not currency_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=currency_data["Par"],
                y=currency_data["Cotação"],
                mode="lines+markers",
                line=dict(color="#00CED1", width=2),
                marker=dict(size=8)
            ))
            fig.update_layout(
                plot_bgcolor="#2E2E2E",
                paper_bgcolor="#2E2E2E",
                font=dict(color="#FFFFFF"),
                xaxis=dict(show=False, title=""),
                yaxis=dict(title="", gridcolor="#555555"),
                height=300,
                margin=dict(l=50, r=50, t=30, b=30)
            )
            st.plotly_chart(fig, use_container_width=True)

    # Commodities
    with col2:
        st.markdown('<p class="subheader">Commodities</p>', unsafe_allow_html=True)
        commodities_data = get_commodities()
        if not commodities_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=commodities_data["Commodity"],
                y=commodities_data["Preço"],
                mode="lines+markers",
                line=dict(color="#FF4500", width=2),
                marker=dict(size=8)
            ))
            fig.update_layout(
                plot_bgcolor="#2E2E2E",
                paper_bgcolor="#2E2E2E",
                font=dict(color="#FFFFFF"),
                xaxis=dict(show=False, title=""),
                yaxis=dict(title="", gridcolor="#555555"),
                height=300,
                margin=dict(l=50, r=50, t=30, b=30)
            )
            st.plotly_chart(fig, use_container_width=True)

    # Ações
    with col3:
        st.markdown('<p class="subheader">Ações</p>', unsafe_allow_html=True)
        stocks_data = get_stocks()
        if not stocks_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=stocks_data["Ação"],
                y=stocks_data["Preço"],
                mode="lines+markers",
                line=dict(color="#FFFFFF", width=2),
                marker=dict(size=8)
            ))
            fig.update_layout(
                plot_bgcolor="#2E2E2E",
                paper_bgcolor="#2E2E2E",
                font=dict(color="#FFFFFF"),
                xaxis=dict(show=False, title=""),
                yaxis=dict(title="", gridcolor="#555555"),
                height=300,
                margin=dict(l=50, r=50, t=30, b=30)
            )
            st.plotly_chart(fig, use_container_width=True)

    # Rodapé
    st.markdown("""
    <div style="text-align: center; font-size: 12px; color: #A9A9A9;">
        <strong>Fonte:</strong> Moedas: ExchangeRate-API | Commodities e Ações: Yahoo Finance<br>
        <strong>Nota:</strong> Atualização automática a cada 30 segundos. Dados para fins informativos.
    </div>
    """, unsafe_allow_html=True)