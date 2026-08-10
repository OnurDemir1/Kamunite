# -*- coding: utf-8 -*-
"""Her bolum -> gectigi ogrenim seviyeleri, ISIM (aciklama) bazli.
Nitelik KODLARI donem donem yeniden atandigi icin KOD KULLANILMAZ; aciklama gercek anlami tasir.
Cikti: data/bolum_kod.json = {"bolumLevel": {bolum:[seviye...]}}  (bolumKod bos, artik kullanilmiyor)"""
import json, glob, os
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

def norm(s):
    s=(s or '').replace('I','ı').replace('İ','i').lower()
    for a,b in [('ç','c'),('ğ','g'),('ı','i'),('ö','o'),('ş','s'),('ü','u'),('â','a'),('î','i'),('û','u')]:
        s=s.replace(a,b)
    return s.strip()

bolumler = json.load(open(os.path.join(DATA,"bolumler.json"),encoding="utf-8"))
BOL_SET = set(norm(b) for b in bolumler)
bol_by_norm = {norm(b): b for b in bolumler}

lvl = defaultdict(Counter)   # bolum(orijinal ad) -> ogrenim sayaci
for f in glob.glob(os.path.join(DATA,"json","*.json")):
    for k in json.load(open(f,encoding="utf-8"))["kadrolar"]:
        ogr = k.get("ogrenim")
        seen = set()
        for n in k.get("nitelikler",[]):
            ac = n.get("aciklama","") or ""
            # tam aciklama + "/" ile ayrilmis parcalar
            for part in [ac] + ac.split("/"):
                p = norm(part)
                if p in BOL_SET and p not in seen:
                    seen.add(p)
                    lvl[bol_by_norm[p]][ogr] += 1

bolumLevel = {b: [s for s,_ in c.most_common() if s] for b,c in lvl.items()}
out = {"bolumKod": {}, "bolumLevel": bolumLevel}
open(os.path.join(DATA,"bolum_kod.json"),"w",encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, separators=(",",":")))

kapsam = sum(1 for b in bolumler if b in bolumLevel)
print("bolumler:", len(bolumler), "| seviye eslesen:", kapsam, "(%.1f%%)"%(100*kapsam/len(bolumler)))
for tb in ["Amerikan Dili ve Edebiyatı","İşletme","Muhasebe","Hemşirelik","Bilgisayar Mühendisliği"]:
    print("  %-30s %s" % (tb, bolumLevel.get(tb, "(yok)")))
