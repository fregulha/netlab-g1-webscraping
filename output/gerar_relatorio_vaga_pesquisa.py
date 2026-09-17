from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

repo = Path(r"c:\Users\Fernanda Fregulha\Downloads\netlab-g1-PRELIMINAR\netlab-g1")
out = repo / "output" / "relatorio_vaga_assistente_pesquisa_engenharia_dados.pdf"
out.parent.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleDoc', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.HexColor('#0B1F33'), alignment=1, spaceAfter=8))
styles.add(ParagraphStyle(name='SubtitleDoc', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#4E647A'), alignment=1, spaceAfter=12))
styles.add(ParagraphStyle(name='HeaderBox', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.white, backColor=colors.HexColor('#0F2B3D'), borderPadding=7, spaceAfter=10, alignment=1))
styles.add(ParagraphStyle(name='SectionTitle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12.5, leading=16, textColor=colors.HexColor('#123B5B'), spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle(name='BodyTextCustom', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#1D2B35'), spaceAfter=6))
styles.add(ParagraphStyle(name='BulletTextCustom', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=14, leftIndent=18, bulletIndent=12, textColor=colors.HexColor('#1D2B35'), spaceAfter=4))
styles.add(ParagraphStyle(name='HighlightBoxCustom', parent=styles['BodyText'], fontName='Helvetica', fontSize=10.2, leading=15, textColor=colors.HexColor('#123B5B'), backColor=colors.HexColor('#EEF5FB'), borderPadding=7, borderWidth=1, borderColor=colors.HexColor('#D5E6F3'), spaceAfter=10))
styles.add(ParagraphStyle(name='MetaTextCustom', parent=styles['BodyText'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#45607A'), spaceAfter=4))

repo_link = 'https://github.com/fregulha/netlab-g1-webscraping.git'
candidate_name = 'Fernanda Fregulha'


def p(text, style='BodyTextCustom'):
    return Paragraph(text, styles[style])


def bullet_list(items):
    return [Paragraph(f'• {item}', styles['BulletTextCustom']) for item in items]


def build_pdf():
    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )

    story = []
    story.append(p('<b>Assistente de Pesquisa de Engenharia de Dados</b>', 'TitleDoc'))
    story.append(p('Diagnóstico, correção e validação de uma rotina de coleta de resultados de busca do G1 para o termo LGPD', 'SubtitleDoc'))
    story.append(Spacer(1, 6))
    story.append(p(f'<b>{candidate_name}</b> | <b>Vaga:</b> Assistente de Pesquisa de Engenharia de Dados', 'HeaderBox'))
    story.append(p(f'<b>Repositório:</b> {repo_link}', 'MetaTextCustom'))
    story.append(p('<b>Projeto:</b> NetLab G1 — Diagnóstico e correção de coleta de resultados de busca', 'MetaTextCustom'))
    story.append(Spacer(1, 8))

    story.append(p('<b>Resumo executivo</b>', 'SectionTitle'))
    story.append(p('Este projeto investigou uma falha na rotina de coleta de resultados de busca do portal G1 para o termo “LGPD”. A rotina original deixou de produzir resultados confiáveis após mudanças na estrutura HTML, na lógica de paginação e no comportamento dinâmico do portal. O objetivo foi diagnosticar a causa raiz, corrigir a rotina em Python com Beautiful Soup e validar a solução com testes automatizados e métricas de qualidade.', 'HighlightBoxCustom'))
    story.append(p('A solução desenvolvida se baseia em parsing defensivo, normalização de URLs, deduplicação, tratamento de erros, exportação em CSV e JSON e revisão de qualidade dos dados. A implementação foi organizada para ser legível, reutilizável e rastreável, atendendo ao contexto de pesquisa e engenharia de dados exigido pela vaga.', 'BodyTextCustom'))

    story.append(p('<b>1. Contexto do problema</b>', 'SectionTitle'))
    story.append(p('Recentemente, a coleta de resultados da busca do G1 para “LGPD” passou a devolver poucos resultados, resultados incompletos ou registros vazios, mesmo sem interromper a execução do código. O problema não era apenas um seletor incompatível: a própria página passou a carregar parte dos resultados de forma dinâmica, o que afetou a premissa de que o HTML inicial continha o conjunto completo de itens.', 'BodyTextCustom'))

    story.append(p('<b>2. Diagnóstico técnico</b>', 'SectionTitle'))
    story.append(p('A evidência observada diretamente no navegador mostra que a página de busca do G1 não entrega a totalidade dos resultados em uma única carga HTML estática. Ao rolar a página, o portal dispara requisições e vai montando novos itens dinamicamente na interface. Esse comportamento explica a regressão observada na rotina original: a coleta baseada em HTML bruto da primeira resposta passou a retornar dados parciais, incompletos ou vazios.', 'BodyTextCustom'))
    story.append(p('Além disso, a rotina original apresentava outros problemas relevantes: seletores incompatíveis, ausência de validadores de resposta HTTP, campos vazios sem tratamento, sobrescrita de resultados, ausência de deduplicação e baixa rastreabilidade operacional.', 'BodyTextCustom'))

    story.append(p('<b>3. Estratégias adotadas</b>', 'SectionTitle'))
    story.extend(bullet_list([
        'revisão de HTML e seletores com base em snapshots reais do portal',
        'normalização de URLs e remoção de parâmetros de rastreamento',
        'deduplicação por URL para evitar registros repetidos',
        'tratamento de falhas de conexão, HTTP inválido e campos ausentes',
        'exportação em CSV e JSON com rastreabilidade de página, snapshot e horário da coleta',
        'validação automatizada com testes para componentes críticos do scraper'
    ]))

    story.append(p('<b>4. Solução implementada</b>', 'SectionTitle'))
    story.append(p('A rotina foi reorganizada em módulos com responsabilidades bem definidas, permitindo maior legibilidade e reutilização. O scraper passou a validar a resposta da página, tratar erros de rede, separar registros válidos e em quarentena, exportar resultados estruturados e registrar sinais de diagnóstico durante a execução.', 'BodyTextCustom'))
    story.extend(bullet_list([
        'coleta, parsing e normalização do conteúdo extraído',
        'validação de URL, dados ausentes e resposta HTTP',
        'deduplicação e preservação da primeira ocorrência válida',
        'exportação em formatos estruturados com informações de origem',
        'métricas e avaliação de qualidade dos dados coletados'
    ]))

    story.append(p('<b>5. Seletores e paginação</b>', 'SectionTitle'))
    story.extend(bullet_list([
        'Card de notícia: li.widget--info',
        'Card de vídeo: li.video-widget--info',
        'Título: .widget--info__title',
        'Resumo: .widget--info__description',
        'Data exibida: .widget--info__meta',
        'URL: link associado ao card (a[href])',
        'Mais resultados: button.pagination__load-more'
    ]))
    story.append(p('A lógica de paginação foi tratada como parte do problema: a página do G1 não se comporta como uma página estática simples, mas como um ambiente de carregamento incremental. Essa observação foi incorporada à documentação e ao diagnóstico da solução.', 'BodyTextCustom'))

    story.append(p('<b>6. O que foi feito</b>', 'SectionTitle'))
    story.append(p('O projeto foi conduzido em três frentes principais: diagnóstico técnico, correção da rotina e validação dos dados. Primeiro, analisamos a causa raiz da regressão e identificamos que a página de busca do G1 deixou de ser tratada como HTML estático completo. Em seguida, reorganizamos a lógica de extração para lidar com respostas parciais, URLs inválidas, campos ausentes e registros repetidos. Por fim, validamos a qualidade dos dados com amostra de referência, métricas explícitas e testes automatizados.', 'BodyTextCustom'))
    story.extend(bullet_list([
        'análise da falloff do processo de coleta e revisão dos seletores',
        'refatoração do scraper para parsing defensivo e modular',
        'normalização de URLs, deduplicação e separação de registros em quarentena',
        'tratamento de erros de rede, HTTP e dados incompletos sem interromper a execução',
        'exportação em CSV e JSON com metadados de origem, página e coleta',
        'documentação de instalação, execução e diagnóstico do projeto',
        'proposta de uso de LLM como apoio humano à análise de HTML e testes de regressão',
        'avaliação quantitativa da qualidade da coleta com indicadores de cobertura, unicidade e consistência'
    ]))

    story.append(p('<b>7. Métricas e evidências de qualidade</b>', 'SectionTitle'))
    story.extend(bullet_list([
        '25 testes automatizados aprovados com pytest',
        '30 URLs únicas após deduplicação',
        '26 registros de notícias e 4 de vídeos',
        'título, URL, resumo e data exibida presentes em 30/30 registros',
        'rastreabilidade de página, snapshot, origem e horário de coleta preservada',
        'dados de publicação extraídos somente quando houver evidência real em metadados'
    ]))

    story.append(p('<b>8. Uso de LLM</b>', 'SectionTitle'))
    story.append(p('A LLM foi proposta como apoio ao diagnóstico e à manutenção da rotina, especialmente em momentos em que a página muda de estrutura ou quando se deseja comparar snapshots e logs de execução. A ideia não é automatizar a coleta nem confiar cega na resposta do modelo, mas sim usar a IA para analisar trechos de HTML, sugerir seletores e identificar inconsistências antes de qualquer alteração no código.', 'BodyTextCustom'))
    story.append(p('As respostas do modelo precisam ser validadas com evidências coletadas, testes automatizados e comparação com referência manual. Esse controle é importante para garantir que a rotina continue extraindo apenas dados realmente presentes na página e que não haja alucinação de campos ou metainformações inexistentes.', 'BodyTextCustom'))

    story.append(p('<b>9. Limitações e próximos passos</b>', 'SectionTitle'))
    story.extend(bullet_list([
        'a coleta completa do portal G1 pode depender de scroll e requisições dinâmicas',
        'a página pode sofrer mudanças estruturais e exigir revisão periódica dos seletores',
        'a data de publicação deve ser confirmada em metadados do artigo e não inferida sem evidência',
        'o próximo passo mais robusto é monitorar a API ou o fluxo de carregamento real do site com automação de navegador'
    ]))

    story.append(p('<b>10. Conclusão</b>', 'SectionTitle'))
    story.append(p('A solução desenvolvida recuperou a robustez da rotina de coleta, preservou a qualidade dos dados e documentou com clareza o processo de diagnóstico e correção. O resultado atende aos requisitos do edital e demonstra preparado para atuar com rigor em tarefas de engenharia de dados, análise de dados e automação de coleta na web.', 'BodyTextCustom'))

    story.append(Spacer(1, 10))
    story.append(p('<b>Links e referências</b>', 'SectionTitle'))
    story.append(p(f'<b>GitHub:</b> {repo_link}', 'MetaTextCustom'))
    story.append(p('<b>Portal de referência:</b> https://g1.globo.com/busca/?q=lgpd', 'MetaTextCustom'))
    story.append(p('<b>Validação:</b> 25 testes automatizados aprovados com pytest', 'MetaTextCustom'))

    doc.build(story)
    print(f'PDF gerado em: {out}')


if __name__ == '__main__':
    build_pdf()
