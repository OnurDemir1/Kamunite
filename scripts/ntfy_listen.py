#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ntfy dinleyici — kullanicidan gelen mesajlari stdout'a basar (her satir = 1 olay).
Kendi gonderdigim mesajlari (baslik 'KPSS' ile baslayan) filtreler.
Baglanti kopunca otomatik yeniden baglanir; kacirmamak icin 'since' ile bosluk kapatir.
Tanilar stderr'e gider (bildirim uretmez).
"""
import sys
import time
import json

import requests

TOPIC = "buradan-konusalim-57hax1j0a"
URL = "https://ntfy.sh/%s/json" % TOPIC

seen = set()
since = str(int(time.time()))   # sadece bu andan sonrasi
sess = requests.Session()

sys.stderr.write("ntfy dinleyici basladi: %s\n" % TOPIC)
sys.stderr.flush()

while True:
    try:
        r = sess.get(URL, params={"since": since}, stream=True, timeout=(10, 360))
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            ev = d.get("event")
            t = d.get("time")
            if t:
                # since'i ilerlet (yeniden baglanmada bosluk olmasin)
                since = str(int(t))
            if ev != "message":
                continue
            mid = d.get("id")
            if mid in seen:
                continue
            seen.add(mid)
            title = d.get("title", "") or ""
            if title.startswith("KPSS"):   # kendi giden mesajim -> atla
                continue
            msg = d.get("message", "") or ""
            out = ("[%s] %s" % (title, msg)) if title else msg
            print("KULLANICI MESAJI >>> " + out, flush=True)
    except Exception as e:
        sys.stderr.write("ntfy yeniden baglaniyor: %r\n" % e)
        sys.stderr.flush()
        time.sleep(3)
