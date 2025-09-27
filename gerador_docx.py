# gerador_docx.py

import re
from io import BytesIO
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def extrair_nome_aluno(texto_completo_ia):
    """Extrai o nome do aluno da seção '### Nome do Aluno'."""
    match = re.search(r"### Nome do Aluno\s*\n(.*?)\n", texto_completo_ia, re.DOTALL)
    if match:
        nome = match.group(1).strip()
        if nome:
            return nome
    return "Nome_Nao_Identificado"

def extrair_secao(texto_completo, titulo_secao):
    """Extrai o conteúdo de uma seção específica do texto da IA."""
    padrao = re.compile(f"### {titulo_secao}(.*?)(?=### |$)", re.DOTALL)
    match = padrao.search(texto_completo)
    if match:
        return match.group(1).strip()
    return ""

def adicionar_paragrafo_com_icone(document, texto, cor):
    """Adiciona um parágrafo com um ícone quadrado colorido e texto em negrito."""
    p = document.add_paragraph()
    run_icone = p.add_run('■ ')
    run_icone.font.color.rgb = cor
    run_icone.font.size = Pt(12)
    run_texto = p.add_run(texto)
    run_texto.bold = True
    run_texto.font.size = Pt(12)

def criar_relatorio_avancado_docx(analise_completa_ia):
    """Cria o relatório .docx final com nome do aluno no cabeçalho."""
    try:
        # Extrai todas as informações da resposta da IA primeiro
        nome_aluno = extrair_nome_aluno(analise_completa_ia)
        analise_competencias = extrair_secao(analise_completa_ia, "Análise das Competências")
        nota_estimada = extrair_secao(analise_completa_ia, "Nota Estimada")
        comentarios_gerais = extrair_secao(analise_completa_ia, "Comentários Gerais")

        document = Document()
        
        mapa_cores = {
            '1': RGBColor(0x00, 0x70, 0xC0),  # Azul
            '2': RGBColor(0x00, 0xB0, 0x50),  # Verde
            '3': RGBColor(0xFF, 0x00, 0x00),  # Vermelho
            '4': RGBColor(0xFF, 0xC0, 0x00),  # Amarelo
            '5': RGBColor(0x70, 0x30, 0xA0),  # Roxo
        }

        # Título Principal
        titulo = document.add_heading('Relatório de Correção da Redação', level=1)
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # --- NOVO: Adiciona o nome do aluno abaixo do título ---
        if nome_aluno != "Nome_Nao_Identificado":
            p_nome = document.add_paragraph()
            p_nome.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_label = p_nome.add_run('Nome: ')
            run_label.bold = True
            p_nome.add_run(nome_aluno)
        
        document.add_paragraph() # Adiciona um espaço

        # Seção: Análise das Competências
        document.add_heading('Análise das Competências', level=2)
        if analise_competencias:
            for linha in analise_competencias.split('\n'):
                linha_limpa = linha.strip()
                if not linha_limpa: continue
                match_competencia = re.match(r'\*\*Competência (\d):.*?\*\*', linha_limpa)
                if match_competencia:
                    num_competencia = match_competencia.group(1)
                    cor = mapa_cores.get(num_competencia, RGBColor(0,0,0))
                    texto_competencia = linha_limpa.strip('*')
                    adicionar_paragrafo_com_icone(document, texto_competencia, cor)
                elif linha_limpa.startswith('*'):
                    texto_lista = linha_limpa.strip('* ').strip()
                    document.add_paragraph(texto_lista, style='List Bullet')
                else:
                    document.add_paragraph(linha_limpa)
        else:
            document.add_paragraph("A IA não conseguiu gerar uma análise detalhada.")
        document.add_paragraph()
        
        # Seção: Nota Estimada
        document.add_heading('Nota Estimada', level=2)
        p_nota = document.add_paragraph()
        run_nota = p_nota.add_run(nota_estimada or "N/A")
        run_nota.font.size = Pt(16)
        run_nota.bold = True
        document.add_paragraph()
        
        # Seção: Comentários Gerais
        document.add_heading('Comentários Gerais', level=2)
        document.add_paragraph(comentarios_gerais or "Sem comentários adicionais.")
        document.add_paragraph()

        # Assinatura
        assinatura = document.add_paragraph("Profª Elaine Vaz")
        assinatura.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc_buffer = BytesIO()
        document.save(doc_buffer)
        doc_buffer.seek(0)
        return doc_buffer

    except Exception as e:
        print(f"❌ Erro ao gerar o arquivo DOCX formatado: {e}")
        # Plano B
        document = Document()
        document.add_heading('Erro ao Gerar Relatório Formatado')
        document.add_paragraph(f"Ocorreu um erro: {e}\n\n{analise_completa_ia}")
        doc_buffer = BytesIO()
        document.save(doc_buffer)
        doc_buffer.seek(0)
        return doc_buffer