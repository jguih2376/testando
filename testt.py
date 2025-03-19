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

def app():
    st.title('📉 Análise Histórica')
    tab1, tab2 = st.tabs(["Heatmap", "Desempenho"])  
    with tab1:  
        st.subheader('Retorno Mensal')

        # Inicializar variáveis no session_state
        if 'tabela_retornos' not in st.session_state:
            st.session_state.tabela_retornos = None
        if 'stats_a' not in st.session_state:
            st.session_state.stats_a = None
        if 'stats_b' not in st.session_state:
            st.session_state.stats_b = None
        if 'escolha' not in st.session_state:
            st.session_state.escolha = None

        # Formulário principal
        with st.expander('...', expanded=True):
            opcao = st.radio('Selecione:', ['Índices', 'Ações', 'Commodities'])
            with st.form(key='form_ativo'):
                if opcao == 'Índices':
                    indices = {'IBOV': '^BVSP', 'S&P500': '^GSPC', 'NASDAQ': '^IXIC', 'FTSE100': '^FTSE', 'DAX': '^GDAXI',
                               'CAC40': '^FCHI', 'SSE Composite': '000001.SS', 'Nikkei225': '^N225', 'Merval': '^MERV'}
                    escolha = st.selectbox('', list(indices.keys()), index=0)
                    ticker = indices[escolha]
                elif opcao == 'Commodities':
                    commodities = {'Ouro': 'GC=F', 'Prata': 'SI=F', 'Platinum': 'PL=F', 'Cobre': 'HG=F', 'WTI Oil': 'CL=F',
                                   'Brent Oil': 'BZ=F', 'Gasolina': 'RB=F', 'Gás Natural': 'NG=F', 'Gado Vivo': 'LE=F',
                                   'Porcos Magros': 'LE=F', 'Milho': 'ZC=F', 'Soja': 'ZS=F', 'Cacau': 'CC=F', 'Café': 'KC=F'}
                    escolha = st.selectbox('', list(commodities.keys()))
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
                    acoes_dict = {acao: acao + '.SA' for acao in acoes}
                    escolha = st.selectbox('', list(acoes_dict.keys()))
                    ticker = acoes_dict[escolha]
                
                analisar = st.form_submit_button('Gerar Gráfico')

            # Gerar os gráficos e tabelas
            if analisar:
                data_inicial = '1999-12-01'
                data_final = '2030-12-31'

                # Baixa os dados do Yahoo Finance
                dados = yf.download(ticker, start=data_inicial, end=data_final, interval="1mo")

                if not dados.empty:
                    retornos = dados['Close'].pct_change().dropna()
                    retornos = retornos.reset_index()
                    retornos['Year'] = retornos['Date'].dt.year
                    retornos['Month'] = retornos['Date'].dt.month

                    # Criar a tabela pivot
                    tabela_retornos = retornos.pivot(index='Year', columns='Month', values='Close')
                    tabela_retornos.columns = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                                               'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

                    # Estatísticas
                    stats = pd.DataFrame(tabela_retornos.mean(), columns=['Média'])
                    stats['Mediana'] = tabela_retornos.median()
                    stats['Maior'] = tabela_retornos.max()
                    stats['Menor'] = tabela_retornos.min()
                    stats['Positivos'] = tabela_retornos.gt(0).sum() / tabela_retornos.count()
                    stats['Negativos'] = tabela_retornos.le(0).sum() / tabela_retornos.count()

                    stats_a = stats[['Média', 'Mediana', 'Maior', 'Menor']].transpose()
                    stats_b = stats[['Positivos', 'Negativos']].transpose()

                    # Armazenar no session_state
                    st.session_state.tabela_retornos = tabela_retornos
                    st.session_state.stats_a = stats_a
                    st.session_state.stats_b = stats_b
                    st.session_state.escolha = escolha

            # Exibir os gráficos se existirem no session_state
            if st.session_state.tabela_retornos is not None:
                # Heatmap principal
                fig1, ax1 = plt.subplots(figsize=(12, 9))
                cmap = sns.color_palette('RdYlGn', 15)
                sns.heatmap(st.session_state.tabela_retornos, cmap=cmap, annot=True, fmt='.2%', center=0, vmax=0.025, vmin=-0.025, cbar=False,
                            linewidths=0.5, xticklabels=True, yticklabels=True, ax=ax1)
                ax1.set_title(f'Heatmap Retorno Mensal - {st.session_state.escolha}', fontsize=18)
                ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0, verticalalignment='center', fontsize='12')
                ax1.set_xticklabels(ax1.get_xticklabels(), fontsize='12')
                plt.ylabel('')
                st.pyplot(fig1)

                # Stats_A
                fig2, ax2 = plt.subplots(figsize=(12, 2))
                sns.heatmap(st.session_state.stats_a, cmap=cmap, annot=True, fmt='.2%', center=0, vmax=0.025, vmin=-0.025, cbar=False,
                            linewidths=0.5, xticklabels=True, yticklabels=True, ax=ax2)
                st.pyplot(fig2)

                # Stats_B
                fig3, ax3 = plt.subplots(figsize=(12, 1))
                sns.heatmap(st.session_state.stats_b, cmap=sns.color_palette("magma", as_cmap=True), annot=True, fmt='.2%', center=0, vmax=0.025, vmin=-0.025, cbar=False,
                            linewidths=0.5, xticklabels=True, yticklabels=True, ax=ax3)
                st.pyplot(fig3)

            elif analisar and st.session_state.tabela_retornos is None:
                st.error("Erro ao buscar os dados. Verifique o ticker ou tente novamente mais tarde.")

            # Botão independente para gerar o PDF
            if st.session_state.tabela_retornos is not None and st.button("Gerar PDF"):
                try:
                    # Converter os heatmaps para imagens
                    buf1 = BytesIO()
                    fig1.savefig(buf1, format="png", bbox_inches='tight')
                    img1_base64 = base64.b64encode(buf1.getvalue()).decode('utf-8')
                    buf1.close()

                    buf2 = BytesIO()
                    fig2.savefig(buf2, format="png", bbox_inches='tight')
                    img2_base64 = base64.b64encode(buf2.getvalue()).decode('utf-8')
                    buf2.close()

                    buf3 = BytesIO()
                    fig3.savefig(buf3, format="png", bbox_inches='tight')
                    img3_base64 = base64.b64encode(buf3.getvalue()).decode('utf-8')
                    buf3.close()

                    # Criar o conteúdo HTML para o PDF
                    html_content = f"""
                    <html>
                    <head><title>Heatmap Retorno Mensal - {st.session_state.escolha}</title></head>
                    <body>
                        <h1>Heatmap Retorno Mensal - {st.session_state.escolha}</h1>
                        <img src="data:image/png;base64,{img1_base64}" style="width:100%;"/>
                        <h2>Estatísticas (Média, Mediana, Maior, Menor)</h2>
                        <img src="data:image/png;base64,{img2_base64}" style="width:100%;"/>
                        <h2>Estatísticas (Positivos, Negativos)</h2>
                        <img src="data:image/png;base64,{img3_base64}" style="width:100%;"/>
                        <p><strong>Fonte:</strong> Yahoo Finance</p>
                    </body>
                    </html>
                    """

                    # Gerar o PDF em memória
                    pdf_bytes = pdfkit.from_string(html_content, False)

                    # Download automático com fallback
                    st.download_button(
                        label="Clique aqui se o download não iniciar automaticamente",
                        data=pdf_bytes,
                        file_name=f"heatmap_{st.session_state.escolha}.pdf",
                        mime="application/pdf",
                        key="download_pdf"
                    )
                    st.markdown(
                        f"""
                        <script>
                            const link = document.createElement('a');
                            link.href = 'data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode('utf-8')}';
                            link.download = 'heatmap_{st.session_state.escolha}.pdf';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar o PDF: {str(e)}. Certifique-se de que as dependências estão instaladas (`pip install pdfkit matplotlib seaborn`).")

    st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; font-size: 14px; color: #A9A9A9; margin-top: 20px;">
        <strong>Fonte:</strong> Yahoo Finance.<br>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    app()