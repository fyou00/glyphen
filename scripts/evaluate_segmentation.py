#!/usr/bin/env python3
"""Audit segmentasi: kotak sumber/crop, anotasi eksplisit, dan metrik status."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from extract_glyphs import H_MM, INSET, MM, page_layout, rectify
from render_document import GlyphBank, read_json


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_review(template, review):
    """Jangan menganggap status ok sebagai hasil penilaian visual."""
    if review.get('manifest_sha256') != template['manifest_sha256']:
        raise ValueError('Anotasi berasal dari manifest berbeda.')
    if review.get('source_sha256') != template['source_sha256']:
        raise ValueError('Anotasi berasal dari scan berbeda.')
    expected = {(e['label'], e['variant']): e for e in template['entries']}
    annotations = {}
    for entry in review['entries']:
        key = (entry['label'], entry['variant'])
        if key not in expected or key in annotations:
            raise ValueError('Anotasi duplikat atau label/varian tidak dikenal.')
        if entry.get('glyph_sha256') != expected[key]['glyph_sha256']:
            raise ValueError('Berkas glyph berbeda dari anotasi.')
        if entry.get('correct') is not None and type(entry['correct']) is not bool:
            raise ValueError('Nilai correct harus true, false, atau null.')
        annotations[key] = entry
    checked = [e for e in annotations.values() if type(e.get('correct')) is bool]
    if checked and not review.get('reviewer', '').strip():
        raise ValueError('Pemeriksa anotasi harus dicatat.')
    correct = sum(e['correct'] for e in checked)
    return {'total_boxes': len(expected), 'reviewed_boxes': len(checked),
            'correct_boxes': correct, 'incorrect_boxes': len(checked)-correct,
            'review_complete': len(checked) == len(expected),
            'crop_accuracy': correct/len(checked) if checked else None,
            'reviewer': review.get('reviewer'),
            'failed_entries': [{'label': e['label'], 'variant': e['variant'],
                                'note': e.get('note', '')} for e in checked if not e['correct']]}


def evaluate(user, out, bank_root, scan_root, review_path=None):
    GlyphBank(user, bank_root)  # Wajib sudah memiliki persetujuan dan tinjauan dasar.
    folder = bank_root / user
    manifest_path = folder/'manifest.json'
    manifest = read_json(manifest_path)
    consent = read_json(folder/'consent.json')
    if out.exists():
        raise ValueError('Folder audit sudah ada; gunakan folder baru.')
    sources, hashes = {}, {}
    for n in (1, 2, 3):
        path = (scan_root/consent['pages'][n-1]['processed']).resolve()
        if not path.is_relative_to(scan_root.resolve()):
            raise ValueError('Lokasi scan keluar folder sumber.')
        sources[n] = path
        hashes[str(n)] = digest(path)
    entries = manifest['entries']
    template = {'user_id': user, 'manifest_sha256': digest(manifest_path),
                'source_sha256': hashes, 'reviewer': '', 'entries': []}
    for entry in entries:
        path = (bank_root/entry['file']).resolve() if entry['file'] else None
        if path and not path.is_relative_to((folder/'glyphs').resolve()):
            raise ValueError('Lokasi glyph keluar folder pengguna.')
        template['entries'].append({'label': entry['label'], 'variant': entry['variant'],
                                    'page': entry['page'], 'correct': None, 'note': '',
                                    'glyph_sha256': digest(path) if path else None})
    review = read_json(review_path) if review_path else template
    visual = score_review(template, review)
    out.mkdir(parents=True)
    for n in (1, 2, 3):
        image = cv2.imread(str(sources[n]))
        if image is None:
            raise ValueError(f'Scan halaman {n} tidak terbaca.')
        warped = rectify(image)
        boxes = page_layout(n)
        labels = list(dict.fromkeys(b[0] for b in boxes))
        lookup = {(e['label'], e['variant']): e for e in entries if e['page'] == n}
        for part, start in enumerate(range(0, len(labels), 13), 1):
            selected = labels[start:start+13]
            sheet = Image.new('RGB', (1100, len(selected)*190), '#eeeeee')
            draw = ImageDraw.Draw(sheet)
            for row, label in enumerate(selected):
                for key, variant, x, y, w, h in [b for b in boxes if b[0] == label]:
                    left, top = variant*220, row*190
                    draw.text((left, top), f'{label} {variant+1}: full / crop', fill='black')
                    x0, y0 = round(x*MM), round((H_MM-y-h)*MM)
                    full = Image.fromarray(cv2.cvtColor(
                        warped[y0:y0+round(h*MM), x0:x0+round(w*MM)], cv2.COLOR_BGR2RGB))
                    inset = round(INSET*MM)
                    ImageDraw.Draw(full).rectangle((inset, inset, full.width-inset, full.height-inset), outline='red')
                    full.thumbnail((208, 85))
                    sheet.paste(full, (left, top+18))
                    entry = lookup[key, variant+1]
                    if entry['file']:
                        with Image.open(bank_root/entry['file']) as glyph:
                            crop = glyph.convert('RGB')
                        crop.thumbnail((208, 80))
                        sheet.paste(crop, (left, top+105))
            sheet.save(out/f'audit_page{n}_part{part}.png')
    statuses = {s: sum(e['status'] == s for e in entries) for s in ('ok', 'empty', 'touches_edge')}
    report = {'counts': statuses, 'total_boxes': len(entries),
              'ratios': {k: v/len(entries) for k, v in statuses.items()},
              'empty_per_label': {k: sum(e['status'] == 'empty' for e in entries if e['label'] == k)
                                  for k in sorted({e['label'] for e in entries})},
              'visual_review': visual}
    for name, data in [('review_template.json', template), ('summary.json', report)]:
        (out/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if review_path:
        (out/'review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', required=True)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--bank-root', type=Path, default=Path('glyph_bank'))
    parser.add_argument('--scan-root', type=Path, default=Path('scan_demo'))
    parser.add_argument('--review', type=Path)
    args = parser.parse_args()
    try:
        result = evaluate(args.user, args.out, args.bank_root, args.scan_root, args.review)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f'Audit dihentikan: {exc}\n')
    print(json.dumps({'counts': result['counts'], 'visual_review': result['visual_review']}, indent=2))


if __name__ == '__main__':
    main()
