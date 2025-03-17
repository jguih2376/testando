import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import pytz
from datetime import datetime, timedelta
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
def load_css():
    st.markdown("""
        <style>
        .subheader {
            color: #FFFFFF;
            font-size: 22px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .timestamp {
            color: #A9A9A9;
            font-size: 14px;
            text-align: right;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_card(title, value, variation, value_format="{:.2f}", flex_ratios=[1, 1, 1]):
    try:
        variation_float = float(variation)
    except (ValueError, TypeError):
        variation_float = 0.0
    bg_color = "#d4edda" if variation_float >= 0 else "#f8d7da"
    arrow = "↑" if variation_float >= 0 else "↓"
    var_color = "#155724" if variation_float >= 0 else "#721c24"
    try:
        value_display = value_format.format(value)
    except (ValueError, TypeError):
        value_display = str(value)
    st.markdown(
        f"""
        <div style="
            background-color: {bg_color}; 
            padding: 12px; 
            border-radius: 8px; 
            margin: 8px 0; 
            box-shadow: 2px 2px 4px rgba(0,0,0,0.1); 
            display: flex; 
            justify-content: space-between; 
            align-items: center;">
            <span style="font-weight: bold; font-size: 14px; color: black; flex: {flex_ratios[0]}; text-align: left;">{title}</span>
            <span style="font-size: 12px; color: black; flex: {flex_ratios[1]}; text-align: center;">{value_display}</span>
            <span style="font-size: 14px; color: {var_color}; font-weight: bold; flex: {flex_ratios[2]}; text-align: right;">{arrow} {abs(variation_float):.2f}%</span>
        </div>
        """, unsafe_allow_html=True
    )

def display_cards(data, title, emoji, cols_num=3, value_col="Cotação", var_col="Variação (%)", title_col="Par", value_format="{:.2f}"):
    st.markdown(f'<p class="subheader">{emoji} {title}</p>', unsafe_allow_html=True)
    if not data.empty:
        cols = st.columns(min(cols_num, len(data)))
        for idx, row in data.iterrows():
            with cols[idx % len(cols)]:
                render_card(row[title_col], row[value_col], row[var_col], value_format)

@st.cache_data(ttl=60)
def get_currency_rates():
    pairs = ["USD-BRL", "EUR-USD", "USD-JPY", "USD-GBP", "USD-CAD", "USD-SEK", "USD-CHF"]
    url = "https://economia.awesomeapi.com.br/json/last/" + ",".join(pairs)
    try:
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame([
            {"Par": pair, "Cotação": float(data[pair.replace('-', '')]["bid"]), 
             "Variação (%)": float(data[pair.replace('-', '')]["pctChange"])}
            for pair in pairs
        ])
    except Exception as e:
        st.error(f"Erro ao carregar moedas: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=1200)
def get_commodities():
    symbols = {
        "Metais": {'Ouro': 'GC=F', 'Prata': 'SI=F', 'Platinum': 'PL=F', 'Cobre': 'HG=F'},
        "Energia": {'WTI Oil': 'CL=F', 'Brent Oil': 'BZ=F', 'Gasolina': 'RB=F', 'Gás Natural': 'NG=F'},
        "Agrícolas": {'Gado Vivo': 'LE=F', 'Porcos Magros': 'HE=F', 'Milho': 'ZC=F', 'Soja': 'ZS=F', 'Cacau': 'CC=F', 'Café': 'KC=F'}
    }
    data = {}
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    for category, items in symbols.items():
        for name, symbol in items.items():
            try:
                hist = yf.download(symbol, start=start_date, end=end_date, interval="1d")["Close"]
                if len(hist) >= 2:
                    current_price = hist.iloc[-1]
                    prev_price = hist.iloc[-2]
                    variation = ((current_price - prev_price) / prev_price) * 100
                    data[f"{name} ({category})"] = {"Preço": round(current_price, 2), "Variação (%)": round(variation, 2)}
                else:
                    data[f"{name} ({category})"] = {"Preço": 0.0, "Variação (%)": 0.0}
            except Exception:
                data[f"{name} ({category})"] = {"Preço": 0.0, "Variação (%)": 0.0}
    return pd.DataFrame([(k, v["Preço"], v["Variação (%)"]) for k, v in data.items()],
                       columns=["Commodity", "Preço", "Variação (%)"])

@st.cache_data(ttl=1200)
def get_stocks():
    symbols = {'IBOV': '^BVSP', 'EWZ': 'EWZ', 'S&P500': '^GSPC', 'NASDAQ': '^IXIC', 'FTSE100': '^FTSE', 
               'DAX': '^GDAXI', 'CAC40': '^FCHI', 'SSE Composite': '000001.SS', 'Nikkei225': '^N225', 'Merval': '^MERV'}
    data = {}
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    for name, symbol in symbols.items():
        try:
            hist = yf.download(symbol, start=start_date, end=end_date, interval="1d")["Close"]
            if len(hist) >= 2:
                current_price = hist.iloc[-1]
                prev_price = hist.iloc[-2]
                variation = ((current_price - prev_price) / prev_price) * 100
                data[name] = {"Preço": round(current_price, 2), "Variação (%)": round(variation, 2)}
            else:
                data[name] = {"Preço": 0.0, "Variação (%)": 0.0}
        except Exception:
            data[name] = {"Preço": 0.0, "Variação (%)": 0.0}
    return pd.DataFrame([(k, v["Preço"], v["Variação (%)"]) for k, v in data.items()],
                       columns=["Índice", "Preço", "Variação (%)"])

@st.cache_data(ttl=1200)
def get_ibov_data():
    acoes = ['ALOS3', 'ABEV3', 'ASAI3', 'AURE3', 'AZUL4', 'AZZA3', 'B3SA3', 'BBSE3', 'BBDC3', 'BBDC4', 
             'BRAP4', 'BBAS3', 'BRKM5', 'BRAV3', 'BRFS3', 'BPAC11', 'CXSE3', 'CRFB3', 'CCRO3', 'CMIG4', 
             'COGN3', 'CPLE6', 'CSAN3', 'CPFE3', 'CMIN3', 'CVCB3', 'CYRE3', 'ELET3', 'ELET6', 'EMBR3', 
             'ENGI11', 'ENEV3', 'EGIE3', 'EQTL3', 'FLRY3', 'GGBR4', 'GOAU4', 'NTCO3', 'HAPV3', 'HYPE3', 
             'IGTI11', 'IRBR3', 'ISAE4', 'ITSA4', 'ITUB4', 'JBSS3', 'KLBN11', 'RENT3', 'LREN3', 'LWSA3', 
             'MGLU3', 'POMO4', 'MRFG3', 'BEEF3', 'MRVE3', 'MULT3', 'PCAR3', 'PETR3', 'PETR4', 'RECV3', 
             'PRIO3', 'PETZ3', 'PSSA3', 'RADL3', 'RAIZ4', 'RDOR3', 'RAIL3', 'SBSP3', 'SANB11', 'STBP3', 
             'SMTO3', 'CSNA3', 'SLCE3', 'SUZB3', 'TAEE11', 'VIVT3', 'TIMS3', 'TOTS3', 'UGPA3', 'USIM5', 
             'VALE3', 'VAMO3', 'VBBR3', 'VIVA3', 'WEGE3', 'YDUQ3']
    tickers = [acao + '.SA' for acao in acoes]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    try:
        data = yf.download(tickers, start=start_date, end=end_date, interval="1d")["Close"]
        if data.shape[0] < 2:
            raise ValueError("Dados insuficientes.")
        variacao = ((data.iloc[-1] - data.iloc[-2]) / data.iloc[-2]) * 100
        return pd.DataFrame({
            "Ação": [col[:-3] for col in data.columns],
            "Variação (%)": variacao.values,
            "Último Preço": data.iloc[-1].values
        }).dropna()
    except Exception as e:
        st.error(f"Erro ao carregar ações: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=1200)
def get_stock_data(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    return yf.download(ticker, start=start_date, end=end_date, interval="1m")

def app():
    st.title("🌎 Panorama do Mercado")
    st.write("Visão geral do mercado atual.")
    tab1, tab2, tab3 = st.tabs(['Panorama', 'TradingView', 'Triple Screen'])

    with tab1:
        load_css()
        st_autorefresh(interval=10000, key="marketrefresh")
        br_tz = pytz.timezone('America/Sao_Paulo')
        br_time = datetime.now(br_tz)

        col1, s, col2 = st.columns([47, 1, 30])

        with col1:
            with st.expander('...', expanded=True):
                display_cards(get_currency_rates(), "Moedas", "💱", value_format="{:.4f}")
                st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
                display_cards(get_stocks(), "Índices", "📈", value_col="Preço", title_col="Índice")
                st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
                display_cards(get_commodities(), "Commodities", "⛽", value_col="Preço", title_col="Commodity")
                st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)

        with col2:
            with st.expander('...', expanded=True):
                try:
                    data = get_stock_data('^BVSP')
                    intraday_data = data.tail(390)
                    daily_data = data.resample('1d').last().tail(2)
                    weekly_data = data.resample('1d').last().tail(5)
                    monthly_data = data.resample('1d').last()

                    preco_atual = intraday_data['Close'].iloc[-1]
                    abertura_hoje = intraday_data['Open'].iloc[0]
                    fechamento_anterior = daily_data['Close'].iloc[-2]
                    variacao_dia = ((preco_atual - abertura_hoje) / abertura_hoje) * 100
                    variacao_semanal = ((preco_atual - weekly_data['Close'].iloc[0]) / weekly_data['Close'].iloc[0]) * 100
                    variacao_mensal = ((preco_atual - monthly_data['Close'].iloc[0]) / monthly_data['Close'].iloc[0]) * 100

                    cor_linha = '#32CD32' if variacao_dia >= 0 else '#FF4500'
                    fig_intraday = go.Figure()
                    fig_intraday.add_trace(go.Scatter(
                        x=intraday_data.index, y=intraday_data['Close'],
                        mode='lines', name="IBOV Intraday", line=dict(color=cor_linha, width=1.5),
                        hovertemplate='%{x|%H:%M}<br>Fechamento: %{y:.2f}<extra></extra>'
                    ))
                    fig_intraday.add_annotation(
                        x=1, y=preco_atual, xref="paper", yref="y",
                        text=f"{preco_atual:.2f}", showarrow=True, arrowhead=0, ax=7, ay=0,
                        font=dict(size=12, color='#FFFFFF'), bgcolor='rgba(0, 0, 0, 0.5)',
                        bordercolor='#FFFFFF', borderwidth=1, xanchor="left", yanchor="middle"
                    )
                    fig_intraday.update_layout(
                        title={'text': "IBOV - Intraday", 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        xaxis=dict(tickformat="%H:%M", gridcolor='rgba(255, 255, 255, 0.1)', zeroline=False, color='#FFFFFF'),
                        yaxis=dict(side="right", gridcolor='rgba(255, 255, 255, 0.1)', zeroline=False, color='#FFFFFF'),
                        template="plotly_dark", height=350, margin=dict(l=40, r=40, t=60, b=40),
                        plot_bgcolor='#1E1E1E', paper_bgcolor='#1E1E1E', font=dict(color='#FFFFFF'), showlegend=False
                    )
                    st.plotly_chart(fig_intraday, use_container_width=True)

                    st.markdown(
                        f"""
                        <div style="background-color: #ffffff; padding: 12px; border-radius: 8px; margin: 8px 0; box-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">Var. do Dia</span>
                                <span style="font-size: 14px; color: {'#155724' if variacao_dia >= 0 else '#721c24'}; font-weight: bold; flex: 1; text-align: right;">{'↑' if variacao_dia >= 0 else '↓'} {abs(variacao_dia):.2f}%</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">Var. Semanal</span>
                                <span style="font-size: 14px; color: {'#155724' if variacao_semanal >= 0 else '#721c24'}; font-weight: bold; flex: 1; text-align: right;">{'↑' if variacao_semanal >= 0 else '↓'} {abs(variacao_semanal):.2f}%</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">Var. Mensal</span>
                                <span style="font-size: 14px; color: {'#155724' if variacao_mensal >= 0 else '#721c24'}; font-weight: bold; flex: 1; text-align: right;">{'↑' if variacao_mensal >= 0 else '↓'} {abs(variacao_mensal):.2f}%</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True
                    )

                    df = get_ibov_data()
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown('<h3 style="text-align: center; font-size: 16px;">↑ Maiores Altas ↑</h3>', unsafe_allow_html=True)
                        for _, row in df.nlargest(5, "Variação (%)").iterrows():
                            render_card(row["Ação"], row["Último Preço"], row["Variação (%)"], "{:.2f}")
                    with col_b:
                        st.markdown('<h3 style="text-align: center; font-size: 16px;">↓ Maiores Baixas ↓</h3>', unsafe_allow_html=True)
                        for _, row in df.nsmallest(5, "Variação (%)").iterrows():
                            render_card(row["Ação"], row["Último Preço"], row["Variação (%)"], "{:.2f}")
                except Exception as e:
                    st.error(f"Erro ao carregar dados: {e}")

            st.markdown(f'<p class="timestamp">Última atualização: {br_time.strftime("%d/%m/%Y %H:%M:%S")}</p>', unsafe_allow_html=True)

        st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; font-size: 12px; color: #A9A9A9; margin-top: 20px;">
            <strong>Fonte:</strong> Moedas: AwesomeAPI | Commodities, Índices e Ações: Yahoo Finance<br>
            <strong>Nota:</strong> Moedas atualizadas a cada 60 segundos; demais cotações a cada 20 minutos.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app()