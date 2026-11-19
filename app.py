#!/usr/bin/env python3
"""Antarmuka lokal Glyphen; jalankan python app.py [--user <id>]."""

import argparse
import asyncio
from pathlib import Path
import re
from typing import Literal, Optional
import uuid

from fastapi import FastAPI, HTTPException, Request, File, Form, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StrictInt, StrictStr, StrictBool
from starlette.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from render_document import read_json, render_document
from profiles import ProfileStore, MAX_FILE_BYTES

PROJECT = Path(__file__).resolve().parent
MAX_CHARACTERS = 12000


class RenderInput(BaseModel):
    user_id: Optional[StrictStr] = None
    text: StrictStr = Field(min_length=1, max_length=MAX_CHARACTERS)
    doc_type: Literal['catatan', 'surat'] = 'catatan'
    seed: Optional[StrictInt] = Field(default=None, ge=0, le=2147483647)
    guidelines: bool = False


class ProfileInput(BaseModel):
    display_name: StrictStr = Field(min_length=1, max_length=80)
    consent: StrictBool


class NameInput(BaseModel):
    display_name: StrictStr = Field(min_length=1, max_length=80)


class DeleteInput(BaseModel):
    confirm: StrictBool


class EdgeInput(BaseModel):
    label: StrictStr
    variant: StrictInt


class ReviewInput(BaseModel):
    pages_checked: list[StrictInt] = []
    crops_correct: StrictBool
    accepted_edges: list[EdgeInput] = []


