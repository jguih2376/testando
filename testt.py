import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.title("🌎 Panorama do Mercado")
st.write("Visão geral do mercado atual.")

# Criando as abas
tab1, tab2, tab3 = st.tabs(['Panorama', 'TradingView', 'Triple Screen'])

# Abas
with tab1:  # Panorama
    st.write('Aqui está o panorama geral do mercado.')

with tab2:  # TradingView
    st.write('Monitorando os mercados com o TradingView.')
    # HTML com o widget do TradingView
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

with tab3:  # Triple Screen
    st.title("Sistema de Cotação de Ações")
    ticker = st.text_input("Digite o código da ação (ex: AAPL, MSFT, PETR4.SA):", value="AAPL")

    # Função para buscar dados das ações
    def get_stock_data(ticker, period, interval):
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period, interval=interval)
            return data
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return None

    # Gráficos para diferentes períodos
    try:
        intraday_data = get_stock_data(ticker, period="1y", interval="1d")
        if intraday_data is not None and not intraday_data.empty:
            fig_intraday = go.Figure()
            fig_intraday.add_trace(go.Candlestick(
                x=intraday_data.index,
                open=intraday_data['Open'],
                high=intraday_data['High'],
                low=intraday_data['Low'],
                close=intraday_data['Close'],
                name="OHLC"
            ))
            fig_intraday.update_layout(
                title=f"Intraday ({ticker})",
                yaxis_title="Preço",
                template="plotly_dark",
                height=700
            )
            st.plotly_chart(fig_intraday, use_container_width=True)
        else:
            st.warning(f"Sem dados intraday para {ticker}.")
    except Exception as e:
        st.error(f"Erro ao carregar dados intraday: {e}")

    # Divisão para gráficos semanal e anual
    col1, col2 = st.columns(2)

    with col1:
        weekly_data = get_stock_data(ticker, period="1y", interval="1wk")
        if weekly_data is not None and not weekly_data.empty:
            fig_weekly = go.Figure()
            fig_weekly.add_trace(go.Candlestick(
                x=weekly_data.index,
                open=weekly_data['Open'],
                high=weekly_data['High'],
                low=weekly_data['Low'],
                close=weekly_data['Close'],
                name="OHLC"
            ))
            fig_weekly.update_layout(
                title="Semanal",
                template="plotly_dark",
                height=450
            )
            st.plotly_chart(fig_weekly, use_container_width=True)
        else:
            st.warning(f"Sem dados semanais para {ticker}.")

    with col2:
        yearly_data = get_stock_data(ticker, period="10y", interval="1mo")
        if yearly_data is not None and not yearly_data.empty:
            fig_yearly = go.Figure()
            fig_yearly.add_trace(go.Candlestick(
                x=yearly_data.index,
                open=yearly_data['Open'],
                high=yearly_data['High'],
                low=yearly_data['Low'],
                close=yearly_data['Close'],
                name="OHLC"
            ))
            fig_yearly.update_layout(
                title="Anual",
                template="plotly_dark",
                height=450
            )
            st.plotly_chart(fig_yearly, use_container_width=True)
        else:
            st.warning(f"Sem dados anuais para {ticker}.")

    st.write("Dados fornecidos por Yahoo Finance via yfinance.")
