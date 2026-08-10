# -*- coding: utf-8 -*-
"""Her bolum -> onu ISTEYEN nitelik kod(lar)i ve gectigi ogrenim seviyeleri.
Ciktilar: data/bolum_kod.json  { "bolumKod": {bolum:[kod...]}, "bolumLevel": {bolum:[seviye...]} }
Boylece 'Bana uygun' bolumu KOD ile (isim tahminiyle degil) eslestirir."""
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
bol_by_norm = {}
for b in bolumler:
    bol_by_norm.setdefault(norm(b), b)   # normalize -> orijinal ad

files = sorted(glob.glob(os.path.join(DATA,"json","*.json")))

# 1) her nitelik kodu -> aciklama; ve kodun kadrolardaki ogrenim dagilimi
kod_ac = {}
kod_ogr = defaultdict(Counter)
for f in files:
    for k in json.load(open(f,encoding="utf-8"))["kadrolar"]:
        ogr = k.get("ogrenim")
        for n in k.get("nitelikler",[]):
            kd = str(n.get("kod","")).strip()
            if not kd: continue
            if kd not in kod_ac: kod_ac[kd] = n.get("aciklama","") or ""
            kod_ogr[kd][ogr] += 1

# 2) kod -> bolum(ler): aciklama "/" ile ayrilir, her parca bir bolum adi olabilir
bolumKod = defaultdict(set)
kodBolum = {}
for kd, ac in kod_ac.items():
    parts = [norm(p) for p in ac.split("/")]
    matched = []
    for p in parts:
        if p in bol_by_norm:
            orig = bol_by_norm[p]
            bolumKod[orig].add(kd)
            matched.append(orig)
    if matched: kodBolum[kd] = matched

# 3) her bolum -> gectigi ogrenim seviyeleri (o bolumun kodlarini iceren kadrolarin ogrenimi)
bolumLevel = {}
for b, kodlar in bolumKod.items():
    lv = Counter()
    for kd in kodlar: lv += kod_ogr[kd]
    # gurultuyu ele: en az 1 kez gecen seviyeler
    bolumLevel[b] = [s for s,_ in lv.most_common() if s]

out = {
    "bolumKod": {b: sorted(kodlar) for b,kodlar in bolumKod.items()},
    "bolumLevel": bolumLevel,
}
open(os.path.join(DATA,"bolum_kod.json"),"w",encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, separators=(",",":")))

# --- rapor ---
kapsam = sum(1 for b in bolumler if b in bolumKod)
print("bolumler.json:", len(bolumler), "| kod eslesen bolum:", kapsam,
      "(%.1f%%)"%(100*kapsam/len(bolumler)))
print("kod->bolum eslesen benzersiz kod:", len(kodBolum))
for tb in ["Amerikan Dili ve Edebiyatı","İşletme","Muhasebe","Hemşirelik",
           "Çocuk Gelişimi","Bilgisayar Mühendisliği","Elektrik-Elektronik Mühendisliği"]:
    if tb in bolumKod:
        print("  %-34s kod=%s  seviye=%s" % (tb, sorted(bolumKod[tb]), bolumLevel[tb]))
    else:
        print("  %-34s (eslesme yok)" % tb)
