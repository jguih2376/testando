import streamlit as st

# Exemplo de uso de links
st.title("Exemplo de Links no Streamlit")

# Link simples com markdown
st.markdown("Acesse o [Google](https://www.google.com) para realizar suas buscas.")

# Botão que redireciona para um link
if st.button("Visitar o Streamlit"):
    st.write("Abrindo o site do Streamlit...")
    st.markdown("<a href='https://streamlit.io' target='_blank'>Clique aqui para abrir</a>", unsafe_allow_html=True)
