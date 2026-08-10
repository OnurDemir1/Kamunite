#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""index.html'den, birkac donem verisi GOMULU (embed) tek dosyalik demo uretir.
Artifact/GitHub olmadan telefondan acilabilsin diye. Cikti: demo.html"""
import os, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
EMBED_IDS = ["2026-1", "2025-2", "2024-1"]   # puan verisi olan, temsili donemler

idx = json.load(open(os.path.join(DATA, "index.json"), encoding="utf-8"))
idx_sub = [r for r in idx if r["id"] in EMBED_IDS]
periods = {}
for pid in EMBED_IDS:
    d = json.load(open(os.path.join(DATA, "json", "%s.json" % pid), encoding="utf-8"))
    periods[pid] = {"kadrolar": d["kadrolar"]}

unvanlar = json.load(open(os.path.join(DATA, "unvanlar.json"), encoding="utf-8"))
bolumler = json.load(open(os.path.join(DATA, "bolumler.json"), encoding="utf-8"))
nitelik_list = json.load(open(os.path.join(DATA, "nitelik_list.json"), encoding="utf-8"))
bolum_kod = json.load(open(os.path.join(DATA, "bolum_kod.json"), encoding="utf-8"))
sertifikalar = json.load(open(os.path.join(DATA, "sertifikalar.json"), encoding="utf-8")).get("list", [])
try: aktif_ilanlar = json.load(open(os.path.join(DATA, "aktif_ilanlar.json"), encoding="utf-8"))
except Exception: aktif_ilanlar = None
try: esanlam = json.load(open(os.path.join(DATA, "bolum_esanlam.json"), encoding="utf-8")).get("gruplar", [])
except Exception: esanlam = []
provinces = sorted(json.load(open(os.path.join(DATA, "il_kodlari.json"), encoding="utf-8")).keys(),
                   key=lambda s: s.lower())
embed = {"index": idx_sub, "periods": periods, "unvanlar": unvanlar,
         "bolumler": bolumler, "nitelikList": nitelik_list, "provinces": provinces,
         "bolumKod": bolum_kod.get("bolumKod", {}), "bolumLevel": bolum_kod.get("bolumLevel", {}),
         "sertifikalar": sertifikalar, "aktifIlanlar": aktif_ilanlar, "esanlam": esanlam}
embed_js = "<script>window.KPSS_EMBED=%s;</script>\n" % json.dumps(embed, ensure_ascii=False, separators=(",", ":"))

html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
# dis kabugu soy (Artifact kendi <!doctype><head><body>'sini ekliyor)
for tag in ["<!DOCTYPE html>", '<html lang="tr">', "<head>", "</head>",
            "<body>", "</body>", "</html>"]:
    html = html.replace(tag, "")
# ana <script>'tan hemen once embed'i ekle
html = html.replace('<script>\n"use strict";', embed_js + '<script>\n"use strict";', 1)
# demo notu: baslik altina kucuk bir rozet
html = html.replace('<p>Sana uygun kadroları bul · 2012–2026</p>',
                    '<p>DEMO · 3 dönem gömülü · tam sürümde 72 dönem</p>')

out = os.path.join(ROOT, "demo.html")
open(out, "w", encoding="utf-8").write(html.strip())
print("yazildi:", out, "(%.2f MB)" % (len(html)/1048576))
print("gomulu donem:", EMBED_IDS, "toplam kadro:", sum(len(periods[p]["kadrolar"]) for p in periods))
