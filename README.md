# NetLab G1 — Diagnóstico e correção de coleta de resultados de busca

## Visão geral

Este projeto foi desenvolvido para investigar e corrigir uma falha na rotina de coleta de resultados de busca do portal G1 para o termo “LGPD”. A rotina original deixou de produzir resultados confiáveis após mudanças na estrutura HTML, no comportamento da página e na forma como os cards de busca são carregados.

O objetivo foi identificar a causa raiz do problema, propor uma correção robusta em Python com Beautiful Soup, validar a solução com testes automatizados e documentar claramente os requisitos, a metodologia e os resultados alcançados.

## Status da solução

Status geral: concluído, validado e documentado.

A solução implementada oferece:

- coleta robusta de resultados a partir de HTML real e snapshots
- normalização de URLs e remoção de parâmetros de rastreamento
- deduplicação de registros
- tratamento de falhas de rede e campos ausentes
- exportação em CSV e JSON
- evidências de qualidade e métricas de validação
- documentação técnica e instruções para execução

## Repositório

- GitHub: https://github.com/fregulha/netlab-g1-webscraping.git

## Problema identificado

A rotina original apresentava falhas estruturais e operacionais, como:

1. seletores HTML antigos e incompatíveis com a página atual
2. uso de uma premissa de conteúdo estático, embora a busca do G1 carregue resultados de forma incremental
3. ausência de validação de HTTP, timeout e tipos de resposta
4. registros vazios ou incompletos não tratados
5. sobrescrita de resultados em vez de acumulação por páginas/lotes
6. ausência de deduplicação e separação de itens inválidos
7. baixa rastreabilidade e ausência de logs úteis para diagnóstico
8. código pouco modular e pouco reutilizável

## Diagnóstico técnico

A evidência observada diretamente no navegador mostra que a página do G1 não entrega a totalidade dos resultados em uma única carga HTML estática. Ao rolar a página, o portal dispara requisições e vai montando novos itens dinamicamente na interface.

Esse comportamento explica a regressão da rotina original: a coleta baseada em HTML bruto da primeira resposta passa a retornar poucos resultados, registros vazios ou registros incompletos, sem indicar de forma explícita que houve falha de extração.

Os principais seletores observados na estrutura atual são:

- `li.widget--info`
- `li.video-widget--info`
- `.widget--info__title`
- `.widget--info__description`
- `.widget--info__meta`
- link `a[href]` do card
- botão de paginação `button.pagination__load-more`

## Solução implementada

A correção foi organizada em módulos com responsabilidades bem definidas:

- `scraper.py`: coleta, parsing, normalização, deduplicação e exportação
- `evaluate.py`: cálculo de métricas de qualidade e comparação com referência
- `tests/test_scraper.py`: testes automatizados para regras críticas

### Melhorias principais

- parsing robusto com Beautiful Soup
- validação e normalização de URLs
- deduplicação por URL mantendo a primeira ocorrência
- tratamento de campos ausentes
- separação entre registros válidos e itens em quarentena
- exportação em CSV e JSON
- logs de execução e diagnóstico
- tratamento de falhas de rede, respostas inválidas e dados incompletos
- suporte a múltiplas páginas e snapshots locais
- enriquecimento de data quando metadados do artigo estiverem disponíveis

## Execução

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

### Coleta online

```bash
python scraper.py --term lgpd --pages 3 --out data/online
```

### Coleta a partir de snapshots locais

```bash
python scraper.py --html evidence/Busca.html evidence/lote_02.html evidence/lote_03.html --out data/coleta_multilotes
python evaluate.py --data data/coleta_multilotes/resultados.json --reference data/referencia_revisada.json --out data/metricas_multilotes.json
python -m pytest -q
```

## Base de dados produzida

Arquivos gerados:

- `data/coleta_multilotes/resultados.json`
- `data/coleta_multilotes/resultados.csv`
- `data/metricas_multilotes.json`

A base validada contém 30 URLs únicas, distribuídas em 26 notícias e 4 vídeos, com deduplicação aplicada e registros preservados pelo primeiro lote em que apareceram.

## Qualidade dos dados e métricas

A avaliação considerou:

- completude
- cobertura
- precisão
- acurácia
- unicidade
- consistência
- rastreabilidade
- atualização temporal

Resultados observados:

- 30 URLs únicas
- 30 registros válidos após deduplicação
- título, URL, resumo e data exibida presentes em 30/30 registros
- `data_publicacao` mantida apenas quando houver evidência em metadados do artigo
- 25 testes automatizados aprovados

## Estratégia de uso de LLM

A LLM pode apoiar o diagnóstico e a manutenção do scraper, mas não deve substituir a validação dos dados. A proposta é usar o modelo em fases de:

- análise de HTML e seleção de seletores
- comparação de versões da página
- revisão de logs e inconsistências de execução
- sugestão de testes de regressão

### Dados fornecidos ao modelo

- trechos de HTML da página de busca
- seletores atuais e anteriores
- logs de execução
- registros coletados e inconsistências detectadas
- snapshots históricos da página

### Validação das respostas

- qualquer sugestão da LLM deve ser validada por testes automáticos
- mudanças só entram no código se forem compatíveis com os dados observados
- campos devem ser preenchidos apenas quando houver evidência real
- respostas devem ser transformadas em regras verificáveis, nunca aceitas como verdade implícita

### Mecanismos para evitar alucinações

- restringir o modelo a dados observáveis e registros reais
- exigir justificativa em trechos do HTML antes da adoção da sugestão
- validar em testes de regressão e amostras de referência
- manter a LLM fora do fluxo de produção de dados, como suporte de análise

## Limitações e próximos passos

- a paginação ao vivo do G1 ainda exige validação em ambiente genuíno de navegador
- a coleta completa do portal pode depender de scroll e de requisições dinâmicas
- a data de publicação precisa ser corroborada por metadados do artigo, não inferida sem evidência
- o site pode evoluir e exigir revisão periódica dos seletores
- melhorias futuras incluem automação de navegador, inspeção de rede e monitoramento contínuo

## Evidências do projeto

Arquivos relevantes:

- `evidence/Busca.html`
- `evidence/lote_02.html`
- `evidence/lote_03.html`
- `evidence/initial.html`
- `docs/llm.md`
- `data/metricas_multilotes.json`

## Conclusão

A solução corrige os principais problemas da rotina original, aumenta a robustez da coleta e entrega uma base de dados rastreável, validada e documentada. O projeto demonstra capacidade de diagnóstico técnico, solução em Python, avaliação de qualidade e apresentação de evidências em um contexto real de engenharia de dados e pesquisa.
