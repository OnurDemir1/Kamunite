#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KPSS veri seti — kapsamli son butunluk denetimi."""
import os, csv, json, glob, re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
JSOND = os.path.join(DATA, "json"); CSVD = os.path.join(DATA, "csv")
CODE = re.compile(r"^\d{6,10}$")
OGR = {"Ortaogretim", "Onlisans", "Lisans"}

ok = []; fail = []; warn = []
def P(c): ok.append(c);  print("  [PASS]", c)
def F(c): fail.append(c); print("  [FAIL]", c)
def W(c): warn.append(c); print("  [warn]", c)

print("="*70, "\n1) DOSYA VARLIGI")
need = ["index.json","index.csv","ozet.json","periods.json","il_kodlari.json",
        "nitelikler_sozluk.json","all_kadrolar.csv","all_kadrolar.jsonl","DOGRULAMA.md"]
for f in need:
    (P if os.path.exists(os.path.join(DATA,f)) else F)("var: "+f)
jf = sorted(glob.glob(os.path.join(JSOND,"*.json")))
cf = sorted(glob.glob(os.path.join(CSVD,"*.csv")))
(P if len(jf)==72 else F)(f"json donem dosyasi = {len(jf)} (beklenen 72)")
(P if len(cf)==72 else F)(f"csv donem dosyasi = {len(cf)} (beklenen 72)")

print("="*70, "\n2) DONEM KUMESI TUTARLILIGI")
index = json.load(open(os.path.join(DATA,"index.json"),encoding="utf-8"))
periods = json.load(open(os.path.join(DATA,"periods.json"),encoding="utf-8"))
ids_json = set(os.path.basename(x)[:-5] for x in jf)
ids_index = set(r["id"] for r in index)
ids_periods = set(p["id"] for p in periods if not p["ekpss"])
(P if ids_json==ids_index==ids_periods else F)("json == index == periods(non-ekpss)")
ekpss_leak = [x for x in ids_json if x.split("-")[1] in ("91","92")]
(P if not ekpss_leak else F)("EKPSS sizmasi yok" + ("" if not ekpss_leak else f" -> {ekpss_leak}"))

print("="*70, "\n3) ALAN BAZLI DOGRULAMA (tum kadrolar)")
tot=0; kont_sum=0
bad_code=0; dup_in_period=0; bad_ogr=0; no_kont=0
puan_bad_range=0; puan_min_gt_max=0; empty_unvan=0; empty_kurum=0; empty_il=0
puan_lo=999; puan_hi=-1
per_json_total_ok=True; per_index_ok=True
il_set=set()
nit_codes_used=set()
for fp in jf:
    d=json.load(open(fp,encoding="utf-8"))
    ks=d["kadrolar"]; n=len(ks)
    if d["scraped_kadro"]!=n: per_json_total_ok=False
    if d["scraped_kontenjan"]!=sum((r["kontenjan"] or 0) for r in ks): per_json_total_ok=False
    seen=set()
    for r in ks:
        tot+=1; kont_sum += (r["kontenjan"] or 0)
        if not CODE.match(r["kadro_kodu"] or ""): bad_code+=1
        if r["kadro_kodu"] in seen: dup_in_period+=1
        seen.add(r["kadro_kodu"])
        if r["ogrenim"] not in OGR: bad_ogr+=1
        if not r.get("kontenjan"): no_kont+=1
        if not (r.get("unvan") or "").strip(): empty_unvan+=1
        if not (r.get("kurum") or "").strip(): empty_kurum+=1
        il=(r.get("il") or "").strip()
        if not il: empty_il+=1
        else: il_set.add(il)
        mn,mx=r.get("min_puan"),r.get("max_puan")
        for v in (mn,mx):
            if v is not None:
                if v<0 or v>130: puan_bad_range+=1
                puan_lo=min(puan_lo,v); puan_hi=max(puan_hi,v)
        if mn is not None and mx is not None and mn>mx: puan_min_gt_max+=1
        for nlt in r.get("nitelikler",[]):
            if nlt.get("kod"): nit_codes_used.add(nlt["kod"])
