# NetLab G1 — Diagnóstico e correção de coleta de resultados de busca

## Visão geral

Este projeto investiga uma falha na rotina de coleta de resultados de busca do portal G1 para o termo "LGPD". A rotina original foi afetada por mudanças na estrutura HTML, na composição dos cards de busca e no comportamento do carregamento dinâmico da página. O código passou a retornar poucos resultados, registros vazios e campos incompletos, mesmo sem interromper a execução.

O objetivo do projeto foi diagnosticar a causa do problema, propor uma correção robusta usando Python e Beautiful Soup e documentar o processo de validação, métricas e limitações.

## Status da solução

**Status geral: funcional para coleta a partir de snapshots reais e validada por testes automatizados.**

A solução foi implementada em Python com extração por Beautiful Soup, normalização de URLs, deduplicação, tratamento de erros, exportação em JSON/CSV e testes automatizados. A base de dados coletada em lotes cumulativos está disponível em `data/coleta_multilotes/`.

## Problemas identificados na rotina original

A rotina inicial apresentava múltiplos problemas estruturais e operacionais:

1. Seletores antigos e incompatíveis com a página atual.
2. Assumiu que a página continha conteúdo estático no HTML inicial, quando a busca do G1 hoje é parcialmente dinâmica.
3. Não tratava ausência de campos, o que gerava registros incompletos.
4. Fazia sobrescrita de resultados ao invés de acumular múltiplas páginas/lotes.
5. Não realizava deduplicação de registros.
6. Não validava HTTP, timeout e tipo de resposta.
7. Não registrava logs ou diagnósticos úteis para rastreabilidade.
8. Não separava claramente aquisição, parsing, normalização e exportação.

## Diagnóstico técnico

A evidência observada diretamente no navegador confirma que a página de busca do G1 não entrega a totalidade dos resultados em uma única carga HTML estática. Ao rolar a página, o portal dispara requisições de rede e vai montando novos itens dinamicamente na interface. Isso torna o HTML inicial insuficiente para coletar o conjunto completo de resultados, porque parte do conteúdo é carregado após a primeira renderização.

Esse comportamento explica a regressão observada na rotina original: a coleta baseada em HTML bruto da primeira carga passa a retornar poucos resultados, registros vazios ou registros incompletos, sem que a rotina registre falha explícita. Em termos práticos, a solução precisa considerar não apenas seletores HTML, mas também carregamento incremental via fetch/scroll e a necessidade de sincronizar a coleta com esse ciclo dinâmico.

Os principais seletores identificados na estrutura atual dos cards são:

- Card de notícia: `li.widget--info`
- Card de vídeo: `li.video-widget--info`
- Título: `.widget--info__title`
- Resumo: `.widget--info__description`
- Data exibida: `.widget--info__meta`
- URL: via link `a[href]` associado ao card
- Mais resultados: `button.pagination__load-more`

## Correção implementada

A solução foi organizada em módulos com responsabilidades distintas:

- `scraper.py`: coleta, parsing, normalização, deduplicação, logs e exportação.
- `evaluate.py`: cálculo de métricas e qualidade dos dados.
- `tests/test_scraper.py`: testes automatizados para componentes críticos.

### Principais melhorias

- Parsing robusto com Beautiful Soup.
- Validação de URLs e remoção de parâmetros de rastreamento conhecidos.
- Deduplicação por URL, preservando a primeira ocorrência.
- Tratamento de campos ausentes com valores nulos.
- Separação entre registros válidos e registros em quarentena.
- Exportação em CSV e JSON.
- Logging para acompanhamento da execução.
- Tratamento de erros de rede, `HTTPError`, resposta sem HTML e campos ausentes.
- Suporte a paginação online em múltiplas páginas com `--pages`.
- Enriquecimento de `data_publicacao` a partir de metadados do artigo quando a busca não expõe a data com segurança.

## Requisitos e execução

### Requisitos

- Python 3.10+
- `requests`
- `beautifulsoup4`
- `pytest`

### Instalação

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

