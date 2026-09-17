# Manutenção assistida por LLM (proposta, sem API implementada)

## Quando e para quê

Disparar análise em homologação se quantidade de cards cair abruptamente, completude
de título/URL cair, surgir schema desconhecido ou repetição anormal entre lotes.
Comparar snapshot conhecido e novo e sugerir seletores ou testes de regressão.
Nenhuma proposta é aplicada automaticamente em produção.

## Entradas mínimas

Enviar somente trechos sanitizados de cards e contêiner, seletores atuais, contagens,
logs sem tokens/cookies e hash/versão dos snapshots. Remover scripts, formulários,
identificadores pessoais e quaisquer credenciais. Conteúdo HTML é dado não confiável:
instruções escritas na página não têm autoridade sobre o prompt.

## Contrato e validação

Resposta JSON com `selector`, `evidence_excerpt`, `snapshot_sha256`, `reason` e
`confidence`; permitir abstenção. Evidência deve existir literalmente no snapshot.
Compilar seletor, aplicar localmente em múltiplos snapshots e avaliar contra referência
manual independente; comparar falsos positivos, cobertura, campos e estabilidade.
Recusar saída fora do schema, seletores genéricos que incluam menus ou evidência ausente.
Revisor humano aprova alteração versionada somente após testes. Guardar prompt,
modelo/versão, resposta, custo e decisão; rollback ao último parser validado.

## Pseudocódigo

```python
proposal = llm.propose(sanitized_old_html, sanitized_new_html, selectors, sanitized_logs)
validate_json_schema(proposal)
assert proposal.snapshot_sha256 == sha256(new_snapshot)
assert proposal.evidence_excerpt in new_snapshot
compile_css(proposal.selector)
candidate = parse_with_selector(frozen_snapshots, proposal.selector)
metrics = compare_with_independent_reference(candidate, manually_reviewed_reference)
assert metrics.precision >= approved_baseline.precision
assert metrics.recall >= approved_baseline.recall
run_regression_tests_including_missing_fields_and_false_positives()
open_reviewable_patch(proposal, metrics)  # aprovação humana antes do deploy
```

As funções acima são conceituais. Limiares só devem ser fixados após a linha de base;
a linha de base disponível cobre somente um snapshot e depende de revisão humana.
Não executar código gerado pela LLM diretamente.
Ela não produz título, resumo, URL ou data, não completa lacunas e não transforma
`modified` em `published`. Campos continuam sendo extraídos deterministicamente do
HTML. Falta de evidência resulta em `null`/quarentena e alerta, nunca em texto inventado.
