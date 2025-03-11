import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.title("🌎 Panorama do Mercado")
st.write("Visão geral do mercado atual.")

# Criando as abas
tab1, tab2, tab3 = st.tabs(['Panorama', 'TradingView', 'Triple Screen'])

# Aba 1: Panorama
with tab1:
    st.write('Aqui está o panorama geral do mercado.')

# Aba 2: TradingView
with tab2:
    st.write('Monitorando os mercados com o TradingView.')
    tradingview_html = """
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:100%;width:100%">
    <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
    <div class="tradingview-widget-copyright"><a href="https://br.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text">Monitore todos os mercados no TradingView</span></a></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
    {
    "width": "700",
    "height": "600",
    "symbol": "BMFBOVESPA:IBOV",
    "timezone": "America/Sao_Paulo",
    "theme": "light",
    "style": "1",
    "locale": "br",
    "backgroundColor": "rgba(242, 242, 242, 1)",
    "withdateranges": true,
    "range": "6M",
    "hide_side_toolbar": false,
    "allow_symbol_change": false,
    "save_image": false,
    "calendar": false,
    "support_host": "https://www.tradingview.com"
    }
    </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(tradingview_html, height=600)

# Aba 3: Triple Screen
with tab3:
    st.title("Sistema de Cotação de Ações")

    # Variável para armazenar o ticker selecionado
    ticker = None

    # Seleção do ativo dentro do expander
    with st.expander("Seleção de Ativo", expanded=True):
        opcao = st.radio('Selecione:', ['Índices', 'Ações', 'Commodities'])
        with st.form(key='form_ativo'):
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
                analisar = st.form_submit_button('Analisar')
                if analisar:
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
                    'Porcos Magros': 'HE=F',  # Corrigido de 'LE=F' duplicado
                    'Milho': 'ZC=F',
                    'Soja': 'ZS=F',
                    'Cacau': 'CC=F',
                    'Café': 'KC=F'
                }    
                escolha = st.selectbox('Escolha o commodity:', list(commodities.keys()))
                analisar = st.form_submit_button('Analisar')
                if analisar:
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
                escolha = st.selectbox('Escolha a ação:', list(acoes_dict.keys()))
                analisar = st.form_submit_button('Analisar')
                if analisar:
                    ticker = acoes_dict[escolha]

    # Seleção do tipo de gráfico (fora do expander)
    chart_type = st.selectbox("Tipo de gráfico:", ["Candlestick", "Linha"], key="chart_type")

    # Função para obter dados da ação
    def get_stock_data(ticker, period, interval):
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        return data

    # Renderizar gráficos apenas se um ticker foi selecionado
    if ticker:
        # Gráfico Diário
        try:
            daily_data = get_stock_data(ticker, period="1y", interval="1d")
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
                        line=dict(color='royalblue', width=1)
                    ))
                last_3_months = daily_data.index[-3:]  # 3 meses
                fig_daily.update_layout(
                    title="Diário",
                    yaxis_side="right",
                    template="plotly_dark",
                    height=700,
                    xaxis=dict(
                        rangeslider=dict(visible=True, thickness=0.015),
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
                            line=dict(color='royalblue', width=1)
                        ))
                    fig_weekly.update_layout(
                        title="Semanal",
                        title_x=0.4,
                        yaxis_side="right",
                        template="plotly_dark",
                        height=450,
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
                            line=dict(color='royalblue', width=1)
                        ))
                    last_5_years = yearly_data.index[-60:]  # 5 anos * 12 meses
                    fig_yearly.update_layout(
                        title="Mensal",
                        title_x=0.4,
                        yaxis_side="right",
                        template="plotly_dark",
                        height=450,
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
    st.write("Dados fornecidos por Yahoo Finance via yfinance.")