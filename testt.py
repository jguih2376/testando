import streamlit as st
import plotly.graph_objects as go
from bcb import sgs
from datetime import datetime
import pandas as pd


@st.cache_data
def get_data():
start_date = '2000-01-01' 
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
fig.update_layout(title=title, yaxis_title=yaxis_title, showlegend=False,                           
                            yaxis=dict(
                            side="right",
                            gridcolor='rgba(255, 255, 255, 0.1)',  
                            zeroline=False,
                            color='#FFFFFF'),

                            xaxis=dict(                                
                            gridcolor='rgba(255, 255, 255, 0.1)',  
                            zeroline=False,
                            color='#FFFFFF'
                        ),
                            height=450)
fig.add_annotation(
                        x=1,  
                        y=atual,  
                        xref="paper", 
                        yref="y",
                        text=f"{atual:.2f}",  
                        showarrow=True,
                        arrowhead=0,
                        ax=5,  
                        ay=0,  
                        font=dict(size=12, color='#FFFFFF'),
                        bgcolor='rgba(0, 0, 0, 0.5)',  
                        bordercolor='#FFFFFF',
                        borderwidth=1,
                        xanchor="left",  
                        yanchor="middle"  
                        )

return fig


st.title("🏛️Estatística Monetária")
tab1, tab2 = st.tabs(['Historico','Tabelas'])
with tab1:
    with st.spinner("Carregando dados..."):
        selic, selic_atual, ipca, ipca_atual, juros_real, dolar, dolar_atual = get_data()
        
    col1, col2 = st.columns([5, 1])
    with col1:
        st.plotly_chart(create_chart(selic, selic_atual, 'Taxa de Juros SELIC', 'Taxa de Juros (%)', '%'))
        st.plotly_chart(create_chart(ipca, ipca_atual, 'IPCA Acumulado 12M', 'IPCA acumulado (%)', '%'))
        st.plotly_chart(create_chart(dolar, dolar_atual, 'Cotação do Dólar', 'Valor em R$', 'R$'))


    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)  
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
    indicadores = {
        "IPCA Mensal": 433,
        "IGP-M Mensal": 189,
        "Taxa SELIC": 432
    }

    st.header("Indicadores Econômicos - Banco Central")

    indicador_selecionado = st.radio("Escolha o indicador:", list(indicadores.keys()))

    start_date = st.date_input("Data de início", pd.to_datetime("2020-01-01").date(), format="DD/MM/YYYY", key="start_date")
    end_date = st.date_input("Data de término", pd.to_datetime("today").date(), format="DD/MM/YYYY", key="end_date")

    # Coletando dados
    @st.cache_data(ttl=3600)
    def fetch_bcb_data(codigo, start_date, end_date):
        try:
            dados = sgs.get(codigo, start=start_date, end=end_date)

            if dados.empty:
                return None

            dados.columns = [f"{indicador_selecionado} (%)"]
            dados.index.name = "Data"

            dados = dados.sort_index(ascending=False)
            dados.index = dados.index.strftime("%d/%m/%Y") 

            return dados
        except Exception:
            return None

    codigo_indicador = indicadores[indicador_selecionado]
    dados = fetch_bcb_data(codigo_indicador, start_date, end_date)

    if dados is not None:
        st.subheader(f"Tabela de Dados - {indicador_selecionado}")
        st.dataframe(dados)

        #CSV
        csv = dados.to_csv(index=True)
        st.download_button(
            label="Baixar dados como CSV",
            data=csv,
            file_name=f"{indicador_selecionado.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )
    else:
        st.warning(f"Nenhum dado encontrado para {indicador_selecionado} no período selecionado.")

    # Informações adicionais
    st.write(f"Dados obtidos do Banco Central do Brasil (SGS) - Indicador: {indicador_selecionado}")
    st.write(f"Período selecionado: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")


st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; font-size: 14px; color: #A9A9A9; margin-top: 20px;">
    <strong>Fonte:</strong> BCB - Banco Central do Brasil<br>

</div>
""", unsafe_allow_html=True)