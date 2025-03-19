import streamlit as st


st.title("Links de Apoio")

# Link simples com markdown
st.markdown("Acesse o [Yahoo Finance](https://finance.yahoo.com) para realizar suas buscas.")
st.markdown("Acesse o [Investing](https://br.investing.com/) para realizar suas buscas.")
st.markdown("Acesse o [Fundamentus](https://www.fundamentus.com.br/index.php) para realizar suas buscas.")
st.markdown("Acesse o [Google](https://www.google.com) para realizar suas buscas.")
st.markdown("Acesse o [Google](https://www.google.com) para realizar suas buscas.")


tab1, tab2 = st.tabs(["Links", "Feedback"])
with tab1:
    st.header("Links de Apoio")
    st.markdown("Acesse os links acima para informações financeiras.")
with tab2:
    st.header("Feedback")
    st.text_area("Deixe seu feedback aqui:")


# Link simples com markdown
st.markdown("Acesse o [Google](https://www.google.com) para realizar suas buscas.")

# Botão que redireciona para um link
if st.button("Visitar o Streamlit"):
    st.write("Abrindo o site do Streamlit...")
    st.markdown("<a href='https://streamlit.io' target='_blank'>Clique aqui para abrir</a>", unsafe_allow_html=True)
