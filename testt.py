import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import pytz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

# Configuração da página com tema escuro
st.set_page_config(page_title="Panorama de Mercado", layout="wide", initial_sidebar_state="collapsed")
# No CSS geral (substitua a seção correspondente no início do código):
st.markdown("""
    <style>
    .main-title {
        font-size: 36px;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }
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
    .card-container {
        display: flex;
        gap: 8px;
        padding: 8px;
        overflow-x: auto;
    }
    .card {
        background-color: #2E2E2E;
        border-radius: 8px;
        padding: 10px;
        width: 140px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        text-align: center;
        transition: transform 0.2s;
        flex: 0 0 auto;
        position: relative;
        margin-bottom: 15px;
    }
    .card:hover {
        transform: scale(1.03);
        background-color: #3E3E3E;
    }
    .card-title {
        font-size: 13px;  
        color: #FFFFFF;
        margin-bottom: 4px;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-value {
        font-size: 15px;  
        margin-top: 4px;
        color: #E0E0E0;
    }
    .card-variation {
        font-size: 12px;
        margin-top: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }
    .positive {
        color: #32CD32; /* Verde */
    }
    .negative {
        color: #FF4500; /* Vermelho */
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    body, .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# Título principal
st.markdown('<p class="main-title">Panorama de Mercado</p>', unsafe_allow_html=True)

# Atualização automática da página a cada 10 segundos
st_autorefresh(interval=10000, key="marketrefresh")

# Ajustar para o fuso horário UTC-3
br_tz = pytz.timezone('America/Sao_Paulo')
br_time = datetime.now(br_tz)
# Timestamp
st.markdown(f'<p class="timestamp">Última atualização: {br_time.strftime("%d/%m/%Y %H:%M:%S")}</p>', unsafe_allow_html=True)

# Funções de dados (com cache ajustado)
@st.cache_data(ttl=10)  # Moedas: 10 segundos
def get_currency_rates():
    try:
        pairs = ["USD-BRL", "EUR-USD", "USD-JPY", "USD-GBP", "USD-CAD", "USD-SEK", "USD-CHF"]
        url = "https://economia.awesomeapi.com.br/json/last/" + ",".join(pairs)
        response = requests.get(url)
        data = response.json()
        rates = {}
        for pair in pairs:
            pair_data = data[f"{pair.replace('-', '')}"]
            base, quote = pair.split("-")
            if pair == "USD-BRL":
                rates[f"{base}/{quote}"] = float(pair_data["bid"])
                rates[f"{base}/{quote}_pct"] = float(pair_data["pctChange"])
            elif base == "USD":
                rates[f"{quote}/{base}"] = 1 / float(pair_data["bid"])
                rates[f"{quote}/{base}_pct"] = -float(pair_data["pctChange"])
            else:
                rates[f"{base}/{quote}"] = float(pair_data["bid"])
                rates[f"{base}/{quote}_pct"] = float(pair_data["pctChange"])
        return pd.DataFrame([
            {"Par": k.split("_")[0], "Cotação": v, "Variação (%)": rates[f"{k}_pct"]}
            for k, v in rates.items() if not k.endswith("_pct")
        ])
    except Exception as e:
        st.error(f"Erro ao carregar moedas: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=1200)  # Commodities: 20 minutos
def get_commodities():
    symbols = {
        "Metais": {'Ouro': 'GC=F', 'Prata': 'SI=F', 'Platinum': 'PL=F', 'Cobre': 'HG=F'},
        "Energia": {'WTI Oil': 'CL=F', 'Brent Oil': 'BZ=F', 'Gasolina': 'RB=F', 'Gás Natural': 'NG=F'},
        "Agrícolas": {'Gado Vivo': 'LE=F', 'Porcos Magros': 'HE=F', 'Milho': 'ZC=F', 'Soja': 'ZS=F', 'Cacau': 'CC=F', 'Café': 'KC=F'}
    }
    data = {}
    for category, items in symbols.items():
        for name, symbol in items.items():
            try:
                commodity = yf.Ticker(symbol)
                hist = commodity.history(period="2d")
                if len(hist) >= 2:
                    current_price = hist["Close"].iloc[-1]
                    prev_price = hist["Close"].iloc[-2]
                    variation = ((current_price - prev_price) / prev_price) * 100
                    data[f"{name} ({category})"] = {"Preço": round(current_price, 2), "Variação (%)": round(variation, 2)}
                else:
                    data[f"{name} ({category})"] = {"Preço": "N/A", "Variação (%)": "N/A"}
            except Exception as e:
                data[f"{name} ({category})"] = {"Preço": "N/A", "Variação (%)": "N/A"}
    return pd.DataFrame([(k, v["Preço"], v["Variação (%)"]) for k, v in data.items()],
                        columns=["Commodity", "Preço", "Variação (%)"])

@st.cache_data(ttl=1200)  # Índices: 20 minutos
def get_stocks():
    symbols = {'IBOV': '^BVSP', 'EWZ': 'EWZ', 'S&P500': '^GSPC', 'NASDAQ': '^IXIC', 'FTSE100': '^FTSE', 
               'DAX': '^GDAXI', 'CAC40': '^FCHI', 'SSE Composite': '000001.SS', 'Nikkei225': '^N225', 'Merval': '^MERV'}
    data = {}
    for name, symbol in symbols.items():
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                current_price = hist["Close"].iloc[-1]
                prev_price = hist["Close"].iloc[-2]
                variation = ((current_price - prev_price) / prev_price) * 100
                data[name] = {"Preço": round(current_price, 2), "Variação (%)": round(variation, 2)}
            else:
                data[name] = {"Preço": "N/A", "Variação (%)": "N/A"}
        except Exception as e:
            data[name] = {"Preço": "N/A", "Variação (%)": "N/A"}
    return pd.DataFrame([(k, v["Preço"], v["Variação (%)"]) for k, v in data.items()],
                        columns=["Índice", "Preço", "Variação (%)"])

@st.cache_data(ttl=1200)  # Ações do IBOV: 20 minutos
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
    data = yf.download(tickers, period="1d", interval="1d")["Close"]
    open_data = yf.download(tickers, period="1d", interval="1d")["Open"]
    
    if data.empty or open_data.empty:
        raise ValueError("Dados insuficientes para calcular a variação do dia.")
    
    variacao = ((data.iloc[-1] - open_data.iloc[-1]) / open_data.iloc[-1]) * 100
    return pd.DataFrame({
        "Ação": [ticker[:-3] for ticker in tickers], 
        "Variação (%)": variacao.values,
        "Último Preço": data.iloc[-1].values
    })

@st.cache_data(ttl=1200)  # Dados do IBOV: 20 minutos
def get_stock_data(ticker, period, interval):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    return data

# Layout principal
col1,s, col2 = st.columns([47,1,30])

with col1:
    with st.expander('...', expanded=True):    
        # Moedas
        st.markdown('<p class="subheader">💱 Moedas</p>', unsafe_allow_html=True)
        currency_data = get_currency_rates()
        if not currency_data.empty:
            cols = st.columns(min(4, len(currency_data)))
            for idx, (index, row) in enumerate(currency_data.iterrows()):
                with cols[idx % len(cols)]:
                    var_class = "positive" if float(row["Variação (%)"]) >= 0 else "negative"
                    arrow = "↑" if float(row["Variação (%)"]) >= 0 else "↓"
                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="tooltip">
                                <div class="card-title">{row['Par']}</div>
                                <span class="tooltiptext">Cotação em {row['Par'].split('/')[1]}</span>
                            </div>
                            <div class="card-value">{row['Cotação']:.4f}</div>
                            <div class="card-variation {var_class}">{row['Variação (%)']:.2f}% {arrow}</div>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)

        # Índices
        st.markdown('<p class="subheader">📈 Índices</p>', unsafe_allow_html=True)
        stocks_data = get_stocks()
        if not stocks_data.empty:
            cols = st.columns(min(4, len(stocks_data)))
            for idx, (index, row) in enumerate(stocks_data.iterrows()):
                with cols[idx % len(cols)]:
                    var_class = "positive" if float(str(row["Variação (%)"]).replace("N/A", "0")) >= 0 else "negative"
                    arrow = "↑" if float(str(row["Variação (%)"]).replace("N/A", "0")) >= 0 else "↓"
                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="tooltip">
                                <div class="card-title">{row['Índice']}</div>
                                <span class="tooltiptext">Índice de Mercado</span>
                            </div>
                            <div class="card-value">{row['Preço']}</div>
                            <div class="card-variation {var_class}">{row['Variação (%)']}% {arrow}</div>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)

        # Commodities
        st.markdown('<p class="subheader">⛽ Commodities</p>', unsafe_allow_html=True)
        commodities_data = get_commodities()
        if not commodities_data.empty:
            cols = st.columns(min(4, len(commodities_data) // 2 + 1))
            for idx, (index, row) in enumerate(commodities_data.iterrows()):
                with cols[idx % len(cols)]:
                    var_class = "positive" if float(str(row["Variação (%)"]).replace("N/A", "0")) >= 0 else "negative"
                    arrow = "↑" if float(str(row["Variação (%)"]).replace("N/A", "0")) >= 0 else "↓"
                    category = row['Commodity'].split('(')[-1].replace(')', '')
                    tooltip_text = f"Preço em USD ({category})"
                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="tooltip">
                                <div class="card-title">{row['Commodity'].split(' (')[0]}</div>
                                <span class="tooltiptext">{tooltip_text}</span>
                            </div>
                            <div class="card-value">{row['Preço']}</div>
                            <div class="card-variation {var_class}">{row['Variação (%)']}% {arrow}</div>
                        </div>
                        """, unsafe_allow_html=True)

    # Dentro do bloco `with col2:` (substitua apenas essa parte no código completo)



