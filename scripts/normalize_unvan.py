#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kadro unvanlarini normalize eder (veri seviyesinde): parantez bosluklari,
kapanmamis parantez, acik yazim hatalari. Sonra unvanlar.json'u yeniden kurar.
--check: sadece rapor, yazma yok."""
import os, re, json, glob, argparse
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# formatlama sonrasi (parantez bosluklari duzeltilmis) EXACT yazim-hatasi haritasi
TYPO_MAP = {
    "Sağlık Teknikeri (Evde Bakim)": "Sağlık Teknikeri (Evde Bakım)",
    "Sağlık Teknisyeni (İlk ve Acil Yardim)": "Sağlık Teknisyeni (İlk ve Acil Yardım)",
    "Kitap Pataloğu": "Kitap Patoloğu",
    "Topoğraf": "Topograf",
    "Mühendis (Makina)": "Mühendis (Makine)",
    "Mühendis (Elektrik-Elektronik)": "Mühendis (Elektrik/Elektronik)",
    "Bilgisayar Mühendisi": "Mühendis (Bilgisayar)",
    "Kimya Mühendisi": "Mühendis (Kimya)",
    "Ziraat Mühendisi": "Mühendis (Ziraat)",
}

def normalize(u):
    if not u:
        return u
    u = " ".join(u.split())            # trim + tek bosluk
    u = re.sub(r"\s*\(\s*", " (", u)   # "X(Y" / "X ( Y" -> "X (Y"
    u = re.sub(r"\s*\)", ")", u)       # " )" -> ")"
    u = " ".join(u.split())
    if u.count("(") > u.count(")"):    # kapanmamis parantez
        u = u + ")"
    u = TYPO_MAP.get(u, u)
    return u


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    cnt_before = Counter()
    merges = defaultdict(set)   # canonical -> set(raw'lar)
    for fp in glob.glob(os.path.join(DATA, "json", "*.json")):
        d = json.load(open(fp, encoding="utf-8"))
        for k in d["kadrolar"]:
            raw = k.get("unvan")
            if raw is None:
                continue
            cnt_before[raw] += 1
            can = normalize(raw)
            if can != raw:
                merges[can].add(raw)

    # yazma
    if not args.check:
        for fp in glob.glob(os.path.join(DATA, "json", "*.json")):
            d = json.load(open(fp, encoding="utf-8"))
            ch = False
            for k in d["kadrolar"]:
                if k.get("unvan"):
                    n = normalize(k["unvan"])
                    if n != k["unvan"]:
                        k["unvan"] = n; ch = True
            if ch:
                json.dump(d, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # yeni unvan listesi
    cnt_after = Counter()
    for fp in glob.glob(os.path.join(DATA, "json", "*.json")):
        d = json.load(open(fp, encoding="utf-8"))
        for k in d["kadrolar"]:
            if k.get("unvan"):
                cnt_after[normalize(k["unvan"]) if args.check else k["unvan"]] += 1
    uni = sorted(cnt_after, key=lambda s: s.lower())
    if not args.check:
        json.dump(uni, open(os.path.join(DATA, "unvanlar.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=0)

    # rapor
    rep = []
    rep.append("Once: %d benzersiz unvan  ->  Sonra: %d" % (len(cnt_before), len(uni)))
    rep.append("Birlestirilen (kanonik <- varyantlar):")
    for can in sorted(merges):
        variants = sorted(merges[can])
        rep.append("  %r  <-  %s" % (can, ", ".join("%r" % v for v in variants)))
    open(os.path.join(DATA, "_unvan_merge_report.txt"), "w", encoding="utf-8").write("\n".join(rep))
    print(rep[0])
    print("birlestirme grubu:", len(merges), "| rapor: data/_unvan_merge_report.txt")


if __name__ == "__main__":
    main()
