#!/usr/bin/env python3
"""Render glyph bank yang sudah ditinjau menjadi PDF/PNG tidak resmi."""

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import random
import re
import statistics
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

WATERMARK = "TIDAK RESMI - HASIL GENERASI"
PX_MM = 10
DPI = 300
PAGE_PX = (round(210 * DPI / 25.4), round(297 * DPI / 25.4))
PUNCT = dict(zip('.,?!:;"\'-()', ('dot', 'comma', 'question', 'exclam',
             'colon', 'semicolon', 'dquote', 'squote', 'hyphen', 'lparen', 'rparen')))
MARGINS = {"catatan": 20, "surat": 25}
LETTERS = [f"lower_{c}" for c in 'abcdefghijklmnopqrstuvwxyz'] + [
    f"upper_{c}" for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']


def label_for(char):
    if 'a' <= char <= 'z':
        return f"lower_{char}"
    if 'A' <= char <= 'Z':
        return f"upper_{char}"
    if '0' <= char <= '9':
        return f"digit_{char}"
    return f"punct_{PUNCT[char]}" if char in PUNCT else None


def normalize_text(text):
    lines = text.replace('\r\n', '\n').replace('\r', '\n').replace('\t', '    ').split('\n')
    return '\n'.join(re.match(r' *', line).group() + re.sub(r' +', ' ', line.lstrip(' '))
                     for line in lines)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError(f"JSON tidak tersedia atau tidak valid: {path.name}") from exc


@dataclass
class Glyph:
    variant: int
    image: Image.Image
    # Jarak baseline template dari sisi atas gambar tinta yang dipangkas.
    ascent: float


class GlyphBank:
    def __init__(self, user_id, root='glyph_bank'):
        if not re.fullmatch(r'[A-Za-z0-9_-]+', user_id):
            raise ValueError('ID pengguna hanya boleh berisi huruf, angka, _ dan -.')
        self.user_id = user_id
        root = Path(root).resolve()
        folder = (root / user_id).resolve()
        if folder.parent != root:
            raise ValueError('Folder pengguna tidak boleh keluar dari glyph bank.')
        manifest = read_json(folder / 'manifest.json')
        coverage = read_json(folder / 'coverage.json')
        consent = read_json(folder / 'consent.json')
        review = read_json(folder / 'extraction_report.json')['visual_review']
        if manifest.get('user') != user_id or coverage.get('user_id') != user_id:
            raise ValueError('Identitas manifest/coverage berbeda dari pengguna.')
        if (consent.get('user_id') != user_id or consent.get('owner_is_uploader') is not True
                or not consent.get('consent_statement', '').strip()):
            raise ValueError('Identitas dan persetujuan pemilik tulisan belum valid.')
        if review.get('passed') is not True:
            raise ValueError('Tinjauan potongan glyph belum lulus.')
        accepted_edges = {(e['label'], e['variant']) for e in review.get('touches_edge_review', [])
                          if e.get('accepted') is True}
        self.glyphs = {}
        seen_files, seen_variants = set(), set()
        for entry in manifest['entries']:
            if entry['status'] not in ('ok', 'touches_edge'):
                continue
            label, variant = entry['label'], entry['variant']
            if entry['status'] == 'touches_edge' and (label, variant) not in accepted_edges:
                raise ValueError(f'Glyph menyentuh tepi belum ditinjau: {label}/{variant}')
            path = (root / entry['file']).resolve()
            if not path.is_relative_to(folder / 'glyphs'):
                raise ValueError('Lokasi glyph keluar dari folder pengguna.')
            if path in seen_files or (label, variant) in seen_variants:
                raise ValueError('Entri glyph duplikat pada manifest.')
            seen_files.add(path)
            seen_variants.add((label, variant))
            try:
                with Image.open(path) as source:
                    gray = np.array(source.convert('L'))
            except OSError as exc:
                raise ValueError(f'File glyph tidak terbaca: {label}/{variant}') from exc
            # Mask tinta saja: hilangkan kertas/garis panduan dan bintik kecil.
            mask = (gray < 128).astype(np.uint8)
            count, components, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
            if count < 2:
                raise ValueError(f'Glyph tidak memiliki tinta: {label}/{variant}')
            minimum = max(2, int(stats[1:, cv2.CC_STAT_AREA].max() * 0.01))
            keep = np.zeros(count, dtype=bool)
            keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= minimum
            ink = keep[components]
            ys, xs = np.where(ink)
            if not len(xs):
                raise ValueError(f'Glyph terlalu kecil: {label}/{variant}')
            x0, x1, y0, y1 = xs.min(), xs.max()+1, ys.min(), ys.max()+1
            alpha = np.where(ink, 255 - gray, 0).astype(np.uint8)
            image = Image.new('RGBA', (x1-x0, y1-y0), (0, 0, 0, 0))
            image.putalpha(Image.fromarray(alpha[y0:y1, x0:x1]))
            # baseline = 20% tinggi kotak dari bawah; inset tetap 1,2 mm.
            box_height = 12 if label.startswith('upper_') else 9 if label.startswith(('digit_', 'punct_')) else 8
            baseline = gray.shape[0] - (0.2 * box_height - 1.2) * PX_MM
            self.glyphs.setdefault(label, []).append(Glyph(variant, image, baseline-y0))
        incomplete = []
        self.below_ideal = []
        for label in set(LETTERS) | set(self.glyphs):
            actual = len(self.glyphs.get(label, []))
            recorded = coverage.get('labels', {}).get(label, {}).get('available')
            if recorded != actual:
                raise ValueError(f'Coverage tidak cocok dengan file glyph: {label}')
            if label in LETTERS and actual < 3:
                incomplete.append(label)
            if label in LETTERS and actual < 5:
                self.below_ideal.append(label)
        if incomplete:
            raise ValueError('Coverage huruf belum lengkap; ulangi halaman terkait: ' + ', '.join(sorted(incomplete)))
        self.mean_widths = {label: statistics.mean(g.image.width for g in gs)
                            for label, gs in self.glyphs.items()}
        self.mean_width = statistics.mean(self.mean_widths.values())
        xheights = [g.image.height for c in 'acemnorsuvwx' for g in self.glyphs[f'lower_{c}']]
        self.xheight = statistics.median(xheights)


@dataclass
class Token:
    image: object
    width: float
    top: float = 0
    gap: float = 0
    variant: object = None
    label: object = None


@dataclass
class Placement:
    image: Image.Image
    x: float
    y: float
    label: object
    variant: object


def layout(text, bank, doc_type, seed=None):
    """Koordinat layout dalam piksel sumber (10 px/mm), origin kiri-atas."""
    rng = random.Random(seed)
    missing = set()
    previous = {}
    space_width = 3.0 * 0.15 * bank.mean_width

    def token(char):
        if char == ' ':
            return Token(None, space_width)
        label = label_for(char)
        choices = bank.glyphs.get(label, [])
        if choices:
            candidates = [g for g in choices if g.variant != previous.get(label)] or choices
            glyph = rng.choice(candidates)
            previous[label] = glyph.variant
            scale = rng.uniform(0.95, 1.05)
            size = tuple(max(1, round(v*scale)) for v in glyph.image.size)
            img = glyph.image.resize(size, Image.Resampling.BICUBIC)
            rotated = img.rotate(rng.uniform(-3, 3), Image.Resampling.BICUBIC, expand=True)
            top = -glyph.ascent*scale - (rotated.height-img.height)/2
            gap = max(1, 0.15*bank.mean_widths[label] + rng.uniform(-3, 3))
            return Token(rotated, rotated.width, top+rng.uniform(-4, 4), gap, glyph.variant, label)
        missing.add(char)
        image = Image.new('RGBA', (max(8, round(bank.mean_width)), max(8, round(bank.xheight))), (0, 0, 0, 0))
        ImageDraw.Draw(image).rectangle((0, 0, image.width-1, image.height-1), outline='black', width=1)
        return Token(image, image.width, -image.height, max(1, 0.15*bank.mean_width))

    paragraphs = [[token(c) for c in line] for line in normalize_text(text).split('\n')]
    margin = MARGINS[doc_type] * PX_MM
    limit = 210*PX_MM - 2*margin
    if any(t.width > limit for p in paragraphs for t in p):
        raise ValueError('Glyph lebih lebar dari area tulis; periksa glyph bank.')
    lines = []
    for paragraph in paragraphs:
        line, used = [], 0
        # Kelompokkan kata; spasi di awal baris tetap dihitung satu per satu.
        groups = []
        for t in paragraph:
            if t.image is None or not groups or groups[-1][-1].image is None:
                groups.append([t])
            else:
                groups[-1].append(t)
        for group in groups:
            width = sum(t.width+t.gap for t in group)
            if line and used+width > limit and width <= limit:
                lines.append(line)
                line, used = [], 0
                if group[0].image is None:
                    continue
            for t in group:
                if line and used+t.width > limit:
                    lines.append(line)
                    line, used = [], 0
                    if t.image is None:
                        continue
                line.append(t)
                used += t.width+t.gap
        lines.append(line)

    tokens = [t for p in paragraphs for t in p if t.image is not None]
    # Envelope semua glyph + jitter baseline menjamin baris tidak bertumpuk.
    top = min([t.top for t in tokens] + [-bank.xheight]) - 3
    bottom = max([t.top+t.image.height for t in tokens] + [0]) + 3
    line_height = max(bank.xheight*2.4, bottom-top+1)
    pages, baselines = [[]], [[]]
    baseline = margin-top
    for line in lines:
        if baseline+bottom > 297*PX_MM-margin:
            pages.append([])
            baselines.append([])
            baseline = margin-top
        shifted = baseline+rng.uniform(-3, 3)
        baselines[-1].append(shifted)
        x = margin
        for t in line:
            if t.image is not None:
                pages[-1].append(Placement(t.image, x, shifted+t.top, t.label, t.variant))
            x += t.width+t.gap
        baseline += line_height
    return pages, baselines, sorted(missing), line_height


def render_document(text, user_id, doc_type='catatan', output_dir='outputs',
                    formats=('pdf', 'png'), seed=None, bank_root='glyph_bank',
                    guidelines=False):
    if doc_type not in MARGINS:
        raise ValueError('Jenis dokumen tersedia: catatan atau surat; undangan ditunda.')
    if not formats or set(formats) - {'pdf', 'png'}:
        raise ValueError('Format keluaran harus pdf dan/atau png.')
    started = time.perf_counter()
    bank = GlyphBank(user_id, bank_root)
    pages, baselines, missing, line_height = layout(text, bank, doc_type, seed)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'document.pdf').exists() or (out / 'render_report.json').exists() or list(out.glob('page_*.png')):
        raise ValueError('Folder output sudah berisi hasil render; gunakan folder baru.')
    pdf_path = out / 'document.pdf'
    pdf = canvas.Canvas(str(pdf_path), pagesize=A4, invariant=1) if 'pdf' in formats else None
    if pdf:
        pdf.setAuthor('')
        pdf.setTitle(WATERMARK)
        pdf.setSubject(json.dumps({'user_id': user_id, 'doc_type': doc_type}))
    png_paths = []
    factor = DPI/25.4/PX_MM
    font = ImageFont.load_default(size=round(7*DPI/72))
    for n, placements in enumerate(pages, 1):
        preview = Image.new('RGB', PAGE_PX, 'white') if 'png' in formats else None
        draw = ImageDraw.Draw(preview) if preview else None
        if guidelines and doc_type == 'catatan':
            for y in baselines[n-1]:
                if draw:
                    draw.line((20*PX_MM*factor, y*factor, 190*PX_MM*factor, y*factor), fill='#dddddd')
                if pdf:
                    pdf.setStrokeColorRGB(0.87, 0.87, 0.87)
                    pdf.line(20*mm, (297-y/PX_MM)*mm, 190*mm, (297-y/PX_MM)*mm)
        for p in placements:
            if preview:
                size = tuple(max(1, round(v*factor)) for v in p.image.size)
                img = p.image.resize(size, Image.Resampling.BICUBIC)
                preview.paste(img, (round(p.x*factor), round(p.y*factor)), img)
            if pdf:
                pdf.drawImage(ImageReader(p.image), p.x/PX_MM*mm,
                              (297-(p.y+p.image.height)/PX_MM)*mm,
                              p.image.width/PX_MM*mm, p.image.height/PX_MM*mm, mask='auto')
        if preview:
            draw.text((PAGE_PX[0]/2, (297-10)*DPI/25.4), WATERMARK,
                      font=font, anchor='mm', fill='#777777')
            path = out / f'page_{n:03d}.png'
            preview.save(path, dpi=(DPI, DPI))
            png_paths.append(str(path))
        if pdf:
            pdf.setFillColorRGB(0.47, 0.47, 0.47)
            pdf.setFont('Helvetica', 7)
            pdf.drawCentredString(A4[0]/2, 10*mm, WATERMARK)
            pdf.showPage()
    if pdf:
        pdf.save()
    result = {'user_id': user_id, 'doc_type': doc_type, 'seed': seed,
              'pages': len(pages), 'pdf': str(pdf_path) if pdf else None, 'png': png_paths,
              'missing_characters': missing, 'below_ideal_labels': sorted(bank.below_ideal),
              'glyph_instances': sum(len(p) for p in pages),
              'line_height_mm': round(float(line_height/PX_MM), 3),
              'elapsed_seconds': round(time.perf_counter()-started, 4)}
    (out / 'render_report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', required=True)
    parser.add_argument('--text-file', required=True, type=Path, help='Teks UTF-8; isi tidak ditulis ke log.')
    parser.add_argument('--doc-type', choices=tuple(MARGINS), default='catatan')
    parser.add_argument('--out', default='outputs')
    parser.add_argument('--format', nargs='+', choices=('pdf', 'png'), default=['pdf', 'png'])
    parser.add_argument('--seed', type=int)
    parser.add_argument('--bank-root', default='glyph_bank')
    parser.add_argument('--guidelines', action='store_true')
    args = parser.parse_args()
    try:
        result = render_document(args.text_file.read_text(encoding='utf-8'), args.user,
                                 args.doc_type, args.out, args.format, args.seed,
                                 args.bank_root, args.guidelines)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f'Render dihentikan: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
