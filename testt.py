import streamlit as st
import plotly.graph_objects as go
from bcb import sgs

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
    fig.update_layout(title=title, yaxis_title=yaxis_title, showlegend=False, height=400)
    fig.add_annotation(x=data.index[-1], y=atual, text=f'{atual:.2f}{unit}', showarrow=True, ay=-40)
    return fig

def app():
    st.title("🏛️Estatística Monetária")
    with st.spinner("Carregando dados..."):
        selic, selic_atual, ipca, ipca_atual, juros_real, dolar, dolar_atual = get_data()
    
    col1, col2 = st.columns([5, 1])
    with col1:
        st.plotly_chart(create_chart(selic, selic_atual, 'Taxa de Juros SELIC', 'Taxa de Juros (%)', '%'))
        st.plotly_chart(create_chart(ipca, ipca_atual, 'IPCA Acumulado 12M', 'IPCA acumulado (%)', '%'))
        st.plotly_chart(create_chart(dolar, dolar_atual, 'Cotação do Dólar', 'Valor em R$', 'R$'))
    
    with col2:
        st.write(f"<div style='text-align: center; color: white;'><h5>Juros Real:</h5><span style='font-size: 35px;'>{juros_real:.2f}%</span></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    app()