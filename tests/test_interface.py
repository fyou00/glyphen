"""Pengujian API lokal dengan glyph buatan, tanpa sampel pengguna."""

import json
from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app import create_app
from render_document import LETTERS


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root/'bank/demo'
        self.folder.mkdir(parents=True)
        entries, labels = [], {}
        for label in LETTERS:
            labels[label] = {'available': 3}
            for variant in (1, 2, 3):
                path = self.folder/'glyphs'/label/f'{variant}.png'
                path.parent.mkdir(parents=True, exist_ok=True)
                image = Image.new('L', (80, 96 if label.startswith('upper_') else 56), 255)
                ImageDraw.Draw(image).line([(20, 12), (20, 40), (32+variant, 25)], fill=25, width=3)
                image.save(path)
                entries.append({'label': label, 'variant': variant, 'status': 'ok',
                                'file': str(path.relative_to(self.root/'bank'))})
        for name, data in {
            'manifest.json': {'user': 'demo', 'entries': entries},
            'coverage.json': {'user_id': 'demo', 'labels': labels},
            'consent.json': {'user_id': 'demo', 'owner_is_uploader': True, 'consent_statement': 'Saya setuju.'},
            'extraction_report.json': {'visual_review': {'passed': True}},
        }.items():
            (self.folder/name).write_text(json.dumps(data))
        self.app = create_app('demo', self.root/'bank', self.root/'output')
        self.client = TestClient(self.app, base_url='http://127.0.0.1')
        self.addCleanup(self.client.close)

    def test_page_profile_and_private_headers(self):
        page = self.client.get('/')
        self.assertEqual(page.status_code, 200)
        self.assertIn('Catatan dalam tulisan tanganmu', page.text)
        self.assertIn("connect-src 'self'", page.headers['content-security-policy'])
        self.assertEqual(page.headers['cache-control'], 'no-store')
        profile = self.client.get('/api/profile').json()
        self.assertTrue(profile['ready'])
        self.assertEqual(profile['minimum_variants'], 3)
        self.assertNotIn('consent_statement', profile)
        self.assertEqual(self.client.get('/assets/app.js').status_code, 200)
        self.assertEqual(self.client.get('/glyph_bank/demo/consent.json').status_code, 404)

    def test_render_preview_download_and_text_not_stored(self):
        text = 'Abc @'
        response = self.client.post('/api/render', json={'text': text, 'seed': 7})
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data['missing_characters'], ['@'])
        self.assertEqual(data['pages'], 1)
        png = self.client.get(data['png_urls'][0])
        self.assertTrue(png.content.startswith(b'\x89PNG'))
        pdf = self.client.get(data['pdf_url']+'?download=true')
        self.assertTrue(pdf.content.startswith(b'%PDF'))
        self.assertIn('attachment', pdf.headers['content-disposition'])
        self.assertEqual(pdf.headers['cache-control'], 'no-store')
        report = (self.root/'output'/data['id']/'render_report.json').read_text()
        self.assertNotIn(text, report)
        self.assertEqual(sorted(p.name for p in (self.root/'output'/data['id']).iterdir()),
                         ['document.pdf', 'page_001.png', 'render_report.json'])
        self.assertEqual(self.client.get(f'/api/renders/{data["id"]}/render_report.json').status_code, 404)
        self.assertEqual(self.client.get('/api/renders/'+'f'*32+'/document.pdf').status_code, 404)

    def test_invalid_fields_and_cross_origin_requests(self):
        for payload in ({'text': ''}, {'text': '  '}, {'text': 'a'*12001},
                        {'text': 'abc', 'doc_type': 'undangan'}, {'text': 'abc', 'seed': -1},
                        {'text': 'abc', 'seed': True}, {'text': ['abc']}):
            self.assertEqual(self.client.post('/api/render', json=payload).status_code, 422)
        denied = self.client.post('/api/render', json={'text': 'Abc'}, headers={'Origin': 'https://outside.example'})
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(self.client.get('/api/profile', headers={'Host': 'outside.example'}).status_code, 400)
        self.assertFalse((self.root/'output').exists())

    def test_unready_bank_blocks_render(self):
        (self.folder/'consent.json').unlink()
        self.assertFalse(self.client.get('/api/profile').json()['ready'])
        self.assertEqual(self.client.post('/api/render', json={'text': 'Abc'}).status_code, 422)

    def test_local_api_multiple_pages_and_isolated_results(self):
        a = self.client.post('/api/render', json={'text': 'Abc\n'*65, 'doc_type': 'surat', 'seed': 1}).json()
        b = self.client.post('/api/render', json={'text': 'Abc', 'seed': 1}).json()
        self.assertGreater(a['pages'], 1)
        self.assertNotEqual(a['id'], b['id'])
        for path in a['png_urls']:
            self.assertEqual(self.client.get(path).status_code, 200)


if __name__ == '__main__':
    unittest.main()
