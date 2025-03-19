import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Seu código existente
st.title("🏛️Estatística Monetária")
with st.spinner("Carregando dados..."):
    selic, selic_atual, ipca, ipca_atual, juros_real, dolar, dolar_atual = get_data()
    
col1, col2 = st.columns([5, 1])
with col1:
    st.plotly_chart(create_chart(selic, selic_atual, 'Taxa de Juros SELIC', 'Taxa de Juros (%)', '%'))
    st.plotly_chart(create_chart(ipca, ipca_atual, 'IPCA Acumulado 12M', 'IPCA acumulado (%)', '%'))
    st.plotly_chart(create_chart(dolar, dolar_atual, 'Cotação do Dólar', 'Valor em R$', 'R$'))

with col2:
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

# Função para gerar o PDF
def generate_pdf(selic_atual, ipca_atual, juros_real, dolar_atual):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica", 12)
    
    # Adicionando título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Estatística Monetária")
    
    # Adicionando dados
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"Taxa de Juros SELIC: {selic_atual:.2f}%")
    p.drawString(100, 700, f"IPCA Acumulado 12M: {ipca_atual:.2f}%")
    p.drawString(100, 680, f"Juros Real: {juros_real:.2f}%")
    p.drawString(100, 660, f"Cotação do Dólar: R${dolar_atual:.2f}")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# Botão para baixar o PDF
pdf_buffer = generate_pdf(selic_atual, ipca_atual, juros_real, dolar_atual)
st.download_button(
    label="📥 Gerar e Baixar PDF",
    data=pdf_buffer,
    file_name="estatistica_monetaria.pdf",
    mime="application/pdf",
)