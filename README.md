# Busca G1 / LGPD — diagnóstico e protótipo auditável

**STATUS: PRELIMINAR. Não está pronto para submissão.**

Há 17 testes automatizados aprovados. Não há ainda base de notícias efetivamente
coletada, amostra manual, métricas empíricas ou validação de paginação. Os arquivos
vazios em `data/diagnostico` documentam a falha diagnosticada, não uma coleta bem-sucedida.

## Diagnóstico com evidências

O código da imagem usa `div.resultado`, `div.titulo`, `p.resumo` e `span.data`.
No HTML HTTP obtido em 17/09/2026 (`evidence/initial.html`), o elemento
`.results__content.all-search-results` está vazio. O componente JS referenciado
pelo próprio HTML (`evidence/component.js`, versão 0.2.9) cria a lista dinamicamente.
Isso demonstra que requests + mudança de seletores, isoladamente, não bastam para
esta resposta observada. Sem snapshot histórico, não se pode datar a mudança nem
atribuir a ela todos os sintomas relatados pela equipe.

O código-fonte do componente indica os seguintes seletores, ainda pendentes de
validação no DOM renderizado:

| Campo | Seletor / regra |
|---|---|
| Card de notícia | `li.widget--info` |
| Título | `.widget--info__title` |
| URL | ancestral `a[href]` do título |
| Resumo | `.widget--info__description` |
| Data exibida | `.widget--info__meta` |
| Mais resultados | `button.pagination__load-more` |

O JS usa `_source.modified` na data exibida. Por isso `data_publicacao` permanece
nula; `data_exibida` e sua semântica são preservadas. Uma extensão deve visitar a
notícia e validar `datePublished` em JSON-LD/metadados, registrando a fonte específica
para esse enriquecimento. Não inferir publicação da URL nem de uma data relativa.

### Problemas certos no código original

1. `resultados = dados_pagina` sobrescreve as páginas anteriores; acumular com `extend`.
2. `.find(...).get_text()` e `.find('a').get(...)` falham se o elemento não existe.
3. Falta timeout, validação de HTTP, política limitada de retry e validação do conteúdo.
4. `range(5)` envia 0–4; a origem da paginação não foi verificada. Não basta mudar para 1–5.
5. Nenhuma deduplicação e nenhum diagnóstico de páginas repetidas ou vazias.
6. CSV sem `encoding`/`newline`, horário sem fuso e ausência de proveniência.
7. Execução ao importar o módulo; falta `if __name__ == '__main__'`.
8. Pausa fixa de 0,2 s sem considerar 429/Retry-After ou limites do serviço.

## Decisões implementadas

Separação de aquisição, parsing Beautiful Soup, normalização, deduplicação,
quarentena e exportação. URL canônica remove somente parâmetros conhecidos de
tracking; query de conteúdo é preservada. Duplicatas conservam a primeira ocorrência.
Registro sem URL vai para quarentena; campo opcional ausente vira `null`.
Snapshots UTF-8 e hash SHA-256 ligam cada registro ao HTML efetivamente analisado.
O horário UTC é o da extração: para HTML enviado, não equivale à captura original.

`pagina` é o número do lote/snapshot fornecido. Não representa uma página HTTP
validada. Snapshots cumulativos devem ser entregues na ordem observada; duplicatas
são eliminadas e cada notícia mantém seu primeiro lote de observação.

Retries limitados para GET em 429/5xx; erros de conexão/status/tipo são registrados
sem perder resultados anteriores. Saídas: 0 = registros em todos os lotes fornecidos;
2 = nenhum registro válido; 3 = execução parcial. Código 0 não prova cobertura online.

## Instalação e execução (Python 3.12)

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Diagnóstico da resposta HTTP atual (não navega automaticamente entre lotes):

```bash
python scraper.py --term lgpd --out data/online
```

Reprodução offline da evidência incluída — saída esperada 2, zero cards:

```bash
python scraper.py --html evidence/initial.html --out data/reproducao
```

Extração de HTML renderizado fornecido pelo usuário, após sua obtenção:

```bash
python scraper.py --html captura_01.html captura_02.html --out data/coleta
python evaluate.py --data data/coleta/resultados.json --reference data/referencia_manual.json --out data/metricas.json
```

## Paginação: diagnóstico e implementação pendente

