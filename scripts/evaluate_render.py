#!/usr/bin/env python3
"""Sepuluh render teks standar; simpan statistik tanpa isi teks masukan."""

import argparse
import json
from pathlib import Path
import platform
import re
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render_document import GlyphBank, layout, render_document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', required=True)
    parser.add_argument('--out', type=Path, default=Path('outputs/evaluation'))
    parser.add_argument('--repeat', type=int, default=1,
                        help='Ulang teks standar untuk uji halaman padat; default 1 tidak mengubah teks.')
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    evaluation = (project/'EVALUATION.md').read_text(encoding='utf-8').split('## 5.')[1]
    text = re.search(r'```\n(.*?)\n```', evaluation, re.S).group(1)
    if args.repeat < 1:
        parser.error('--repeat harus positif')
    text = '\n\n'.join([text]*args.repeat)
    bank = GlyphBank(args.user, project/'glyph_bank')
    results, overlaps, widths = [], 0, {}
    for seed in range(10):
        result = render_document(text, args.user, 'surat', args.out/f'seed_{seed:02d}',
                                 seed=seed, bank_root=project/'glyph_bank')
        results.append(result)
        pages, _, _, _ = layout(text, bank, 'surat', seed)
        for page in pages:
            for i, a in enumerate(page):
                if a.label:
                    widths.setdefault(a.label, []).append(a.image.width)
                for b in page[i+1:]:
                    overlaps += int(a.x < b.x+b.image.width and b.x < a.x+a.image.width
                                    and a.y < b.y+b.image.height and b.y < a.y+a.image.height)
    seconds = [r['elapsed_seconds']/r['pages'] for r in results]
    summary = {'runs': 10, 'python': platform.python_version(), 'platform': platform.system(),
               'text_repetitions': args.repeat,
               'machine': platform.machine(), 'mean_seconds_per_page': statistics.mean(seconds),
               'min_seconds_per_page': min(seconds), 'max_seconds_per_page': max(seconds),
               'missing_characters': sorted({c for r in results for c in r['missing_characters']}),
               'rectangle_overlap_pairs': overlaps,
               'width_stddev_px_per_label': {k: statistics.pstdev(v) for k, v in sorted(widths.items())},
               'glyph_width_stddev_px_per_label': {k: statistics.pstdev(g.image.width for g in v)
                                                  for k, v in sorted(bank.glyphs.items())},
               'total_pages': sum(r['pages'] for r in results)}
    (args.out/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in summary.items() if 'stddev' not in k}, indent=2))


if __name__ == '__main__':
    main()
