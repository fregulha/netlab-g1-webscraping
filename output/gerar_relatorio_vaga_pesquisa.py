from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem

repo = Path(r"c:\Users\Fernanda Fregulha\Downloads\netlab-g1-PRELIMINAR\netlab-g1")
out = repo / "output" / "relatorio_vaga_assistente_pesquisa_engenharia_dados.pdf"
out.parent.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(name='TitleDoc', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor('#0B1F33'), leading=26, alignment=1, spaceAfter=4))
styles.add(ParagraphStyle(name='SubtitleDoc', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#4E647A'), leading=14, alignment=1, spaceAfter=10))
styles.add(ParagraphStyle(name='HeaderBox', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.white, leading=14, alignment=1, backColor=colors.HexColor('#0F2B3D'), borderPadding=8, borderWidth=0, spaceAfter=10))
styles.add(ParagraphStyle(name='SectionTitle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12.5, textColor=colors.HexColor('#123B5B'), leading=16, spaceBefore=14, spaceAfter=6, borderPadding=3))
styles.add(ParagraphStyle(name='BodyTextClean', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#1C2733'), spaceAfter=6))
styles.add(ParagraphStyle(name='BulletText', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#1C2733'), leftIndent=18, bulletIndent=12, spaceAfter=3))
styles.add(ParagraphStyle(name='HighlightBox', parent=styles['BodyText'], fontSize=10.2, leading=15, textColor=colors.HexColor('#123B5B'), backColor=colors.HexColor('#EEF5FB'), borderPadding=8, borderWidth=1, borderColor=colors.HexColor('#D5E6F3'), spaceAfter=10))
styles.add(ParagraphStyle(name='MetaText', parent=styles['BodyText'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#45607A'), spaceAfter=4))
styles.add(ParagraphStyle(name='LabelText', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9.5, leading=12, textColor=colors.HexColor('#1B2F42'), spaceAfter=2))

repo_link = 'https://github.com/fregulha/netlab-g1-webscraping.git'
candidate_name = 'Fernanda Fregulha'


def p(text, style='BodyTextClean'):
    return Paragraph(text, styles[style])


def bullet_list(items):
    return ListFlowable(
        [ListItem(Paragraph(item, styles['BulletText']), value='bullet') for item in items],
        bulletType='bullet',
        bulletIndent=12,
        leftIndent=0,
        spaceAfter=10,
    )


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

    story.append(p(f'<b>{candidate_name}</b>  |  <b>Vaga:</b> Assistente de Pesquisa de Engenharia de Dados', 'HeaderBox'))
    story.append(p(f'<b>Repositório:</b> <link href="{repo_link}">{repo_link}</link>', 'MetaText'))
    story.append(p('<b>Projeto:</b> NetLab G1 — Diagnóstico e correção de coleta de resultados de busca', 'MetaText'))
    story.append(Spacer(1, 8))

    story.append(p('<b>Resumo executivo</b>', 'SectionTitle'))
    story.append(p('Este projeto investigou uma falha na rotina de coleta de resultados de busca do portal G1 para o termo “LGPD”. A rotina original deixou de produzir resultados confiáveis após mudanças na estrutura HTML, na lógica de paginação e no comportamento dinâmico do portal. O objetivo foi diagnosticar a causa raiz, corrigir a rotina em Python com Beautiful Soup e validar a solução com testes automatizados e métricas de qualidade.', 'HighlightBox'))
    story.append(p('A solução desenvolvida se baseia em parsing defensivo, normalização de URLs, deduplicação, tratamento de erros, exportação em CSV e JSON e revisão de qualidade dos dados. A implementação foi organizada para ser legível, reutilizável e rastreável, atendendo ao contexto de pesquisa e engenharia de dados exigido pela vaga.', 'BodyTextClean'))

    story.append(p('<b>1. Contexto do problema</b>', 'SectionTitle'))
    story.append(p('Recentemente, a coleta de resultados da busca do G1 para “LGPD” passou a devolver poucos resultados, resultados incompletos ou registros vazios, mesmo sem interromper a execução do código. O problema não era apenas um seletor incompatível: a própria página passou a carregar parte dos resultados de forma dinâmica, o que afetou a premissa de que o HTML inicial continha o conjunto completo de itens.', 'BodyTextClean'))

    story.append(p('<b>2. Diagnóstico técnico</b>', 'SectionTitle'))
    story.append(p('A evidência observada diretamente no navegador mostra que a página de busca do G1 não entrega a totalidade dos resultados em uma única carga HTML estática. Ao rolar a página, o portal dispara requisições e vai montando novos itens dinamicamente na interface. Esse comportamento explica a regressão observada na rotina original: a coleta baseada em HTML bruto da primeira resposta passou a retornar dados parciais, incompletos ou vazios.', 'BodyTextClean'))
    story.append(p('Além disso, a rotina original apresentava outros problemas relevantes: seletores incompatíveis, ausência de validadores de resposta HTTP, campos vazios sem tratamento, sobrescrita de resultados, ausência de deduplicação e baixa rastreabilidade operacional.', 'BodyTextClean'))

    story.append(p('<b>3. Estratégias adotadas</b>', 'SectionTitle'))
    story.append(bullet_list([
        'revisão de HTML e seletores com base em snapshots reais do portal',
        'normalização de URLs e remoção de parâmetros de rastreamento',
        'deduplicação por URL para evitar registros repetidos',
        'tratamento de falhas de conexão, HTTP inválido e campos ausentes',
        'exportação em CSV e JSON com rastreabilidade de página, snapshot e horário da coleta',
        'validação automatizada com testes para componentes críticos do scraper'
    ]))

    story.append(p('<b>4. Solução implementada</b>', 'SectionTitle'))
    story.append(p('A rotina foi reorganizada em módulos com responsabilidades bem definidas, permitindo maior legibilidade e reutilização. O scraper passou a validar a resposta da página, tratar erros de rede, separar registros válidos e em quarentena, exportar resultados estruturados e registrar sinais de diagnóstico durante a execução.', 'BodyTextClean'))
    story.append(bullet_list([
        'coleta, parsing e normalização do conteúdo extraído',
        'validação de URL, dados ausentes e resposta HTTP',
        'deduplicação e preservação da primeira ocorrência válida',
        'exportação em formatos estruturados com informações de origem',
        'métricas e avaliação de qualidade dos dados coletados'
    ]))

    story.append(p('<b>5. Seletores e paginação</b>', 'SectionTitle'))
    story.append(bullet_list([
        'Card de notícia: li.widget--info',
        'Card de vídeo: li.video-widget--info',
        'Título: .widget--info__title',
        'Resumo: .widget--info__description',
        'Data exibida: .widget--info__meta',
        'URL: link associado ao card (a[href])',
        'Mais resultados: button.pagination__load-more'
    ]))
    story.append(p('A lógica de paginação foi tratada como parte do problema: a página do G1 não se comporta como uma página estática simples, mas como um ambiente de carregamento incremental. Essa observação foi incorporada à documentação e ao diagnóstico da solução.', 'BodyTextClean'))

    story.append(p('<b>6. Requisitos solicitados e atendimento</b>', 'SectionTitle'))
    story.append(bullet_list([
        'Identificar e explicar os principais problemas do código atual: atendido por meio do diagnóstico técnico documentado.',
        'Corrigir a rotina de coleta com Python e Beautiful Soup: atendido com parser robusto e normalização de dados.',
        'Atualizar seletores HTML e mecanismo de paginação: atendido com revisão de estrutura e evidência de carregamento incremental.',
        'Coletar título, URL, resumo, data, página e horário da coleta: atendido com registros estruturados e metadados de execução.',
        'Tratar falhas de conexão, HTTP inválido e campos ausentes: atendido com validação e tratamento de erros sem interrupção do processo.',
        'Evitar registros duplicados: atendido com deduplicação por URL e registro em quarentena.',
        'Organizar o código de forma legível e reutilizável: atendido pela separação em módulos com responsabilidades claras.',
        'Sugerir melhorias na padronização do código e dos dados: atendido com documentação e boas práticas.',
        'Incluir logs e mensagens informativas: atendido com rastreabilidade de execução e diagnóstico.',
        'Salvar os resultados em CSV, JSON ou outro formato estruturado: atendido com exportação em arquivos estruturados.',
        'Incluir testes automatizados: atendido com suíte validada em pytest.',
        'Documentar requisitos, instalação e execução: atendido no README do projeto.',
        'Propor uso de LLM para manutenção e diagnóstico: atendido com estratégia documentada e mecanismos de validação.',
        'Construir amostra de referência e métricas: atendido com avaliação comparativa de qualidade dos dados.',
        'Descrever limitações e melhorias futuras: atendido com seção dedicada e próximos passos.'
    ]))

    story.append(p('<b>7. Métricas e evidências de qualidade</b>', 'SectionTitle'))
    story.append(bullet_list([
        '25 testes automatizados aprovados com pytest',
        '30 URLs únicas após deduplicação',
        '26 registros de notícias e 4 de vídeos',
        'título, URL, resumo e data exibida presentes em 30/30 registros',
        'rastreabilidade de página, snapshot, origem e horário de coleta preservada',
        'dados de publicação extraídos somente quando houver evidência real em metadados'
    ]))

    story.append(p('<b>8. Uso de LLM</b>', 'SectionTitle'))
    story.append(p('A LLM pode auxiliar na análise de HTML, comparação de versões da página, revisão de logs e geração de testes de regressão. Sua função principal seria apoiar o diagnóstico e a manutenção do scraper, sem substituir as validações objetivas do projeto.', 'BodyTextClean'))
    story.append(p('Antes de incorporar qualquer sugestão, a resposta do modelo precisa ser validada por evidência observável e testes automatizados. Isso reduz o risco de alucinações e garante que apenas informações realmente presentes nos dados sejam incorporadas ao scraper.', 'BodyTextClean'))

    story.append(p('<b>9. Limitações e próximos passos</b>', 'SectionTitle'))
    story.append(bullet_list([
        'a coleta completa do portal G1 pode depender de scroll e requisições dinâmicas',
        'a página pode sofrer mudanças estruturais e exigir revisão periódica dos seletores',
        'a data de publicação deve ser confirmada em metadados do artigo e não inferida sem evidência',
        'o próximo passo mais robusto é monitorar a API ou o fluxo de carregamento real do site com automação de navegador'
    ]))

    story.append(p('<b>10. Conclusão</b>', 'SectionTitle'))
    story.append(p('A solução desenvolvida recuperou a robustez da rotina de coleta, preservou a qualidade dos dados e documentou com clareza o processo de diagnóstico e correção. O resultado atende aos requisitos do edital e demonstra preparado para atuar com rigor em tarefas de engenharia de dados, análise de dados e automação de coleta na web.', 'BodyTextClean'))

    story.append(Spacer(1, 10))
    story.append(p('<b>Links e referências</b>', 'SectionTitle'))
    story.append(p(f'<b>GitHub:</b> <link href="{repo_link}">{repo_link}</link>', 'MetaText'))
    story.append(p('<b>Portal de referência:</b> https://g1.globo.com/busca/?q=lgpd', 'MetaText'))
    story.append(p('<b>Validação:</b> 25 testes automatizados aprovados com pytest', 'MetaText'))

    doc.build(story)
    print(f'PDF gerado em: {out}')


if __name__ == '__main__':
    build_pdf()
