import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from datetime import datetime
import pytz

# Função para pegar dados do Ibovespa do dia atual
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

# Interface com Streamlit
st.set_page_config(page_title="Ibovespa Hoje", layout="wide")
st.title("📊 Maiores Altas e Baixas do Ibovespa")

# Horário atual em BRT
brt = pytz.timezone('America/Sao_Paulo')
data_atual = datetime.now(brt).strftime("%d/%m/%Y %H:%M:%S")
st.write(f"**Data:** 11 de Março de 2025 (atualizado até {data_atual} BRT)")

try:
    df = get_ibov_data().dropna()
    maiores_altas = df.nlargest(5, "Variação (%)")
    maiores_baixas = df.nsmallest(5, "Variação (%)")

    # Layout em colunas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚀 Maiores Altas do Dia")
        # Gráfico de barras horizontais
        fig_altas = px.bar(
            maiores_altas, y="Ação", x="Variação (%)", 
            orientation="h", 
            color="Variação (%)", color_continuous_scale="Greens",
            text=maiores_altas["Variação (%)"].round(2).astype(str) + "%",
            height=300
        )
        fig_altas.update_traces(textposition="auto")
        fig_altas.update_layout(showlegend=False)
        st.plotly_chart(fig_altas, use_container_width=True)

        # Cartões estilizados para altas
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
                    <span style="font-weight: bold; font-size: 16px;">{row['Ação']}</span>
                    <span style="color: #155724; font-size: 16px; font-weight: bold;">{row['Variação (%)']:.2f}%</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

    with col2:
        st.subheader("📉 Maiores Baixas do Dia")
        # Gráfico de barras horizontais
        fig_baixas = px.bar(
            maiores_baixas, y="Ação", x="Variação (%)", 
            orientation="h", 
            color="Variação (%)", color_continuous_scale="Reds",
            text=maiores_baixas["Variação (%)"].round(2).astype(str) + "%",
            height=300
        )
        fig_baixas.update_traces(textposition="auto")
        fig_baixas.update_layout(showlegend=False)
        st.plotly_chart(fig_baixas, use_container_width=True)

        # Cartões estilizados para baixas
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
                    <span style="font-weight: bold; font-size: 16px;">{row['Ação']}</span>
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