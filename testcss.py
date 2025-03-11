import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuração básica do Streamlit
st.title("Sistema de Cotação de Ações")

# Entrada do usuário para o ticker da ação
ticker = st.text_input("Digite o código da ação (ex: AAPL, MSFT, PETR4.SA):", value="AAPL")

# Definição das opções de intervalo
interval_options = {"5min": "5m", "15min": "15m", "30min": "30m", "1h": "1h"}

# Função para obter dados da ação
def get_stock_data(ticker, period, interval):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    return data

# Gráfico Intraday
st.subheader(f"Gráfico Intraday")
col1, col2 = st.columns([6, 1])  # Define as colunas: 6 partes para o gráfico, 1 parte para os controles

with col1:
    try:
        # O intervalo será definido fora do bloco try para ser acessível
        interval_label = st.session_state.get("interval_label", "5min")  # Default inicial
        interval = interval_options[interval_label]
        intraday_data = get_stock_data(ticker, period="1d", interval=interval)
        if not intraday_data.empty:
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
                title=f"Intraday ({interval_label})",
                yaxis_title="Preço",
                yaxis_side="right",
                xaxis_title="Horário",
                template="plotly_dark",
                height=700,
            )
            st.plotly_chart(fig_intraday, use_container_width=True)
        else:
            st.warning("Nenhum dado intraday disponível para este ticker.")
    except Exception as e:
        st.error(f"Erro ao carregar dados intraday: {e}")

with col2:
    st.write(" ")
    st.write(" ")

    interval_label = st.radio(
        "",
        list(interval_options.keys()),
        key="interval_label"  # Usamos uma chave para manter o estado
    )


# Divisão em duas colunas para os gráficos semanal e anual
col1, col2 = st.columns(2)

# Gráfico Semanal
with col1:
    try:
        weekly_data = get_stock_data(ticker, period="1y", interval="1wk")
        if not weekly_data.empty:
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
                title_x=0.4,  
                yaxis_side="right",  
                template="plotly_dark",
                height=450,
                xaxis=dict(
                    rangeslider=dict(
                        visible=True,  
                        thickness=0.03  
                    ),
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
            fig_yearly.add_trace(go.Candlestick(
                x=yearly_data.index,
                open=yearly_data['Open'],
                high=yearly_data['High'],
                low=yearly_data['Low'],
                close=yearly_data['Close'],
                name="OHLC"
            ))

            # Define o range inicial para os últimos 5 anos
            last_5_years = yearly_data.index[-60:]  # 5 anos * 12 meses = 60 pontos

            fig_yearly.update_layout(
                title="Mensal",
                title_x=0.4,                
                yaxis_side="right",               
                template="plotly_dark",
                height=450,
                xaxis=dict(
                    range=[last_5_years[0], last_5_years[-1]],  # Aplica o zoom inicial de 5 anos
                    rangeslider=dict(
                        visible=True,  
                        thickness=0.03  
                    ),
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


# Rodapé
st.write("Dados fornecidos por Yahoo Finance via yfinance.")