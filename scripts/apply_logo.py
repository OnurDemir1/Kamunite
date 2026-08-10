#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Logoyu kirp/kucult, index.html'e header logosu + favicon olarak goom (data-URI),
ayrica exe icin assets/logo.ico uret."""
import os, io, re, base64
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = r"C:\Users\Onur\Downloads\gpt-image-2_a_surreal_and_vibrant_cinematic_photo_of_A_highly_marginal_and_vibrant_app_logo_-0-removebg-preview.png"
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

im = Image.open(SRC).convert("RGBA")
im = im.crop(im.getbbox())          # seffaf kenarlari kirp
w, h = im.size

def uri(img):
    b = io.BytesIO(); img.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()

# header logosu: yukseklik 128
hh = 128; hw = round(w * hh / h)
logo = im.resize((hw, hh), Image.LANCZOS)
logo_uri = uri(logo)
logo.save(os.path.join(ASSETS, "logo.png"))

# kare tuval (favicon + ico icin)
s = max(w, h)
canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
canvas.paste(im, ((s - w) // 2, (s - h) // 2))
fav = canvas.resize((64, 64), Image.LANCZOS)
fav_uri = uri(fav)
fav.save(os.path.join(ASSETS, "favicon.png"))
canvas.resize((256, 256), Image.LANCZOS).save(
    os.path.join(ASSETS, "logo.ico"),
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

# index.html enjeksiyonu
fp = os.path.join(ROOT, "index.html")
html = open(fp, encoding="utf-8").read()

# favicon (title'dan sonra)
if 'rel="icon"' not in html:
    html = html.replace(
        '<title>Kamunite — KPSS Tercih Robotu</title>',
        '<title>Kamunite — KPSS Tercih Robotu</title>\n<link rel="icon" type="image/png" href="%s">' % fav_uri, 1)
else:
    html = re.sub(r'<link rel="icon"[^>]*>',
                  '<link rel="icon" type="image/png" href="%s">' % fav_uri, html, count=1)

# .mark CSS
html = re.sub(r"\.mark\{[^}]*\}",
              ".mark{width:40px;height:40px;flex:none;display:grid;place-items:center}",
              html, count=1)
if ".mark img{" not in html:
    html = html.replace(
        ".mark{width:40px;height:40px;flex:none;display:grid;place-items:center}",
        ".mark{width:40px;height:40px;flex:none;display:grid;place-items:center}\n.mark img{width:100%;height:100%;object-fit:contain;display:block}", 1)

# mark HTML (K -> logo). Zaten logo varsa src'yi guncelle.
if '<div class="mark"><img' in html:
    html = re.sub(r'<div class="mark"><img src="data:image/png;base64,[^"]*"',
                  '<div class="mark"><img src="%s"' % logo_uri, html, count=1)
else:
    html = html.replace('<div class="mark">K</div>',
                        '<div class="mark"><img src="%s" alt="Kamunite"></div>' % logo_uri, 1)

open(fp, "w", encoding="utf-8").write(html)
print("header logo data-URI:", len(logo_uri), "byte | favicon:", len(fav_uri), "byte")
print("assets: logo.png, favicon.png, logo.ico | index.html guncellendi")
