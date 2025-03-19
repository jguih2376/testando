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




st.title('📉 Análise Histórica')
tab1, tab2, tab3 = st.tabs(["Triple Screen","Heatmap", "Desempenho"])
with tab1:
    st.title("Triple Screen")

    # Variável para armazenar o ticker selecionado
    ticker = None

    # Seleção do ativo e tipo de gráfico dentro do expander
    with st.expander("Seleção de Ativo", expanded=True):
        opcao = st.selectbox('Selecione:', ['Índices', 'Ações', 'Commodities'])
        
        # Seleção do tipo de gráfico dentro do expander
        col1,col2 = st.columns([3,1])
        with col2:
            chart_type = st.selectbox("Tipo de gráfico:", ["Candlestick", "Linha"], key="chart_type")
        with col1:    
            if opcao == 'Índices':
                indices = {
                    'IBOV': '^BVSP',
                    'S&P500': '^GSPC',     
                    'NASDAQ': '^IXIC',
                    'FTSE100': '^FTSE',
                    'DAX': '^GDAXI',
                    'CAC40': '^FCHI',
                    'SSE Composite': '000001.SS',
                    'Nikkei225': '^N225',
                    'Merval': '^MERV'
                }
                escolha = st.selectbox('Escolha o índice:', list(indices.keys()), index=0)
                ticker = indices[escolha]

            elif opcao == 'Commodities':
                commodities = {
                    'Ouro': 'GC=F',
                    'Prata': 'SI=F',
                    'Platinum': 'PL=F',     
                    'Cobre': 'HG=F',
                    'WTI Oil': 'CL=F',
                    'Brent Oil': 'BZ=F',
                    'Gasolina': 'RB=F',
                    'Gás Natural': 'NG=F',
                    'Gado Vivo': 'LE=F',
                    'Porcos Magros': 'HE=F',
                    'Milho': 'ZC=F',
                    'Soja': 'ZS=F',
                    'Cacau': 'CC=F',
                    'Café': 'KC=F'
                }    
                escolha = st.selectbox('Escolha o commodity:', list(commodities.keys()))
                ticker = commodities[escolha]

            elif opcao == 'Ações':
                acoes = ["PETR4", "VALE3", "ITUB4", "BBAS3", "BBDC4", "RAIZ4", "PRIO3", "VBBR3", "CSAN3", "UGPA3", "BPAC11", "SANB11",
                        "GGBR4", "CSNA3", "USIM5", "JBSS3", "ABEV3", "MRFG3", "BRFS3", "BEEF3", "ELET3", "NEOE3", "CPFE3", "ENGI11",
                        "EQTL3", "SUZB3", "KLBN11", "DTEX3", "RANI3", "MRFG3", "CYRE3", "MRVE3", "EZTC3", "CVCB3", "TRIS3", "WEGE3", "B3SA3",'EMBR3']
                acoes_dict = {acao: acao + '.SA' for acao in acoes}
                escolha = st.selectbox('Escolha a ação:', list(acoes_dict.keys()))
                ticker = acoes_dict[escolha]

    # Função para obter dados da ação
    def get_stock_data(ticker, period, interval):
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        return data

    # Renderizar gráficos apenas se um ticker foi selecionado
    if ticker:
        # Gráfico Diário
        try:
            daily_data = get_stock_data(ticker, period="6mo", interval="1d")
            if not daily_data.empty:
                fig_daily = go.Figure()
                if chart_type == "Candlestick":
                    fig_daily.add_trace(go.Candlestick(
                        x=daily_data.index,
                        open=daily_data['Open'],
                        high=daily_data['High'],
                        low=daily_data['Low'],
                        close=daily_data['Close'],
                        name="OHLC"
                    ))
                else:  # Linha
                    fig_daily.add_trace(go.Scatter(
                        x=daily_data.index,
                        y=daily_data['Close'],
                        mode='lines',
                        name="Fechamento",
                        line=dict(color='#00ccff', width=1)
                    ))
                fig_daily.update_layout(
                    title="Diário",
                    title_x=0.5,
                    yaxis_side="right",
                    template="plotly_dark",
                    height=700,
                    dragmode='pan',
                    xaxis=dict(
                        rangeslider=dict(visible=True, thickness=0.015),
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1, label="1m", step="month", stepmode="backward"),
                                dict(count=3, label="3m", step="month", stepmode="backward"),
                                dict(count=6, label="6m", step="month", stepmode="backward"),
                                dict(count=1, label="YTD", step="year", stepmode="todate")
                            ])
                        )
                    )
                )
                st.plotly_chart(fig_daily, use_container_width=True)
            else:
                st.warning("Nenhum dado diário disponível para este ticker.")
        except Exception as e:
            st.error(f"Erro ao carregar dados diários: {e}")

        # Divisão para gráficos semanal e anual
        col1, col2 = st.columns(2)

        # Gráfico Semanal
        with col1:
            try:
                weekly_data = get_stock_data(ticker, period="1y", interval="1wk")
                if not weekly_data.empty:
                    fig_weekly = go.Figure()
                    if chart_type == "Candlestick":
                        fig_weekly.add_trace(go.Candlestick(
                            x=weekly_data.index,
                            open=weekly_data['Open'],
                            high=weekly_data['High'],
                            low=weekly_data['Low'],
                            close=weekly_data['Close'],
                            name="OHLC"
                        ))
                    else:  # Linha
                        fig_weekly.add_trace(go.Scatter(
                            x=weekly_data.index,
                            y=weekly_data['Close'],
                            mode='lines',
                            name="Fechamento",
                            line=dict(color='#00ccff',width=1)
                        ))
                    fig_weekly.update_layout(
                        title="Semanal",
                        title_x=0.4,
                        yaxis_side="right",
                        template="plotly_dark",
                        height=450,
                        #margin=dict(l=40, r=40, t=60, b=40),  # Margens ajustadas
                        dragmode='pan',
                        xaxis=dict(
                            rangeslider=dict(visible=True, thickness=0.03),
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1, label="1m", step="month", stepmode="backward"),
                                    dict(count=3, label="3m", step="month", stepmode="backward"),
                                    dict(count=6, label="6m", step="month", stepmode="backward"),
                                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                                    dict(step="all")
                                ])
                            )
                        )
                    )
                    st.plotly_chart(fig_weekly, use_container_width=True)
                else:
                    st.warning("Nenhum dado semanal disponível para este ticker.")
            except Exception as e:
                st.error(f"Erro ao carregar dados semanais: {e}")

        # Gráfico Anual
        with col2:
            try:
                yearly_data = get_stock_data(ticker, period="10y", interval="1mo")
                if not yearly_data.empty:
                    fig_yearly = go.Figure()
                    if chart_type == "Candlestick":
                        fig_yearly.add_trace(go.Candlestick(
                            x=yearly_data.index,
                            open=yearly_data['Open'],
                            high=yearly_data['High'],
                            low=yearly_data['Low'],
                            close=yearly_data['Close'],
                            name="OHLC"
                        ))
                    else:  # Linha
                        fig_yearly.add_trace(go.Scatter(
                            x=yearly_data.index,
                            y=yearly_data['Close'],
                            mode='lines',
                            name="Fechamento",
                            line=dict(color='#00ccff',width=1)
                        ))
                    last_5_years = yearly_data.index[-60:]  # 5 anos * 12 meses
                    fig_yearly.update_layout(
                        title="Mensal",
                        title_x=0.4,
                        yaxis_side="right",
                        template="plotly_dark",
                        height=450,
                        dragmode='pan',
                        xaxis=dict(
                            range=[last_5_years[0], last_5_years[-1]],
                            rangeslider=dict(visible=True, thickness=0.03),
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1, label="1a", step="year", stepmode="backward"),
                                    dict(count=3, label="3a", step="year", stepmode="backward"),
                                    dict(count=5, label="5a", step="year", stepmode="backward"),
                                    dict(count=10, label="10a", step="year", stepmode="backward"),
                                    dict(step="all")
                                ])
                            )
                        )
                    )
                    st.plotly_chart(fig_yearly, use_container_width=True)
                else:
                    st.warning("Nenhum dado anual disponível para este ticker.")
            except Exception as e:
                st.error(f"Erro ao carregar dados anuais: {e}")

    else:
        st.info("Selecione um ativo e clique em 'Analisar' para visualizar os gráficos.")

    # Rodapé
    st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; font-size: 14px; color: #A9A9A9; margin-top: 20px;">
        <strong>Fonte:</strong> Yahoo Finance.<br>
    </div>
    """, unsafe_allow_html=True)





#__________________________________________________________________________________________________________________________________________________  
with tab2:  
    st.subheader('Retorno Mensal')
    # Formulário principal
    with st.expander('...', expanded=True):
        opcao = st.radio('Selecione:', ['Índices', 'Ações', 'Commodities'])

            

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


#"_______________________________________________________________________________________________________________________________________________________"
with tab3:
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

    # Usar sessão para armazenar os dados gerados
    if 'dados' not in st.session_state:
        st.session_state.dados = None
    if 'fig' not in st.session_state:
        st.session_state.fig = None
    if 'df_valorizacao' not in st.session_state:
        st.session_state.df_valorizacao = None
    if 'ticker' not in st.session_state:
        st.session_state.ticker = None
    if 'legenda_dict' not in st.session_state:
        st.session_state.legenda_dict = None
    if 'normalizado' not in st.session_state:
        st.session_state.normalizado = True

    with st.expander('...', expanded=True):
        opcao1 = st.radio ('Selecione:', ['Ações','Índices', 'Commodities'])
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

        # Gerar o gráfico e a tabela
        if submit_button and ticker:
            dados = carregar_dados(ticker, data_inicio, data_fim)
            if not dados.empty:
                fig = criar_grafico(ticker, dados, normalizado, legenda_dict)
                df_valorizacao = calcular_valorizacao(dados, legenda_dict)
                df_valorizacao = df_valorizacao.sort_values(by='Período (%)', ascending=False)

                # Armazenar os dados na sessão
                st.session_state.dados = dados
                st.session_state.fig = fig
                st.session_state.df_valorizacao = df_valorizacao
                st.session_state.ticker = ticker
                st.session_state.legenda_dict = legenda_dict
                st.session_state.normalizado = normalizado

        # Exibir o gráfico e a tabela se existirem na sessão
        if st.session_state.fig and st.session_state.df_valorizacao is not None:
            col1, col2, col3 = st.columns([1, 4, 1])
            st.plotly_chart(st.session_state.fig)
            col1, col2 = st.columns([1, 4])
            with col2:
                st.dataframe(st.session_state.df_valorizacao)
        elif submit_button and not st.session_state.dados:
            st.warning("Nenhum dado disponível para os tickers selecionados.")

        # Botão independente para gerar o PDF
        if st.session_state.fig and st.button("Gerar PDF"):
            try:
                img_bytes = st.session_state.fig.to_image(format="png")
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                img_html = f'<img src="data:image/png;base64,{img_base64}" style="width:100%;"/>'
                table_html = st.session_state.df_valorizacao.to_html()
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
                pdf_bytes = pdfkit.from_string(html_content, False)

                st.download_button(
                    label="Clique aqui se o download não iniciar automaticamente",
                    data=pdf_bytes,
                    file_name="desempenho_relativo.pdf",
                    mime="application/pdf",
                    key="download_pdf"
                )
                st.markdown(
                    f"""
                    <script>
                        const link = document.createElement('a');
                        link.href = 'data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode('utf-8')}';
                        link.download = 'desempenho_relativo.pdf';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    </script>
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Erro ao gerar o PDF: {str(e)}. Certifique-se de que o Kaleido está instalado (`pip install kaleido`).")

    st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; font-size: 14px; color: #A9A9A9; margin-top: 20px;">
        <strong>Fonte:</strong> Yahoo Finance.<br>
    </div>
    """, unsafe_allow_html=True)