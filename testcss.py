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
periodo = st.sidebar.selectbox("Selecione o período", 
                              ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd"],
                              index=5)  # Default: 1 ano
intervalo = st.sidebar.selectbox("Selecione o intervalo",
                                ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"],
                                index=5)  # Default: 1 dia

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

# Carregar os dados
dados = carregar_dados(ticker, periodo, intervalo)

# Exibir informações
if dados is not None:
    # Informações básicas da ação
    st.subheader(f"Dados da Ação: {ticker}")
    
    # Último preço
    ultimo_preco = dados['Close'].iloc[-1]
    preco_anterior = dados['Close'].iloc[-2]
    variacao = ((ultimo_preco - preco_anterior) / preco_anterior) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("Último Preço", f"${ultimo_preco:.2f}")
    col2.metric("Variação", f"{variacao:.2f}%", 
                delta_color="normal" if variacao >= 0 else "inverse")

    # Gráfico de candlestick
    fig = go.Figure(data=[go.Candlestick(x=dados.index,
                                        open=dados['Open'],
                                        high=dados['High'],
                                        low=dados['Low'],
                                        close=dados['Close'])])
    
    fig.update_layout(
        title=f'Gráfico de Candlestick - {ticker}',
        yaxis_title='Preço',
        xaxis_title='Data',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Exibir tabela de dados
    st.subheader("Histórico Recente")
    st.dataframe(dados.tail().style.format({'Open': '${:.2f}', 
                                          'High': '${:.2f}',
                                          'Low': '${:.2f}',
                                          'Close': '${:.2f}',
                                          'Volume': '{:,.0f}'}))

else:
    st.warning("Nenhum dado disponível. Verifique o símbolo da ação ou os parâmetros.")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.write(f"Data atual: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.sidebar.write("Desenvolvido com Streamlit e yfinance")