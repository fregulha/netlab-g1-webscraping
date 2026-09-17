"""Gera o relatório PDF a partir das evidências locais; não inventa validação online."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
TARGET = OUT / '2etapa - FERNANDA FREGULHA.pdf'
fontdir = Path('C:/Windows/Fonts')
for name, file in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Mono','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(fontdir / file)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Body', boldItalic='Bold')
NAVY=colors.HexColor('#143044'); TEAL=colors.HexColor('#087E83'); GRAY=colors.HexColor('#506270')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Text', fontName='Body', fontSize=10, leading=14.8, textColor=NAVY, spaceAfter=9))
styles.add(ParagraphStyle(name='SmallText', parent=styles['Text'], fontSize=8.3, leading=11.4, spaceAfter=5))
styles.add(ParagraphStyle(name='TitleX', fontName='Bold', fontSize=28, leading=33, textColor=NAVY, spaceAfter=20))
styles.add(ParagraphStyle(name='SectionX', fontName='Bold', fontSize=20, leading=25, textColor=NAVY, spaceAfter=17))
styles.add(ParagraphStyle(name='SubX', fontName='Bold', fontSize=12, leading=16, textColor=TEAL, spaceBefore=9, spaceAfter=8))
styles.add(ParagraphStyle(name='CodeX', fontName='Mono', fontSize=8, leading=11.2, textColor=NAVY, backColor=colors.HexColor('#F1F5F7'), borderPadding=10, spaceBefore=5, spaceAfter=12))
story=[]
def p(t, small=False): story.append(Paragraph(t,styles['SmallText' if small else 'Text']))
def h(t): story.append(Paragraph(t,styles['SubX']))
def page(n,t):
    if story: story.append(PageBreak())
    p(f'RELATÓRIO TÉCNICO  /  {n:02d}',True)
    story.append(Paragraph(t,styles['SectionX']))
def code(t): story.append(Preformatted(t.strip(),styles['CodeX']))
def table(headers, rows, widths):
    data=[[Paragraph(escape(str(x)),styles['SmallText']) for x in headers]]
    data += [[Paragraph(str(x),styles['SmallText']) for x in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DDEDEF')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),1,TEAL),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#D7E0E5'))]))
    story.append(t); story.append(Spacer(1,10))

page(1,'Busca G1: diagnóstico e correção')
story.append(Spacer(1,14))
story.append(Paragraph('FERNANDA<br/>FREGULHA',styles['TitleX']))
p('<b>Processo seletivo NetLab UFRJ | 2ª etapa</b><br/>Termo pesquisado: LGPD • Verificação: 17 de setembro de 2026')
p('Página-alvo: <link href="https://g1.globo.com/busca/?q=lgpd" color="#087E83">g1.globo.com/busca/?q=lgpd</link>')
h('Resultado demonstrado')
p('A extração com Python e Beautiful Soup foi validada em três HTMLs renderizados fornecidos. Foram recuperados <b>30 resultados únicos</b> (26 cards de notícia e 4 de vídeo), com título, URL, resumo e data exibida. Os <b>24 testes automatizados</b> passaram. Os snapshots contêm 10, 20 e 30 cards cumulativos; 30 ocorrências repetidas foram removidas.')
h('Limite da conclusão')
p('<b>A coleta automática online ainda não está restabelecida de ponta a ponta.</b> A resposta HTTP observada não contém os cards renderizados. A navegação por “Veja mais” não pôde ser testada porque não há navegador conectado nesta sessão. Os resultados abaixo comprovam o parser no snapshot, não a cobertura total da busca.')
table(['Indicador','Evidência'],[
('Base extraída','30 registros únicos; 3 snapshots cumulativos; 30 repetições removidas'),
('Campos de publicação','0/30 com data de publicação comprovada; campo preservado como null'),
('Referência','10 registros revisados pelo assistente; validação humana independente pendente'),
('Repositório','Git local disponível no pacote; publicação remota depende de conexão ao GitHub')],[140,365])
p('O PDF inclui o anexo netlab-g1-entrega.zip, também disponibilizado separadamente, com código, README, dados, testes e evidências. As pendências são explicitadas para que resultados parciais não sejam apresentados como validação integral.',True)

page(2,'Diagnóstico sustentado por evidências')
p('A investigação comparou o código da imagem, o HTML HTTP inicial, um componente JavaScript público referenciado pela página e o HTML renderizado já incluído no projeto. Não há snapshot histórico que permita determinar quando a estrutura mudou.')
table(['Problema no original','Efeito e correção'],[
('resultados = dados_pagina','Sobrescreve a coleta anterior a cada iteração. Acumular com extend e deduplicar ao final.'),
('div.resultado / div.titulo / p.resumo / span.data','O seletor de card original encontra 0 elementos no HTML renderizado. Os seletores verificados são apresentados na página seguinte.'),
('find(...).get_text() sem guarda','Elemento ausente provoca AttributeError. Ler texto apenas se o nó existir; ausência opcional vira null.'),
('requests.get sem timeout e validação','Pode travar ou analisar uma página de erro como resultado. Usar sessão, timeout, raise_for_status e Content-Type.'),
('range(5), com page=0 até 4','Pressupõe uma paginação não demonstrada. Alterar para 1 até 5, sozinho, não valida o mecanismo.'),
('Sem identidade ou controle de repetição','Duplicatas podem inflar o volume. Canonizar URLs e preservar a primeira ocorrência.'),
('CSV e horário sem padronização','Definir UTF-8, newline, horário UTC com fuso e metadados de proveniência.'),
('Execução no import e pouca observabilidade','Usar funções reutilizáveis, guarda __main__, logs e status de execução parcial.')],[180,325])
h('Três observações distintas')
p('<b>HTML inicial:</b> 0 cards; contêiner .results__content.all-search-results vazio. <b>Componente JS 0.2.9:</b> constrói cards e controla carregamento incremental. <b>HTML renderizado Busca.html:</b> 10 cards com a estrutura atual observada. Beautiful Soup interpreta HTML, mas não executa JavaScript.')
p('A nova consulta em data/verificacao_http também retornou 0 cards. Isso não significa que a busca não tenha notícias. Sem comparação histórica, mudança de estrutura é uma explicação compatível com a evidência atual, não uma cronologia comprovada.',True)

page(3,'Seletores, datas e paginação')
table(['Elemento','Seletor / regra verificada'],[
('Card de notícia','li.widget--info'),('Card de vídeo','li.video-widget--info'),
('Título','.widget--info__title'),('URL','Ancestral a[href] do título; fallback no contêiner de texto'),
('Resumo','.widget--info__description'),('Data exibida','.widget--info__meta'),
('Próximo lote','button.pagination__load-more; texto “Veja mais”')],[133,372])
p('Nos campos de vídeo, usar o prefixo video-widget--info. Os seletores foram conferidos no arquivo evidence/Busca.html e no componente JavaScript. Outros tipos de resultado exigem parsers e validação próprios.')
h('Data exibida não equivale a publicação')
p('O componente de notícia utiliza <b>_source.modified</b> ao formatar a data. Portanto, o parser preserva data_exibida e sua semântica; data_publicacao permanece null. No vídeo, a semântica não foi confirmada. Datas relativas, como “há 2 dias”, não são convertidas sem uma captura temporal conhecida.')
p('Extensão proposta: visitar a notícia e extrair datePublished de JSON-LD ou metadados explícitos, diferenciando dateModified, validando fuso e formato e guardando o URL e o hash da evidência adicional. Não derivar a publicação da URL.')
h('Paginação observada no código; interação pendente')
p('O JS referencia pagination.nextPage, scrollCount e IntersectionObserver. Os novos arquivos têm títulos “Página 2” e “Página 3”, com 20 e 30 cards: o prefixo de URLs do lote anterior é preservado. Isso comprova acumulação nos snapshots, mas não um endpoint, cursor ou funcionamento de page na URL. O comentário de origem dos arquivos mantém apenas ?q=lgpd.')
p('Para concluir a aquisição: instrumentar a interação ao vivo, capturar HTML e horário de cada lote e fornecer o DOM ao parser. Parar em fim explícito, limite, falha ou ausência de novos IDs, registrando o motivo. Os três snapshots ainda contêm “Veja mais”; nenhum comprova esgotamento. Timeout não deve ser classificado como fim da busca.')
p('<b>Implementação atual:</b> recebe snapshots ordenados por --html. pagina representa o lote de observação; não uma página HTTP validada. Uma aquisição por navegador pode ser acoplada sem substituir a extração Beautiful Soup.',True)

page(4,'Implementação e contrato dos dados')
p('O código separa aquisição, interpretação, normalização, deduplicação e exportação. A CLI registra cada lote, mantém snapshots e salva resultados mesmo quando há falha em outro lote.')
table(['Componente','Responsabilidade'],[
('session / fetch_html','Sessão Requests; timeout (10, 30); até 2 retries para 429/5xx; backoff e Retry-After; rejeição de HTTP inválido e conteúdo não HTML.'),
('parse_html','Beautiful Soup; seletores explícitos; espaços normalizados; null para ausência; sem geração de conteúdo.'),
('normalize_url','Resolve links relativos; remove fragmento e rastreadores conhecidos; mantém parâmetros de conteúdo.'),
('deduplicate','Chave URL normalizada; primeira ocorrência mantida; registro sem URL enviado à quarentena.'),
('save_output / main','JSON, CSV UTF-8 com BOM, quarentena, eventos e logs; acumulação com extend; execução somente sob __main__.'),
('evaluate / verify_snapshots','Calcula métricas no escopo da referência e verifica SHA-256 dos snapshots locais.')],[153,352])
p('Links measures.globo.com/v1/click são decodificados pelo parâmetro u, sem visitar o rastreador. Nessa regra, só destinos HTTP(S) no host g1.globo.com são aceitos. Assim, diferentes IDs de rastreamento não geram notícias distintas.')
h('Esquema de saída')
p('<b>Conteúdo:</b> titulo, url, resumo, data_publicacao, data_exibida e semantica_data_exibida. <b>Origem:</b> pagina, posicao, fonte_url, snapshot e sha256. <b>Execução:</b> coletado_em e avisos.')
p('coletado_em usa ISO 8601 em UTC e registra a extração. Para um arquivo fornecido, esse valor não é o horário original da captura. O hash refere-se ao texto UTF-8 analisado; o manifesto também registra hashes dos bytes originais.')
h('Estados observáveis')
p('Código 0: houve registros em todos os lotes fornecidos. Código 2: nenhum registro válido. Código 3: execução parcial. Código 0 não certifica cobertura online. Erros de conexão, HTTP, leitura e tipo de resposta entram no log e nos eventos de execução.')

page(5,'Trechos centrais da correção')
p('Os trechos abaixo correspondem à lógica do projeto. O código integral e os testes estão no pacote anexo; a execução é feita pela CLI descrita na página 9.')
code('''# Parser: ausência não interrompe a extração
def text(node):
    return ' '.join(node.get_text(' ', strip=True).split()) \\
        if node else None

soup = BeautifulSoup(html, 'html.parser')
cards = soup.select('li.widget--info, li.video-widget--info')
for pos, card in enumerate(cards, 1):
    prefix = ('video-widget--info'
              if 'video-widget--info' in card.get('class', [])
              else 'widget--info')
    title = card.select_one(f'.{prefix}__title')
    link = title.find_parent('a') if title else None
    if link is None:
        link = card.select_one(
            f'.{prefix}__text-container a[href]')
    url = normalize_url(link.get('href') if link else None,
                        source_url)
    # O registro inclui texto, fonte, lote, hash e horário.
    # data_publicacao=None: o card não comprova publicação.''')
code('''# Acumulação de lotes: não sobrescrever resultados anteriores
records.extend(rows)

def deduplicate(records):
    unique, quarantine, seen = [], [], set()
    duplicates = 0
    for row in records:
        if not row['url']:
            quarantine.append(row)
        elif row['url'] in seen:
            duplicates += 1
        else:
            seen.add(row['url'])
            unique.append(row)
    return unique, quarantine, duplicates''')
p('As saídas estruturadas preservam campos nulos. Melhorias recomendadas: anotações de tipo, dataclass ou schema versionado; lint e formatação automatizados; configuração de seletores; lock completo de dependências e testes de URL malformada e de falha por card.',True)

page(6,'Referência e desenho da avaliação')
p('A referência local contém todos os <b>10 cards do primeiro lote</b> de evidence/Busca.html. O README original descreve sua transcrição após inspeção do HTML, fora do parser, com revisão pelo assistente. <b>Não há comprovação de revisão manual humana independente.</b> Portanto, esta é uma referência provisória, e não o cumprimento integral desse requisito do edital.')
p('A comparação usa URLs normalizadas como chave. Título, resumo e data exibida são comparados exatamente após normalização de espaços. Precisão é interpretável apenas porque a referência enumera o mesmo lote inteiro; não representa toda a busca ou o portal.')
ref=json.loads((ROOT/'data/referencia_revisada.json').read_text(encoding='utf-8'))
table(['Pos.','Título presente na referência','Data exibida'],[(str(r['posicao']),escape(r['titulo']),escape(r['data_exibida'])) for r in ref],[35,360,110])
p('Os textos acima são transcrições da evidência local, não verificação da veracidade jornalística. URLs completas, resumos e posições constam de data/referencia_revisada.json; o lote contém também conteúdo publicitário e vídeo, preservados por pertencerem ao resultado da busca.',True)
h('Como completar a referência manual')
p('Uma pessoa deve conferir os 10 cards no HTML/página, sem consultar previamente a saída do parser, transcrever os campos e registrar ausências, data de captura e responsável. Uma segunda revisão reduz erros. Depois, incluir outros lotes, cards incompletos e repetições e recalcular as métricas.',True)

page(7,'Qualidade: métricas e resultados')
p('Escopo da comparação: 10 registros da referência e os 10 primeiros resultados da base de 30 URLs únicas. Métricas em data/metricas_multilotes.json. Os 20 registros adicionais não integram a referência. Denominador zero produz null, nunca 100%.')
table(['Dimensão e definição','Resultado','Interpretação'],[
('Cobertura: URLs da referência encontradas / URLs de referência','10/10 = 100%','Cobertura do snapshot, não da busca completa.'),
('Precisão: URLs coletadas pertencentes à referência / URLs únicas coletadas','10/10 = 100%','Pertencimento ao mesmo lote.'),
('Completude: valores presentes / registros, por campo','10/10 = 100%','Título, URL, resumo e data exibida.'),
('Completude de publicação','0/10 = 0%','Publicação não comprovada no card; sem preenchimento inferido.'),
('Acurácia: campos iguais / campos comparáveis','10/10 por campo','Título, resumo e data exibida; 100% de concordância com referência provisória.'),
('Acurácia de publicação','0 comparáveis','Não avaliável; não confundir com 0% de acurácia.'),
('Unicidade: URLs distintas / registros','10/10 = 100%','0 duplicados observados; remoção também testada com fixtures.'),
('Consistência: URL HTTP(S), lote positivo e timestamp com fuso','10/10 = 100%','Validação estrutural básica, não completa do schema.'),
('Rastreabilidade: fonte, snapshot, hash e horário presentes','10/10 = 100%','Presença de metadados da extração.'),
('Integridade: hashes conferidos / registros','30/30 = 100%','Base completa: arquivos locais correspondem ao texto analisado.'),
('Atualidade: defasagem captura-extração e conferência contemporânea','Não mensurada','Sem horário independente de captura; não é possível calcular a defasagem.')],[252,92,161])
p('<b>Base completa:</b> completude de título, URL, resumo e data exibida = 30/30; publicação = 0/30; unicidade bruta = 30/60 (50%) e após deduplicação = 30/30 (100%). Integridade conferida para os 30 registros; acurácia restrita aos 10 da referência.',True)
p('<b>Validade:</b> referência pequena e sem revisão humana independente. Não extrapolar concordância para os outros 20 registros. Atualidade permanece não mensurada.',True)

page(8,'Testes e proposta de uso de LLM')
h('Verificação automatizada executada')
p('<b>24 passed in 0.30s</b>, Python 3.14.4, pytest 9.1.1. Evidência: evidence/tests_multilotes.txt. Os testes incluem parsing e semântica de datas; campos ausentes; quarentena; HTML vazio; múltiplos lotes; deduplicação; URLs de tracking; Unicode; timeout, conexão, HTTP e Content-Type; métricas; vídeo e regressão dos snapshots reais.')
p('Os testes acrescentados verificam adulteração de snapshot, preservação de dados após falha e progressão real de 10/20/30 cards com 30 repetições removidas. pytest.ini limita a descoberta à pasta tests, evitando interpretar logs .txt como testes. Não foi executada integração da paginação ao vivo.')
h('LLM como apoio à manutenção, fora da coleta')
p('Acionar em homologação quando houver queda de cards ou de completude, seletor sem correspondência ou repetição anormal. Fornecer trechos sanitizados do HTML antigo e novo, seletores, contagens, logs sem credenciais e hashes. A função do modelo é propor seletores e testes e explicar diferenças estruturais.')
p('Exigir JSON com selector, evidence_excerpt, snapshot_sha256, reason e confidence, permitindo abstenção. Conteúdo da página é dado não confiável: instruções nele contidas não devem alterar a tarefa. Não fornecer cookies, tokens ou dados pessoais desnecessários.')
code('''# Proposta conceitual; não há integração com API implementada.
proposal = llm.propose(html_old, html_new, selectors, logs)
validate_json_schema(proposal)
assert proposal.snapshot_sha256 == sha256(snapshot)
assert proposal.evidence_excerpt in snapshot
compile_css(proposal.selector)
candidate = parse_frozen_snapshots(proposal.selector)
metrics = compare(candidate, human_reviewed_reference)
assert metrics.precision >= approved_baseline.precision
assert metrics.recall >= approved_baseline.recall
run_regression_tests()
open_reviewable_patch(proposal, metrics)''')
p('O trecho acima é pseudocódigo. Um revisor aprova o patch antes da adoção. Guardar prompt, versão do modelo, resposta, métricas e decisão; manter rollback. Confiança declarada pelo modelo não substitui validação. A linha de base atual ainda depende da revisão humana.')
p('<b>Barreira contra invenção:</b> a LLM não escreve títulos, resumos, URLs ou datas; não preenche lacunas nem converte modified em published. A extração continua determinística. Sem evidência, manter null, quarentena ou alerta.',True)

page(9,'Instalação, execução e arquivos')
p('Ambiente verificado: Python 3.14.4 no Windows. Dependências fixadas: requests 2.34.2, beautifulsoup4 4.15.0 e pytest 9.1.1. Executar os comandos na pasta netlab-g1. O gerador deste PDF usa ReportLab, separadamente das dependências do scraper.')
code('''python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q

# Reproduzir os snapshots (comando em uma linha)
python scraper.py --html evidence/Busca.html \\
  evidence/lote_02.html evidence/lote_03.html --out data/repro
python evaluate.py --data data/repro/resultados.json \\
  --reference data/referencia_revisada.json \\
  --out data/repro/metricas.json

# Consultar HTML HTTP; zero cards foi o resultado observado
python scraper.py --term lgpd --out data/online''')
p('As barras invertidas ao fim das linhas indicam continuação em shells Unix. No PowerShell, execute cada comando em uma única linha. Linux/macOS: ativar com source .venv/bin/activate.',True)
table(['Arquivo / pasta','Conteúdo'],[
('scraper.py / evaluate.py','Rotina modular de extração e avaliador reproduzível.'),
('tests/test_scraper.py / pytest.ini','24 casos executados, incluindo parametrizações; descoberta restrita à pasta tests.'),
('data/coleta_multilotes/','Base atual: 30 registros em JSON e CSV; HTMLs, log, eventos e quarentena.'),
('data/referencia_revisada.json / data/metricas_multilotes.json','Referência provisória de 10 registros e métricas de comparação.'),
('evidence/','HTML inicial e renderizado, componente JS, manifesto, testes e conferência de hashes.'),
('data/verificacao_http/','Nova observação HTTP sem cards; não substituir a base extraída por esta saída vazia.'),
('docs/llm.md / README.md','Estratégia de LLM, diagnóstico e instruções de reprodução.')],[229,276])
p('<b>Git:</b> o pacote contém o histórico em netlab-g1.bundle. Para restaurá-lo: git clone netlab-g1.bundle netlab-g1-restaurado. A publicação externa ainda exige conectar o GitHub; não há URL remota verificada para informar.',True)

page(10,'Limitações, próximos passos e fontes')
h('Condições para considerar a entrega completa')
table(['Pendência','Critério de aceite proposto'],[
('Aquisição e paginação automáticas','Executar em pelo menos dois lotes reais; registrar IDs novos, horário, snapshots e condição de parada. Comparar cada lote com observação independente.'),
('Referência humana','Revisar os 10 cards com responsável e data; corrigir divergências e repetir a avaliação.'),
('Publicação e atualidade','Validar datePublished onde disponível; separar captura de extração; medir defasagem e confrontar com página contemporânea.'),
('Disponibilização Git','Publicar o pacote em repositório acessível à banca e inserir o link. Não há publicação remota comprovada nesta versão.')],[154,351])
p('Outras melhorias: retomar coletas interrompidas; limites de ritmo e volume configuráveis; cache; alertas por queda de completude; validação de schema; deduplicação entre execuções; testes de formatos adicionais e de estado de carregamento. Respeitar limites e condições de acesso do portal sem contornar bloqueios.')
h('Fontes e trilha de auditoria')
p('1. Código original: imagem fornecida no enunciado.<br/>2. Página-alvo: <link href="https://g1.globo.com/busca/?q=lgpd">https://g1.globo.com/busca/?q=lgpd</link>.<br/>3. Evidências locais: evidence/initial.html, evidence/Busca.html e evidence/component.js. O URL completo e hashes constam de evidence/manifest.json.<br/>4. Verificação desta revisão: evidence/verificacao.json, evidence/tests_verificacao.txt e data/verificacao_http/.<br/>5. Dados e avaliação: data/coleta/resultados.json e data/metricas.json.',True)
p('Documentação técnica para consulta: <link href="https://www.crummy.com/software/BeautifulSoup/bs4/doc/">Beautiful Soup</link>; <link href="https://requests.readthedocs.io/en/latest/user/quickstart/">Requests</link>; <link href="https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html">urllib3 Retry</link>. O diagnóstico desta entrega se baseia nas evidências locais e na nova consulta HTTP; estes links não substituem os testes.',True)
h('Identificação da evidência principal')
p('SHA-256 dos bytes de evidence/Busca.html:',True)
code('852efdc38000c52573042554f43e49de9a84d1097a50e0822fbbffb599dff589')
p('Os três arquivos originais do manifesto tiveram seus hashes conferidos e coincidentes nesta revisão. Um hash demonstra integridade em relação ao arquivo registrado; não certifica autoria, horário original de captura ou autenticidade editorial.',True)
p('<b>Transparência de escopo:</b> este relatório documenta uma correção de parser comprovada em snapshot e uma proposta para completar a aquisição. Não apresenta coleta online, referência humana, atualidade ou repositório público como etapas já concluídas.',True)

page(11,'Novas evidências: três lotes cumulativos')
p('Esta revisão incorpora os três arquivos indicados pela usuária no Desktop. Busca.html é idêntico, pelo SHA-256, ao snapshot inicial do projeto. Os outros dois arquivos acrescentam resultados e permitem testar a deduplicação com dados reais.')
table(['Arquivo fornecido','Título / cards','Novas URLs'],[
('Busca.html','Busca / 10 cards','10'),
('Resultado da busca por lgpd.html','Página 2 / 20 cards','10'),
('Resultado da busca por lgpd _ Página 3.html','Página 3 / 30 cards','10')],[254,165,86])
h('O que foi demonstrado')
p('A lista de URLs do primeiro snapshot é o prefixo exato do segundo; a lista do segundo é o prefixo exato do terceiro. Logo, somar os arquivos sem deduplicação contaria 60 ocorrências para apenas 30 URLs distintas. O parser preserva o primeiro lote em que cada URL aparece: 10 registros por lote.')
p('A base final contém 26 cards de notícia e 4 de vídeo. A unicidade passou de 50% nas ocorrências brutas para 100% na saída. Não houve registro enviado à quarentena. Todos os 30 registros têm título, URL, resumo e data exibida; nenhum tem publicação comprovada no card.')
h('O que continua sem comprovação')
p('Os arquivos salvos não demonstram a requisição que produziu os lotes nem a condição de término. O botão “Veja mais” está nos três HTMLs. O título “Página 3” não valida um parâmetro HTTP page=3. O horário original das capturas é desconhecido e não foi substituído pela data de modificação do arquivo.')
p('A referência de acurácia continua limitada aos 10 primeiros cards. Não foi criada uma referência dos outros 20 a partir da própria saída do parser: isso produziria uma comparação circular. Revisão humana independente permanece pendente.')
h('Arquivos para reproduzir esta revisão')
p('Novos snapshots: evidence/lote_02.html e evidence/lote_03.html.<br/>Base: data/coleta_multilotes/resultados.json e resultados.csv.<br/>Comparação com referência: data/metricas_multilotes.json.<br/>Auditoria dos três HTMLs e hashes: data/auditoria_multilotes.json.<br/>Teste de regressão: test_real_cumulative_snapshots.<br/>Saída dos 24 testes: evidence/tests_multilotes.txt.',True)
code('python docs/avaliar_multilotes.py')
p('A execução anterior de um lote foi preservada em data/coleta/ para rastreabilidade. Para a entrega atual, utilizar a base de 30 registros em data/coleta_multilotes/.',True)

def footer(c,doc):
    w,h=doc.pagesize
    c.setStrokeColor(TEAL); c.setLineWidth(2); c.line(45,h-35,w-45,h-35)
    c.setStrokeColor(colors.HexColor('#D7E0E5')); c.setLineWidth(.4); c.line(45,40,w-45,40)
    c.setFont('Body',8); c.setFillColor(GRAY)
    c.drawString(45,27,'FERNANDA FREGULHA  |  NetLab UFRJ  |  17.09.2026')
    c.drawRightString(w-45,27,str(doc.page))

doc=SimpleDocTemplate(str(TARGET),pagesize=(595.28,841.89),rightMargin=45,leftMargin=45,topMargin=52,bottomMargin=54,title='2etapa - FERNANDA FREGULHA',author='Fernanda Fregulha',subject='Diagnóstico e extração auditável da busca G1 por LGPD')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(TARGET)
