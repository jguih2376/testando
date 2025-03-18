import streamlit as st
import plotly.graph_objects as go
from bcb import sgs
from datetime import datetime
import pandas as pd

# Função para buscar os dados do Banco Central
def fetch_bcb_data(code, start_date=None, end_date=None):
    data = sgs.get({'IPCA': code}, start=start_date, end=end_date)
    return data

@st.cache_data
def get_data():
    start_date = '2010-01-01'  # Reduzindo o período
    dolar = sgs.get({'Dólar': 10813}, start=start_date)
    selic = sgs.get({'Selic': 432}, start=start_date)
    ipca = sgs.get({'IPCA': 13522}, start=start_date)
    
    dolar_atual = dolar.iloc[-1].values[0]
    selic_atual = selic.iloc[-1].values[0]
    ipca_atual = ipca.iloc[-1].values[0]
    juros_real = (((1 + selic_atual/100) / (1 + ipca_atual/100)) - 1) * 100
    
    return selic, selic_atual, ipca, ipca_atual, juros_real, dolar, dolar_atual

@st.cache_resource
def create_chart(data, atual, title, yaxis_title, unit):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data.iloc[:, 0], mode='lines'))
    fig.add_trace(go.Scatter(x=[data.index[-1]], y=[atual], mode='markers', marker=dict(color='red', size=5)))
    fig.update_layout(title=title, yaxis_title=yaxis_title, showlegend=False,                            yaxis=dict(
                                side="right",
                                gridcolor='rgba(255, 255, 255, 0.1)',  # Gridlines sutis
                                zeroline=False,
                                color='#FFFFFF'),
                                                            xaxis=dict(
                                
                                gridcolor='rgba(255, 255, 255, 0.1)',  # Gridlines sutis
                                zeroline=False,
                                color='#FFFFFF'
                            ),
                                height=450)
    fig.add_annotation(
                            x=1,  # Posição no extremo direito (relativo ao eixo X)
                            y=atual,  # Posição no valor do preço atual (eixo Y)
                            xref="paper",  # Referência relativa ao papel (0 a 1)
                            yref="y",  # Referência ao eixo Y em valores absolutos
                            text=f"{atual:.2f}",  # Texto com o preço atual formatado
                            showarrow=True,
                            arrowhead=0,
                            ax=5,  # Deslocamento horizontal da seta
                            ay=0,  # Sem deslocamento vertical
                            font=dict(size=12, color='#FFFFFF'),
                            bgcolor='rgba(0, 0, 0, 0.5)',  # Fundo semi-transparente para legibilidade
                            bordercolor='#FFFFFF',
                            borderwidth=1,
                            xanchor="left",  # Ancorar o texto à esquerda para não invadir o gráfico
                            yanchor="middle"  # Centralizar verticalmente no preço atual
                            )
   
    return fig