python -m pip install -r requirements.txt
```

### Execução da coleta

```bash
python scraper.py --term lgpd --pages 3 --out data/online
```

A opção `--pages` permite processar múltiplas páginas da busca, aproximando a rotina da estratégia esperada em paginação real. Quando a data de publicação não está disponível no card da busca, a rotina tenta extrair `datePublished` em metadados do artigo, sem inventar dados que não existam no HTML.

### Execução sobre snapshots locais

```bash
python scraper.py --html evidence/Busca.html evidence/lote_02.html evidence/lote_03.html --out data/coleta_multilotes
python evaluate.py --data data/coleta_multilotes/resultados.json --reference data/referencia_revisada.json --out data/metricas_multilotes.json
python -m pytest -q
```

## Base de dados produzida

Os resultados coletados e validados estão em:

- `data/coleta_multilotes/resultados.json`
- `data/coleta_multilotes/resultados.csv`
- `data/metricas_multilotes.json`

A base atual contém 30 URLs únicas, distribuídas em 26 notícias e 4 vídeos. Os registros foram deduplicados e preservam o primeiro lote em que cada item apareceu.

## Qualidade dos dados e métricas

A avaliação usa uma amostra de referência manual, comparando os registros gerados pela rotina com os resultados efetivamente exibidos na página. A análise considera:

- completude
- cobertura
- precisão
- acurácia
- unicidade
- consistência
- rastreabilidade
- atualização temporal

As métricas são calculadas pelo módulo `evaluate.py`, e a partir dos snapshots validados, os resultados observados foram:

- 30 URLs únicas
- 30 registros válidos após deduplicação
- título, URL, resumo e data exibida presentes em 30/30 registros
- `data_publicacao` permanece nula, pois a página expõe a data de atualização e não necessariamente a data de publicação do conteúdo
- 24 testes automatizados aprovados

## LLM: proposta de uso

A LLM pode ser utilizada como apoio em etapas de diagnóstico e manutenção, sem substituir a validação dos dados. A proposta é a seguinte:

### Etapa de uso

- Diagnóstico de HTML e seleção de seletores
- Comparação de versões de página
- Identificação de anomalias ou alterações estruturais
- Sugestão de testes e validação de regras

### Dados enviados ao modelo

- trechos de HTML da página de busca
- seletores atuais e anteriores
- logs de execução
- registros coletados e inconsistências detectadas
- versões diferentes da página ou snapshots históricos

### Validação das respostas

- qualquer sugestão do modelo deve ser validada por testes automatizados
- as recomendações só devem ser incorporadas se forem compatíveis com o HTML observado
- não deve haver preenchimento automático de campos sem evidência no HTML
- respostas devem ser convertidas em regras verificáveis e não aceitas como verdade implícita

### Mecanismos para evitar alucinações

- restringir o modelo a dados observáveis e registros reais
- exigir que qualquer sugestão seja justificada por trechos do HTML
- validar com testes de regressão e amostras de referência
- manter a LLM fora do fluxo de produção de dados, apenas como módulo de análise e suporte

## Limitações e próximos passos

- A paginação online real exige validação em ambiente genuíno de navegador, porque a página do G1 carrega novos resultados dinamicamente ao rolar e não apenas em uma única resposta HTML.
- O enriquecimento de data de publicação exige leitura de metadados do artigo e validação em fonte específica, porque o card de busca pode expor apenas data exibida e não necessariamente a data de publicação oficial.
- A página G1 pode continuar evoluindo; a rotina deve ser revisada periodicamente.
- A coleta ao vivo ainda deve ser monitorada com logs, fingerprints de HTML, inspeção de rede e validação de continuidade.
- Em caso de necessidade de cobertura completa, a abordagem mais robusta é seguir o comportamento real de carregamento com automação de navegador ou pelo consumo da API de busca que alimenta o resultado em tempo real.

## Documentação de evidências

Arquivos relevantes do projeto:

- `evidence/Busca.html`
- `evidence/lote_02.html`
- `evidence/lote_03.html`
- `evidence/initial.html`
- `docs/llm.md`
- `data/metricas_multilotes.json`

## Conclusão

A solução corrige grande parte dos problemas observados na rotina original, melhora a robustez da coleta e fornece uma base reproduzível para monitoramento e refinamento contínuo. A principal pendência que permanece é a validação do mecanismo de paginação ao vivo da página G1 em produção, que depende de contexto externo e não pode ser concluída apenas com HTML estático.

## Repositório

- GitHub: https://github.com/fregulha/netlab-g1-webscraping.git
