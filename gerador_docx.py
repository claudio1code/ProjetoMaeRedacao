# gerador_docx.py

import re
from io import BytesIO
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_COLOR_INDEX

def parse_analise_ia(texto_analise):
    """
    Lê a análise em Markdown da IA e a transforma em dados estruturados (dicionários)
    que o Python pode usar para construir o documento.
    """
    dados = {'competencias': {}}
    
    # Extrai a nota estimada geral
    nota_match = re.search(r"\*\*Nota Estimada:\*\*\s*(\d+)", texto_analise)
    if nota_match:
        dados['nota_geral'] = nota_match.group(1)

    # Separa o texto em blocos de competência
    blocos = re.split(r'####\s*(Competência \d+.*)', texto_analise)
    
    # Processa cada bloco de competência
    for i in range(1, len(blocos), 2):
        nome_competencia_full = blocos[i].strip()
        conteudo_competencia = blocos[i+1].strip()
        
        # Extrai o número da competência (C1, C2, etc.)
        num_competencia_match = re.search(r"Competência (\d+)", nome_competencia_full)
        if not num_competencia_match:
            continue
        
        id_competencia = f"C{num_competencia_match.group(1)}"
        dados['competencias'][id_competencia] = {
            'nome_full': nome_competencia_full,
            'conteudo': conteudo_competencia,
            'erros': []
        }
        
        # Procura por todos os "Trecho com erro" dentro do bloco da competência
        erros_matches = re.finditer(r"\*\*Trecho com erro:\*\*\s*\"(.*?)\"", conteudo_competencia, re.DOTALL)
        for erro_match in erros_matches:
            trecho_com_erro = erro_match.group(1).strip()
            # Adiciona apenas trechos válidos (ignora placeholders)
            if trecho_com_erro and "insira aqui" not in trecho_com_erro:
                dados['competencias'][id_competencia]['erros'].append(trecho_com_erro)
                
    return dados

def highlight_text(paragraph, text_to_highlight, color):
    """
    Função auxiliar para encontrar um texto dentro de um parágrafo
    e aplicar uma cor de fundo (highlight).
    """
    # Lógica para adicionar o highlight. O texto no parágrafo é dividido em "runs".
    # Precisamos juntar, encontrar o texto e depois recriar os "runs" com o highlight.
    # Esta é uma simplificação. Uma implementação completa seria mais complexa.
    # Por enquanto, vamos usar uma abordagem mais simples que funciona na maioria dos casos.
    if text_to_highlight in paragraph.text:
        # Abordagem simplificada: destaca a linha inteira.
        # Uma abordagem run-a-run seria necessária para destacar apenas a palavra.
        for run in paragraph.runs:
            if text_to_highlight in run.text:
                run.font.highlight_color = color

def criar_relatorio_avancado_docx(texto_original, texto_analise_ia):
    """
    Cria o relatório .docx final, com texto destacado e análise formatada.
    """
    try:
        dados_analise = parse_analise_ia(texto_analise_ia)
        document = Document()
        
        # --- Título do Documento ---
        nota_geral = dados_analise.get('nota_geral', 'N/A')
        document.add_heading(f'Relatório de Correção - Nota Estimada: {nota_geral}', level=1)
        
        # --- Seção 1: Redação Original com Destaques ---
        document.add_heading('Redação Original com Destaques', level=2)
        p_original = document.add_paragraph(texto_original)
        
        # Mapeamento de cores
        mapa_cores = {
            'C1': WD_COLOR_INDEX.TURQUOISE, # Azul
            'C2': WD_COLOR_INDEX.BRIGHT_GREEN, # Verde
            'C3': WD_COLOR_INDEX.PINK, # Vermelho
            'C4': WD_COLOR_INDEX.YELLOW, # Amarelo
            'C5': WD_COLOR_INDEX.VIOLET, # Roxo
        }
        
        # Aplica os destaques
        for id_comp, dados_comp in dados_analise.get('competencias', {}).items():
            cor = mapa_cores.get(id_comp)
            if cor:
                for erro in dados_comp.get('erros', []):
                    # Tenta encontrar e destacar o texto. Pode não funcionar se o texto for ligeiramente diferente.
                    highlight_text(p_original, erro, cor)

        # --- Seção 2: Análise Detalhada ---
        document.add_heading('Análise Detalhada da IA', level=2)
        document.add_paragraph(texto_analise_ia) # Adiciona a análise completa em texto
        
        # Salva em memória para download
        doc_buffer = BytesIO()
        document.save(doc_buffer)
        doc_buffer.seek(0)
        return doc_buffer

    except Exception as e:
        print(f"❌ Erro ao gerar o arquivo DOCX: {e}")
        # Se falhar, retorna um DOCX simples como fallback
        document = Document()
        document.add_heading('Erro ao Gerar Relatório')
        document.add_paragraph(f"Ocorreu um erro: {e}")
        document.add_paragraph("\n--- Análise da IA (texto puro) ---\n")
        document.add_paragraph(texto_analise_ia)
        doc_buffer = BytesIO()
        document.save(doc_buffer)
        doc_buffer.seek(0)
        return doc_buffer

