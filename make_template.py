from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import black, lightgrey, grey

W, H = A4
OUT = "template_tulisan_A4.pdf"

def marker(c):
    s, i = 8*mm, 10*mm
    c.setFillColor(black)
    for x, y in [(i, H-i-s), (W-i-s, H-i-s), (i, i), (W-i-s, i)]:
        c.rect(x, y, s, s, fill=1, stroke=0)

def guides(c, x, y, w, h):
    c.setStrokeColor(lightgrey)
    c.setLineWidth(0.4)
    c.setDash(2, 2)
    c.line(x, y + 0.2*h, x + w, y + 0.2*h)   # baseline
    c.line(x, y + 0.55*h, x + w, y + 0.55*h) # x-height
    c.setDash()

def box(c, x, y, w, h, stroke=black):
    c.setStrokeColor(stroke)
    c.setLineWidth(0.6)
    c.rect(x, y, w, h, fill=0, stroke=1)
    guides(c, x, y, w, h)

def header(c, title, hint, code):
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(25*mm, H-22*mm, title)
    c.setFont("Helvetica", 8.5)
    c.drawString(25*mm, H-27*mm, hint)
    c.setFont("Helvetica", 8)
    c.setFillColor(grey)
    c.drawCentredString(W/2, 14*mm, code)
    c.setFillColor(black)

def grid(c, x, ytop, labels, cols, label_w, cw, gap, bh, rh):
    for i, lab in enumerate(labels):
        row_bottom = ytop - (i+1)*rh
        y = row_bottom + (rh - bh)/2
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(black)
        c.drawCentredString(x + label_w/2, y + bh/2 - 3.5, lab)
        for j in range(cols):
            bx = x + label_w + j*(cw + gap)
            box(c, bx, y, cw, bh)

def page1(c):
    header(c, "Template Tulisan 1/3: Huruf kecil a-z",
           "Tulis tiap huruf di dalam kotak sesuai labelnya. Pakai pulpen hitam atau biru tua. Jangan keluar dari kotak.",
           "TPL-01")
    grid(c, 25*mm, H-32*mm, list("abcdefghijklmnopqrstuvwxyz"),
         cols=5, label_w=12*mm, cw=22*mm, gap=2*mm, bh=8*mm, rh=9.3*mm)
    marker(c)

def page2(c):
    header(c, "Template Tulisan 2/3: Huruf kapital A-Z",
           "Tulis tiap huruf di dalam kotak sesuai labelnya. Kapital ditulis sebagai huruf kapital biasa, bukan huruf cetak besar.",
           "TPL-02")
    grid(c, 15*mm, H-32*mm, list("ABCDEFGHIJKLM"),
         cols=5, label_w=10*mm, cw=14*mm, gap=1.5*mm, bh=12*mm, rh=16*mm)
    grid(c, 110*mm, H-32*mm, list("NOPQRSTUVWXYZ"),
         cols=5, label_w=10*mm, cw=14*mm, gap=1.5*mm, bh=12*mm, rh=16*mm)
    marker(c)

PUNCT = ['.', ',', '?', '!', ':', ';', '"', "'", '-', '(', ')']

def page3(c):
    header(c, "Template Tulisan 3/3: Angka, tanda baca, dan kalimat contoh",
           "Isi kotak angka dan tanda baca. Tulis kalimat contoh dua kali: satu kalimat per kotak besar.",
           "TPL-03")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(15*mm, H-40*mm, "Angka 0-9")
    c.drawString(110*mm, H-40*mm, "Tanda baca")
    grid(c, 15*mm, H-42*mm, list("0123456789"),
         cols=3, label_w=10*mm, cw=16*mm, gap=2*mm, bh=9*mm, rh=12*mm)
    grid(c, 110*mm, H-42*mm, PUNCT,
         cols=3, label_w=12*mm, cw=16*mm, gap=2*mm, bh=9*mm, rh=12*mm)

    y_title = 113*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(15*mm, y_title, "Kalimat contoh (dua kali, satu kalimat per kotak besar)")
    c.setFillColor(black)
    for i in range(2):
        box(c, 15*mm, (97 - i*14)*mm, 180*mm, 12*mm, stroke=lightgrey)
    marker(c)


def main():
    c = canvas.Canvas(OUT, pagesize=A4)
    for draw_page in (page1, page2, page3):
        draw_page(c)
        c.showPage()
    c.save()
    print(f"Template tersimpan: {OUT} (3 halaman A4)")


if __name__ == "__main__":
    main()
