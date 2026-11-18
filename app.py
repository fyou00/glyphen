#!/usr/bin/env python3
"""Antarmuka lokal Glyphen; jalankan python app.py --user <id>."""

import argparse
import asyncio
from pathlib import Path
import re
from typing import Literal, Optional
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StrictInt, StrictStr
from starlette.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from render_document import GlyphBank, LETTERS, read_json, render_document

PROJECT = Path(__file__).resolve().parent
MAX_CHARACTERS = 12000


class RenderInput(BaseModel):
    text: StrictStr = Field(min_length=1, max_length=MAX_CHARACTERS)
    doc_type: Literal['catatan', 'surat'] = 'catatan'
    seed: Optional[StrictInt] = Field(default=None, ge=0, le=2147483647)
    guidelines: bool = False


def create_app(user_id, bank_root=None, output_root=None):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', user_id):
        raise ValueError('ID pengguna tidak valid.')
    bank_root = Path(bank_root or PROJECT/'glyph_bank').resolve()
    output_root = Path(output_root or PROJECT/'outputs/ui').resolve()
    app = FastAPI(title='Glyphen lokal', docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', '[::1]'])
    queue = asyncio.Semaphore(1)

    @app.middleware('http')
    async def local_requests(request: Request, call_next):
        origin = request.headers.get('origin')
        if origin and origin != str(request.base_url).rstrip('/'):
            return JSONResponse({'detail': 'Permintaan harus berasal dari halaman aplikasi lokal.'}, status_code=403)
        content_length = request.headers.get('content-length', '0')
        if not content_length.isdecimal() or int(content_length) > 100000:
            return JSONResponse({'detail': 'Ukuran permintaan terlalu besar.'}, status_code=413)
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self'; font-src 'self'; connect-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request, exc):
        return JSONResponse({'detail': 'Periksa teks (maksimal 12.000 karakter), jenis dokumen, dan angka kunci variasi.'}, status_code=422)

    @app.get('/')
    def home():
        return FileResponse(PROJECT/'web/index.html')

    @app.get('/api/profile')
    async def profile():
        try:
            bank = await asyncio.to_thread(GlyphBank, user_id, bank_root)
        except (ValueError, OSError, KeyError, TypeError):
            return {'user_id': user_id, 'ready': False, 'detail':
                    'Glyph bank belum siap. Periksa persetujuan, tinjauan potongan, dan coverage sebelum membuat dokumen.'}
        return {'user_id': user_id, 'ready': True, 'letter_labels': len(LETTERS),
                'minimum_variants': min(len(bank.glyphs[label]) for label in LETTERS),
                'max_characters': MAX_CHARACTERS}

    @app.post('/api/render')
    async def render(payload: RenderInput):
        if not payload.text.strip():
            raise HTTPException(422, 'Tulis catatan terlebih dahulu.')
        job_id = uuid.uuid4().hex
        try:
            async with queue:
                result = await asyncio.to_thread(
                    render_document, payload.text, user_id, payload.doc_type,
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
            if report['user_id'] != user_id or filename not in allowed or path.parent != folder or not path.is_file():
                raise ValueError('File tidak tersedia.')
        except (ValueError, OSError, KeyError, TypeError):
            raise HTTPException(404, 'Dokumen tidak ditemukan.')
        return FileResponse(path, media_type='application/pdf' if filename.endswith('.pdf') else 'image/png',
                            filename=f'glyphen-{filename}' if download else None)

    app.mount('/assets', StaticFiles(directory=PROJECT/'web'), name='assets')
    return app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', required=True)
    parser.add_argument('--port', type=int, default=8010)
    args = parser.parse_args()
    uvicorn.run(create_app(args.user), host='127.0.0.1', port=args.port,
                access_log=False, log_level='warning')


if __name__ == '__main__':
    main()