def create_app(user_id=None, bank_root=None, output_root=None):
    if user_id is not None and not re.fullmatch(r'[A-Za-z0-9_-]+', user_id):
        raise ValueError('ID pengguna tidak valid.')
    default_storage = bank_root is None and output_root is None
    bank_root = Path(bank_root or PROJECT/'glyph_bank').resolve()
    output_root = Path(output_root or PROJECT/'outputs/ui').resolve()
    app = FastAPI(title='Glyphen lokal', docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', '[::1]'])
    queue = asyncio.Semaphore(1)
    store = ProfileStore(bank_root, PROJECT/'outputs' if default_storage else output_root,
                         PROJECT/'scan_demo' if default_storage else None)

    def selected_id(explicit=None):
        if explicit:
            store.folder(explicit)
            return explicit
        if user_id and (bank_root/user_id).is_dir():
            return user_id
        profiles = store.list()
        return next((p['user_id'] for p in profiles if p['ready']), profiles[0]['user_id'] if profiles else None)

    @app.exception_handler(FileNotFoundError)
    async def missing_profile(request, exc):
        return JSONResponse({'detail': 'Profil atau berkas tidak ditemukan.'}, status_code=404)

    @app.exception_handler(ValueError)
    async def invalid_profile(request, exc):
        return JSONResponse({'detail': str(exc)}, status_code=422)

    @app.exception_handler(OSError)
    async def storage_error(request, exc):
        return JSONResponse({'detail': 'Penyimpanan lokal belum dapat diakses. Periksa izin folder dan coba lagi.'}, status_code=500)

    @app.middleware('http')
    async def local_requests(request: Request, call_next):
        origin = request.headers.get('origin')
        if origin and origin != str(request.base_url).rstrip('/'):
            return JSONResponse({'detail': 'Permintaan harus berasal dari halaman aplikasi lokal.'}, status_code=403)
        content_length = request.headers.get('content-length', '0')
        limit = 31*1024*1024 if request.url.path.endswith('/samples') else 100000
        if not content_length.isdecimal() or int(content_length) > limit:
            return JSONResponse({'detail': 'Ukuran permintaan terlalu besar.'}, status_code=413)
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' blob:; font-src 'self'; connect-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request, exc):
        return JSONResponse({'detail': 'Periksa isian formulir, persetujuan, dan berkas yang wajib diisi.'}, status_code=422)

    @app.get('/')
    def home():
        return FileResponse(PROJECT/'web/index.html')

    @app.get('/api/profile')
    async def profile(user_id: Optional[str] = None):
        chosen = await asyncio.to_thread(selected_id, user_id)
        return await asyncio.to_thread(store.detail, chosen) if chosen else {
            'user_id': None, 'display_name': '', 'ready': False, 'status': 'empty',
            'detail': 'Tambahkan profil tulisan tangan untuk mulai menulis.'}

    @app.get('/api/profiles')
    async def profiles():
        items = await asyncio.to_thread(store.list)
        default_id = next((p['user_id'] for p in items if p['user_id'] == user_id), None)
        if not default_id:
            default_id = next((p['user_id'] for p in items if p['ready']), items[0]['user_id'] if items else None)
        return {'profiles': items, 'default_user_id': default_id}

    @app.post('/api/profiles', status_code=201)
    async def create_profile(payload: ProfileInput):
        async with queue:
            return await asyncio.to_thread(store.create, payload.display_name, payload.consent)

    @app.get('/api/profiles/{profile_id}')
    async def get_profile(profile_id: str):
        return await asyncio.to_thread(store.detail, profile_id)

    @app.patch('/api/profiles/{profile_id}')
    async def rename_profile(profile_id: str, payload: NameInput):
        async with queue:
            return await asyncio.to_thread(store.rename, profile_id, payload.display_name)

    @app.delete('/api/profiles/{profile_id}')
    async def delete_profile(profile_id: str, payload: DeleteInput):
        async with queue:
            return await asyncio.to_thread(store.delete, profile_id, payload.confirm)

    @app.post('/api/profiles/{profile_id}/samples')
    async def samples(profile_id: str, tpl01: UploadFile = File(...), tpl02: UploadFile = File(...),
                      tpl03: UploadFile = File(...), rotation1: int = Form(0),
                      rotation2: int = Form(0), rotation3: int = Form(0),
                      owner_confirmation: Literal['true'] = Form(...)):
        try:
            store.folder(profile_id)
            data = [await f.read(MAX_FILE_BYTES+1) for f in (tpl01, tpl02, tpl03)]
            async with queue:
                return await asyncio.to_thread(store.upload, profile_id, data, [rotation1, rotation2, rotation3])
        finally:
            for f in (tpl01, tpl02, tpl03):
                await f.close()

    @app.post('/api/profiles/{profile_id}/review')
    async def review_profile(profile_id: str, payload: ReviewInput):
        async with queue:
            return await asyncio.to_thread(store.review, profile_id, payload.pages_checked,
                                            payload.crops_correct, [e.model_dump() for e in payload.accepted_edges])

    @app.get('/api/profiles/{profile_id}/debug/{page}')
    def debug_image(profile_id: str, page: int):
        return FileResponse(store.debug_file(profile_id, page), media_type='image/png')

    @app.get('/api/profiles/{profile_id}/glyph/{label}/{variant}')
    def edge_image(profile_id: str, label: str, variant: int):
        return FileResponse(store.glyph_file(profile_id, label, variant), media_type='image/png')

    @app.post('/api/render')
    async def render(payload: RenderInput):
        if not payload.text.strip():
            raise HTTPException(422, 'Tulis catatan terlebih dahulu.')
        job_id = uuid.uuid4().hex
        try:
            async with queue:
                chosen = await asyncio.to_thread(selected_id, payload.user_id)
                selected = await asyncio.to_thread(store.detail, chosen, False) if chosen else None
                if not selected or not selected['ready']:
                    raise ValueError('Profil belum siap untuk render.')
                result = await asyncio.to_thread(
                    render_document, payload.text, chosen, payload.doc_type,
                    output_root/job_id, ('pdf', 'png'), payload.seed, bank_root, payload.guidelines)
        except (ValueError, OSError, KeyError, TypeError):
            raise HTTPException(422, 'Dokumen belum bisa dibuat. Periksa kesiapan glyph bank dan folder keluaran.')
        return {'id': job_id, 'pages': result['pages'], 'doc_type': result['doc_type'],
                'elapsed_seconds': result['elapsed_seconds'],
                'missing_characters': result['missing_characters'],
                'below_ideal_labels': result['below_ideal_labels'],
                'pdf_url': f'/api/renders/{job_id}/document.pdf',
                'png_urls': [f'/api/renders/{job_id}/{Path(p).name}' for p in result['png']]}

    @app.get('/api/renders/{job_id}/{filename}')
    def artifact(job_id: str, filename: str, download: bool = False):
        if not re.fullmatch(r'[a-f0-9]{32}', job_id):
            raise HTTPException(404, 'Dokumen tidak ditemukan.')
        folder = (output_root/job_id).resolve()
        if folder.parent != output_root:
            raise HTTPException(404, 'Dokumen tidak ditemukan.')
        try:
            report = read_json(folder/'render_report.json')
            allowed = {Path(p).name for p in report['png']} | {'document.pdf'}
            path = (folder/filename).resolve()
            store.folder(report['user_id'])
            if filename not in allowed or path.parent != folder or not path.is_file():
                raise ValueError('File tidak tersedia.')
        except (ValueError, OSError, KeyError, TypeError):
            raise HTTPException(404, 'Dokumen tidak ditemukan.')
        return FileResponse(path, media_type='application/pdf' if filename.endswith('.pdf') else 'image/png',
                            filename=f'glyphen-{filename}' if download else None)

    app.mount('/assets', StaticFiles(directory=PROJECT/'web'), name='assets')
    return app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', help='Profil awal opsional; profil juga dapat dibuat lewat interface.')
    parser.add_argument('--port', type=int, default=8010)
    args = parser.parse_args()
    uvicorn.run(create_app(args.user), host='127.0.0.1', port=args.port,
                access_log=False, log_level='warning')


if __name__ == '__main__':
    main()
