"""Siklus profil dengan halaman template buatan dan data sementara."""

import io
import json
from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app import create_app
from extract_glyphs import H_MM, MM, page_layout
from profiles import MAX_FILE_BYTES, write_json, ProfileStore


def sample(page, empty_label=None, edge=False):
    image = Image.new('RGB', (2100, 2970), 'white')
    draw = ImageDraw.Draw(image)
    for x, y in ((100, 100), (1920, 100), (1920, 2790), (100, 2790)):
        draw.rectangle((x, y, x+80, y+80), fill='black')
    for label, variant, x, y, w, h in page_layout(page):
        left, top = round(x*MM), round((H_MM-y-h)*MM)
        draw.rectangle((left, top, left+round(w*MM), top+round(h*MM)), outline='black', width=2)
        if label == empty_label:
            continue
        cx = left+round(w*MM*.45)
        bottom = top+round(h*MM*.65)
        if edge and label == 'lower_a' and variant == 0:
            bottom = top+round(h*MM)-12
        draw.line([(cx, top+round(h*MM*.35)), (cx, bottom), (cx+10, bottom-8)], fill='black', width=3)
    return image


def png_bytes(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples = [png_bytes(sample(n)) for n in (1, 2, 3)]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bank = self.root/'bank'
        self.output = self.root/'output'
        self.client = TestClient(create_app(bank_root=self.bank, output_root=self.output), base_url='http://127.0.0.1')
        self.addCleanup(self.client.close)

    def create(self, name='Nama pemilik'):
        response = self.client.post('/api/profiles', json={'display_name': name, 'consent': True})
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()['user_id']

    def upload(self, user, images=None, rotations=None):
        data = images or self.samples
        files = {f'tpl0{n}': (f'page{n}.png', content, 'image/png') for n, content in enumerate(data, 1)}
        return self.client.post(f'/api/profiles/{user}/samples', files=files,
                                data={'owner_confirmation': 'true', **{f'rotation{n}': str(v) for n, v in enumerate(rotations or [0, 0, 0], 1)}})

    def approve(self, user, profile):
        return self.client.post(f'/api/profiles/{user}/review', json={
            'crops_correct': True, 'pages_checked': [1, 2, 3],
            'accepted_edges': [{'label': e['label'], 'variant': e['variant']} for e in profile['edges']]})

    def test_empty_state_and_identity_before_upload(self):
        self.assertFalse(self.client.get('/api/profile').json()['ready'])
        self.assertEqual(self.client.get('/api/profiles').json()['profiles'], [])
        for payload in ({'display_name': 'A', 'consent': False}, {'display_name': 'A', 'consent': 'true'},
                        {'display_name': '  ', 'consent': True}, {'display_name': 'a\nb', 'consent': True}):
            self.assertEqual(self.client.post('/api/profiles', json=payload).status_code, 422)
        self.assertEqual(self.upload('missing').status_code, 404)
        self.assertFalse(self.bank.exists())
        user = self.create()
        files = {f'tpl0{n}': (f'page{n}.png', content, 'image/png') for n, content in enumerate(self.samples, 1)}
        self.assertEqual(self.client.post(f'/api/profiles/{user}/samples', files=files).status_code, 422)
        self.assertFalse((self.bank/user/'sources').exists())

    def test_create_upload_review_activate_rename_render_delete(self):
        user = self.create()
        consent = json.loads((self.bank/user/'consent.json').read_text())
        self.assertTrue(consent['owner_is_uploader'])
        self.assertEqual(consent['owner_name'], 'Nama pemilik')
        profile = self.upload(user).json()
        self.assertEqual(profile['status'], 'awaiting_review')
        self.assertFalse((self.bank/user/'coverage.json').exists())
        self.assertEqual(self.client.post('/api/render', json={'text': 'Abc', 'user_id': user}).status_code, 422)
        for page in profile['pages']:
            self.assertEqual(self.client.get(page['url']).status_code, 200)
        self.assertEqual(self.client.post(f'/api/profiles/{user}/review', json={
            'crops_correct': True, 'pages_checked': [1, 2], 'accepted_edges': []}).status_code, 422)
        ready = self.approve(user, profile)
        self.assertEqual(ready.status_code, 200, ready.text)
        self.assertTrue(ready.json()['ready'])
        renamed = self.client.patch(f'/api/profiles/{user}', json={'display_name': 'Nama baru'})
        self.assertEqual(renamed.json()['user_id'], user)
        self.assertEqual(renamed.json()['display_name'], 'Nama baru')
        render = self.client.post('/api/render', json={'text': 'Abc', 'user_id': user}).json()
        self.assertEqual(self.client.get(render['pdf_url']).status_code, 200)
        self.assertEqual(self.client.request('DELETE', f'/api/profiles/{user}', json={'confirm': False}).status_code, 422)
        self.assertTrue((self.bank/user).exists())
        other = self.create('Tetap ada')
        deleted = self.client.request('DELETE', f'/api/profiles/{user}', json={'confirm': True})
        self.assertEqual(deleted.status_code, 200)
        self.assertFalse((self.bank/user).exists())
        self.assertTrue((self.bank/other).exists())
        self.assertEqual(self.client.get(render['pdf_url']).status_code, 404)
        self.assertFalse((self.output/render['id']).exists())

    def test_coverage_shortfall_requests_specific_page_and_retry(self):
        user = self.create()
        p = self.upload(user, [png_bytes(sample(1, empty_label='lower_a')), *self.samples[1:]]).json()
        self.assertEqual(p['empty_per_label']['lower_a'], 5)
        reviewed = self.approve(user, p).json()
        self.assertFalse(reviewed['ready'])
        self.assertEqual(reviewed['repeat_pages'], [1])
        self.assertIn('lower_a', reviewed['incomplete_labels'])
        self.assertFalse((self.bank/user/'glyphs/lower_a').exists())
        (self.bank/user/'profile.json').unlink()  # Bank lama tanpa metadata profil juga dapat diperbaiki.
        fresh = self.upload(user).json()
        self.assertFalse((self.bank/user/'coverage.json').exists())
        self.assertTrue(self.approve(user, fresh).json()['ready'])
        self.assertEqual(len(list((self.bank/user/'glyphs/lower_a').glob('*.png'))), 5)

    def test_wrong_crop_stops_before_coverage_and_edges_require_review(self):
        user = self.create()
        p = self.upload(user, [png_bytes(sample(1, edge=True)), *self.samples[1:]]).json()
        self.assertTrue(p['edges'])
        self.assertEqual(self.client.post(f'/api/profiles/{user}/review', json={
            'crops_correct': True, 'pages_checked': [1, 2, 3], 'accepted_edges': []}).status_code, 422)
        rejected = self.client.post(f'/api/profiles/{user}/review', json={'crops_correct': False}).json()
        self.assertEqual(rejected['status'], 'needs_samples')
        self.assertFalse((self.bank/user/'coverage.json').exists())
        p = self.upload(user, [png_bytes(sample(1, edge=True)), *self.samples[1:]]).json()
        self.assertTrue(self.approve(user, p).json()['ready'])

    def test_rotations_metadata_removal_invalid_images_and_upload_limit(self):
        user = self.create()
        self.assertEqual(self.upload(user, [b'not image', *self.samples[1:]]).status_code, 422)
        self.assertEqual(self.upload(user, [self.samples[0]]*3).status_code, 422)
        self.assertEqual(self.upload(user, rotations=[45, 0, 0]).status_code, 422)
        self.assertEqual(self.upload(user, [b'x'*(MAX_FILE_BYTES+1), *self.samples[1:]]).status_code, 422)
        source = sample(1).rotate(180)
        buffer = io.BytesIO()
        exif = Image.Exif(); exif[315] = 'Private artist'
        source.save(buffer, format='JPEG', quality=95, exif=exif)
        result = self.upload(user, [buffer.getvalue(), *self.samples[1:]], [180, 0, 0])
        self.assertEqual(result.status_code, 200, result.text)
        for path in (self.bank/user/'sources').rglob('*.png'):
            with Image.open(path) as image:
                self.assertNotIn('exif', image.info)
                self.assertFalse(image.getexif())
        self.assertGreater(result.json()['counts']['ok'], 300)

    def test_deletion_archives_sources_owned_artifacts_and_path_isolation(self):
        user = self.create()
        other = self.create('Lain')
        archive = self.bank/'history'/user/'attempt01'; archive.mkdir(parents=True)
        (archive/'sample.txt').write_text('private')
        own = self.output/'audit'; own.mkdir(parents=True)
        write_json(own/'owner.json', {'user_id': user})
        (own/'preview.png').write_bytes(b'private')
        keep = self.output/'other'; keep.mkdir()
        write_json(keep/'owner.json', {'user_id': other})
        mixed = self.output/'mixed'; mixed.mkdir()
        write_json(mixed/'owner.json', {'user_id': user})
        (mixed/'own-preview.png').write_bytes(b'private')
        foreign = mixed/'foreign'; foreign.mkdir()
        write_json(foreign/'render_report.json', {'user_id': other})
        (foreign/'document.pdf').write_bytes(b'keep')
        outside = self.root/'outside'; outside.mkdir()
        (outside/'keep').write_text('keep')
        (self.bank/'symlink').symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.client.request('DELETE', '/api/profiles/symlink', json={'confirm': True}).status_code, 404)
        self.assertEqual(self.client.request('DELETE', f'/api/profiles/{user}', json={'confirm': True}).status_code, 200)
        self.assertFalse(own.exists());self.assertFalse(archive.exists())
        self.assertTrue(keep.exists());self.assertTrue((outside/'keep').exists())
        self.assertTrue((foreign/'document.pdf').exists())
        self.assertFalse((mixed/'own-preview.png').exists())
        self.assertFalse((mixed/'owner.json').exists())
        self.assertTrue((self.bank/other).exists())


if __name__ == '__main__':
    unittest.main()
