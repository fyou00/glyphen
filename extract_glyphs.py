#!/usr/bin/env python3
"""
extract_glyphs.py

Membaca foto halaman template tulisan (TPL-01, TPL-02, TPL-03), mendeteksi
4 marker sudut, mengoreksi perspektif ke A4, lalu memotong setiap kotak dan
menyimpannya sebagai glyph bank per user dengan label dari kode kotaknya.

Pemakaian:
    python extract_glyphs.py --user fathur --pages tpl01.jpg tpl02.jpg tpl03.jpg
"""

import argparse
import json
import os
import sys

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Geometri template (harus sama dengan make_template.py), satuan mm
# ---------------------------------------------------------------------------
W_MM, H_MM = 210, 297
MM = 10                 # resolusi hasil koreksi: piksel per mm
INSET = 1.2             # mm dipotong dari tepi kotak agar garis kotak tidak ikut
MARKER_CENTERS = [(14, 14), (196, 14), (196, 283), (14, 283)]  # TL, TR, BR, BL (origin kiri-atas)

LOWER = list("abcdefghijklmnopqrstuvwxyz")
UPPER = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGITS = list("0123456789")
PUNCT = ['.', ',', '?', '!', ':', ';', '"', "'", '-', '(', ')']
PUNCT_NAMES = {
    '.': 'dot', ',': 'comma', '?': 'question', '!': 'exclam', ':': 'colon',
    ';': 'semicolon', '"': 'dquote', "'": 'squote', '-': 'hyphen',
    '(': 'lparen', ')': 'rparen',
}

INK_THRESHOLD = 128     # piksel lebih gelap dari ini dianggap tinta
EMPTY_RATIO = 0.003     # di bawah ini kotak dianggap kosong
EDGE_PX = 3             # tinta di 3 px tepi kotak = tulisan keluar kotak


def grid_entries(labels, x, ytop, cols, label_w, cw, gap, bh, rh, keyfn):
    """Hitung kotak (key, variant, x, y, w, h) dalam mm, origin kiri-bawah."""
    out = []
    for i, lab in enumerate(labels):
        yb = ytop - (i + 1) * rh
        y = yb + (rh - bh) / 2
        for j in range(cols):
            bx = x + label_w + j * (cw + gap)
            out.append((keyfn(lab), j, bx, y, cw, bh))
    return out


def page_layout(n):
    if n == 1:
        return grid_entries(LOWER, 25, 265, 5, 12, 22, 2, 8, 9.3,
                            lambda c: f"lower_{c}")
    if n == 2:
        return (grid_entries(UPPER[:13], 15, 265, 5, 10, 14, 1.5, 12, 16,
                             lambda c: f"upper_{c}")
                + grid_entries(UPPER[13:], 110, 265, 5, 10, 14, 1.5, 12, 16,
                               lambda c: f"upper_{c}"))
    if n == 3:
        # Dua kotak kalimat contoh (D-016) hanya untuk evaluasi gaya;
        # tidak diekstrak. Geometri angka dan tanda baca tetap sama.
        return (grid_entries(DIGITS, 15, 255, 3, 10, 16, 2, 9, 12,
                             lambda c: f"digit_{c}")
                + grid_entries(PUNCT, 110, 255, 3, 12, 16, 2, 9, 12,
                               lambda c: f"punct_{PUNCT_NAMES[c]}"))
    raise ValueError("Halaman harus 1, 2, atau 3")


