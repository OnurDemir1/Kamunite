#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sinif_derece.jsonl -> her donem JSON'una sinif/sinif_kod/derece ekler.
Ayrica tam kapsama raporu verir (eksik guid'ler). --check ile sadece rapor."""
import os, json, glob, argparse
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
JSOND = os.path.join(DATA, "json")
SRC = os.path.join(DATA, "sinif_derece.jsonl")

def load_map():
    m = {}
    if os.path.exists(SRC):
        with open(SRC, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    kod = r.get("kod")
                    if kod and kod.isascii():   # 'sh' -> 'SH' (Turkce kodlar (GİH) korunur)
                        kod = kod.upper()
                    m[r["guid"]] = (r.get("sinif"), kod, r.get("derece"))
                except Exception:
                    pass
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="sadece kapsama raporu, yazma yok")
    args = ap.parse_args()
    m = load_map()
    total = 0; have = 0
    missing_guids = []
    per_missing = Counter()
    kod_dagilim = Counter()
    for fp in sorted(glob.glob(os.path.join(JSOND, "*.json"))):
        d = json.load(open(fp, encoding="utf-8"))
        changed = False
        for k in d["kadrolar"]:
            total += 1
            sd = m.get(k["kadro_guid"])
            if sd:
                have += 1
                kod_dagilim[sd[1] or ("Sözleşmeli" if sd[0]=="Sözleşmeli" else "?")] += 1
                if not args.check:
                    k["sinif"], k["sinif_kod"], k["derece"] = sd
                    changed = True
            else:
                missing_guids.append(k["kadro_guid"])
                per_missing[d["id"]] += 1
                if not args.check:
                    k.setdefault("sinif", None); k.setdefault("sinif_kod", None); k.setdefault("derece", None)
        if changed and not args.check:
            json.dump(d, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("KAPSAMA: %d / %d  (%.2f%%)" % (have, total, 100*have/total if total else 0))
    print("EKSIK: %d kadro" % len(missing_guids))
    if per_missing:
        print("Eksik olan donemler:", dict(per_missing))
    print("Sinif kod dagilimi:", dict(kod_dagilim.most_common()))
    if not args.check:
        print("Merge tamam (donem JSON'lari guncellendi).")

if __name__ == "__main__":
    main()
