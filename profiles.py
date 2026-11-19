"""Profil lokal, ekstraksi bertahap, tinjauan pemilik, dan penghapusan turunan."""

from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import unicodedata
import uuid

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from extract_glyphs import process_page
from render_document import GlyphBank, LETTERS, read_json

CONSENT = ('Saya menyatakan sampel ini adalah tulisan tangan saya sendiri dan menyetujui '
           'pemrosesannya untuk glyph bank pribadi serta dokumen berpenanda '
           'TIDAK RESMI - HASIL GENERASI.')
MAX_FILE_BYTES = 10 * 1024 * 1024


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, data):
    path = Path(path)
    temp = path.with_name('.'+uuid.uuid4().hex+'.tmp')
    try:
        with os.fdopen(os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write('\n')
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def optional_json(path):
    try:
        data = read_json(path)
        return data if isinstance(data, dict) else {}
    except (ValueError, OSError):
        return {}


class ProfileStore:
    def __init__(self, bank_root, artifact_root, scan_root=None):
        self.root = Path(bank_root).resolve()
        self.artifacts = Path(artifact_root).resolve()
        self.scans = Path(scan_root).resolve() if scan_root else None

    def folder(self, user_id):
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', user_id):
            raise ValueError('ID profil tidak valid.')
        path = self.root/user_id
        if path.is_symlink() or path.resolve().parent != self.root or not path.is_dir():
            raise FileNotFoundError('Profil tidak ditemukan.')
        return path

    def create(self, display_name, consent):
        if consent is not True:
            raise ValueError('Persetujuan pemilik tulisan wajib diberikan sebelum upload.')
        name = self.valid_name(display_name)
        self.root.mkdir(parents=True, exist_ok=True)
        user_id = 'p_'+uuid.uuid4().hex
        path = self.root/user_id
        path.mkdir(mode=0o700)
        write_json(path/'profile.json', {'user_id': user_id, 'display_name': name,
                                        'status': 'draft', 'created_at': now()})
        write_json(path/'consent.json', {'user_id': user_id, 'owner_is_uploader': True,
                                         'owner_name': name, 'consent_statement': CONSENT,
                                         'consent_date': now(), 'pages': []})
        return self.detail(user_id)

    @staticmethod
    def valid_name(name):
        name = name.strip()
        if not 1 <= len(name) <= 80 or any(unicodedata.category(c).startswith('C') for c in name):
            raise ValueError('Nama/alias wajib diisi, maksimal 80 karakter, tanpa karakter kontrol.')
        return name

    def rename(self, user_id, name):
        path = self.folder(user_id)
        metadata = optional_json(path/'profile.json')
        metadata.update(user_id=user_id, display_name=self.valid_name(name), updated_at=now())
        write_json(path/'profile.json', metadata)
        return self.detail(user_id)

    def list(self):
        if not self.root.exists():
            return []
        profiles = []
        for path in sorted(self.root.iterdir()):
            if (path.is_dir() and not path.is_symlink() and not path.name.startswith('.')
                    and any((path/name).is_file() for name in ('profile.json', 'manifest.json'))):
                try:
                    profiles.append(self.detail(path.name, include_review=False))
                except (ValueError, OSError, KeyError, TypeError):
                    continue
        return profiles

    def detail(self, user_id, include_review=True):
        path = self.folder(user_id)
        metadata = optional_json(path/'profile.json')
        status = metadata.get('status', 'ready')
        ready, minimum, detail = False, 0, metadata.get('detail', '')
        if status == 'ready':
            try:
                bank = GlyphBank(user_id, self.root)
                ready = True
                minimum = min(len(bank.glyphs[label]) for label in LETTERS)
            except (ValueError, OSError, KeyError, TypeError):
                status = 'needs_samples'
                detail = 'Periksa persetujuan, tinjauan potongan, dan coverage profil.'
        result = {'user_id': user_id, 'display_name': metadata.get('display_name', user_id),
                  'status': status, 'ready': ready, 'minimum_variants': minimum,
                  'letter_labels': len(LETTERS), 'max_characters': 12000, 'detail': detail}
        if include_review:
            report = optional_json(path/'extraction_report.json')
            result['counts'] = report.get('counts')
            result['empty_per_label'] = report.get('empty_per_label', {})
            result['pages'] = [{'page': n, 'url': f'/api/profiles/{user_id}/debug/{n}'}
                               for n in (1, 2, 3) if (path/f'debug_page{n}.png').is_file()]
            entries = optional_json(path/'manifest.json').get('entries', [])
            result['edges'] = [{'label': e['label'], 'variant': e['variant'],
                                'url': f'/api/profiles/{user_id}/glyph/{e["label"]}/{e["variant"]}'}
                               for e in entries if e['status'] == 'touches_edge']
            coverage = optional_json(path/'coverage.json')
            result['incomplete_labels'] = coverage.get('incomplete_letter_labels', [])
            result['repeat_pages'] = coverage.get('repeat_pages', [])
        return result

    def upload(self, user_id, files, rotations):
        path = self.folder(user_id)
        metadata = optional_json(path/'profile.json')
        status = metadata.get('status') or ('ready' if self.detail(user_id, False)['ready'] else 'needs_samples')
        if status not in ('draft', 'awaiting_review', 'needs_samples'):
            raise ValueError('Buat profil baru untuk sampel baru; profil siap pakai tidak ditimpa.')
        metadata.update(user_id=user_id, display_name=metadata.get('display_name', user_id))
        consent = read_json(path/'consent.json')
        if consent.get('user_id') != user_id or consent.get('owner_is_uploader') is not True or not consent.get('consent_statement'):
            raise ValueError('Persetujuan dan identitas pemilik belum valid.')
        images = []
        for n, (data, rotation) in enumerate(zip(files, rotations), 1):
            if not data or len(data) > MAX_FILE_BYTES or rotation not in (0, 90, 180, 270):
                raise ValueError(f'TPL-0{n}: gunakan JPEG/PNG maksimal 10 MiB dan rotasi kelipatan 90°.')
            try:
                with Image.open(io.BytesIO(data)) as source:
                    if source.format not in ('JPEG', 'PNG') or source.width*source.height > 20000000 or getattr(source, 'n_frames', 1) != 1:
                        raise ValueError(f'TPL-0{n}: gunakan satu gambar JPEG/PNG maksimal 20 megapiksel.')
                    decoded = ImageOps.exif_transpose(source).convert('RGBA')
                    clean = Image.new('RGB', decoded.size, 'white')
                    clean.paste(decoded, mask=decoded.getchannel('A'))
            except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
                raise ValueError(f'TPL-0{n}: gambar tidak dapat dibaca.') from exc
            images.append(clean)
        if len(images) != 3 or len(set(hashlib.sha256(im.tobytes()).hexdigest() for im in images)) != 3:
            raise ValueError('Upload tiga gambar halaman berbeda dalam urutan TPL-01, TPL-02, TPL-03.')
        attempt = path/'sources'/uuid.uuid4().hex
        attempt.mkdir(parents=True, mode=0o700)
        result_root = attempt/'results'
        candidate = result_root/user_id
        candidate.mkdir(parents=True)
        entries, pages = [], []
        for n, (image, rotation) in enumerate(zip(images, rotations), 1):
            source = attempt/f'tpl0{n}_source.png'
            image.save(source)
            upright = image.rotate(-rotation, expand=True)
            processed = attempt/f'tpl0{n}.png'
            upright.save(processed)
            pages.append({'page': f'TPL-0{n}', 'processed': str(processed.relative_to(path)),
                          'rotation_degrees': rotation, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
            try:
                process_page(cv2.cvtColor(np.asarray(upright), cv2.COLOR_RGB2BGR), n,
                             user_id, str(result_root), entries)
            except RuntimeError as exc:
                metadata.update(status='needs_samples', detail=f'TPL-0{n}: {exc}', updated_at=now())
                write_json(path/'profile.json', metadata)
                raise ValueError(f'TPL-0{n}: marker belum terbaca. Periksa rotasi dan keempat marker.') from exc
        write_json(candidate/'manifest.json', {'user': user_id, 'entries': entries})
        counts = {s: sum(e['status'] == s for e in entries) for s in ('ok', 'empty', 'touches_edge')}
        empty = {label: sum(e['status'] == 'empty' for e in entries if e['label'] == label)
                 for label in sorted({e['label'] for e in entries})}
        report = {'user_id': user_id, 'counts': counts, 'empty_per_label': empty,
                  'visual_review': {'passed': False, 'touches_edge_review': []}}
        write_json(candidate/'extraction_report.json', report)
        # Semua halaman berhasil sebelum mengganti hasil aktif. Salinan percobaan
        # lengkap tetap tersimpan dalam sources/ dan ikut dihapus bersama profil.
        if (path/'glyphs').exists():
            shutil.rmtree(path/'glyphs')
        if (candidate/'glyphs').exists():
            shutil.copytree(candidate/'glyphs', path/'glyphs')
        for name in ('manifest.json', 'extraction_report.json', 'debug_page1.png', 'debug_page2.png', 'debug_page3.png'):
            shutil.copyfile(candidate/name, path/name)
        (path/'coverage.json').unlink(missing_ok=True)
        consent['pages'] = pages
        consent['source_root'] = 'profile'
        write_json(path/'consent.json', consent)
        metadata.update(status='awaiting_review', detail='', updated_at=now())
        write_json(path/'profile.json', metadata)
        return self.detail(user_id)

    def review(self, user_id, pages_checked, crops_correct, accepted_edges):
        path = self.folder(user_id)
        metadata = read_json(path/'profile.json')
        if metadata.get('status') != 'awaiting_review':
            raise ValueError('Profil tidak sedang menunggu tinjauan.')
        if crops_correct is not True:
            metadata.update(status='needs_samples', detail='Potongan salah. Perbaiki atau ulangi halaman terkait sebelum melanjutkan.')
            write_json(path/'profile.json', metadata)
            return self.detail(user_id)
        if sorted(pages_checked) != [1, 2, 3]:
            raise ValueError('Periksa dan konfirmasi ketiga halaman debug terlebih dahulu.')
        entries = read_json(path/'manifest.json')['entries']
        expected = {(e['label'], e['variant']) for e in entries if e['status'] == 'touches_edge'}
        actual = {(e['label'], e['variant']) for e in accepted_edges}
        if actual != expected or len(accepted_edges) != len(actual):
            raise ValueError('Periksa dan terima setiap potongan bertanda touches_edge satu per satu.')
        report = read_json(path/'extraction_report.json')
        report['visual_review'] = {'passed': True, 'debug_pages_reviewed': [1, 2, 3],
                                   'reviewer': 'owner', 'reviewed_at': now(),
                                   'touches_edge_review': [{**e, 'accepted': True} for e in accepted_edges]}
        write_json(path/'extraction_report.json', report)
        labels = {}
        for label in sorted({e['label'] for e in entries}):
            group = [e for e in entries if e['label'] == label]
            available = sum(e['status'] in ('ok', 'touches_edge') for e in group)
            labels[label] = {'available': available, 'minimum': 3,
                             'ideal': 5 if label in LETTERS else 3, 'page': group[0]['page']}
        incomplete = [label for label in LETTERS if labels.get(label, {}).get('available', 0) < 3]
        repeat = sorted({labels[label]['page'] for label in incomplete})
        write_json(path/'coverage.json', {'user_id': user_id, 'labels': labels,
                                         'incomplete_letter_labels': incomplete, 'repeat_pages': repeat,
                                         'all_letters_meet_minimum': not incomplete, 'visual_review_passed': True})
        metadata.update(status='needs_samples' if incomplete else 'ready', updated_at=now(),
                        detail='Ulangi halaman '+', '.join(f'TPL-0{n}' for n in repeat)+'.' if incomplete else '')
        if not incomplete:
            try:
                GlyphBank(user_id, self.root)
            except (ValueError, OSError, KeyError, TypeError) as exc:
                metadata.update(status='needs_samples', detail='Glyph belum valid untuk render; periksa kembali sampel.')
        write_json(path/'profile.json', metadata)
        return self.detail(user_id)

    def debug_file(self, user_id, page):
        if page not in (1, 2, 3):
            raise FileNotFoundError('Halaman tidak ditemukan.')
        path = self.folder(user_id)/f'debug_page{page}.png'
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError('Halaman tidak ditemukan.')
        return path

    def glyph_file(self, user_id, label, variant):
        folder = self.folder(user_id)
        for e in read_json(folder/'manifest.json')['entries']:
            if (e['label'], e['variant']) == (label, variant) and e['file']:
                path = (self.root/e['file']).resolve()
                if path.is_relative_to(folder/'glyphs') and path.is_file():
                    return path
        raise FileNotFoundError('Glyph tidak ditemukan.')

    def delete(self, user_id, confirm):
        if confirm is not True:
            raise ValueError('Konfirmasi penghapusan diperlukan.')
        folder = self.folder(user_id)
        targets = [folder]
        history = self.root/'history'/user_id
        if history.is_dir() and not history.is_symlink() and history.resolve().is_relative_to(self.root):
            targets.append(history)
        # Hanya metadata pemilik yang dikenali, bukan path bebas dari request.
        for root in [self.artifacts, self.scans]:
            if not root or not root.exists():
                continue
            for name in ('render_report.json', 'owner.json', 'metadata.json'):
                for marker in root.rglob(name):
                    if marker.is_symlink():
                        continue
                    data = optional_json(marker)
                    owner_ids = data.get('owner_ids', [])
                    if data.get('user_id') != user_id and user_id not in (owner_ids if isinstance(owner_ids, list) else []):
                        continue
                    parent = marker.parent
                    if parent.is_symlink() or not parent.resolve().is_relative_to(root):
                        continue
                    if any(optional_json(report).get('user_id') not in (None, user_id)
                           for report in parent.rglob('render_report.json') if not report.is_symlink()):
                        # Marker memiliki berkas langsung di direktori ini;
                        # subdirektori dengan hasil pemilik lain dipertahankan.
                        if name == 'owner.json':
                            for child in parent.iterdir():
                                if child.is_symlink():
                                    continue
                                other = child.is_dir() and any(
                                    optional_json(p).get('user_id') not in (None, user_id)
                                    for p in child.rglob('render_report.json') if not p.is_symlink())
                                if not other:
                                    targets.append(child)
                        continue
                    if parent == root:
                        # Root scan hanya boleh dihapus bila metadata menyatakan
                        # kepemilikan seluruh direktori melalui owner.json.
                        if name != 'owner.json':
                            continue
                    targets.append(parent)
        unique = sorted(set(targets), key=lambda p: len(p.parts))
        selected = []
        for target in unique:
            if not any(target.is_relative_to(parent) for parent in selected):
                selected.append(target)
        for target in sorted(selected, key=lambda p: p == folder):
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink(missing_ok=True)
        return {'deleted': True, 'user_id': user_id}
