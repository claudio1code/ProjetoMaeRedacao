# app.py

import streamlit as st
from datetime import datetime
from PIL import Image # Importa a biblioteca de imagem

# Importa as funções CORRETAS e DEFINITIVAS dos seus arquivos de lógica
from logica_ia import pre_processar_imagem, extrair_texto_da_imagem, analisar_redacao_com_gemini, analisar_redacao_com_ia, criar_documento_docx

# --- Configuração da Página ---
st.set_page_config(layout="wide")
st.title("🤖 Corretor de Redação IA")
st.markdown("Faça o upload da foto de uma redação manuscrita para receber uma análise detalhada e precisa.")

# Adicionando um toque pessoal, conectando com o propósito do projeto
st.write("Este projeto foi desenvolvido com um propósito especial: ajudar na reforma da casa para a chegada do meu filho. Cada correção feita com esta ferramenta contribui para um futuro melhor.")
st.divider()

# --- Área de Upload ---
imagem_redacao = st.file_uploader(
    "Envie a foto da redação aqui (formato .jpg, .png ou .jpeg)",
    type=['jpg', 'png', 'jpeg']
)

st.divider()

# --- Lógica Principal (só executa se uma imagem for enviada) ---
if imagem_redacao is not None:
    
    # Exibe a imagem enviada para o usuário conferir
    st.image(imagem_redacao, caption='Imagem da Redação Enviada', use_column_width=True)
    st.divider()

    # Seletor de Modelo de IA
    modelo_ia_selecionado = st.selectbox(
        "Escolha o modelo de IA para a correção:",
        ("Google (Gemini Pro - Gratuito)", "OpenAI (GPT-4o - Pago)")
    )
    
    if st.button("Analisar Redação", type="primary"):
        
        conteudo_imagem_bytes = imagem_redacao.getvalue()

        # --- Etapa 1: Pré-processamento da Imagem ---
        with st.spinner("1/4 - Otimizando a imagem para melhor leitura..."):
            imagem_processada_bytes = pre_processar_imagem(conteudo_imagem_bytes)

        # --- Etapa 2: OCR com Google Vision ---
        with st.spinner("2/4 - Lendo o texto da imagem otimizada..."):
            texto_extraido = extrair_texto_da_imagem(imagem_processada_bytes)
        
        # Verifica se o OCR falhou
        if "❌" in texto_extraido:
            st.error(texto_extraido) # Mostra o erro detalhado da função
        else:
            st.success("Texto extraído com sucesso!", icon="✅")

            # --- Etapa 3: Análise com a IA Escolhida ---
            correcao_da_ia = ""
            with st.spinner(f"3/4 - {modelo_ia_selecionado} está analisando a redação..."):
                if "Google (Gemini Pro - Gratuito)" in modelo_ia_selecionado:
                    correcao_da_ia = analisar_redacao_com_gemini(texto_extraido)
                elif "OpenAI (GPT-4o - Pago)" in modelo_ia_selecionado:
                    correcao_da_ia = analisar_redacao_com_ia(texto_extraido)

            st.success("Análise da IA concluída!", icon="🧠")
            st.divider()
            
            # --- Exibição dos Resultados ---
            st.header("Resultados da Análise")
            
            if "❌" in correcao_da_ia:
                st.error(correcao_da_ia)
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Texto Original Extraído")
                    st.text_area("Texto:", value=texto_extraido, height=500, disabled=True)
                with col2:
                    st.subheader("Análise e Correção da IA")
                    st.markdown(correcao_da_ia)
                
                # --- Etapa 4: Download do DOCX ---
                st.divider()
                with st.spinner("4/4 - Gerando relatório .docx para download..."):
                    # Aqui chamamos a função que usa o nosso especialista gerador_docx.py
                    arquivo_docx = criar_documento_docx(texto_extraido, correcao_da_ia)
                    nome_arquivo = f"correcao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                
                st.download_button(
                    label="📥 Baixar Relatório Completo em .docx",
                    data=arquivo_docx,
                    file_name=nome_arquivo,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