O JS mostra `pagination.nextPage`, `scrollCount`, carregamento por interseção e
botão “Veja mais”. A interação ao vivo foi bloqueada pela política de segurança do
navegador desta sessão. Não foi validado endpoint, cursor, tamanho de lote nem uso
de `page` na URL. Não afirmar que o mecanismo antigo funciona.

Para terminar, observar uma interação real, comparar quantidade e URLs antes/depois,
e salvar HTML e horário de cada lote. A aquisição deverá fornecer esse HTML ao
mesmo parser. Parar no fim comprovado, limite configurado, erro ou ausência de novos
IDs, registrando a causa; um timeout não equivale a fim da busca. Limitar ritmo e
volume, respeitar termos e robots aplicáveis, não contornar barreiras de acesso.

## Avaliação de qualidade

Escolher manualmente TODOS os cards de notícia do primeiro lote renderizado, antes
de abrir a saída do parser. Transcrever título, URL, resumo e data exatamente como
exibidos, usando `null` para ausências. Salvar como `data/referencia_manual.json`,
com `pagina: 1`, e manter screenshot, HTML e horário. Uma segunda pessoa deve revisar.
A referência não deve ser derivada do parser. Incluir depois lotes com ausências e
repetições para ampliar a avaliação; o primeiro lote não é amostra aleatória do portal.

| Dimensão | Métrica / interpretação |
|---|---|
| Completude | Valores presentes / registros, por campo; ausência legítima documentada |
| Cobertura | URLs da referência encontradas / URLs da referência |
| Precisão | URLs coletadas que pertencem à referência / URLs coletadas no MESMO escopo |
| Acurácia | Campos iguais / campos comparáveis, por campo; fidelidade à página, não veracidade jornalística |
| Unicidade | URLs distintas / registros, antes e depois da deduplicação |
| Consistência | Proporção com URL HTTP(S), página inteira positiva e timestamp com fuso |
| Rastreabilidade | Proporção com fonte, snapshot, hash e horário; verificar hashes em auditoria |
| Atualidade | Defasagem captura–extração e concordância com página contemporânea; notícia antiga não é dado desatualizado |

`evaluate.py` calcula métricas do escopo representado na referência. Denominador
zero retorna `null`, nunca 100%. Atualidade fica `null` até haver observação temporal
independente. Rastreabilidade calculada é presença de metadados; não valida o arquivo
fisicamente. Precisão só é interpretável se a referência enumera todo o escopo.

**Resultados obtidos:** 17 testes sintéticos aprovados; 0 cards de notícia extraídos
do HTML inicial. Métricas reais: não avaliadas. Não há evidência para alegar
precisão/cobertura de 100%, nem para dizer que o G1 não tem resultados para LGPD.

## Proposta LLM

Ver `docs/llm.md`. A LLM sugere manutenção fora da rotina de produção. Não escreve
registros de notícia nem preenche campos ausentes. Alterações exigem validação e revisão.

## Limitações e próximos passos obrigatórios

- Adquirir e validar DOM renderizado e paginação atual; a aquisição automática ainda não foi restabelecida.
- Parser cobre cards `widget--info`; vídeo, live e navegação precisam de parsers próprios e avaliação.
- Publicação não enriquecida; resumo pode estar truncado na busca.
- Adicionar captura de consentimento/estado de carregamento como diagnóstico se necessário.
- Construir referência independente, rodar métricas e incluir a base efetivamente obtida.
- Validar falha de um lote seguida de sucesso em teste de integração do orquestrador.
- Verificar hash contra arquivo em avaliação, datas futuras e defasagem temporal.
- Antes da entrega: revisar nome completo, publicar em repositório Git e inserir seu link no PDF.

## Git

O ZIP contém um repositório local com commit inicial; não foi publicado em conta externa.
Também é possível criar um repositório vazio no GitHub e enviar os arquivos, preservando
`evidence`, `tests`, `data` e `docs`. Nunca incluir senhas, cookies ou tokens.

## Fontes técnicas e evidências

- Página-alvo: https://g1.globo.com/busca/?q=lgpd
- Componente referenciado pela página: caminho completo no `evidence/manifest.json`.
- Beautiful Soup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Requests: https://requests.readthedocs.io/en/latest/user/quickstart/
- urllib3 Retry: https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html

Os links de documentação são referências para consulta; o diagnóstico está ancorado
nos arquivos locais obtidos do portal e na imagem fornecida, não em suposições de LLM.
