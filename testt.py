import streamlit as st
import pandas as pd
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime
import pdfkit
import base64
from io import BytesIO


st.subheader('Retorno Mensal')
# Formulário principal
with st.expander('...', expanded=True):
    opcao = st.radio('Selecione:', ['Índices', 'Ações', 'Commodities'])

    col1,col2 = st.columns([3,1])
    with col2:
        chart_type = st.selectbox("Tipo de gráfico:", ["Candlestick", "Linha"], key="chart_type")
        
    with col1:
        with st.form(key='form_ativo'):
            if opcao == 'Índices':
                indices = {'IBOV': '^BVSP',
                        'S&P500': '^GSPC',     
                        'NASDAQ': '^IXIC',
                        'FTSE100':'^FTSE',
                        'DAX':'^GDAXI',
                        'CAC40':'^FCHI',
                        'SSE Composite':'000001.SS',
                        'Nikkei225':'^N225',
                        'Merval':'^MERV'}
                
                escolha = st.selectbox('', list(indices.keys()),index=0)
                analisar = st.form_submit_button('Analisar')
                ticker = indices[escolha]

            elif opcao == 'Commodities':
                commodities = {'Ouro': 'GC=F',
                            'Prata': 'SI=F',
                            'Platinum': 'PL=F',     
                            'Cobre': 'HG=F',
                            
                            'WTI Oil':'CL=F',
                            'Brent Oil':'BZ=F',
                            'Gasolina':'RB=F',
                            'Gás Natural':'NG=F',
                            
                            'Gado Vivo':'LE=F',
                            'Porcos Magros':'LE=F',

                            'Milho':'ZC=F',
                            'Soja':'ZS=F',
                            'Cacau':'CC=F',
                            'Café':'KC=F'}    
                
                escolha = st.selectbox('', list(commodities.keys()))
                analisar = st.form_submit_button('Analisar')
                ticker = commodities[escolha]

            elif opcao == 'Ações':
                acoes = ['ALOS3', 'ABEV3', 'ASAI3', 'AURE3', 'AMOB3', 'AZUL4', 'AZZA3', 'B3SA3', 'BBSE3', 'BBDC3', 'BBDC4', 
                        'BRAP4', 'BBAS3', 'BRKM5', 'BRAV3', 'BRFS3', 'BPAC11', 'CXSE3', 'CRFB3', 'CCRO3', 'CMIG4', 'COGN3', 
                        'CPLE6', 'CSAN3', 'CPFE3', 'CMIN3', 'CVCB3', 'CYRE3', 'ELET3', 'ELET6', 'EMBR3', 'ENGI11', 'ENEV3', 
                        'EGIE3', 'EQTL3', 'FLRY3', 'GGBR4', 'GOAU4', 'NTCO3', 'HAPV3', 'HYPE3', 'IGTI11', 'IRBR3', 'ISAE4', 
                        'ITSA4', 'ITUB4', 'JBSS3', 'KLBN11', 'RENT3', 'LREN3', 'LWSA3', 'MGLU3', 'POMO4', 'MRFG3', 'BEEF3', 
                        'MRVE3', 'MULT3', 'PCAR3', 'PETR3', 'PETR4', 'RECV3', 'PRIO3', 'PETZ3', 'PSSA3', 'RADL3', 'RAIZ4', 
                        'RDOR3', 'RAIL3', 'SBSP3', 'SANB11', 'STBP3', 'SMTO3', 'CSNA3', 'SLCE3', 'SUZB3', 'TAEE11', 'VIVT3', 
                        'TIMS3', 'TOTS3', 'UGPA3', 'USIM5', 'VALE3', 'VAMO3', 'VBBR3', 'VIVA3', 'WEGE3', 'YDUQ3']

                # Criando um dicionário com chave como o nome da ação e valor como o nome da ação com '.SA'
                acoes_dict = {acao: acao + '.SA' for acao in acoes}

                escolha = st.selectbox('', list(acoes_dict.keys()))
                analisar = st.form_submit_button('Analisar')
                ticker = acoes_dict[escolha]

    if analisar:









        
        data_inicial = ('1999-12-01')
        data_final = ('2030-12-31')

        # Baixa os dados do Yahoo Finance
        dados = yf.download(ticker, start=data_inicial, end=data_final, interval="1mo")

        if not dados.empty:
            retornos = dados['Close'].pct_change().dropna()
            # Adiciona colunas de ano e mês para organização
            retornos = retornos.reset_index()
            retornos['Year'] = retornos['Date'].dt.year
            retornos['Month'] = retornos['Date'].dt.month

            # Criar a tabela pivot sem média, apenas reorganizando os dados
            tabela_retornos = retornos.pivot(index='Year', columns='Month', values=ticker)
            tabela_retornos.columns = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                                        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

            # Criando Heatmap
            fig, ax = plt.subplots(figsize=(12, 9))
            cmap = sns.color_palette('RdYlGn', 15)
            sns.heatmap(tabela_retornos, cmap=cmap, annot=True, fmt='.2%', center=0, vmax=0.025, vmin=-0.025, cbar=False,
                        linewidths=0.5, xticklabels=True, yticklabels=True, ax=ax)
            ax.set_title(f'Heatmap Retorno Mensal - {escolha}', fontsize=18)
            ax.set_yticklabels(ax.get_yticklabels(), rotation=0, verticalalignment='center', fontsize='12')
            ax.set_xticklabels(ax.get_xticklabels(), fontsize='12')
            plt.ylabel('')
            st.pyplot(fig)

            # Estatísticas
            stats = pd.DataFrame(tabela_retornos.mean(), columns=['Média'])
            stats['Mediana'] = tabela_retornos.median()
            stats['Maior'] = tabela_retornos.max()
            stats['Menor'] = tabela_retornos.min()
            stats['Positivos'] = tabela_retornos.gt(0).sum() / tabela_retornos.count() # .gt(greater than) = Contagem de números maior que zero
            stats['Negativos'] = tabela_retornos.le(0).sum() / tabela_retornos.count() # .le(less than) = Contagem de números menor que zero

            # Stats_A
            stats_a = stats[['Média', 'Mediana', 'Maior', 'Menor']].transpose()

            fig, ax = plt.subplots(figsize=(12, 2))
            sns.heatmap(stats_a, cmap=cmap, annot=True, fmt='.2%', center=0, vmax=0.025, vmin=-0.025, cbar=False,
                        linewidths=0.5, xticklabels=True, yticklabels=True, ax=ax)
            st.pyplot(fig)

            # Stats_B
            stats_b = stats[['Positivos', 'Negativos']].transpose()

            fig, ax = plt.subplots(figsize=(12, 1))
            sns.heatmap(stats_b, cmap=sns.color_palette("magma", as_cmap=True), annot=True, fmt='.2%', center=0, vmax=0.025, vmin=-0.025, cbar=False,
                        linewidths=0.5, xticklabels=True, yticklabels=True, ax=ax)
            st.pyplot(fig)

        else:
            st.error("Erro ao buscar os dados. Verifique o ticker ou tente novamente mais tarde.")