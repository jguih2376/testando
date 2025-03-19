import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pdfkit
import base64
from io import BytesIO

with st.tab2:
    st.subheader("Desempenho Relativo dos Ativos")

    @st.cache_data(ttl=600)  
    def carregar_dados(tickers, data_inicio, data_fim):
        if not tickers:
            return pd.DataFrame()

        dados = {}
        for ticker in tickers:
            hist = yf.Ticker(ticker).history(start=data_inicio, end=data_fim)['Close']
            dados[ticker] = hist

        return pd.DataFrame(dados).dropna()  

    def calcular_performance(dados):
        if not dados.empty:
            return (dados / dados.iloc[0] - 1) * 100
        return dados

    def calcular_valorizacao(dados, legenda_dict):
        if dados.empty:
            return pd.DataFrame()
        
        df_var = pd.DataFrame(index=dados.columns)
        df_var['1 Dia (%)'] = ((dados.iloc[-1] / dados.iloc[-2]) - 1) * 100 if len(dados) > 1 else None
        df_var['1 Semana (%)'] = ((dados.iloc[-1] / dados.iloc[-5]) - 1) * 100 if len(dados) > 5 else None
        df_var['1 Mês (%)'] = ((dados.iloc[-1] / dados.iloc[-21]) - 1) * 100 if len(dados) > 21 else None
        df_var['Período (%)'] = ((dados.iloc[-1] / dados.iloc[0]) - 1) * 100
        df_var = df_var.round(2)
        df_var.index = df_var.index.map(lambda ticker: legenda_dict.get(ticker, ticker))
        return df_var

    def criar_grafico(ativos_selecionados, dados, normalizado=True, legenda_dict=None):
        fig = go.Figure()
        for ativo in ativos_selecionados:
            nome_ativo = legenda_dict.get(ativo, ativo)
            y_data = calcular_performance(dados)[ativo] if normalizado else dados[ativo]
            fig.add_trace(go.Scatter(
                x=dados.index,
                y=y_data,
                name=nome_ativo,
                mode='lines',
                line=dict(width=1)
            ))
            fig.add_trace(go.Scatter(
                x=[dados.index[-1]],
                y=[y_data.iloc[-1]],
                mode='markers',
                marker=dict(size=5, color='red', symbol='circle'),
                name=f'{nome_ativo} - Último Preço',
                showlegend=False
            ))
        fig.update_layout(
            title=f"{'Desempenho Relativo (%)' if normalizado else 'Preço dos Ativos'}",
            yaxis_title='Performance (%)' if normalizado else 'Preço',
            xaxis=dict(
                tickformat='%b %Y',
                tickmode='array',
                tickvals=dados.index[::63]
            ),
            legend_title='Ativos',
            legend_orientation='h',
            plot_bgcolor='rgba(211, 211, 211, 0.10)',
            height=600,
            margin=dict(r=10)
        )
        fig.update_xaxes(showgrid=True, gridwidth=0.1, gridcolor='gray', griddash='dot')
        fig.update_yaxes(showgrid=True, gridwidth=0.1, gridcolor='gray', griddash='dot')
        return fig

    indices = {'IBOV': '^BVSP', 'EWZ': 'EWZ', 'S&P500': '^GSPC', 'NASDAQ': '^IXIC', 'FTSE100': '^FTSE', 'DAX': '^GDAXI',
               'CAC40': '^FCHI', 'SSE Composite': '000001.SS', 'Nikkei225': '^N225', 'Merval': '^MERV'}
    commodities = {'Ouro': 'GC=F', 'Prata': 'SI=F', 'Platinum': 'PL=F', 'Cobre': 'HG=F', 'WTI Oil': 'CL=F', 'Brent Oil': 'BZ=F',
                   'Gasolina': 'RB=F', 'Gás Natural': 'NG=F', 'Gado Vivo': 'LE=F', 'Porcos Magros': 'LE=F', 'Milho': 'ZC=F',
                   'Soja': 'ZS=F', 'Cacau': 'CC=F', 'Café': 'KC=F'}
    acoes = ["PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4", "RAIZ4", "PRIO3", "VBBR3", "CSAN3", "UGPA3", "BPAC11", "SANB11",
             "GGBR4", "CSNA3", "USIM5", "JBSS3", "ABEV3", "MRFG3", "BRFS3", "BEEF3", "ELET3", "NEOE3", "CPFE3", "ENGI11",
             "EQTL3", "SUZB3", "KLBN11", "DTEX3", "RANI3", "MRFG3", "CYRE3", "MRVE3", "EZTC3", "CVCB3", "TRIS3", "WEGE3", "B3SA3"]
    acoes_dict = {acao: acao + '.SA' for acao in acoes}

    with st.expander('...', expanded=True):
        opcao1 = st.selectbox('Selecione:', ['Índices', 'Ações', 'Commodities'])
        with st.form(key='meu_form'):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if opcao1 == 'Índices':
                    escolha = st.multiselect('', list(indices.keys()), placeholder='')
                    ticker = [indices[indice] for indice in escolha]
                    legenda_dict = {v: k for k, v in indices.items()}
                elif opcao1 == 'Commodities':
                    escolha = st.multiselect('', list(commodities.keys()), placeholder='')
                    ticker = [commodities[commodity] for commodity in escolha]
                    legenda_dict = {v: k for k, v in commodities.items()}
                elif opcao1 == 'Ações':
                    escolha = st.multiselect('', list(acoes_dict.keys()), placeholder='')
                    ticker = [acoes_dict[acao] for acao in escolha]
                    legenda_dict = {v: k for k, v in acoes_dict.items()}
            with col2:
                data_inicio = st.date_input('Data de início', pd.to_datetime('2020-01-01').date(), format='DD/MM/YYYY')
            with col3:
                data_fim = st.date_input('Data de término', pd.to_datetime('today').date(), format='DD/MM/YYYY')
            normalizado = st.checkbox("Exibir desempenho percentual", value=True)
            submit_button = st.form_submit_button(label='Gerar Gráfico')

        if submit_button and ticker:
            col1, col2, col3 = st.columns([1, 4, 1])
            dados = carregar_dados(ticker, data_inicio, data_fim)
            if not dados.empty:
                fig = criar_grafico(ticker, dados, normalizado, legenda_dict)
                st.plotly_chart(fig)
                df_valorizacao = calcular_valorizacao(dados, legenda_dict)
                df_valorizacao = df_valorizacao.sort_values(by='Período (%)', ascending=False)
                col1, col2 = st.columns([1, 4])
                with col2:
                    st.dataframe(df_valorizacao)

                # Botão para gerar PDF
                if st.button("Gerar PDF"):
                    # Converter o gráfico para imagem (base64)
                    img_bytes = fig.to_image(format="png")
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    img_html = f'<img src="data:image/png;base64,{img_base64}" style="width:100%;"/>'

                    # Converter a tabela para HTML
                    table_html = df_valorizacao.to_html()

                    # Criar o HTML completo
                    html_content = f"""
                    <html>
                    <head><title>Desempenho Relativo dos Ativos</title></head>
                    <body>
                        <h1>Desempenho Relativo dos Ativos</h1>
                        {img_html}
                        <h2>Valorização</h2>
                        {table_html}
                        <p><strong>Fonte:</strong> Yahoo Finance</p>
                    </body>
                    </html>
                    """

                    # Gerar o PDF
                    pdf_file = "desempenho_relativo.pdf"
                    pdfkit.from_string(html_content, pdf_file)

                    # Fornecer o download do PDF
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="Baixar PDF",
                            data=f,
                            file_name="desempenho_relativo.pdf",
                            mime="application/pdf"
                        )
            else:
                st.warning("Nenhum dado disponível para os tickers selecionados.")

    st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; font-size: 14px; color: #A9A9A9; margin-top: 20px;">
        <strong>Fonte:</strong> Yahoo Finance.<br>
    </div>
    """, unsafe_allow_html=True)