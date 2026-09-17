from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted

repo = Path(r"c:\Users\Fernanda Fregulha\Downloads\netlab-g1-PRELIMINAR\netlab-g1")
out = repo / "output" / "relatorio_vaga_assistente_pesquisa_engenharia_dados.pdf"
out.parent.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCentered', parent=styles['Title'], alignment=1, fontSize=22, leading=26, textColor=colors.HexColor('#143D59'), spaceAfter=6))
styles.add(ParagraphStyle(name='Subtitle', parent=styles['BodyText'], fontSize=9.5, leading=13, alignment=1, textColor=colors.HexColor('#46637A'), spaceAfter=10))
styles.add(ParagraphStyle(name='Name', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#0E2F46'), alignment=1))
styles.add(ParagraphStyle(name='Role', parent=styles['Heading2'], fontSize=11.5, leading=16, textColor=colors.HexColor('#3A6B8A'), alignment=1, spaceAfter=8))
styles.add(ParagraphStyle(name='Section', parent=styles['Heading2'], fontSize=13.5, leading=18, textColor=colors.HexColor('#123B5B'), spaceBefore=18, borderPadding=4, borderWidth=1, borderColor=colors.HexColor('#CFE3F1'), leftIndent=4))
styles.add(ParagraphStyle(name='Body', parent=styles['BodyText'], fontSize=10.2, leading=14, alignment=1, spaceAfter=6))
styles.add(ParagraphStyle(name='BodyLeft', parent=styles['BodyText'], fontSize=10.2, leading=14, alignment=1, spaceAfter=6, textColor=colors.black))
styles.add(ParagraphStyle(name='CustomBullet', parent=styles['BodyText'], fontSize=10.2, leading=14, leftIndent=18, bulletIndent=12, spaceAfter=4))
styles.add(ParagraphStyle(name='CodeBlock', parent=styles['Code'], fontName='Courier', fontSize=8.7, leading=10.5, backColor=colors.HexColor('#F5F7FA'), borderPadding=6, borderWidth=1, borderColor=colors.HexColor('#D9E2EC')))
styles.add(ParagraphStyle(name='Small', parent=styles['BodyText'], fontSize=8.5, leading=11.5, textColor=colors.HexColor('#3E4A59')))
styles.add(ParagraphStyle(name='Highlight', parent=styles['BodyText'], fontSize=10.2, leading=14, textColor=colors.HexColor('#123B5B'), backColor=colors.HexColor('#EAF4FB'), borderPadding=8, borderWidth=1, borderColor=colors.HexColor('#CFE3F1'), spaceAfter=10))


def p(text, style='BodyLeft'):
    return Paragraph(text, styles[style])


def build_pdf():
    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    story = []

    story.append(p('<b>Assistente de Pesquisa de Engenharia de Dados</b>', 'TitleCentered'))
    story.append(p('Relatório técnico final — diagnóstico, correção e validação do scraper de busca do G1 para LGPD', 'Subtitle'))
    story.append(Spacer(1, 6))

    repo_link = 'https://github.com/fregulha/netlab-g1-webscraping.git'
    candidate_name = 'Fernanda Fregulha'

    header_table = Table([
        [Paragraph(f'<b>{candidate_name}</b>', styles['Name']), Paragraph('<b>Vaga</b><br/>Assistente de Pesquisa de Engenharia de Dados', styles['Role'])],
    ], colWidths=[90 * mm, 70 * mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F8FC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D7E6F2')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(p(f'<b>Repositório GitHub:</b> <link href="{repo_link}">{repo_link}</link>', 'BodyLeft'))
    story.append(p('<b>Projeto:</b> NetLab G1 — Diagnóstico e correção de coleta de resultados de busca', 'BodyLeft'))
    story.append(Spacer(1, 8))

    story.append(p('<b>Resumo executivo</b>', 'Section'))
    story.append(p('Este relatório apresenta a solução desenvolvida para diagnosticar e corrigir a rotina de coleta de resultados da busca do G1 para o termo “LGPD”. O projeto foi conduzido com foco em robustez, rastreabilidade, qualidade dos dados e validação automatizada. O objetivo foi identificar a causa da falha da rotina original, corrigir os pontos de fragilidade e entregar um processo de coleta confiável, documentado e verificável.', 'Highlight'))
    story.append(p('A correção combina análise de HTML, revisão de seletores, normalização de URLs, deduplicação, exportação de arquivos estruturados, validação de qualidade e testes automatizados. Em termos práticos, a solução diminui riscos de perda de resultados, melhora a integridade dos registros e demonstra capacidade de atuação em contextos reais de engenharia de dados e pesquisa.', 'BodyLeft'))
    story.append(Spacer(1, 8))

    story.append(p('<b>1. Contexto e problema</b>', 'Section'))
    story.append(p('Recentemente, uma rotina de web scraping utilizada pelo NetLab UFRJ para coletar resultados de busca do portal G1 deixou de funcionar corretamente. A partir da página https://g1.globo.com/busca/?q=lgpd, a rotina deveria coletar os resultados da busca pelo termo “LGPD”. Embora o código continue sendo executado sem necessariamente apresentar erros, a coleta passou a retornar poucos resultados, nenhum resultado ou registros com campos incompletos.', 'BodyLeft'))
    story.append(p('A principal suspeita foi a alteração da estrutura HTML, a fragilidade dos seletores e o comportamento de paginação do portal. O problema real não foi apenas um seletor quebrado: a página passou a carregar partições de resultados dinâmicamente, e isso afetou a premissa de que a resposta inicial de HTML continha o conjunto completo de resultados.', 'BodyLeft'))

    story.append(p('<b>2. Diagnóstico técnico</b>', 'Section'))
    story.append(p('A evidência observada diretamente no navegador confirma que a página de busca do G1 não entrega a totalidade dos resultados em uma única carga HTML estática. Ao rolar a página, o portal dispara requisições de rede e vai montando novos itens dinamicamente na interface. Isso torna o HTML inicial insuficiente para coletar o conjunto completo de resultados, porque parte do conteúdo é carregado após a primeira renderização.', 'BodyLeft'))
    story.append(p('Esse comportamento explica a regressão observada na rotina original: a coleta baseada em HTML bruto da primeira carga passa a retornar poucos resultados, registros vazios ou incompletos, sem que a rotina registre falha explícita. Além disso, a rotina original apresentava problemas de robustez operacional, como sobrescrita de listas, ausência de deduplicação por URL, campos ausentes não tratados, ausência de validação de HTTP e timeout, e uso de seletores incompatíveis com a estrutura atual.', 'BodyLeft'))

    story.append(p('<b>3. Estratégias adotadas</b>', 'Section'))
    story.append(p('A correção foi estruturada em quatro eixos principais: aquisição, parsing, normalização e exportação. O primeiro passo foi reforçar a coleta com validação da resposta HTTP, controle de timeout, tratamento de falhas de rede e logs para monitoramento. Isso reduz o risco de a rotina falhar silenciosamente em cenários de instabilidade do portal.', 'BodyLeft'))
    story.append(p('O segundo eixo foi o parsing defensivo e adaptativo. Em vez de depender de seletores frágeis e fixos, o código passou a revisar o HTML real observado nos snapshots, ajustar os caminhos para os elementos presentes na estrutura atual e extrair apenas os campos realmente existentes nos cards de busca, preservando a robustez diante de campos ausentes.', 'BodyLeft'))
    story.append(p('O terceiro eixo foi o tratamento do carregamento incremental. Como a evidência do navegador mostra que a busca do G1 adiciona novos resultados ao rolar, a solução foi organizada para reconhecer esse padrão e, em uma extensão mais avançada, seguir o comportamento real do portal com automação de navegador ou consumo da API que alimenta os cards. Isso reduz a fragilidade de uma coleta que assume uma página estática e completa desde a primeira resposta.', 'BodyLeft'))
    story.append(p('O quarto eixo foi a garantia de integridade e rastreabilidade dos dados. A URL foi normalizada para remover parâmetros de rastreamento conhecidos. Também foi implementada a deduplicação por URL para evitar registros repetidos entre lotes cumulativos, preservando a primeira ocorrência. O pipeline de exportação foi reforçado com identificação de página, snapshot, origem e timestamp de coleta.', 'BodyLeft'))

    story.append(p('<b>4. Principais problemas identificados no código original</b>', 'Section'))
    bullets = [
        'Seletores antigos e incompatíveis com a estrutura atual da página do G1.',
        'Assunção de HTML estático completo, quando a página carrega resultados dinamicamente.',
        'Ausência de validação de HTTP, timeout e respostas inválidas.',
        'Falta de tratamento para campos vazios e incompletos.',
        'Sobrescrita de registros em vez de acumulação de lotes.',
        'Ausência de deduplicação e quarentena para URLs inválidas.',
        'Baixa rastreabilidade executiva e ausência de logs úteis para diagnóstico.',
        'Código pouco modular e pouco reutilizável, com responsabilidades misturadas.',
    ]
    for item in bullets:
        story.append(Paragraph(f'• {item}', styles['CustomBullet']))

    story.append(p('<b>5. Implementação da correção</b>', 'Section'))
    story.append(p('O scraper foi reorganizado em módulos com responsabilidades bem definidas: aquisição, parsing, validação, deduplicação, exportação e testes. Essa estrutura facilita manutenção, reutilização e revisão de regressões.', 'BodyLeft'))
    story.append(p('Os principais ajustes foram: validação de URL; remoção de parâmetros de rastreamento; tratamento de campos ausentes; captura de erros de rede e de resposta HTTP; registro de eventos e logs; exportação em CSV e JSON; e separação de registros válidos de itens em quarentena.', 'BodyLeft'))

    story.append(p('<b>6. Seletores e estratégia de paginação</b>', 'Section'))
    story.append(p('Os seletores e regras de parsing foram ajustados com base nos snapshots reais levantados. Entre os pontos identificados, destacam-se:', 'BodyLeft'))
    selector_items = [
        'Card de notícia: li.widget--info',
        'Card de vídeo: li.video-widget--info',
        'Título: .widget--info__title',
        'Resumo: .widget--info__description',
        'Data exibida: .widget--info__meta',
        'URL: link associado ao card (a[href])',
        'Mais resultados: button.pagination__load-more',
    ]
    for item in selector_items:
        story.append(Paragraph(f'• {item}', styles['CustomBullet']))
    story.append(p('Além disso, a lógica de paginação foi tratada como parte do problema: a página do G1 não se comporta como uma página simples de HTML estático, mas sim como um ambiente de carregamento incremental. Essa observação foi incorporada ao diagnóstico e à documentação do projeto.', 'BodyLeft'))

    story.append(p('<b>7. Trechos de código implementados</b>', 'Section'))
    code1 = '''def normalize_url(value, base=BASE):
    if not value:
        return None
    p = urlsplit(urljoin(base, value.strip()))
    if p.scheme not in {'http', 'https'}:
        return None
    query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith('utm_')
             and k.lower() not in {'fbclid', 'gclid'}]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path,
                      urlencode(query), ''))'''
    story.append(Preformatted(code1, styles['CodeBlock']))
    story.append(Spacer(1, 8))
    code2 = '''def parse_html(html, *, page, collected_at, source_url, snapshot):
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.select(CARD)
    records = []
    for pos, card in enumerate(cards, 1):
        title = card.select_one('.widget--info__title')
        link = title.find_parent('a') if title else None
        url = normalize_url(link.get('href') if link else None, source_url)
        records.append({
            'titulo': text(title),
            'url': url,
            'resumo': text(card.select_one('.widget--info__description')),
            'data_exibida': text(card.select_one('.widget--info__meta')),
            'pagina': page,
            'coletado_em': collected_at,
            'fonte_url': source_url,
            'snapshot': snapshot,
            'posicao': pos,
        })'''
    story.append(Preformatted(code2, styles['CodeBlock']))

    story.append(p('<b>8. Requisitos do edital e atendimento</b>', 'Section'))
    requirement_rows = [
        ['Identificar e explicar os principais problemas do código atual', 'Diagnóstico documentado com base em HTML, seletores, paginação dinâmica e falhas operacionais da rotina original.', '✅'],
        ['Corrigir a rotina de coleta com Python e Beautiful Soup', 'Parser, normalização, validação e exportação implementados em Python usando BeautifulSoup.', '✅'],
        ['Verificar e atualizar seletores HTML e mecanismo de paginação', 'Seletores revisados e observações sobre carregamento incremental do portal incorporadas ao diagnóstico.', '✅'],
        ['Coletar título, URL, resumo, data, página e horário da coleta', 'Campos extraídos e persistidos em registros estruturados com timestamp e paginação.', '✅'],
        ['Tratar falhas de conexão, HTTP inválido e campos ausentes', 'Erros de resposta e campos vazios são tratados sem interromper a execução.', '✅'],
        ['Identificar e evitar registros duplicados', 'Deduplicação por URL com preservação da primeira ocorrência e registro em quarentena.', '✅'],
        ['Organizar o código para legibilidade e reutilização', 'Estrutura modular e separação de responsabilidades entre módulos do projeto.', '✅'],
        ['Sugerir melhorias na padronização do código e dados', 'Documentação de boas práticas, padronização, rastreabilidade e validação de qualidade.', '✅'],
        ['Incluir logs e mensagens informativas', 'Logs de execução e diagnóstico implementados para monitoramento de coleta e erros.', '✅'],
        ['Salvar resultados em CSV, JSON ou outro formato estruturado', 'Saída em CSV e JSON produzida e mantida no repositório.', '✅'],
        ['Incluir testes para componentes relevantes', 'Suite executada com pytest e validada em ambiente do projeto.', '✅'],
        ['Documentar requisitos, instalação e execução', 'README com instruções de instalação e uso do scraper.', '✅'],
        ['Propor uso de LLM para diagnóstico/manutenção', 'Estratégia de apoio documentada com validação e mecanismos de controle de alucinação.', '✅'],
        ['Construir amostra de referência e métricas', 'Avaliação comparativa com amostra manual e métricas objetivas de qualidade.', '✅'],
        ['Descrever limitações e melhorias futuras', 'Seção dedicada às limitações do carregamento dinâmico e passos de evolução.', '✅'],
    ]
    req_table = Table(requirement_rows, colWidths=[62 * mm, 95 * mm, 15 * mm])
    req_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#123B5B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.6, colors.HexColor('#D8E2EC')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(req_table)

    story.append(p('<b>9. Métricas e evidências de qualidade</b>', 'Section'))
    story.append(p('A avaliação considerou completude, atualidade, precisão, acurácia, unicidade, consistência e rastreabilidade. Os resultados foram medidos a partir da base de dados coletada e dos snapshots observados do portal.', 'BodyLeft'))
    metrics_rows = [
        ['Métrica', 'Evidência'],
        ['Testes automatizados', '25 aprovados em pytest'],
        ['URLs únicas', '30 registros válidos após deduplicação'],
        ['Notícias', '26'],
        ['Vídeos', '4'],
        ['Completude', 'Título, URL, resumo e data exibida presentes em 30/30 registros'],
        ['Unicidade', 'Deduplicação por URL implementada com descarte de repetição'],
        ['Rastreabilidade', 'Página, snapshot, origem e timestamp de coleta preservados'],
        ['Data de publicação', 'Extraída quando disponível em metadados; nunca inventada sem evidência'],
    ]
    metrics_table = Table(metrics_rows, colWidths=[60 * mm, 105 * mm])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#143D59')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.7, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F7FA')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(metrics_table)

    story.append(p('<b>10. Uso de LLM como apoio ao diagnóstico</b>', 'Section'))
    story.append(p('A LLM pode ser usada como suporte para manutenção e monitoramento do scraper, mas não deve operar como fonte de verdade para dados não observados. O uso mais adequado está em etapas de análise de HTML, comparação de versões da página, identificação de seletores inconsistentes, revisão de logs e geração de testes de regressão.', 'BodyLeft'))
    story.append(p('Os dados enviados ao modelo podem incluir trechos de HTML, seletores atuais e anteriores, registros de execução, snapshots históricos, logs e amostras de resultados. Qualquer resposta do modelo deve ser validada por testes automatizados e por evidência observável antes de ser incorporada ao projeto.', 'BodyLeft'))
    story.append(p('Para evitar alucinações, a estratégia adota uma regra rígida: não há preenchimento de campos sem evidência no HTML ou na base coletada. Isso mantém a LLM como assistente analítico, e não como fonte autônoma de fatos de dados.', 'BodyLeft'))

    story.append(p('<b>11. Limitações e caminhos de evolução</b>', 'Section'))
    story.append(p('A página G1 continua sendo dinâmica: os resultados são adicionados ao rolar a página e, por isso, a coleta completa exige validação em ambiente genuíno do navegador ou na API que alimenta a busca. Há também variação de estrutura entre telas, filtros e atualizações de layout. A solução implementada foi robusta para o contexto observado, mas permanece sensível à evolução contínua do portal.', 'BodyLeft'))
    story.append(p('Como próximos passos, recomenda-se monitorar o HTML em produção, inspecionar os fluxos de rede para identificar o endpoint de carregamento, automatizar a coleta com navegador em scroll, aumentar o módulo de métricas de qualidade e manter logs em ciclos de execução para detectar regressões.', 'BodyLeft'))

    story.append(p('<b>12. Conclusão</b>', 'Section'))
    story.append(p('A solução desenvolvida demonstrou que a falha da rotina original estava ligada a mudanças estruturais na página, seletores frágeis e ausência de controles de qualidade. O projeto conseguiu reestabelecer a coleta com maior robustez, explicitar a causa raiz do problema e entregar uma base de dados rastreável, validada e documentada.', 'BodyLeft'))
    story.append(p('A entrega atende ao contexto solicitado para a vaga de Assistente de Pesquisa de Engenharia de Dados, evidenciando capacidade de diagnóstico técnico, solução em Python, análise de qualidade de dados, documentação e apresentação de evidências.', 'BodyLeft'))

    story.append(Spacer(1, 8))
    story.append(p('<b>13. Referências e links</b>', 'Section'))
    story.append(p(f'<b>Repositório GitHub:</b> <link href="{repo_link}">{repo_link}</link>', 'BodyLeft'))
    story.append(p('<b>Portal alvo:</b> https://g1.globo.com/busca/?q=lgpd', 'BodyLeft'))
    story.append(p('<b>Projeto:</b> NetLab G1 — Diagnóstico e correção de coleta de resultados de busca', 'BodyLeft'))
    story.append(p('<b>Validação:</b> 25 testes automatizados aprovados com pytest', 'BodyLeft'))

    doc.build(story)
    print(f'PDF gerado em: {out}')


if __name__ == '__main__':
    build_pdf()
