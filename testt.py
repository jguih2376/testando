import streamlit as st

# Título principal
st.title("Sobre")

# Seção: Visão Geral
st.markdown("""
### Visão Geral
O MarketView é uma plataforma inovadora para acompanhamento de mercados financeiros. 
Reúne, em um único ambiente, cotações de commodities, pares de moedas, índices de bolsas mundiais e dados fundamentalistas de ações brasileiras, 
oferecendo uma visão ampla e integrada do cenário econômico.
""")

# Seção: Nosso Propósito
st.markdown("""
# Nosso Propósito
Criamos o MarketView para tornar a análise financeira mais acessível e eficiente. 
Com gráficos interativos, tabelas dinâmicas e uma interface otimizada, ajudamos investidores e profissionais a tomarem decisões informadas com base em dados atualizados e de fácil visualização.
""")

# Seção: Nosso Compromisso
st.markdown("""
## Nosso Compromisso
Estamos sempre aprimorando o MarketView para oferecer a melhor experiência possível. 
Nossos próximos passos incluem otimizações de desempenho, ampliação da base de dados e novas funcionalidades, como alertas personalizados e integração com outras ferramentas financeiras.
""")

# Botão: Feedback
if st.button("Feedback"):
    st.markdown("Deixe seu [Feedback](https://forms.gle/M3abZwUMnBjBUi1q6)")

# Botão: Links de Apoio
if st.button("Links de Apoio"):
    st.markdown("### Links de Apoio")
    st.markdown("[Investing](https://br.investing.com/)")
    st.markdown("[InfoMoney](https://www.infomoney.com.br)")
    st.markdown("[Fundamentus](https://www.fundamentus.com.br/index.php)")
    st.markdown("[Yahoo Finance](https://finance.yahoo.com)")
    st.markdown("[TradingEconomics](https://tradingeconomics.com)")
    st.markdown("[TradingView](https://www.tradingview.com/)")
    st.markdown("[Tesouro Direto](https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm#0)")
