# gerador_docx.py

import re
from io import BytesIO
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_COLOR_INDEX

def normalizar_texto(texto):
    """
    Função de limpeza para a busca flexível. Remove espaços extras, 
    quebras de linha e converte para minúsculas.
    """
    return re.sub(r'\s+', ' ', texto).strip().lower()

def parse_analise_ia(texto_analise):
    """
    Lê a análise em Markdown da IA e a transforma em dados estruturados (dicionários)
    que o Python pode usar para construir o documento.
    """
    dados = {'competencias': {}}
    nota_match = re.search(r"\*\*Nota Estimada:\*\*\s*(\d+)", texto_analise)
    if nota_match:
        dados['nota_geral'] = nota_match.group(1)

    blocos = re.split(r'####\s*(Competência \d+.*)', texto_analise)
    
    for i in range(1, len(blocos), 2):
        nome_competencia_full = blocos[i].strip()
        conteudo_competencia = blocos[i+1].strip()
        
        num_competencia_match = re.search(r"Competência (\d+)", nome_competencia_full)
        if not num_competencia_match: continue
        
        id_competencia = f"C{num_competencia_match.group(1)}"
        dados['competencias'][id_competencia] = { 'erros': [] }
        
        erros_matches = re.finditer(r"\*\*Trecho com erro:\*\*\s*\"(.*?)\"", conteudo_competencia, re.DOTALL)
        for erro_match in erros_matches:
            trecho_com_erro = erro_match.group(1).strip().replace('\n', ' ')
            if trecho_com_erro and "copie aqui" not in trecho_com_erro:
                dados['competencias'][id_competencia]['erros'].append(trecho_com_erro)
                
    return dados

def highlight_text(paragraph, text_to_highlight, color):
    """
    Busca flexível que encontra um texto dentro de um parágrafo e aplica
    uma cor de fundo (highlight), ignorando pequenas diferenças.
    """
    texto_normalizado_paragrafo = normalizar_texto(paragraph.text)
    texto_normalizado_highlight = normalizar_texto(text_to_highlight)
    
    if texto_normalizado_highlight in texto_normalizado_paragrafo:
        # Esta é uma abordagem que destaca todo o parágrafo se o erro for encontrado.
        # Uma implementação palavra por palavra é significativamente mais complexa.
        for run in paragraph.runs:
            run.font.highlight_color = color
        return True
    return False

def criar_relatorio_avancado_docx(texto_original, texto_analise_ia):
    """
    Cria o relatório .docx final, com texto destacado e análise formatada.
    """
    try:
        dados_analise = parse_analise_ia(texto_analise_ia)
        document = Document()
        
        nota_geral = dados_analise.get('nota_geral', 'N/A')
        document.add_heading(f'Relatório de Correção - Nota Estimada: {nota_geral}', level=1)
        
        document.add_heading('Redação Original com Destaques', level=2)
        p_original = document.add_paragraph(texto_original)
        
        mapa_cores = {
            'C1': WD_COLOR_INDEX.TURQUOISE,
            'C2': WD_COLOR_INDEX.BRIGHT_GREEN,
            'C3': WD_COLOR_INDEX.PINK,
            'C4': WD_COLOR_INDEX.YELLOW,
            'C5': WD_COLOR_INDEX.VIOLET,
        }
        
        for id_comp, dados_comp in dados_analise.get('competencias', {}).items():
            cor = mapa_cores.get(id_comp)
            if cor:
                for erro in dados_comp.get('erros', []):
                    highlight_text(p_original, erro, cor)

        document.add_heading('Análise Detalhada da IA', level=2)
        document.add_paragraph(texto_analise_ia)
        
        doc_buffer = BytesIO()
        document.save(doc_buffer)
        doc_buffer.seek(0)
        return doc_buffer

    except Exception as e:
        print(f"❌ Erro ao gerar o arquivo DOCX: {e}")
        # Fallback para um DOCX simples em caso de erro
        document = Document()
        document.add_heading('Erro ao Gerar Relatório')
        document.add_paragraph(f"Ocorreu um erro: {e}")
        document.add_paragraph(texto_analise_ia)
        doc_buffer = BytesIO()
        document.save(doc_buffer)
        doc_buffer.seek(0)
        return doc_buffer

