"""Avaliação contra referência independente, nunca gerada pelo parser."""
import argparse
import json
import hashlib
from datetime import datetime
from pathlib import Path


def ratio(n, d):
    return n / d if d else None


def verify_snapshots(rows, directory):
    """Confere o hash do texto UTF-8 analisado, sem sair do diretório da coleta."""
    directory = Path(directory).resolve()
    valid = 0
    for row in rows:
        try:
            path = (directory / row['snapshot']).resolve()
            if not path.is_relative_to(directory):
                continue
            digest = hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest()
            valid += digest == row['sha256']
        except (OSError, KeyError, ValueError, TypeError):
            continue
    return {'verificados': len(rows), 'validos': valid, 'taxa': ratio(valid, len(rows))}


def evaluate(rows, reference):
    expected = {r['url']: r for r in reference}
    # Amostra exaustiva do escopo escolhido (p.ex. lote 1), não de todo o portal.
    scope = {r['pagina'] for r in reference}
    selected = [r for r in rows if r['pagina'] in scope]
    observed = {r['url']: r for r in selected if r.get('url')}
    matched = expected.keys() & observed.keys()
    fields = ['titulo', 'resumo', 'data_publicacao', 'data_exibida']
    agreement = {}
    for field in fields:
        pairs = [(observed[u].get(field), expected[u].get(field)) for u in matched
                 if expected[u].get(field) is not None]
        agreement[field] = {'iguais': sum(a == b for a, b in pairs), 'comparaveis': len(pairs),
                            'taxa': ratio(sum(a == b for a, b in pairs), len(pairs))}
    consistent = 0
    for r in selected:
        try:
            dt = datetime.fromisoformat(r['coletado_em'])
            consistent += bool(dt.tzinfo and isinstance(r['pagina'], int) and r['pagina'] >= 1
                               and (r.get('url') or '').startswith(('http://', 'https://')))
        except (ValueError, TypeError, KeyError):
            pass
    return {'referencia_n': len(reference), 'escopo_paginas': sorted(scope), 'coletados_escopo': len(selected),
            'cobertura': ratio(len(matched), len(expected)),
            'precisao_pertencimento': ratio(len(matched), len(observed)),
            'unicidade': ratio(len(observed), len(selected)),
            'completude': {f: ratio(sum(r.get(f) not in (None, '') for r in selected), len(selected))
                          for f in ['titulo', 'url', 'resumo', 'data_publicacao', 'data_exibida']},
            'acuracia_campos': agreement, 'consistencia': ratio(consistent, len(selected)),
            'rastreabilidade_declarada': ratio(sum(all(r.get(k) for k in ['snapshot', 'sha256', 'fonte_url', 'coletado_em'])
                                                  for r in selected), len(selected)),
            'atualidade': None,
            'nota_atualidade': 'Requer comparação temporal com captura contemporânea; não inferir de notícias antigas.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    rows = json.loads(a.data.read_text(encoding='utf-8'))
    ref = json.loads(a.reference.read_text(encoding='utf-8'))
    if not ref:
        p.error('Amostra de referência vazia; não produzir métricas fictícias.')
    metrics = evaluate(rows, ref)
    metrics['integridade_snapshot'] = verify_snapshots(rows, a.data.parent)
    metrics['referencia_metodo'] = 'Referência local revisada pelo assistente; revisão humana independente pendente.'
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding='utf-8')
