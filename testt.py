import streamlit as st
import pandas as pd
from bcb import sgs
from datetime import datetime

# Dicionário com os indicadores e seus códigos no SGS do Banco Central
indicadores = {
    "IPCA Mensal": 433,
    "IGP-M Mensal": 189,
    "Taxa SELIC": 432
}

# Configuração do título do app
st.title("Indicadores Econômicos - Banco Central")

# Seleção do indicador
indicador_selecionado = st.selectbox("Escolha o indicador:", list(indicadores.keys()))

# Definir intervalo de datas com keys únicas
start_date = st.date_input("Data de início", pd.to_datetime("2020-01-01").date(), format="DD/MM/YYYY", key="start_date")
end_date = st.date_input("Data de término", pd.to_datetime("today").date(), format="DD/MM/YYYY", key="end_date")

# Função para buscar os dados do BCB com cache
@st.cache_data(ttl=3600)  # Cache válido por 1 hora
def fetch_bcb_data(codigo, start_date, end_date):
    try:
        # Obter os dados do SGS do Banco Central
        dados = sgs.get(codigo, start=start_date, end=end_date)

        # Verificar se os dados estão vazios
        if dados.empty:
            return None

        # Renomear coluna para o nome do indicador
        dados.columns = [f"{indicador_selecionado} (%)"]
        dados.index.name = "Data"

        # Ordenação decrescente e formatação das datas
        dados = dados.sort_index(ascending=False)
        dados.index = dados.index.strftime("%d/%m/%Y")  # Formatar índice para DD/MM/YYYY

        return dados
    except Exception:
        return None

# Buscar os dados com cache
codigo_indicador = indicadores[indicador_selecionado]
dados = fetch_bcb_data(codigo_indicador, start_date, end_date)

# Exibir os dados no Streamlit
if dados is not None:
    st.subheader(f"Tabela de Dados - {indicador_selecionado}")
    st.dataframe(dados)

    # Criar botão para baixar CSV
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
st.write(f"Data atual: {datetime.now().strftime('%d/%m/%Y')}")
st.write(f"Período selecionado: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
