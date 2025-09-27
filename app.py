# app.py

import streamlit as st
from datetime import datetime

# Importa as funções da nossa nova lógica multimodal
from logica_ia import analisar_imagem_com_gemini_multimodal, criar_documento_docx

st.set_page_config(layout="wide")
st.title("🤖 Corretor de Redação IA (Versão Multimodal)")
st.markdown("Faça o upload da foto de uma redação manuscrita para receber uma análise completa e precisa, lida diretamente pela IA.")
st.write("Este projeto foi desenvolvido com um propósito especial: ajudar na reforma da casa para a chegada do meu filho. Cada correção feita com esta ferramenta contribui para um futuro melhor.")
st.divider()

# --- Área de Upload ---
imagem_redacao = st.file_uploader(
    "Envie a foto da redação aqui (formato .jpg ou .png)",
    type=['jpg', 'png', 'jpeg']
)

st.divider()

if imagem_redacao is not None:
    if st.button("Analisar Redação com IA Multimodal", type="primary"):
        
        conteudo_imagem_bytes = imagem_redacao.getvalue()

        # --- Etapa Única: Análise Multimodal ---
        # A IA agora lê a imagem, extrai o texto e corrige, tudo de uma só vez!
        with st.spinner("Analisando a imagem e corrigindo a redação... Isso pode levar um minuto."):
            analise_completa = analisar_imagem_com_gemini_multimodal(conteudo_imagem_bytes)
        
        # Verifica se houve algum erro durante a análise
        if "❌" in analise_completa:
            st.error(analise_completa)
        else:
            st.success("Análise concluída com sucesso!", icon="🎉")
            st.divider()
            
            # --- Exibição e Download ---
            st.header("Resultados da Análise")
            st.markdown(analise_completa) # Mostra a análise completa (transcrição + correção)
            
            st.divider()
            with st.spinner("Gerando relatório .docx para download..."):
                arquivo_docx = criar_documento_docx(analise_completa)
                
                if arquivo_docx:
                    nome_arquivo = f"correcao_multimodal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                    st.download_button(
                        label="📥 Baixar Relatório Completo em .docx",
                        data=arquivo_docx,
                        file_name=nome_arquivo,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error("Não foi possível gerar o arquivo .docx.")

