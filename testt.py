import streamlit as st
import pandas as pd
import yfinance as yf

# Função para buscar dados com cache
@st.cache_data(ttl=1200)  # Cache de 20 minutos
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
    resultados = {"Ação": [], "Variação (%)": [], "Último Preço": []}
    
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="2d", interval="1d")["Close"]
            if len(data) < 2:
                st.warning(f"{ticker[:-3]}: Dados insuficientes para calcular a variação.")
                continue
            
            ultimo_preco = data.iloc[-1]
            variacao = ((data.iloc[-1] - data.iloc[-2]) / data.iloc[-2]) * 100
            
            resultados["Ação"].append(ticker[:-3])
            resultados["Variação (%)"].append(variacao)
            resultados["Último Preço"].append(ultimo_preco)
        except Exception as e:
            st.error(f"Erro ao processar {ticker[:-3]}: {e}")
    
    # Criar DataFrame
    df = pd.DataFrame(resultados)
    # Arredondar valores para melhor visualização
    df["Variação (%)"] = df["Variação (%)"].round(2)
    df["Último Preço"] = df["Último Preço"].round(2)
    return df

# Interface do Streamlit
st.title("Ações do IBOV - Variação Diária")
st.write("Dados atualizados a cada 20 minutos.")

# Buscar e exibir os dados
try:
    df = get_ibov_data()
    if df.empty:
        st.error("Nenhum dado disponível no momento.")
    else:
        # Exibir tabela interativa
        st.dataframe(df, use_container_width=True)
        
        # Adicionar opção para baixar os dados como CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar dados como CSV",
            data=csv,
            file_name="ibov_variacao.csv",
            mime="text/csv"
        )
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")

# Rodapé
st.write(f"Última atualização: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}")