(P if tot==170627 else F)(f"toplam kadro = {tot}")
(P if per_json_total_ok else F)("her json: scraped_kadro/kontenjan ic tutarli")
(P if bad_code==0 else F)(f"gecersiz kadro_kodu = {bad_code}")
(P if dup_in_period==0 else F)(f"donem ici tekrar eden kadro_kodu = {dup_in_period}")
(P if bad_ogr==0 else F)(f"beklenmedik ogrenim degeri = {bad_ogr}")
(P if empty_unvan==0 else F)(f"bos unvan = {empty_unvan}")
(P if empty_kurum==0 else F)(f"bos kurum = {empty_kurum}")
(W if empty_il else P)(f"bos il = {empty_il}")
(W if no_kont else P)(f"kontenjani bos/0 olan kadro = {no_kont}")
(P if puan_bad_range==0 else F)(f"puan araligi disi (0-130) = {puan_bad_range}  | gozlenen aralik: {puan_lo:.3f}..{puan_hi:.3f}")
(P if puan_min_gt_max==0 else F)(f"min_puan > max_puan = {puan_min_gt_max}")

print("="*70, "\n4) BIRLESIK DOSYA TUTARLILIGI")
with open(os.path.join(DATA,"all_kadrolar.jsonl"),encoding="utf-8") as f:
    jsonl_n=sum(1 for _ in f)
(P if jsonl_n==tot else F)(f"all_kadrolar.jsonl satir = {jsonl_n} (== {tot})")
# csv say + kolon tutarliligi
with open(os.path.join(DATA,"all_kadrolar.csv"),encoding="utf-8-sig",newline="") as f:
    rd=csv.reader(f,delimiter=";"); hdr=next(rd)
    ncol=len(hdr); rows=0; badcol=0
    for row in rd:
        rows+=1
        if len(row)!=ncol: badcol+=1
(P if rows==tot else F)(f"all_kadrolar.csv veri satiri = {rows} (== {tot})")
(P if badcol==0 else F)(f"all_kadrolar.csv kolon bozuk satir = {badcol} (kolon={ncol})")
ozet=json.load(open(os.path.join(DATA,"ozet.json"),encoding="utf-8"))
(P if ozet["toplam_kadro"]==tot and ozet["toplam_kontenjan"]==kont_sum else F)(
    f"ozet.json toplamlar (kadro={ozet['toplam_kadro']}, kont={ozet['toplam_kontenjan']})")

print("="*70, "\n5) PER-DONEM CSV <-> JSON SATIR SAYISI")
mismatch=0
for fp in jf:
    pid=os.path.basename(fp)[:-5]
    d=json.load(open(fp,encoding="utf-8"))
    cpath=os.path.join(CSVD,pid+".csv")
    with open(cpath,encoding="utf-8-sig",newline="") as f:
        rd=csv.reader(f,delimiter=";"); next(rd); c=sum(1 for _ in rd)
    if c!=len(d["kadrolar"]): mismatch+=1
(P if mismatch==0 else F)(f"csv/json satir uyusmazligi olan donem = {mismatch}")

print("="*70, "\n6) NITELIK SOZLUK BUTUNLUGU")
soz=json.load(open(os.path.join(DATA,"nitelikler_sozluk.json"),encoding="utf-8"))
missing=[c for c in nit_codes_used if c not in soz]
(P if not missing else F)(f"sozlukte olmayan nitelik kodu = {len(missing)} (kullanilan benzersiz={len(nit_codes_used)}, sozluk={len(soz)})")

print("="*70, "\n7) TURKCE KODLAMA (mojibake) KONTROLU")
# JSON'da bozuk karakter (replacement char) veya cift-kodlama izi
sample=json.load(open(os.path.join(JSOND,"2024-1.json"),encoding="utf-8"))
txt=json.dumps(sample,ensure_ascii=False)
bad = ("�" in txt) or ("Ã¼" in txt) or ("Ä°" in txt) or ("ÅŸ" in txt)
(P if not bad else F)("2024-1.json Turkce karakterler saglam (mojibake yok)")
# csv icinde de kontrol
with open(os.path.join(CSVD,"2024-1.csv"),encoding="utf-8-sig") as f:
    ctxt=f.read()
(P if "�" not in ctxt and "Ã" not in ctxt else W)("2024-1.csv kodlama saglam")

print("="*70, "\n8) ILLER")
print(f"  farkli il degeri: {len(il_set)}")
odd=[i for i in il_set if i not in json.load(open(os.path.join(DATA,'il_kodlari.json'),encoding='utf-8'))]
(W if odd else P)(f"il_kodlari.json'da olmayan il etiketi = {len(odd)}" + (f" -> {sorted(odd)[:10]}" if odd else ""))

print("\n"+"="*70)
print(f"SONUC: PASS={len(ok)}  FAIL={len(fail)}  WARN={len(warn)}")
if fail: print("FAIL kalemleri:"); [print("   -",c) for c in fail]
print("Denetim tamam.")
