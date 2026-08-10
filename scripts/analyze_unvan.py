#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unvan listesini incele: yakin-kopyalar, supheli girdiler, nadir olanlar.
Cikti: data/_unvan_report.txt (UTF-8, Read ile bakilacak)."""
import os, re, json, glob
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# her unvanin kac kadroda gectigini say
cnt = Counter()
for fp in glob.glob(os.path.join(DATA, "json", "*.json")):
    d = json.load(open(fp, encoding="utf-8"))
    for k in d["kadrolar"]:
        u = k.get("unvan")
        if u is not None:
            cnt[u] += 1

unvanlar = sorted(cnt, key=lambda s: s.lower())

def norm_key(s):
    s = " ".join(s.split())                 # bosluklari sadelestir + trim
    s = s.replace("İ", "i").replace("I", "ı")  # noktali/noktasiz I birlestir
    return s.lower()

groups = defaultdict(list)
for u in unvanlar:
    groups[norm_key(u)].append(u)

dupe_groups = {k: v for k, v in groups.items() if len(v) > 1}

def suspicious(u):
    reasons = []
    if re.search(r"\d", u): reasons.append("rakam")
    if any(c in u for c in "()[]/;,"): reasons.append("noktalama")
    if u != u.strip(): reasons.append("bas/son bosluk")
    if "  " in u: reasons.append("cift bosluk")
    if len(u) > 38: reasons.append("cok uzun")
    if len(u) < 3: reasons.append("cok kisa")
    return reasons

lines = []
lines.append("TOPLAM benzersiz unvan: %d\n" % len(unvanlar))

lines.append("="*60)
lines.append("YAKIN-KOPYA GRUPLARI (ayni sayilabilecek varyantlar): %d grup" % len(dupe_groups))
lines.append("="*60)
for k in sorted(dupe_groups):
    vs = dupe_groups[k]
    lines.append("  * " + "   |   ".join("%r [%d kadro]" % (v, cnt[v]) for v in vs))

lines.append("")
lines.append("="*60)
lines.append("SUPHELI GIRDILER")
lines.append("="*60)
for u in unvanlar:
    r = suspicious(u)
    if r:
        lines.append("  %-45r [%d kadro]  <- %s" % (u, cnt[u], ", ".join(r)))

lines.append("")
lines.append("="*60)
lines.append("NADIR UNVANLAR (1-3 kadro) — yazim hatasi olabilir")
lines.append("="*60)
for u in unvanlar:
    if cnt[u] <= 3:
        lines.append("  %-45r [%d kadro]" % (u, cnt[u]))

open(os.path.join(DATA, "_unvan_report.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("rapor: data/_unvan_report.txt")
print("toplam unvan:", len(unvanlar), "| yakin-kopya grup:", len(dupe_groups))
