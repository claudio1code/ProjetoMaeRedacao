# app.py
import streamlit as st
from logica_ia import analisar_imagem_com_gemini_multimodal, criar_documento_docx
# --- NOVO: Importa a função para extrair o nome ---
from gerador_docx import extrair_nome_aluno

st.set_page_config(layout="wide")
st.title("🤖 Corretor de Redação IA")
st.markdown("Faça o upload da foto de uma redação manuscrita para receber uma análise completa e precisa.")
st.write("Este projeto foi desenvolvido com um propósito especial: ajudar na reforma da casa para a chegada do meu filho. Cada correção feita com esta ferramenta contribui para um futuro melhor.")
st.divider()

# --- CAMPO DE NOME REMOVIDO ---

imagem_redacao = st.file_uploader(
    "Envie a foto da redação aqui (formato .jpg ou .png)",
    type=['jpg', 'png', 'jpeg']
)

st.divider()

if imagem_redacao is not None:
    if st.button("Analisar Redação com IA", type="primary"):
        
        conteudo_imagem_bytes = imagem_redacao.getvalue()

        with st.spinner("Analisando a imagem e corrigindo a redação..."):
            analise_completa = analisar_imagem_com_gemini_multimodal(conteudo_imagem_bytes)
        
        if "❌" in analise_completa:
            st.error(analise_completa)
        else:
            st.success("Análise concluída com sucesso!", icon="🎉")
            st.divider()
            
            st.header("Resultados da Análise")
            st.markdown(analise_completa)
            
            st.divider()
            with st.spinner("Gerando relatório .docx para download..."):
                # --- LÓGICA ATUALIZADA ---
                nome_aluno = extrair_nome_aluno(analise_completa)
                arquivo_docx = criar_documento_docx(analise_completa)
                
                if arquivo_docx:
                    nome_arquivo_final = f"correcao_{nome_aluno.replace(' ', '_')}.docx"
                    st.download_button(
                        label=f"📥 Baixar Relatório de {nome_aluno} em .docx",
                        data=arquivo_docx,
                        file_name=nome_arquivo_final,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error("Não foi possível gerar o arquivo .docx.")