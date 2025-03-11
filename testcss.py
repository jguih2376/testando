import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Título da aplicação
st.title("Sistema de Cotação de Ações")

# Sidebar para entrada de dados
st.sidebar.header("Parâmetros")
ticker = st.sidebar.text_input("Digite o símbolo da ação (ex: AAPL, MSFT, PETR4.SA)", "AAPL")

# Função para carregar os dados da ação
@st.cache_data
def carregar_dados(ticker, periodo, intervalo):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=periodo, interval=intervalo)
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# Aba principal combinando Intraday e Diário
tab1, tab2 = st.tabs(["Intraday + Diário", "Semanal", "Mensal"])[0]

with tab1:
    st.subheader("Gráficos Intraday e Diário")
    
    # Criar duas colunas para exibir os gráficos lado a lado
    col1, col2 = st.columns(2)
    st.subheader("Gráfico Intraday")
    intervalo_intraday = st.selectbox("Selecione o intervalo (Intraday)", 
                                    ["5m", "15m", "30m", "1h"], 
                                    key="intraday_interval")
    dados_intraday = carregar_dados(ticker, "1d", intervalo_intraday)
    
    if dados_intraday is not None:
        fig_intraday = go.Figure(data=[go.Candlestick(x=dados_intraday.index,
                                                    open=dados_intraday['Open'],
                                                    high=dados_intraday['High'],
                                                    low=dados_intraday['Low'],
                                                    close=dados_intraday['Close'])])
        
        fig_intraday.update_layout(
            title=f'Intraday - {ticker} ({intervalo_intraday})',
            yaxis_title='Preço',
            xaxis_title='Hora',
            template='plotly_white',
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False),
            yaxis2=dict(visible=False, overlaying='y', matches=None),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_intraday, use_container_width=True)
    else:
        st.warning("Nenhum dado Intraday disponível.")    
    # --- Intraday ---
    with col1:
        st.subheader("Gráfico Semanal")
        periodo_semanal = st.selectbox("Selecione o período (Semanal)", 
                                    ["1mo", "3mo", "6mo", "1y"], 
                                    key="weekly_period")
        dados_semanal = carregar_dados(ticker, periodo_semanal, "1wk")
        
        if dados_semanal is not None:
            fig_semanal = go.Figure(data=[go.Candlestick(x=dados_semanal.index,
                                                    open=dados_semanal['Open'],
                                                    high=dados_semanal['High'],
                                                    low=dados_semanal['Low'],
                                                    close=dados_semanal['Close'])])
            fig_semanal.update_layout(
                title=f'Semanal - {ticker} ({periodo_semanal})',
                yaxis_title='Preço',
                xaxis_title='Data',
                template='plotly_white',
                yaxis=dict(showgrid=False),
                xaxis=dict(showgrid=False),
                yaxis2=dict(visible=False, overlaying='y', matches=None),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_semanal, use_container_width=True)
        else:
            st.warning("Nenhum dado Semanal disponível.")

    # --- Diário ---
    with col2:

        st.subheader("Gráfico Mensal")
        periodo_mensal = st.selectbox("Selecione o período (Mensal)", 
                                    ["6mo", "1y", "2y", "5y"], 
                                    key="monthly_period")
        dados_mensal = carregar_dados(ticker, periodo_mensal, "1mo")
        
        if dados_mensal is not None:
            fig_mensal = go.Figure(data=[go.Candlestick(x=dados_mensal.index,
                                                    open=dados_mensal['Open'],
                                                    high=dados_mensal['High'],
                                                    low=dados_mensal['Low'],
                                                    close=dados_mensal['Close'])])
            fig_mensal.update_layout(
                title=f'Mensal - {ticker} ({periodo_mensal})',
                yaxis_title='Preço',
                xaxis_title='Data',
                template='plotly_white',
                yaxis=dict(showgrid=False),
                xaxis=dict(showgrid=False),
                yaxis2=dict(visible=False, overlaying='y', matches=None),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_mensal, use_container_width=True)
        else:
            st.warning("Nenhum dado Mensal disponível.")

# --- Semanal ---
with tab2:
    st.subheader("Gráfico Semanal")
    periodo_semanal = st.selectbox("Selecione o período (Semanal)", 
                                  ["1mo", "3mo", "6mo", "1y"], 
                                  key="weekly_period")
    dados_semanal = carregar_dados(ticker, periodo_semanal, "1wk")
    
    if dados_semanal is not None:
        fig_semanal = go.Figure(data=[go.Candlestick(x=dados_semanal.index,
                                                   open=dados_semanal['Open'],
                                                   high=dados_semanal['High'],
                                                   low=dados_semanal['Low'],
                                                   close=dados_semanal['Close'])])
        fig_semanal.update_layout(
            title=f'Semanal - {ticker} ({periodo_semanal})',
            yaxis_title='Preço',
            xaxis_title='Data',
            template='plotly_white',
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False),
            yaxis2=dict(visible=False, overlaying='y', matches=None),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_semanal, use_container_width=True)
    else:
        st.warning("Nenhum dado Semanal disponível.")

# --- Mensal ---
with st.tabs(["Intraday + Diário", "Semanal", "Mensal"])[2]:
    st.subheader("Gráfico Mensal")
    periodo_mensal = st.selectbox("Selecione o período (Mensal)", 
                                 ["6mo", "1y", "2y", "5y"], 
                                 key="monthly_period")
    dados_mensal = carregar_dados(ticker, periodo_mensal, "1mo")
    
    if dados_mensal is not None:
        fig_mensal = go.Figure(data=[go.Candlestick(x=dados_mensal.index,
                                                  open=dados_mensal['Open'],
                                                  high=dados_mensal['High'],
                                                  low=dados_mensal['Low'],
                                                  close=dados_mensal['Close'])])
        fig_mensal.update_layout(
            title=f'Mensal - {ticker} ({periodo_mensal})',
            yaxis_title='Preço',
            xaxis_title='Data',
            template='plotly_white',
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False),
            yaxis2=dict(visible=False, overlaying='y', matches=None),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_mensal, use_container_width=True)
    else:
        st.warning("Nenhum dado Mensal disponível.")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.write(f"Data atual: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.sidebar.write("Desenvolvido com Streamlit e yfinance")