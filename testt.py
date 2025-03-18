import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Configuração do Streamlit
st.title("Painel de Cotações - Variação Diária")

# Definir intervalo de datas (último dia disponível)
end_date = datetime.now().date()
start_date = end_date - timedelta(days=2)  # Pegar 2 dias para calcular variação

# Dicionários de símbolos
commodities_symbols = {
    "Metais": {'Ouro': 'GC=F', 'Prata': 'SI=F', 'Platinum': 'PL=F', 'Cobre': 'HG=F'},
    "Energia": {'WTI Oil': 'CL=F', 'Brent Oil': 'BZ=F', 'Gasolina': 'RB=F', 'Gás Natural': 'NG=F'},
    "Agrícolas": {'Gado Vivo': 'LE=F', 'Porcos Magros': 'HE=F', 'Milho': 'ZC=F', 'Soja': 'ZS=F', 'Cacau': 'CC=F', 'Café': 'KC=F'}
}
indices_symbols = {
    'IBOV': '^BVSP', 'EWZ': 'EWZ', 'S&P500': '^GSPC', 'NASDAQ': '^IXIC', 'FTSE100': '^FTSE', 
    'DAX': '^GDAXI', 'CAC40': '^FCHI', 'SSE Composite': '000001.SS', 'Nikkei225': '^N225', 'Merval': '^MERV'
}

# Combinar todos os símbolos em um único dicionário
all_symbols = {}
for category, items in commodities_symbols.items():
    all_symbols.update(items)
all_symbols.update(indices_symbols)

# Buscar dados
data = {}
for name, symbol in all_symbols.items():
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date)
        if not hist.empty and len(hist) >= 2:
            # Calcular variação diária percentual
            last_close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            variation = ((last_close - prev_close) / prev_close) * 100
            data[name] = variation
        else:
            data[name] = None  # Dados insuficientes
    except Exception as e:
        st.warning(f"Erro ao buscar dados de {name}: {e}")
        data[name] = None

# Criar DataFrame com as variações
df = pd.DataFrame(list(data.items()), columns=['Ativo', 'Variação Diária (%)'])
df = df.dropna()  # Remover ativos sem dados

# Configurar estilo do Seaborn
sns.set(style="whitegrid")

# Criar gráfico de barras com Seaborn
plt.figure(figsize=(12, 6))
ax = sns.barplot(x='Ativo', y='Variação Diária (%)', data=df, palette='RdYlGn')
plt.xticks(rotation=90)
plt.title(f"Variação Diária - {end_date.strftime('%d/%m/%Y')}")
plt.xlabel("Ativo")
plt.ylabel("Variação Diária (%)")

# Adicionar rótulos nas barras
for p in ax.patches:
    ax.annotate(f'{p.get_height():.2f}%', 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='bottom' if p.get_height() >= 0 else 'top', 
                xytext=(0, 5), textcoords='offset points')

# Exibir o gráfico no Streamlit
st.pyplot(plt)

# Informações adicionais
st.write(f"Data atual: {datetime.now().strftime('%d/%m/%Y')}")
st.write(f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
st.write("Fonte: Yahoo Finance")