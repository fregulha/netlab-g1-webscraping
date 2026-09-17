"""Extração auditável. O HTML renderizado atual ainda requer validação em campo."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOG = logging.getLogger(__name__)
BASE = 'https://g1.globo.com/busca/'
CARD = 'li.widget--info, li.video-widget--info'
FIELDS = ['titulo', 'url', 'resumo', 'data_publicacao', 'data_exibida',
          'semantica_data_exibida', 'pagina', 'coletado_em', 'fonte_url',
          'snapshot', 'sha256', 'posicao', 'avisos']


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def normalize_url(value, base=BASE):
    """Remove só rastreadores conhecidos, preservando parâmetros de conteúdo."""
    if not value:
        return None
    p = urlsplit(urljoin(base, value.strip()))
    if p.scheme not in {'http', 'https'} or not p.hostname or p.username or p.password:
        return None
    if p.hostname == 'measures.globo.com' and p.path == '/v1/click':
        targets = [v for k, v in parse_qsl(p.query) if k == 'u']
        if len(targets) != 1:
            return None
        target = urlsplit(targets[0])
        if target.hostname != 'g1.globo.com' or target.scheme not in {'http', 'https'}:
            return None
        return normalize_url(targets[0], base)
    query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in {'fbclid', 'gclid'}]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path, urlencode(query), ''))


def text(node):
    return ' '.join(node.get_text(' ', strip=True).split()) if node else None


def parse_html(html, *, page, collected_at, source_url, snapshot):
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.select(CARD)
    digest = hashlib.sha256(html.encode('utf-8')).hexdigest()
    records = []
    for pos, card in enumerate(cards, 1):
        prefix = 'video-widget--info' if 'video-widget--info' in card.get('class', []) else 'widget--info'
        title = card.select_one(f'.{prefix}__title')
        link = title.find_parent('a') if title else None
        if link is None:
            link = card.select_one(f'.{prefix}__text-container a[href]')
        url = normalize_url(link.get('href') if link else None, source_url)
        warnings = []
        if not url:
            warnings.append('url_ausente_ou_invalida')
        if not text(title):
            warnings.append('titulo_ausente')
        # O componente do portal usa _source.modified, não published.
        # Não converter a data relativa de atualização em data de publicação.
        records.append(dict(zip(FIELDS, [
            text(title), url, text(card.select_one(f'.{prefix}__description')),
            None, text(card.select_one(f'.{prefix}__meta')),
            ('data_exibida_semantica_nao_confirmada' if prefix.startswith('video') else 'atualizacao_conforme_componente_js'), page, collected_at, source_url,
            snapshot, digest, pos, warnings,
        ])))
    if not cards:
        LOG.warning('zero_cards: possível HTML sem renderização ou mudança estrutural')
    excluded = len(soup.select('.results__list > li')) - len(cards)
    return records, {'cards': len(cards), 'outros_cards': max(excluded, 0),
                     'container_vazio': bool(soup.select_one('.all-search-results')) and not cards,
                     'veja_mais': bool(soup.select_one('button.pagination__load-more'))}


def deduplicate(records):
    """Conserva a primeira ocorrência; sem URL vai para quarentena, sem sumir."""
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
    return unique, quarantine, duplicates


def session():
    s = requests.Session()
    s.headers['User-Agent'] = 'NetLabSelectionResearch/0.1 (limited diagnostic collection)'
    retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=['GET'], respect_retry_after_header=True)
    s.mount('https://', HTTPAdapter(max_retries=retry))
    return s


def fetch_html(s, url):
    response = s.get(url, timeout=(10, 30))
    response.raise_for_status()
    if 'text/html' not in response.headers.get('Content-Type', '').lower():
        raise ValueError('Resposta não é HTML')
    response.encoding = 'utf-8'
    return response.text, response.url


def save_output(out, records, events):
    out.mkdir(parents=True, exist_ok=True)
    unique, quarantine, duplicates = deduplicate(records)
    for name, value in [('resultados.json', unique), ('quarentena.json', quarantine),
                        ('execucao.json', {'eventos': events, 'duplicados': duplicates,
                                          'registros': len(unique), 'quarentena': len(quarantine)})]:
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    with (out / 'resultados.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in unique:
            writer.writerow({**row, 'avisos': json.dumps(row['avisos'], ensure_ascii=False)})
    return unique


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--html', nargs='+', type=Path, help='Snapshots ordenados, um por lote observado')
    p.add_argument('--term', default='lgpd')
    p.add_argument('--out', type=Path, default=Path('data/run'))
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        handlers=[logging.StreamHandler(), logging.FileHandler(args.out / 'run.log', encoding='utf-8')])
    url = BASE + '?' + urlencode({'q': args.term})
    events, records = [], []
    inputs = args.html or [None]
    for page, path in enumerate(inputs, 1):
        try:
            if path:
                html = path.read_text(encoding='utf-8')
                collected = utcnow()  # horário da extração; não inventa horário de captura
                acquisition = 'arquivo_fornecido; horario_original_de_captura_desconhecido'
            else:
                with session() as s:
                    html, url = fetch_html(s, url)
                collected, acquisition = utcnow(), 'requests'
            snapshot = f'pagina_{page:03d}.html'
            (args.out / snapshot).write_text(html, encoding='utf-8')
            rows, diagnostics = parse_html(html, page=page, collected_at=collected,
                                          source_url=url, snapshot=snapshot)
            records.extend(rows)
            events.append({'pagina': page, 'aquisicao': acquisition, 'coletado_em': collected,
                           'fonte_url': url, **diagnostics})
            LOG.info('lote=%s cards=%s veja_mais=%s', page, len(rows), diagnostics['veja_mais'])
        except (requests.RequestException, ValueError, OSError) as exc:
            LOG.error('falha lote=%s tipo=%s mensagem=%s', page, type(exc).__name__, exc)
            events.append({'pagina': page, 'erro': type(exc).__name__, 'mensagem': str(exc)})
    output = save_output(args.out, records, events)
    if not output:
        LOG.error('Nenhum registro válido. Não interpretar como ausência de notícias.')
        return 2
    if any('erro' in e or not e.get('cards') for e in events):
        return 3  # entrega parcial explicitada ao orquestrador
    LOG.info('extração concluída; paginação online não validada')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
