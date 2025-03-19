import streamlit as st
import pandas as pd
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pdfkit  # Para converter HTML em PDF
import os

def app():
    st.title('📉 Análise Histórica')
    tab1, tab2 = st.tabs(["Heatmap", "Desempenho"])  

    with tab1:  
        st.subheader('Retorno Mensal')
        with st.expander('...', expanded=True):
            opcao = st.radio('Selecione:', ['Índices', 'Ações', 'Commodities'])
            with st.form(key='form_ativo'):
                # [Código existente para seleção de índices, ações e commodities permanece igual]
                # ... (omitido por brevidade)

                if analisar:
                    data_inicial = '1999-12-01'
                    data_final = '2030-12-31'
                    dados = yf.download(ticker, start=data_inicial, end=data_final, interval="1mo")

                    if not dados.empty:
                        # [Código existente para heatmap e estatísticas permanece igual]
                        # ... (omitido por brevidade)

                        # Botão para salvar em PDF
                        if st.button("Salvar Heatmap em PDF"):
                            # Salvar heatmap como imagem temporária
                            fig.savefig("heatmap_temp.png")
                            # Converter para PDF
                            pdfkit.from_file("heatmap_temp.html", "heatmap_output.pdf")
                            st.success("Heatmap salvo como 'heatmap_output.pdf'!")
                            # Remover arquivo temporário
                            os.remove("heatmap_temp.png")

    with tab2:
        st.subheader("Desempenho Relativo dos Ativos")
        
        @st.cache_data(ttl=600)  
        def carregar_dados(tickers, data_inicio, data_fim):
            # [Código existente permanece igual]
            # ... (omitido por brevidade)

        # [Funções calcular_performance, calcular_valorizacao, criar_grafico permanecem iguais]
        # ... (omitido por brevidade)

        with st.expander('...', expanded=True):
            # [Código existente para seleção de ativos permanece igual]
            # ... (omitido por brevidade)

            if submit_button and ticker:
                dados = carregar_dados(ticker, data_inicio, data_fim)
                if not dados.empty:
                    fig = criar_grafico(ticker, dados, normalizado, legenda_dict)
                    st.plotly_chart(fig)
                    df_valorizacao = calcular_valorizacao(dados, legenda_dict)
                    df_valorizacao = df_valorizacao.sort_values(by='Período (%)', ascending=False)
                    
                    # Botão para salvar gráfico em PDF
                    if st.button("Salvar Gráfico em PDF"):
                        # Salvar gráfico Plotly como HTML temporário
                        fig.write_html("graph_temp.html")
                        # Converter para PDF
                        pdfkit.from_file("graph_temp.html", "graph_output.pdf")
                        st.success("Gráfico salvo como 'graph_output.pdf'!")
                        # Remover arquivo temporário
                        os.remove("graph_temp.html")

                    st.dataframe(df_valorizacao)

    # [Rodapé permanece igual]
    # ... (omitido por brevidade)

if __name__ == "__main__":
    app()