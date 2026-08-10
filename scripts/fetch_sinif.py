#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Her kadronun detay sayfasindan (/kadro/{guid}/) Sinif/Derece ceker.

Cikti (append, resume'li):  data/sinif_derece.jsonl
  {"guid":..., "kadro_kodu":..., "donem":..., "sinif":..., "kod":..., "derece":...}

Yeniden calistirilinca: mevcut jsonl'deki guid'ler atlanir (kaldigi yerden devam +
basarisizlari tekrar dener). Ham HTML saklanmaz (170k dosya olmasin diye).
"""
import os, re, sys, json, time, threading, argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
JSOND = os.path.join(DATA, "json")
OUT = os.path.join(DATA, "sinif_derece.jsonl")
BASE = "https://kpss.memurlar.net"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

_tls = threading.local()
def sess():
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session(); s.headers.update({"User-Agent": UA})
        _tls.s = s
    return s

def clean(x): return re.sub(r"\s+", " ", (x or "")).strip()

def parse_sd(content):
    soup = BeautifulSoup(content, "lxml", from_encoding="iso-8859-9")
    for tr in soup.find_all("tr"):
        cs = tr.find_all(["td", "th"])
        if len(cs) >= 2 and clean(cs[0].get_text()).startswith("Sınıf"):
            val = clean(cs[1].get_text(" "))
            m = re.match(r"(.*?)\s*\(([^)]*)\)\s*/\s*(.*)$", val)
            if m:
                ad = m.group(1).strip() or None
                kod = m.group(2).strip() or None
                der = m.group(3).strip()
            else:
                ad, kod, der = (val or None), None, ""
            derece = int(der) if der.isdigit() else None
            return {"sinif": ad, "kod": kod, "derece": derece}
    return None

def fetch_one(item, delay):
    guid, kod_, donem = item
    url = "%s/kadro/%s/" % (BASE, guid)
    for i in range(3):
        try:
            r = sess().get(url, timeout=40)
            if r.status_code == 200 and len(r.content) > 1500:
                sd = parse_sd(r.content)
                time.sleep(delay)
                if sd is not None:
                    sd.update({"guid": guid, "kadro_kodu": kod_, "donem": donem})
                    return sd
                return {"guid": guid, "kadro_kodu": kod_, "donem": donem,
                        "sinif": None, "kod": None, "derece": None, "_nosd": True}
        except Exception:
            pass
        time.sleep(1 + i)
    return None  # basarisiz -> jsonl'ye yazilmaz, sonraki calistirmada tekrar denenir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--delay", type=float, default=0.1)
    ap.add_argument("--limit", type=int, default=0, help="test icin ilk N kadro")
    args = ap.parse_args()

    # tum kadrolar
    all_items = []
    for f in sorted(os.listdir(JSOND)):
        if not f.endswith(".json"):
            continue
        d = json.load(open(os.path.join(JSOND, f), encoding="utf-8"))
        for k in d["kadrolar"]:
            all_items.append((k["kadro_guid"], k["kadro_kodu"], d["id"]))

    done = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fp:
            for line in fp:
                try:
                    done.add(json.loads(line)["guid"])
                except Exception:
                    pass
    todo = [it for it in all_items if it[0] not in done]
    if args.limit:
        todo = todo[:args.limit]
    print("Toplam kadro: %d | tamam: %d | yapilacak: %d" %
          (len(all_items), len(done), len(todo)), flush=True)
    if not todo:
        print("Hepsi tamam."); return

    lock = threading.Lock()
    counts = {"ok": 0, "nosd": 0, "fail": 0}
    t0 = time.time()
    with open(OUT, "a", encoding="utf-8") as out:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(fetch_one, it, args.delay) for it in todo]
            for i, fut in enumerate(as_completed(futs), 1):
                rec = fut.result()
                with lock:
                    if rec is None:
                        counts["fail"] += 1
                    else:
                        if rec.get("_nosd"):
                            counts["nosd"] += 1; rec.pop("_nosd", None)
                        else:
                            counts["ok"] += 1
                        out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        if (counts["ok"] + counts["nosd"]) % 500 == 0:
                            out.flush()
                    if i % 2000 == 0:
                        el = time.time() - t0
                        rate = i / el if el else 0
                        eta = (len(todo) - i) / rate / 60 if rate else 0
                        print("[%6d/%6d] ok=%d nosd=%d fail=%d | %.0f/s | ETA %.0fdk" %
                              (i, len(todo), counts["ok"], counts["nosd"],
                               counts["fail"], rate, eta), flush=True)
    print("BITTI: ok=%d nosd=%d fail=%d (sure %.0fdk)" %
          (counts["ok"], counts["nosd"], counts["fail"], (time.time()-t0)/60), flush=True)


if __name__ == "__main__":
    main()
