# -*- coding: utf-8 -*-
"""Kadro ilanlarinda istenen TUM sertifikalari cikarir -> data/sertifikalar.json
   { "list": [ {"kod","ad","tam","n"} ... ] }   ad=temiz gorunen isim, n=kac kadroda gecti"""
import json, glob, os, re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

def norm(s):
    s=(s or '').replace('I','ı').replace('İ','i').lower()
    for a,b in [('ç','c'),('ğ','g'),('ı','i'),('ö','o'),('ş','s'),('ü','u'),('â','a'),('î','i'),('û','u')]:
        s=s.replace(a,b)
    return s

def temizle(ac):
    """'M.E.B.'Dan Onaylı X Sertifikası Sahibi olmak.' -> 'X Sertifikası'"""
    t = ac.strip()
    t = re.sub(r"^M\.?E\.?B\.?['’]?\s*[dD]an\s+[Oo]nayl[ıi]\s+", "", t)
    t = re.sub(r"\s*[Ss]ahibi?\s+[Oo]lmak\.?$", "", t)
    t = re.sub(r"['’]?\s*[nN][ae]\s+[Ss]ahip\s+[Oo]lmak\.?$", "", t)
    t = re.sub(r"\s*[Ss]ahip\s+[Oo]lmak\.?$", "", t)
    t = t.strip(" .")
    return t or ac.strip()

kod_ac = {}
kod_cnt = Counter()
for f in glob.glob(os.path.join(DATA,"json","*.json")):
    for k in json.load(open(f,encoding="utf-8"))["kadrolar"]:
        for n in k.get("nitelikler",[]):
            ac = n.get("aciklama","") or ""; kd = str(n.get("kod","")).strip()
            if kd and "sertifika" in norm(ac):
                if kd not in kod_ac: kod_ac[kd] = ac
                kod_cnt[kd] += 1

lst = [{"kod": kd, "ad": temizle(kod_ac[kd]), "tam": kod_ac[kd], "n": kod_cnt[kd]}
       for kd in kod_ac]
lst.sort(key=lambda r: (-r["n"], r["ad"].lower()))     # en cok istenen en ustte

open(os.path.join(DATA,"sertifikalar.json"),"w",encoding="utf-8").write(
    json.dumps({"list": lst}, ensure_ascii=False, separators=(",",":")))

print("sertifika sayisi:", len(lst))
for r in lst:
    print("  %5s x%-5d %s" % (r["kod"], r["n"], r["ad"]))