tab1, tab2 = st.tabs(['Historico','IPCA'])
with tab1:
    st.title("🏛️Estatística Monetária")
    with st.spinner("Carregando dados..."):
        selic, selic_atual, ipca, ipca_atual, juros_real, dolar, dolar_atual = get_data()
        
    col1, col2 = st.columns([5, 1])
    with col1:
        st.plotly_chart(create_chart(selic, selic_atual, 'Taxa de Juros SELIC', 'Taxa de Juros (%)', '%'))
        st.plotly_chart(create_chart(ipca, ipca_atual, 'IPCA Acumulado 12M', 'IPCA acumulado (%)', '%'))
        st.plotly_chart(create_chart(dolar, dolar_atual, 'Cotação do Dólar', 'Valor em R$', 'R$'))


    with col2:
        # Exibindo o iframe com alinhamento ajustado
        st.markdown("<br><br><br>", unsafe_allow_html=True)  # Spacing above the box
        combined_code = f"""
            <div style="
                background-color: #ffffff; 
                padding: 12px; 
                border-radius: 8px; 
                margin: 8px 0; 
                box-shadow: 2px 2px 4px rgba(0,0,0,0.1); 
                text-align: center; 
                font-family: sans-serif; 
                max-width: 150px; 
                margin-left: auto; 
                margin-right: auto;">
                <!-- Mundo Section -->
                <span style="font-size: 20px; font-weight: bold; display: block; margin-bottom: 8px; color: black;">Mundo</span>
                <div style="display: flex; justify-content: center; margin-bottom: 12px;">
                    <iframe frameborder="0" scrolling="no" height="146" width="108" allowtransparency="true" marginwidth="0" marginheight="0" 
                    src="https://sslirates.investing.com/index.php?rows=1&bg1=FFFFFF&bg2=F1F5F8&text_color=333333&enable_border=hide&border_color=0452A1&
                    header_bg=ffffff&header_text=FFFFFF&force_lang=12"></iframe>
                </div>
                <!-- Juros Real Section -->
                <span style="font-weight: bold; font-size: 14px; color: black; display: block; margin-bottom: 8px;">Juros Real 🇧🇷</span>
                <span style="font-size: 20px; color: black; font-weight: normal;">{juros_real:.2f}%</span>
            </div>
            """
        st.components.v1.html(combined_code, height=350)

with tab2:




# Função para buscar os dados do Banco Central



    # Configuração do título do app
    st.title("Indicadores Econômicos: IPCA, IGP-M e SELIC")

    # Definir intervalo de datas usando o formato padrão DD/MM/YYYY
    start_date = st.date_input('Data de início', pd.to_datetime('2020-01-01').date(), format='DD/MM/YYYY')
    end_date = st.date_input('Data de término', pd.to_datetime('today').date(), format='DD/MM/YYYY')

    # Converter datas para exibição em DD/MM/YYYY
    start_date_str = start_date.strftime('%d/%m/%Y')
    end_date_str = end_date.strftime('%d/%m/%Y')

    # Converter as datas para uso interno no formato YYYY-MM-DD (necessário para APIs e funções)
    start_date_bcb = start_date.strftime('%Y-%m-%d')
    end_date_bcb = end_date.strftime('%Y-%m-%d')

    # Dicionário com os códigos e nomes das séries
    series = {
        'IPCA Mensal (%)': 433,
        'IGP-M Mensal (%)': 189,
        'SELIC Acumulada no Mês (%)': 1178
    }

    # Busca e exibição dos dados
    for name, code in series.items():
        try:
            # Buscar os dados para cada série
            data = fetch_bcb_data(code, start_date_bcb, end_date_bcb, name.split(' ')[0])  # Nome curto para a API

            # Renomear a coluna para o nome completo
            data.columns = [name]

            # Atualizar o nome do índice para "Data"
            data.index.name = 'Data'

            # Ordenar a tabela pela ordem das datas (crescente)
            data = data.sort_index(ascending=True)

            # Formatando as datas no índice para DD/MM/YYYY
            data.index = data.index.strftime('%d/%m/%Y')

            # Exibir a tabela no Streamlit
            st.subheader(f"Tabela de Dados - {name}")
            st.dataframe(data)

            # Opcional: botão para download como CSV
            csv = data.to_csv(index=True)
            st.download_button(
                label=f"Baixar {name} como CSV",
                data=csv,
                file_name=f"{name.lower().replace(' ', '_')}.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Erro ao buscar os dados de {name}: {e}")

    # Informações adicionais com formato de datas atualizado
    st.write("Dados obtidos do Banco Central do Brasil (SGS):")
    st.write("- Código 433: IPCA mensal, em pontos percentuais.")
    st.write("- Código 189: IGP-M mensal, em pontos percentuais.")
    st.write("- Código 1178: SELIC acumulada no mês, em pontos percentuais.")
    st.write(f"Data atual: {datetime.now().strftime('%d/%m/%Y')}")
    st.write(f"Período selecionado: {start_date_str} a {end_date_str}")