def find_markers(gray):
    """Cari 4 marker sudut pejal; toleransi tekstur scan mengikuti D-017."""
    h, w = gray.shape
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Otsu mempertahankan area marker scan yang terbelah oleh threshold adaptif.
    _, solid_ink = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    cnts, hier = cv2.findContours(solid_ink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if hier is None:
        raise RuntimeError("Tidak ada kontur ditemukan")

    cands = []
    for i, c in enumerate(cnts):
        area = cv2.contourArea(c)
        if not (0.00015 * h * w < area < 0.01 * h * w):
            continue
        x, y, bw, bh = cv2.boundingRect(c)
        if not (0.75 < bw / bh < 1.33):
            continue
        if area / (bw * bh) < 0.9:    # harus pejal, bukan coretan
            continue
        if float((solid_ink[y:y+bh, x:x+bw] > 0).mean()) < 0.9:
            continue                 # tolak kotak garis meski kontur luarnya pejal
        M = cv2.moments(c)
        cands.append((M["m10"] / M["m00"], M["m01"] / M["m00"]))

    if len(cands) < 4:
        raise RuntimeError(f"Hanya {len(cands)} marker terdeteksi, perlu 4")

    picks = []
    for ox, oy in [(0, 0), (w, 0), (w, h), (0, h)]:  # TL, TR, BR, BL foto
        best = min(cands, key=lambda p: (p[0] - ox) ** 2 + (p[1] - oy) ** 2)
        dist = np.hypot(best[0] - ox, best[1] - oy)
        if dist > 0.25 * min(h, w):
            raise RuntimeError("Marker tidak ditemukan dekat sudut foto. "
                               "Pastikan keempat marker masuk ke dalam foto.")
        picks.append(best)
    if len({(round(x), round(y)) for x, y in picks}) < 4:
        raise RuntimeError("Marker yang terdeteksi tidak unik")
    return np.float32(picks)


def rectify(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    src = find_markers(gray)
    dst = np.float32([[x * MM, y * MM] for x, y in MARKER_CENTERS])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img_bgr, M, (W_MM * MM, H_MM * MM),
                                 borderValue=(255, 255, 255))
    return warped


def crop_box(gray, x, y, w, h):
    x0 = int((x + INSET) * MM)
    x1 = int((x + w - INSET) * MM)
    y0 = int((H_MM - (y + h) + INSET) * MM)
    y1 = int((H_MM - y - INSET) * MM)
    return gray[y0:y1, x0:x1]


def analyze(crop):
    ink = float((crop < INK_THRESHOLD).mean())
    edge = (crop[:EDGE_PX] < INK_THRESHOLD).any() \
        or (crop[-EDGE_PX:] < INK_THRESHOLD).any() \
        or (crop[:, :EDGE_PX] < INK_THRESHOLD).any() \
        or (crop[:, -EDGE_PX:] < INK_THRESHOLD).any()
    if ink < EMPTY_RATIO:
        status = "empty"
    elif edge:
        status = "touches_edge"
    else:
        status = "ok"
    return status, ink


DEBUG_COLORS = {"ok": (0, 200, 0), "empty": (0, 0, 255), "touches_edge": (0, 220, 255)}


def process_page(img, page_no, user, out_root, manifest):
    warped = rectify(img)
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    debug = warped.copy()
    glyph_root = os.path.join(out_root, user, "glyphs")

    for key, variant, x, y, w, h in page_layout(page_no):
        crop = crop_box(gray, x, y, w, h)
        status, ink = analyze(crop)

        rel_file = None
        if status != "empty":
            folder = os.path.join(glyph_root, key)
            os.makedirs(folder, exist_ok=True)
            rel_file = os.path.join(user, "glyphs", key, f"{key}_{variant + 1:02d}.png")
            cv2.imwrite(os.path.join(out_root, rel_file), crop)

        manifest.append({
            "label": key,
            "variant": variant + 1,
            "page": page_no,
            "status": status,
            "ink_ratio": round(ink, 4),
            "file": rel_file,
        })

        x0 = int((x) * MM); x1 = int((x + w) * MM)
        y0 = int((H_MM - (y + h)) * MM); y1 = int((H_MM - y) * MM)
        cv2.rectangle(debug, (x0, y0), (x1, y1), DEBUG_COLORS[status], 2)

    cv2.imwrite(os.path.join(out_root, user, f"debug_page{page_no}.png"), debug)


def main():
    ap = argparse.ArgumentParser(description="Ekstrak glyph bank dari foto template")
    ap.add_argument("--user", required=True, help="ID user, dipakai sebagai nama folder")
    ap.add_argument("--pages", nargs=3, required=True,
                    metavar=("TPL01", "TPL02", "TPL03"),
                    help="Foto halaman 1, 2, dan 3 dengan urutan ini")
    ap.add_argument("--out", default="glyph_bank", help="Folder output")
    args = ap.parse_args()

    out_root = args.out
    os.makedirs(os.path.join(out_root, args.user), exist_ok=True)

    manifest = []
    for n, path in enumerate(args.pages, start=1):
        img = cv2.imread(path)
        if img is None:
            sys.exit(f"Gagal membaca {path}")
        try:
            process_page(img, n, args.user, out_root, manifest)
        except RuntimeError as e:
            sys.exit(f"Halaman {n} ({path}): {e}")

    meta = {"user": args.user, "entries": manifest}
    with open(os.path.join(out_root, args.user, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    counts = {}
    for e in manifest:
        counts[e["status"]] = counts.get(e["status"], 0) + 1
    print("Selesai:", counts)
    print("Periksa debug_page*.png: kotak hijau = ok, kuning = tinta keluar kotak, merah = kosong.")


if __name__ == "__main__":
    main()
