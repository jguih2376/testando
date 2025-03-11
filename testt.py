import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pytz

# Função para pegar dados do Ibovespa do dia atual (ações individuais)
def get_ibov_data():
    acoes = [
        'ALOS3', 'ABEV3', 'ASAI3', 'AURE3', 'AMOB3', 'AZUL4', 'AZZA3', 'B3SA3', 'BBSE3', 'BBDC3', 'BBDC4', 
        'BRAP4', 'BBAS3', 'BRKM5', 'BRAV3', 'BRFS3', 'BPAC11', 'CXSE3', 'CRFB3', 'CCRO3', 'CMIG4', 'COGN3', 
        'CPLE6', 'CSAN3', 'CPFE3', 'CMIN3', 'CVCB3', 'CYRE3', 'ELET3', 'ELET6', 'EMBR3', 'ENGI11', 'ENEV3', 
        'EGIE3', 'EQTL3', 'FLRY3', 'GGBR4', 'GOAU4', 'NTCO3', 'HAPV3', 'HYPE3', 'IGTI11', 'IRBR3', 'ISAE4', 
        'ITSA4', 'ITUB4', 'JBSS3', 'KLBN11', 'RENT3', 'LREN3', 'LWSA3', 'MGLU3', 'POMO4', 'MRFG3', 'BEEF3', 
        'MRVE3', 'MULT3', 'PCAR3', 'PETR3', 'PETR4', 'RECV3', 'PRIO3', 'PETZ3', 'PSSA3', 'RADL3', 'RAIZ4', 
        'RDOR3', 'RAIL3', 'SBSP3', 'SANB11', 'STBP3', 'SMTO3', 'CSNA3', 'SLCE3', 'SUZB3', 'TAEE11', 'VIVT3', 
        'TIMS3', 'TOTS3', 'UGPA3', 'USIM5', 'VALE3', 'VAMO3', 'VBBR3', 'VIVA3', 'WEGE3', 'YDUQ3'
    ]
    
    tickers = [acao + '.SA' for acao in acoes]
    data = yf.download(tickers, period="1d", interval="1d")["Close"]
    open_data = yf.download(tickers, period="1d", interval="1d")["Open"]
    
    if data.empty or open_data.empty:
        raise ValueError("Dados insuficientes para calcular a variação do dia.")
    
    variacao = ((data.iloc[-1] - open_data.iloc[-1]) / open_data.iloc[-1]) * 100
    return pd.DataFrame({
        "Ação": [ticker[:-3] for ticker in tickers], 
        "Variação (%)": variacao.values
    })

# Função para obter dados intraday do IBOV
def get_stock_data(ticker, period, interval):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    return data

# Interface com Streamlit
st.set_page_config(page_title="Ibovespa Hoje", layout="wide")
st.title("📊 Maiores Altas e Baixas do Ibovespa")

# Horário atual em BRT
brt = pytz.timezone('America/Sao_Paulo')
data_atual = datetime.now(brt).strftime("%d/%m/%Y %H:%M:%S")
st.write(f"**Data:** 11 de Março de 2025 (atualizado até {data_atual} BRT)")

# Dados do IBOV
st.subheader("IBOV")
try:
    # Dados intraday (5 minutos)
    intraday_data = get_stock_data('^BVSP', period="1d", interval="5m")
    # Dados do dia anterior para fechamento
    previous_day_data = get_stock_data('^BVSP', period="2d", interval="1d")
    
    if not intraday_data.empty and not previous_day_data.empty:
        # Preço atual (último fechamento intraday)
        preco_atual = intraday_data['Close'].iloc[-1]
        # Abertura de hoje (primeiro valor do dia)
        abertura_hoje = intraday_data['Open'].iloc[0]
        # Fechamento do dia anterior
        fechamento_anterior = previous_day_data['Close'].iloc[-2]
        # Variação percentual do dia
        variacao_dia = ((preco_atual - abertura_hoje) / abertura_hoje) * 100
        
        # Exibindo métricas
        col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
        with col_metrics1:
            st.metric("Preço Atual", f"{preco_atual:.2f}")
        with col_metrics2:
            st.metric("Variação do Dia", f"{variacao_dia:.2f}%", delta_color="normal")
        with col_metrics3:
            st.metric("Fechamento Anterior", f"{fechamento_anterior:.2f}")
        with col_metrics4:
            st.metric("Abertura Hoje", f"{abertura_hoje:.2f}")
        
        # Gráfico de linha
        fig_intraday = go.Figure()
        fig_intraday.add_trace(go.Scatter(
            x=intraday_data.index,
            y=intraday_data['Close'],
            mode='lines',
            name="Fechamento",
            line=dict(color='royalblue', width=1)
        ))
        fig_intraday.update_layout(
            title="Intraday IBOV (5min)",
            yaxis_side="right",
            template="plotly_dark",
            height=700,
        )
        st.plotly_chart(fig_intraday, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para o IBOV.")
except Exception as e:
    st.error(f"Erro ao carregar dados intraday: {e}")

# Dados das ações
try:
    df = get_ibov_data().dropna()
    maiores_altas = df.nlargest(5, "Variação (%)")
    maiores_baixas = df.nsmallest(5, "Variação (%)")

    # Layout em colunas
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <h3 style="text-align: center;">↑ Maiores Altas do Dia ↑</h3>
            """, 
            unsafe_allow_html=True
        )
        for _, row in maiores_altas.iterrows():
            st.markdown(
                f"""
                <div style="
                    background-color: #d4edda; 
                    padding: 12px; 
                    border-radius: 8px; 
                    margin: 8px 0; 
                    box-shadow: 2px 2px 4px rgba(0,0,0,0.1); 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;">
                    <span style="font-weight: bold; font-size: 16px; color: black;">{row['Ação']}</span>
                    <span style="color: #155724; font-size: 16px; font-weight: bold;">{row['Variação (%)']:.2f}%</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

    with col2:
        st.markdown(
            """
            <h3 style="text-align: center;">↓ Maiores Baixas do Dia ↓</h3>
            """, 
            unsafe_allow_html=True
        )
        for _, row in maiores_baixas.iterrows():
            st.markdown(
                f"""
                <div style="
                    background-color: #f8d7da; 
                    padding: 12px; 
                    border-radius: 8px; 
                    margin: 8px 0; 
                    box-shadow: 2px 2px 4px rgba(0,0,0,0.1); 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;">
                    <span style="font-weight: bold; font-size: 16px; color: black;">{row['Ação']}</span>
                    <span style="color: #721c24; font-size: 16px; font-weight: bold;">{row['Variação (%)']:.2f}%</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

    # Botão para atualizar
    if st.button("🔄 Atualizar Dados"):
        st.experimental_rerun()

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")

# Rodapé
st.markdown("---")
st.write("**Fonte:** Yahoo Finance via yfinance. Dados refletem o pregão até o momento mais recente.")