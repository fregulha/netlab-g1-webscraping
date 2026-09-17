"""Audita os três snapshots fornecidos; não gera referência de acurácia."""
import hashlib
import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from scraper import parse_html
from evaluate import verify_snapshots

def main():
    names = ['Busca.html', 'lote_02.html', 'lote_03.html']
    sets, counts, files = [], [], []
    for page, name in enumerate(names, 1):
        path = ROOT / 'evidence' / name
        html = path.read_text(encoding='utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        rows, _ = parse_html(html, page=page, collected_at='audit',
                             source_url='https://g1.globo.com/busca/?q=lgpd', snapshot=name)
        urls = [r['url'] for r in rows]
        sets.append(urls)
        counts.append(len(urls))
        files.append({'arquivo': name, 'titulo_html': soup.title.get_text(),
                      'sha256_bytes': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'captura_em': None, 'origem': 'arquivo fornecido pela usuária',
                      'cards': len(rows), 'videos': len(soup.select('li.video-widget--info')),
                      'noticias': len(soup.select('li.widget--info')),
                      'veja_mais': bool(soup.select_one('button.pagination__load-more'))})
    data = ROOT / 'data/coleta_multilotes'
    rows = json.loads((data / 'resultados.json').read_text(encoding='utf-8'))
    unique = len({r['url'] for r in rows})
    raw = sum(counts)
    result = {
        'verificado_em': datetime.now(timezone.utc).isoformat(),
        'arquivos': files, 'cards_por_snapshot': counts,
        'prefixo_1_preservado_em_2': sets[0] == sets[1][:len(sets[0])],
        'prefixo_2_preservado_em_3': sets[1] == sets[2][:len(sets[1])],
        'ocorrencias_brutas': raw, 'registros_unicos': unique,
        'duplicados_removidos': raw-len(rows),
        'unicidade_antes': unique/raw, 'unicidade_depois': unique/len(rows),
        'primeiro_lote_observado': dict(Counter(r['pagina'] for r in rows)),
        'completude': {f: {'presentes': sum(r.get(f) not in (None, '') for r in rows),
                           'total': len(rows)}
                       for f in ['titulo', 'url', 'resumo', 'data_publicacao', 'data_exibida']},
        'integridade_snapshot': verify_snapshots(rows, data),
        'referencia_independente': 'Somente 10 cards do lote 1, ainda sem revisão humana.',
        'atualidade': None, 'paginacao_ao_vivo_validada': False,
    }
    (ROOT/'data/auditoria_multilotes.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
