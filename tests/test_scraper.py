"""Fixtures sintéticas: verificam lógica, não provam cobertura do portal atual."""
from unittest.mock import Mock
import requests
import pytest
from scraper import parse_html, deduplicate, normalize_url, fetch_html, save_output
from evaluate import evaluate

HTML = '''<ul class="results__list"><li class="widget widget--info"><div class="widget--info__text-container"><a href="/x?utm_source=t"><div class="widget--info__title"> Lei <b>LGPD</b> </div><p class="widget--info__description"> A   lei </p><div class="widget--info__meta"><span>há 2 dias</span></div></a></div></li></ul>'''

def parse(html=HTML, page=1):
    return parse_html(html, page=page, collected_at='2026-09-17T18:00:00+00:00', source_url='https://g1.globo.com/busca/?q=lgpd', snapshot='teste.html')[0]

def test_fields_and_date_semantics():
    row = parse()[0]
    assert row['titulo'] == 'Lei LGPD'
    assert row['resumo'] == 'A lei'  # espaços normalizados
    assert row['data_publicacao'] is None
    assert row['data_exibida'] == 'há 2 dias'
    assert len(row['sha256']) == 64

def test_missing_optional():
    row = parse(HTML.replace('<p class="widget--info__description"> A   lei </p>', ''))[0]
    assert row['resumo'] is None

def test_missing_link_quarantine():
    rows = parse('<li class="widget--info"><div class="widget--info__title">X</div></li>')
    good, quarantine, n = deduplicate(rows)
    assert not good and len(quarantine) == 1 and n == 0

def test_empty_dynamic_not_success():
    rows, d = parse_html('<div class="all-search-results"></div>', page=1, collected_at='t', source_url='u', snapshot='s')
    assert not rows and d['container_vazio']

def test_multiple_pages_and_duplicates():
    rows = parse() + parse(HTML.replace('/x?', '/y?'), 2) + parse(page=3)
    good, _, n = deduplicate(rows)
    assert len(good) == 2 and n == 1 and good[1]['pagina'] == 2

@pytest.mark.parametrize('url', ['javascript:alert(1)', 'data:x', '', None])
def test_invalid_urls(url):
    assert normalize_url(url) is None

def test_preserves_semantic_query():
    assert normalize_url('/a?id=2&utm_medium=x#fragment') == 'https://g1.globo.com/a?id=2'

@pytest.mark.parametrize('error', [requests.Timeout('timeout'), requests.ConnectionError('offline')])
def test_network_errors_are_exposed_to_orchestrator(error):
    s = Mock(); s.get.side_effect = error
    with pytest.raises(type(error)):
        fetch_html(s, 'https://example.org')

def test_invalid_http():
    response = Mock(); response.raise_for_status.side_effect = requests.HTTPError('500')
    s = Mock(); s.get.return_value = response
    with pytest.raises(requests.HTTPError): fetch_html(s, 'https://example.org')

def test_invalid_content_type():
    response = Mock(); response.headers = {'Content-Type': 'application/json'}
    s = Mock(); s.get.return_value = response
    with pytest.raises(ValueError): fetch_html(s, 'https://example.org')

def test_outputs_preserve_unicode(tmp_path):
    save_output(tmp_path, parse(), [])
    assert 'há 2 dias' in (tmp_path / 'resultados.json').read_text(encoding='utf-8')
    assert (tmp_path / 'resultados.csv').read_bytes().startswith(b'\xef\xbb\xbf')

def test_quality_detects_missing_and_wrong():
    rows = parse()
    ref = [{**rows[0], 'titulo': 'outro'}, {**rows[0], 'url': 'https://g1.globo.com/missing'}]
    m = evaluate(rows, ref)
    assert m['cobertura'] == .5
    assert m['acuracia_campos']['titulo']['taxa'] == 0
    assert m['completude']['data_publicacao'] == 0

def test_empty_metrics_not_perfect():
    m = evaluate([], [])
    assert m['cobertura'] is None and m['unicidade'] is None


def test_tracking_link_decoded_and_deduplicated():
    url = 'https://measures.globo.com/v1/click?rid=abc&u=https%3A%2F%2Fg1.globo.com%2Fa'
    assert normalize_url(url) == 'https://g1.globo.com/a'
    assert normalize_url(url.replace('rid=abc', 'rid=xyz')) == normalize_url(url)

def test_untrusted_tracking_target_rejected():
    assert normalize_url('https://measures.globo.com/v1/click?u=https://evil.example/a') is None

def test_video():
    row = parse(HTML.replace('widget--info', 'video-widget--info'))[0]
    assert row['titulo'] == 'Lei LGPD'
    assert row['semantica_data_exibida'] == 'data_exibida_semantica_nao_confirmada'

def test_real_snapshot_coverage():
    from pathlib import Path
    html = (Path(__file__).resolve().parents[1] / 'evidence/Busca.html').read_text(encoding='utf-8')
    rows = parse(html)
    assert len(rows) == 10
    assert len({r['url'] for r in rows}) == 10
    assert all(r['url'].startswith('https://g1.globo.com/') for r in rows)
    assert rows[0]['titulo'] == 'Integração TEC: mais de 37% dos órgãos e empresas não seguem regras da LGPD'


def test_snapshot_integrity_detects_tampering(tmp_path):
    from evaluate import verify_snapshots
    (tmp_path / 'teste.html').write_text(HTML, encoding='utf-8')
    assert verify_snapshots(parse(), tmp_path)['taxa'] == 1
    (tmp_path / 'teste.html').write_text(HTML + 'alterado', encoding='utf-8')
    assert verify_snapshots(parse(), tmp_path)['taxa'] == 0


def test_orchestrator_preserves_success_after_failure(tmp_path, monkeypatch):
    import json
    import sys
    from scraper import main
    valid = tmp_path / 'valid.html'
    valid.write_text(HTML, encoding='utf-8')
    out = tmp_path / 'out'
    monkeypatch.setattr(sys, 'argv', ['scraper.py', '--html', str(tmp_path / 'missing.html'),
                                    str(valid), '--out', str(out)])
    assert main() == 3
    rows = json.loads((out / 'resultados.json').read_text(encoding='utf-8'))
    assert len(rows) == 1 and rows[0]['pagina'] == 2
