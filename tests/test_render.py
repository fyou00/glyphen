"""Uji renderer dengan bank buatan; tidak menyimpan sampel pribadi."""

import base64
import json
from pathlib import Path
import re
import tempfile
import unittest
import zlib

from PIL import Image, ImageDraw

from render_document import (GlyphBank, LETTERS, PAGE_PX, WATERMARK,
                             layout, normalize_text, render_document)


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / 'demo'
        self.folder.mkdir()
        entries, labels = [], {}
        for label in LETTERS:
            labels[label] = {'available': 3}
            for variant in (1, 2, 3):
                path = self.folder / 'glyphs' / label / f'{variant}.png'
                path.parent.mkdir(parents=True, exist_ok=True)
                im = Image.new('L', (80, 96 if label.startswith('upper_') else 56), 255)
                draw = ImageDraw.Draw(im)
                draw.line([(20, 12), (20, 40), (30+variant*3, 30), (20, 12)], fill=25, width=3)
                im.save(path)
                entries.append({'label': label, 'variant': variant, 'status': 'ok',
                                'file': str(path.relative_to(self.root))})
        self.write('manifest.json', {'user': 'demo', 'entries': entries})
        self.write('coverage.json', {'user_id': 'demo', 'labels': labels})
        self.write('consent.json', {'user_id': 'demo', 'owner_is_uploader': True,
                                  'consent_statement': 'Saya pemilik dan menyetujui pemrosesan.'})
        self.write('extraction_report.json', {'visual_review': {'passed': True}})

    def write(self, name, data):
        (self.folder / name).write_text(json.dumps(data))

    def read(self, name):
        return json.loads((self.folder / name).read_text())

    def bank(self):
        return GlyphBank('demo', self.root)

    def render(self, text, folder, **kwargs):
        return render_document(text, 'demo', output_dir=self.root/folder,
                               bank_root=self.root, **kwargs)

    def test_normalization_preserves_indentation_newlines_and_case(self):
        self.assertEqual(normalize_text('  Aa\t B\r\n\tC  D\rE'), '  Aa B\n    C D\nE')

    def test_consent_owner_review_and_cross_user_path_are_enforced(self):
        consent = self.read('consent.json')
        for field, value in [('user_id', 'someone_else'), ('owner_is_uploader', False),
                             ('consent_statement', '')]:
            self.write('consent.json', {**consent, field: value})
            with self.assertRaises(ValueError):
                self.bank()
        self.write('consent.json', consent)
        self.write('extraction_report.json', {'visual_review': {'passed': False}})
        with self.assertRaises(ValueError):
            self.bank()
        self.write('extraction_report.json', {'visual_review': {'passed': True}})
        manifest = self.read('manifest.json')
        manifest['entries'][0]['file'] = '../outside.png'
        self.write('manifest.json', manifest)
        with self.assertRaisesRegex(ValueError, 'keluar'):
            self.bank()

    def test_missing_user_duplicate_entries_and_missing_files_are_rejected(self):
        with self.assertRaises(ValueError):
            GlyphBank('unknown', self.root)
        with self.assertRaises(ValueError):
            GlyphBank('../demo', self.root)
        manifest = self.read('manifest.json')
        self.write('manifest.json', {**manifest, 'entries': manifest['entries']+[manifest['entries'][0]]})
        with self.assertRaisesRegex(ValueError, 'duplikat'):
            self.bank()
        self.write('manifest.json', manifest)
        (self.root / manifest['entries'][0]['file']).unlink()
        with self.assertRaisesRegex(ValueError, 'tidak terbaca'):
            self.bank()

    def test_real_coverage_is_checked_instead_of_trusting_flags(self):
        manifest, coverage = self.read('manifest.json'), self.read('coverage.json')
        manifest['entries'] = [e for e in manifest['entries'] if (e['label'], e['variant']) != ('lower_a', 3)]
        self.write('manifest.json', manifest)
        with self.assertRaisesRegex(ValueError, 'tidak cocok'):
            self.bank()
        coverage['labels']['lower_a']['available'] = 2
        self.write('coverage.json', coverage)
        with self.assertRaisesRegex(ValueError, 'belum lengkap'):
            self.bank()

    def test_edge_glyph_requires_explicit_review(self):
        manifest = self.read('manifest.json')
        manifest['entries'][0]['status'] = 'touches_edge'
        self.write('manifest.json', manifest)
        with self.assertRaisesRegex(ValueError, 'belum ditinjau'):
            self.bank()
        self.write('extraction_report.json', {'visual_review': {'passed': True,
                   'touches_edge_review': [{'label': 'lower_a', 'variant': 1, 'accepted': True}]}})
        self.assertEqual(len(self.bank().glyphs['lower_a']), 3)

    def test_seed_repeatability_and_variation(self):
        a = self.render('Aa banana banana', 'a', seed=7)
        b = self.render('Aa banana banana', 'b', seed=7)
        c = self.render('Aa banana banana', 'c', seed=8)
        for key in ('pdf',):
            self.assertEqual(Path(a[key]).read_bytes(), Path(b[key]).read_bytes())
        self.assertEqual(Path(a['png'][0]).read_bytes(), Path(b['png'][0]).read_bytes())
        self.assertNotEqual(Path(a['png'][0]).read_bytes(), Path(c['png'][0]).read_bytes())

    def test_variants_do_not_repeat_for_a_label(self):
        pages, _, _, _ = layout('a aaaaa aaa', self.bank(), 'catatan', 9)
        variants = [p.variant for page in pages for p in page]
        self.assertTrue(all(a != b for a, b in zip(variants, variants[1:])))

    def test_wrap_pagination_margin_and_no_rectangle_overlap(self):
        # Kata panjang, indentasi, baris kosong, dan pergantian halaman.
        text = '  ' + 'a'*600 + '\n\n' + ('Abc def ghi jkl mno\n'*70)
        for doc_type, margin in [('catatan', 200), ('surat', 250)]:
            pages, baselines, missing, _ = layout(text, self.bank(), doc_type, 4)
            self.assertGreater(len(pages), 1)
            self.assertFalse(missing)
            self.assertEqual(sum(len(p) for p in pages), len(text.replace(' ', '').replace('\n', '')))
            for page in pages:
                for p in page:
                    self.assertGreaterEqual(p.x, margin)
                    self.assertGreaterEqual(p.y, margin)
                    self.assertLessEqual(p.x+p.image.width, 2100-margin)
                    self.assertLessEqual(p.y+p.image.height, 2970-margin)
                for a, b in zip(page, page[1:]):
                    overlaps = (a.x < b.x+b.image.width and b.x < a.x+a.image.width and
                                a.y < b.y+b.image.height and b.y < a.y+a.image.height)
                    self.assertFalse(overlaps)
            # Baris kosong eksplisit tidak hilang.
            short, ys, _, _ = layout('A\n\nB', self.bank(), doc_type, 4)
            self.assertEqual(len(ys[0]), 3)

    def test_missing_characters_get_placeholders_and_report(self):
        result = self.render('a@é#\x00', 'missing', seed=1)
        self.assertEqual(set(result['missing_characters']), {'@', 'é', '#', '\x00'})
        self.assertEqual(result['glyph_instances'], 5)
        report = json.loads((self.root/'missing/render_report.json').read_text())
        self.assertNotIn('text', report)

    def test_every_page_has_watermark_pdf_and_png(self):
        result = self.render('Abc\n'*75, 'pages', seed=1, guidelines=True)
        pdf = Path(result['pdf']).read_bytes()
        self.assertEqual(len(re.findall(rb'/Type\s*/Page\b', pdf)), result['pages'])
        texts = []
        for stream in re.findall(rb'stream\r?\n(.*?)endstream', pdf, re.S):
            try:
                texts.append(zlib.decompress(base64.a85decode(stream.strip(), adobe=True)))
            except (ValueError, zlib.error):
                pass
        self.assertEqual(sum(t.count(WATERMARK.encode()) for t in texts), result['pages'])
        for path in result['png']:
            with Image.open(path) as im:
                self.assertEqual(im.size, PAGE_PX)
                self.assertEqual(im.mode, 'RGB')
                self.assertEqual(im.getpixel((0, 0)), (255, 255, 255))
                self.assertGreater(im.info['dpi'][0], 299)
                footer = im.crop((0, PAGE_PX[1]-180, PAGE_PX[0], PAGE_PX[1]-70)).convert('L')
                self.assertLess(footer.getextrema()[0], 180)
                self.assertNotIn('user_id', im.info)

    def test_formats_empty_input_and_existing_output(self):
        pdf = self.render('', 'empty_pdf', formats=['pdf'])
        self.assertEqual(pdf['pages'], 1)
        self.assertEqual(pdf['png'], [])
        self.assertEqual(pdf['glyph_instances'], 0)
        png = self.render('A', 'only_png', formats=['png'])
        self.assertIsNone(png['pdf'])
        with self.assertRaisesRegex(ValueError, 'sudah berisi'):
            self.render('A', 'only_png')
        with self.assertRaises(ValueError):
            self.render('A', 'invitation', doc_type='undangan')


if __name__ == '__main__':
    unittest.main()
