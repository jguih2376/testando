import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# Função para pegar dados do Ibovespa do dia atual
def get_ibov_data():
    # Lista de tickers do Ibovespa
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
    
    # Baixando os dados do dia atual (fechamento até o momento)
    data = yf.download(tickers, period="1d", interval="1d")["Close"]
    
    # Pegando o preço de abertura para calcular a variação do dia
    open_data = yf.download(tickers, period="1d", interval="1d")["Open"]
    
    if data.empty or open_data.empty:
        raise ValueError("Dados insuficientes para calcular a variação do dia.")
    
    # Calculando a variação percentual do dia (fechamento vs abertura)
    variacao = ((data.iloc[-1] - open_data.iloc[-1]) / open_data.iloc[-1]) * 100
    
    return pd.DataFrame({
        "Ação": [ticker[:-3] for ticker in tickers], 
        "Variação (%)": variacao.values
    })

# Interface com Streamlit
st.title("Maiores Altas e Baixas do Ibovespa - Dia Atual")
# Horário atual em BRT
brt = pytz.timezone('America/Sao_Paulo')
data_atual = datetime.now(brt).strftime("%d/%m/%Y %H:%M:%S")
st.write(f"Data: 11 de Março de 2025 (atualizado até {data_atual} BRT)")

try:
    df = get_ibov_data()
    
    # Removendo valores NaN (caso alguma ação não tenha dados)
    df = df.dropna()
    
    # Filtrando as 5 maiores altas e baixas
    maiores_altas = df.nlargest(5, "Variação (%)")
    maiores_baixas = df.nsmallest(5, "Variação (%)")
    
    st.subheader("5 Maiores Altas do Dia")
    st.dataframe(maiores_altas.style.format({"Variação (%)": "{:.2f}"}))

    st.subheader("5 Maiores Baixas do Dia")
    st.dataframe(maiores_baixas.style.format({"Variação (%)": "{:.2f}"}))

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")

st.write("Fonte: Yahoo Finance via yfinance. Dados refletem o pregão até o momento mais recente.")