with col2:
    with st.expander('...', expanded=True):
        st.markdown('<p class="subheader">IBOV</p>', unsafe_allow_html=True)

        try:
            # Dados intraday (5 minutos)
            intraday_data = get_stock_data('^BVSP', period="1d", interval="5m")
            # Dados do dia anterior para fechamento e diário
            previous_day_data = get_stock_data('^BVSP', period="2d", interval="1d")
            # Dados semanal (5 dias úteis)
            weekly_data = get_stock_data('^BVSP', period="5d", interval="1d")
            # Dados mensal (1 mês)
            monthly_data = get_stock_data('^BVSP', period="1mo", interval="1d")
            
            if not intraday_data.empty and not previous_day_data.empty and not weekly_data.empty and not monthly_data.empty:
                # Preço atual (último fechamento intraday)
                preco_atual = intraday_data['Close'].iloc[-1]
                # Abertura de hoje (primeiro valor do dia)
                abertura_hoje = intraday_data['Open'].iloc[0]
                # Fechamento do dia anterior
                fechamento_anterior = previous_day_data['Close'].iloc[-2]   

                # Variações
                variacao_dia = ((preco_atual - abertura_hoje) / abertura_hoje) * 100
                fechamento_semana_passada = weekly_data['Close'].iloc[0]
                variacao_semanal = ((preco_atual - fechamento_semana_passada) / fechamento_semana_passada) * 100
                fechamento_mes_passado = monthly_data['Close'].iloc[0]
                variacao_mensal = ((preco_atual - fechamento_mes_passado) / fechamento_mes_passado) * 100

                # Cartão HTML único para Fechamento Anterior e Preço Atual com número no final
                st.markdown(
                    f"""
                    <div style="
                        background-color: #ffffff; 
                        padding: 12px; 
                        border-radius: 8px; 
                        margin: 8px 0; 
                        box-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
                        <div style="
                            display: flex; 
                            justify-content: space-between; 
                            align-items: center; 
                            margin-bottom: 8px;">
                            <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">Fechamento Anterior</span>
                            <span style="font-size: 12px; color: black; font-weight: bold; flex: 1; text-align: right;">{fechamento_anterior:.2f}</span>
                        </div>
                        <div style="
                            display: flex; 
                            justify-content: space-between; 
                            align-items: center;">
                            <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">Preço Atual</span>
                            <span style="font-size: 12px; color: black; font-weight: bold; flex: 1; text-align: right;">{preco_atual:.2f}</span>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

                # Todas as variações em um único cartão (mantido como estava)
                st.markdown(
                    f"""
                    <div style="
                        background-color: #ffffff; 
                        padding: 12px; 
                        border-radius: 8px; 
                        margin: 8px 0; 
                        box-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
                        <div style="
                            display: flex; 
                            justify-content: space-between; 
                            align-items: center; 
                            margin-bottom: 8px;">
                            <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">Var. do Dia</span>
                            <span style="font-size: 12px; color: black; flex: 1; text-align: center;"></span>
                            <span style="font-size: 14px; color: {'#155724' if variacao_dia >= 0 else '#721c24'}; font-weight: bold; flex: 1; text-align: right;">{'↑' if variacao_dia >= 0 else '↓'} {abs(variacao_dia):.2f}%</span>
                        </div>
                        <div style="
                            display: flex; 
                            justify-content: space-between; 
                            align-items: center; 
                            margin-bottom: 8px;">
                            <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">Var. Semanal</span>
                            <span style="font-size: 12px; color: black; flex: 1; text-align: center;"></span>
                            <span style="font-size: 14px; color: {'#155724' if variacao_semanal >= 0 else '#721c24'}; font-weight: bold; flex: 1; text-align: right;">{'↑' if variacao_semanal >= 0 else '↓'} {abs(variacao_semanal):.2f}%</span>
                        </div>
                        <div style="
                            display: flex; 
                            justify-content: space-between; 
                            align-items: center;">
                            <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">Var. Mensal</span>
                            <span style="font-size: 12px; color: black; flex: 1; text-align: center;"></span>
                            <span style="font-size: 14px; color: {'#155724' if variacao_mensal >= 0 else '#721c24'}; font-weight: bold; flex: 1; text-align: right;">{'↑' if variacao_mensal >= 0 else '↓'} {abs(variacao_mensal):.2f}%</span>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                # Definindo a cor da linha do gráfico com base na variação do dia
                cor_linha = '#32CD32' if variacao_dia >= 0 else '#FF4500'  # Verde mais claro e vermelho mais vibrante

                # Gráfico de linha (intraday) com melhorias
                fig_intraday = go.Figure()
                fig_intraday.add_trace(go.Scatter(
                    x=intraday_data.index,
                    y=intraday_data['Close'],
                    mode='lines',
                    name="IBOV Intraday",
                    line=dict(color=cor_linha, width=1.5),  # Linha um pouco mais grossa
                    hovertemplate='%{x|%H:%M}<br>Fechamento: %{y:.2f}<extra></extra>'  # Tooltip personalizado
                ))
                fig_intraday.update_layout(
                    title={
                        'text': "IBOV - Variação Intraday",
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': dict(size=16, color='#FFFFFF')
                    },
                    xaxis=dict(
                        tickformat="%H:%M",  # Formato de hora
                        gridcolor='rgba(255, 255, 255, 0.1)',  # Gridlines sutis
                        zeroline=False,
                        color='#FFFFFF'
                    ),
                    yaxis=dict(
                        side="right",
                        gridcolor='rgba(255, 255, 255, 0.1)',  # Gridlines sutis
                        zeroline=False,
                        color='#FFFFFF'
                    ),
                    template="plotly_dark",
                    height=350,
                    margin=dict(l=40, r=40, t=60, b=40),  # Margens ajustadas
                    plot_bgcolor='#1E1E1E',  # Fundo do gráfico alinhado ao tema
                    paper_bgcolor='#1E1E1E',  # Fundo externo alinhado ao tema
                    font=dict(color='#FFFFFF'),  # Cor da fonte geral
                    showlegend=False,
                    legend=dict(
                        x=0.01,
                        y=0.99,
                        bgcolor='rgba(0, 0, 0, 0.5)',
                        font=dict(color='#FFFFFF')
                    )
                )
                st.plotly_chart(fig_intraday, use_container_width=True)
                # Cartão HTML único para Fechamento Anterior e Preço Atual com número no final
                st.markdown(
                    f"""
                    <div style="
                        background-color: #ffffff; 
                        padding: 12px; 
                        border-radius: 8px; 
                        margin: 8px 0; 
                        box-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
                        <div style="
                            display: flex; 
                            justify-content: space-between; 
                            align-items: center; 
                            margin-bottom: 8px;">
                            <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">Fechamento Anterior</span>
                            <span style="font-size: 12px; color: black; font-weight: bold; flex: 1; text-align: right;">{fechamento_anterior:.2f}</span>
                        </div>
                        <div style="
                            display: flex; 
                            justify-content: space-between; 
                            align-items: center;">
                            <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">Preço Atual</span>
                            <span style="font-size: 12px; color: black; font-weight: bold; flex: 1; text-align: right;">{preco_atual:.2f}</span>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.warning("Nenhum dado disponível para o IBOV.")
        except Exception as e:
            st.error(f"Erro ao carregar dados intraday: {e}")



        # Dados das ações
        try:
            df = get_ibov_data().dropna()
            maiores_altas = df.nlargest(5, "Variação (%)")
            maiores_baixas = df.nsmallest(5, "Variação (%)")

            # Layout em colunas para ações
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                """
                <h3 style="text-align: center; font-size: 16px;">↑ Maiores Altas ↑</h3>
                """, 
                unsafe_allow_html=True
            )
                for _, row in maiores_altas.iterrows():
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #d4edda; 
                            padding: 12px; 
                            border-radius: 8px; 
                            margin: 8px 0; 
                            box-shadow: 2px 2px 4px rgba(0,0,0,0.1); 
                            display: flex; 
                            justify-content: space-between; 
                            align-items: center;">
                            <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">{row['Ação']}</span>
                            <span style="font-size: 12px; color: black; flex: 1; text-align: center;">R$ {row['Último Preço']:.2f}</span>
                            <span style="font-size: 14px; color: #155724; font-weight: bold; flex: 1; text-align: right;">{row['Variação (%)']:.2f}%</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

            with col2:
                st.markdown(
                    """
                    <h3 style="text-align: center; font-size: 16px;">↓ Maiores Baixas ↓</h3>
                    """, 
                    unsafe_allow_html=True
                )
                for _, row in maiores_baixas.iterrows():
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #f8d7da; 
                            padding: 12px; 
                            border-radius: 8px; 
                            margin: 8px 0; 
                            box-shadow: 2px 2px 4px rgba(0,0,0,0.1); 
                            display: flex; 
                            justify-content: space-between; 
                            align-items: center;">
                            <span style="font-weight: bold; font-size: 14px; color: black; flex: 1; text-align: left;">{row['Ação']}</span>
                            <span style="font-size: 12px; color: black; flex: 1; text-align: center;">R$ {row['Último Preço']:.2f}</span>
                            <span style="font-size: 14px; color: #721c24; font-weight: bold; flex: 1; text-align: right;">{row['Variação (%)']:.2f}%</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

        except Exception as e:
            st.error(f"Erro ao carregar os dados das ações: {e}")





# Rodapé
st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; font-size: 12px; color: #A9A9A9; margin-top: 20px;">
    <strong>Fonte:</strong> Moedas: AwesomeAPI | Commodities, Índices e Ações: Yahoo Finance<br>
    <strong>Nota:</strong> Moedas atualizadas a cada 10 segundos; demais cotações a cada 20 minutos.
</div>
""", unsafe_allow_html=True)
