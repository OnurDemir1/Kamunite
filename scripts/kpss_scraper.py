#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KPSS Kadro Scraper
==================
memurlar.net KPSS robot sayfalarindan (resmi OSYM tercih kilavuzlarinin
yapilandirilmis hali) tum acilan kadrolari ve detaylarini indirir.

Kaynak endpoint (Cloudflare arkasinda ama duz GET calisiyor):
  /kpssrobotu/{YIL}/{DONEM}/default.aspx
      ?SelectedItem=Kadro+Arama&BranchType={2|3|4}&BranchCode=&Organization=&JobTitle=&CityCode=

BranchType (ogrenim duzeyi):  2=Ortaogretim, 3=Onlisans, 4=Lisans
Her donem icin 3 istek atilir; sonuclar kadro koduna gore birlestirilir.

EKPSS (donem kodu 91/92) HARIC tutulur.

Her kadro satiri sunlari icerir:
  kadro_kodu, kurum, unvan, il, kontenjan, bos_kadro, min_puan, max_puan,
  kadro_guid (detay sayfasi), nitelikler[] (nitelik kodu + aciklama)

Ciktilar:
  data/raw/{yil}-{donem}_b{branch}.html.gz   ham HTML (yeniden uretilebilirlik)
  data/json/{yil}-{donem}.json               donem bazli tam detay
  data/csv/{yil}-{donem}.csv                 donem bazli duz tablo (Excel/BOM)
  data/all_kadrolar.csv / .jsonl             tum donemler birlesik
  data/index.json / index.csv                donem ozetleri + dogrulama
  data/periods.json                          donem listesi + referans sayilar
"""
import os
import re
import sys
import csv
import json
import gzip
import time
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

BASE = "https://kpss.memurlar.net"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(DATA, "raw")
JSOND = os.path.join(DATA, "json")
CSVD = os.path.join(DATA, "csv")
for d in (DATA, RAW, JSOND, CSVD):
    os.makedirs(d, exist_ok=True)

BRANCHES = {"2": "Ortaogretim", "3": "Onlisans", "4": "Lisans"}
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
GUID_RE = re.compile(r"^/kadro/([0-9a-fA-F][0-9a-fA-F-]{18,})/$")
KADRO_CODE_RE = re.compile(r"^\d{6,10}$")
HEADER_KK_RE = re.compile(
    r"Bu\s*al[ıi]mda\s*([\d.,]+)\s*kadro.*?toplam\s*([\d.,]+)\s*kontenjan",
    re.IGNORECASE | re.DOTALL,
)
HEADER_BASVURAN_RE = re.compile(r"([\d.,]+)\s*ki\w+\s*tercih", re.IGNORECASE)
HEADER_YERLESEN_RE = re.compile(r"([\d.,]+)\s*ki\w+\s*yerle", re.IGNORECASE)

_tls = threading.local()


def get_session():
    s = getattr(_tls, "session", None)
    if s is None:
        s = requests.Session()
        s.headers.update({
            "User-Agent": UA,
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml",
        })
        _tls.session = s
    return s


CITY_CODES = {}   # doldurulur (isim -> kod) ilk tam donemden
_city_lock = threading.Lock()
_raw_lock = threading.Lock()


# --------------------------------------------------------------------------- #
# yardimcilar
# --------------------------------------------------------------------------- #
def make_soup(html):
    """lxml, str + <meta charset=iso-8859-9> gorunce Turkce karakterleri
    cift-kodluyor. UTF-8 bayt + from_encoding vererek bunu engelliyoruz."""
    if isinstance(html, str):
        html = html.encode("utf-8")
    return BeautifulSoup(html, "lxml", from_encoding="utf-8")


def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def to_int(s):
    s = clean(s).replace(".", "").replace(",", "")
    return int(s) if s.isdigit() else None


def parse_puan(s):
    """KPSS puani '93.692' seklinde (nokta = ondalik). Float dondur."""
    s = clean(s)
    if not s or s in ("-", "--", "---", "0", "0.000"):
        # not: gercek 0 puan olmaz; bos yerlestirme demek
        if s in ("-", "--", "---", ""):
            return None
    if not s or s in ("-", "--", "---"):
        return None
    try:
        return float(s)
    except ValueError:
        try:
            return float(s.replace(",", "."))
        except ValueError:
            return None


def fetch(url, tries=5):
    last = None
    session = get_session()
    for i in range(tries):
        try:
            r = session.get(url, timeout=60)
            if r.status_code == 200 and len(r.content) > 2000:
                r.encoding = "iso-8859-9"
                return r.text
            last = "HTTP %s len %s" % (r.status_code, len(r.content))
        except Exception as e:  # noqa
            last = repr(e)
        time.sleep(2 * (i + 1))
    raise RuntimeError("fetch failed %s :: %s" % (url, last))


PAGE_SIZE = 50


def raw_path(y, p, b, page):
    return os.path.join(RAW, "%s-%s_b%s_p%03d.html.gz" % (y, p, b, page))


def get_branch_page(y, p, b, page, refresh=False, delay=0.6):
    fp = raw_path(y, p, b, page)
    if os.path.exists(fp) and not refresh:
        with gzip.open(fp, "rt", encoding="utf-8") as f:
            return f.read()
    url = ("%s/kpssrobotu/%s/%s/%d.sayfa?SelectedItem=Kadro+Arama"
           "&BranchType=%s&BranchCode=&Organization=&JobTitle=&CityCode=" %
           (BASE, y, p, page, b))
    html = fetch(url)
    with gzip.open(fp, "wt", encoding="utf-8") as f:
        f.write(html)
    time.sleep(delay)
    return html


def get_branch_rows(y, p, b, label, refresh=False, delay=0.6, max_pages=600):
    """Bir branch icin tum sayfalari gez, satirlari topla. (rows, stats)"""
    rows = []
    stats = {}
    seen_codes = set()
    page = 1
    while page <= max_pages:
        html = get_branch_page(y, p, b, page, refresh=refresh, delay=delay)
        prows, st = parse_branch(html, label)
        if page == 1 and st:
            stats = st
        new = [r for r in prows if r["kadro_kodu"] not in seen_codes]
        for r in new:
            seen_codes.add(r["kadro_kodu"])
        rows.extend(new)
        # son sayfa: 50'den az satir, ya da yeni satir gelmedi
        if len(prows) < PAGE_SIZE or not new:
            break
        page += 1
    return rows, stats


# --------------------------------------------------------------------------- #
# parse
# --------------------------------------------------------------------------- #
def parse_header_stats(soup):
    txt = clean(soup.get_text(" "))
    m = HEADER_KK_RE.search(txt)
    if not m:
        return {}
    out = {
        "stated_kadro": to_int(m.group(1)),
        "stated_kontenjan": to_int(m.group(2)),
        "stated_basvuran": None,
        "stated_yerlesen": None,
    }
    mb = HEADER_BASVURAN_RE.search(txt)
    if mb:
        out["stated_basvuran"] = to_int(mb.group(1))
    my = HEADER_YERLESEN_RE.search(txt)
    if my:
        out["stated_yerlesen"] = to_int(my.group(1))
    return out


def _kurum_and_nitelik(td):
    nitelikler = []
    nested = td.find("table")
    if nested:
        for nr in nested.find_all("tr"):
            cells = [clean(c.get_text(" ")) for c in nr.find_all("td")]
            if len(cells) < 2:
                continue
            code, desc = cells[0], cells[1]
            if not code and " - " in desc:
                a, b = desc.split(" - ", 1)
                if a.strip().isdigit():
                    code, desc = a.strip(), b.strip()
            if code or desc:
                nitelikler.append({"kod": code or None, "aciklama": desc})
    # kurum adi = hucre metni (ic tablolar cikarilinca)
    for t in td.find_all("table"):
        t.extract()
    kurum = clean(td.get_text(" "))
    return kurum, nitelikler


def parse_branch(html, branch_label):
    soup = make_soup(html)
    stats = parse_header_stats(soup)

    # sehir kodlarini yakala (form select CityCode)
    if not CITY_CODES:
        for sel in soup.find_all("select"):
            if (sel.get("name") or sel.get("id") or "") == "CityCode":
                with _city_lock:
                    for op in sel.find_all("option"):
                        v = clean(op.get("value"))
                        t = clean(op.get_text())
                        if v and v.isdigit():
                            CITY_CODES[t] = int(v)

    rows = []
    seen_tr = set()

    def cell(tds, i):
        return clean(tds[i].get_text(" ")) if 0 <= i < len(tds) else ""

    for a in soup.select('a[href^="/kadro/"]'):
        m = GUID_RE.match(a.get("href", ""))
        if not m:
            continue
        tr = a.find_parent("tr")
        if tr is None or id(tr) in seen_tr:
            continue
        seen_tr.add(id(tr))
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 6:
            continue
        # kodu hucresi: kadro kodu regexine uyan ilk hucre
        ki = next((i for i, td in enumerate(tds)
                   if KADRO_CODE_RE.match(clean(td.get_text(" ")))), None)
        if ki is None:
            continue
        kodu = clean(tds[ki].get_text(" "))
        # kurum hucresi: ic tablo (nitelik) iceren hucre; yoksa kodu+1
        kui = next((i for i, td in enumerate(tds)
                    if i > ki and td.find("table")), ki + 1)
        if kui >= len(tds):
            continue
        kurum, nitelikler = _kurum_and_nitelik(tds[kui])
        # kurum hucresinden sonraki hucreler: unvan, il, kontenjan, bos, min, max
        rows.append({
            "kadro_kodu": kodu,
            "kadro_guid": m.group(1),
            "kurum": kurum,
            "unvan": cell(tds, kui + 1),
            "il": cell(tds, kui + 2),
            "kontenjan": to_int(cell(tds, kui + 3)),
            "bos_kadro": to_int(cell(tds, kui + 4)),
            "min_puan": parse_puan(cell(tds, kui + 5)),
            "max_puan": parse_puan(cell(tds, kui + 6)),
            "ogrenim": branch_label,
            "nitelikler": nitelikler,
        })
    return rows, stats


# --------------------------------------------------------------------------- #
# donem listesi
# --------------------------------------------------------------------------- #
def load_periods(refresh=False):
    fp = os.path.join(DATA, "periods.json")
    if os.path.exists(fp) and not refresh:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    html = fetch("%s/kpssrobotlari/" % BASE)
    soup = make_soup(html)
    pat = re.compile(r"^/kpssrobotu/(\d{4})/(\d+)/?$")
    out = []
    for a in soup.select('a[href^="/kpssrobotu/"]'):
        m = pat.match(a.get("href", ""))
        if not m:
            continue
        yil, donem = m.group(1), m.group(2)
        is_ekpss = donem in ("91", "92") or "EKPSS" in a.get_text().upper()
        out.append({
            "yil": yil,
            "donem": donem,
            "id": "%s-%s" % (yil, donem),
            "baslik": clean(a.get_text(" ")),
            "url": BASE + a.get("href"),
            "ekpss": is_ekpss,
        })
    # tekillestir
    uniq = {}
    for p in out:
        uniq[p["id"]] = p
    out = sorted(uniq.values(), key=lambda x: (int(x["yil"]), int(x["donem"])),
                 reverse=True)
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return out


# --------------------------------------------------------------------------- #
# donem indir
# --------------------------------------------------------------------------- #
CSV_COLS = ["kadro_kodu", "kurum", "unvan", "il", "ogrenim",
            "kontenjan", "bos_kadro", "min_puan", "max_puan",
            "nitelik_kodlari", "nitelikler", "kadro_guid"]


def nitelik_join(nits):
    kodlar = ";".join([n["kod"] for n in nits if n.get("kod")])
    acik = " | ".join(
        (("%s - %s" % (n["kod"], n["aciklama"])) if n.get("kod") else n["aciklama"])
        for n in nits if n.get("aciklama")
    )
    return kodlar, acik


def scrape_period(p, refresh=False, delay=0.6, branch_workers=3):
    all_rows = {}
    stats = {}
    branch_counts = {}

    def _one(item):
        b, label = item
        rows, st = get_branch_rows(p["yil"], p["donem"], b, label,
                                   refresh=refresh, delay=delay)
        return label, rows, st

    results = []
    if branch_workers > 1:
        with ThreadPoolExecutor(max_workers=branch_workers) as ex:
            for fut in [ex.submit(_one, it) for it in BRANCHES.items()]:
                results.append(fut.result())
    else:
        results = [_one(it) for it in BRANCHES.items()]

    for label, rows, st in results:
        if st:
            stats.update(st)
        branch_counts[label] = len(rows)
        for r in rows:
            key = r["kadro_kodu"]
            if key in all_rows:
                # ayni kadro birden fazla branch'te -> not dus
                all_rows[key].setdefault("_dup_branches", []).append(label)
            else:
                all_rows[key] = r
    rows = list(all_rows.values())

    scraped_kadro = len(rows)
    scraped_kontenjan = sum((r["kontenjan"] or 0) for r in rows)

    period_obj = {
        "id": p["id"],
        "yil": p["yil"],
        "donem": p["donem"],
        "baslik": p["baslik"],
        "url": p["url"],
        "stats": stats,
        "branch_counts": branch_counts,
        "scraped_kadro": scraped_kadro,
        "scraped_kontenjan": scraped_kontenjan,
        "kadrolar": rows,
    }

    # json
    with open(os.path.join(JSOND, "%s.json" % p["id"]), "w", encoding="utf-8") as f:
        json.dump(period_obj, f, ensure_ascii=False, indent=1)

    # csv (utf-8-sig -> Excel Turkce)
    with open(os.path.join(CSVD, "%s.csv" % p["id"]), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["yil", "donem"] + CSV_COLS)
        for r in rows:
            kodlar, acik = nitelik_join(r["nitelikler"])
            w.writerow([p["yil"], p["donem"], r["kadro_kodu"], r["kurum"],
                        r["unvan"], r["il"], r["ogrenim"], r["kontenjan"],
                        r["bos_kadro"], r["min_puan"], r["max_puan"],
                        kodlar, acik, r["kadro_guid"]])

    return period_obj


# --------------------------------------------------------------------------- #
# birlesik ciktilar
# --------------------------------------------------------------------------- #
def build_combined(period_objs):
    # index
    index = []
    for po in period_objs:
        s = po["stats"] or {}
        sk = po["scraped_kadro"]
        skont = po["scraped_kontenjan"]
        stk = s.get("stated_kadro")
        stko = s.get("stated_kontenjan")
        index.append({
            "id": po["id"], "yil": po["yil"], "donem": po["donem"],
            "baslik": po["baslik"],
            "scraped_kadro": sk, "stated_kadro": stk,
            "scraped_kontenjan": skont, "stated_kontenjan": stko,
            "stated_basvuran": s.get("stated_basvuran"),
            "stated_yerlesen": s.get("stated_yerlesen"),
            "kadro_match": (stk is None) or (sk == stk),
            "kontenjan_match": (stko is None) or (skont == stko),
            "branch_counts": po["branch_counts"],
        })
    index.sort(key=lambda x: (int(x["yil"]), int(x["donem"])), reverse=True)
    with open(os.path.join(DATA, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "index.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "yil", "donem", "baslik", "scraped_kadro",
                    "stated_kadro", "kadro_match", "scraped_kontenjan",
                    "stated_kontenjan", "kontenjan_match", "stated_basvuran",
                    "stated_yerlesen"])
        for r in index:
            w.writerow([r["id"], r["yil"], r["donem"], r["baslik"],
                        r["scraped_kadro"], r["stated_kadro"], r["kadro_match"],
                        r["scraped_kontenjan"], r["stated_kontenjan"],
                        r["kontenjan_match"], r["stated_basvuran"],
                        r["stated_yerlesen"]])

    # nitelik sozlugu (kod -> aciklama), normalize edilmis
    nitelik_dict = {}
    for po in period_objs:
        for r in po["kadrolar"]:
            for n in r["nitelikler"]:
                k = n.get("kod")
                a = n.get("aciklama")
                if k and a and k not in nitelik_dict:
                    nitelik_dict[k] = a
    with open(os.path.join(DATA, "nitelikler_sozluk.json"), "w",
              encoding="utf-8") as f:
        json.dump(nitelik_dict, f, ensure_ascii=False, indent=1)

    # all_kadrolar.csv (yalin) + jsonl (yalin, nitelik = kod listesi)
    lean_cols = ["yil", "donem", "kadro_kodu", "kurum", "unvan", "il",
                 "ogrenim", "kontenjan", "bos_kadro", "min_puan", "max_puan",
                 "nitelik_kodlari", "kadro_guid"]
    with open(os.path.join(DATA, "all_kadrolar.csv"), "w",
              encoding="utf-8-sig", newline="") as fc, \
         open(os.path.join(DATA, "all_kadrolar.jsonl"), "w",
              encoding="utf-8") as fj:
        w = csv.writer(fc, delimiter=";")
        w.writerow(lean_cols)
        for po in period_objs:
            for r in po["kadrolar"]:
                kodlar = ";".join([n["kod"] for n in r["nitelikler"] if n.get("kod")])
                w.writerow([po["yil"], po["donem"], r["kadro_kodu"], r["kurum"],
                            r["unvan"], r["il"], r["ogrenim"], r["kontenjan"],
                            r["bos_kadro"], r["min_puan"], r["max_puan"],
                            kodlar, r["kadro_guid"]])
                fj.write(json.dumps({
                    "yil": po["yil"], "donem": po["donem"],
                    "kadro_kodu": r["kadro_kodu"], "kadro_guid": r["kadro_guid"],
                    "kurum": r["kurum"], "unvan": r["unvan"], "il": r["il"],
                    "ogrenim": r["ogrenim"], "kontenjan": r["kontenjan"],
                    "bos_kadro": r["bos_kadro"], "min_puan": r["min_puan"],
                    "max_puan": r["max_puan"],
                    "nitelik_kodlari": [n["kod"] for n in r["nitelikler"] if n.get("kod")],
                }, ensure_ascii=False) + "\n")

    # sehir kodlari
    if CITY_CODES:
        with open(os.path.join(DATA, "il_kodlari.json"), "w",
                  encoding="utf-8") as f:
            json.dump(CITY_CODES, f, ensure_ascii=False, indent=2)

    # ozet istatistik
    summary = {
        "donem_sayisi": len(index),
        "toplam_kadro": sum(r["scraped_kadro"] for r in index),
        "toplam_kontenjan": sum(r["scraped_kontenjan"] for r in index),
        "benzersiz_nitelik": len(nitelik_dict),
        "uyusmayan_donemler": [r["id"] for r in index
                               if not (r["kadro_match"] and r["kontenjan_match"])],
    }
    with open(os.path.join(DATA, "ozet.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return index


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="virgullu id listesi (or. 2014-4,2025-2)")
    ap.add_argument("--refresh", action="store_true", help="ham HTML'i yeniden indir")
    ap.add_argument("--delay", type=float, default=0.35)
    ap.add_argument("--period-workers", type=int, default=2,
                    help="ayni anda islenecek donem sayisi")
    ap.add_argument("--branch-workers", type=int, default=3,
                    help="donem basina ayni anda cekilecek branch sayisi")
    ap.add_argument("--include-ekpss", action="store_true")
    ap.add_argument("--combine-only", action="store_true",
                    help="sadece mevcut json'lardan birlesik cikti uret")
    args = ap.parse_args()

    periods = load_periods(refresh=args.refresh)
    if not args.include_ekpss:
        periods = [p for p in periods if not p["ekpss"]]
    if args.only:
        want = set(args.only.split(","))
        periods = [p for p in periods if p["id"] in want]

    print("Toplam donem: %d" % len(periods))

    period_objs = []
    if args.combine_only:
        for p in periods:
            fp = os.path.join(JSOND, "%s.json" % p["id"])
            if os.path.exists(fp):
                with open(fp, "r", encoding="utf-8") as f:
                    period_objs.append(json.load(f))
    else:
        todo = []
        for p in periods:
            jp = os.path.join(JSOND, "%s.json" % p["id"])
            if os.path.exists(jp) and not args.refresh:
                with open(jp, "r", encoding="utf-8") as f:
                    po = json.load(f)
                period_objs.append(po)
                print("%-9s (mevcut, atlandi) cekilen=%d" %
                      (p["id"], po["scraped_kadro"]), flush=True)
            else:
                todo.append(p)

        done = [0]
        lock = threading.Lock()

        def work(p):
            t0 = time.time()
            po = scrape_period(p, refresh=args.refresh, delay=args.delay,
                               branch_workers=args.branch_workers)
            s = po["stats"] or {}
            stk = s.get("stated_kadro")
            ok = "OK" if (stk is None or po["scraped_kadro"] == stk) else "FARK!"
            with lock:
                done[0] += 1
                print("[%2d/%2d] %-9s cekilen=%5d beyan=%-6s kont=%6d/%-6s %s (%.1fs)"
                      % (done[0], len(todo), p["id"], po["scraped_kadro"], stk,
                         po["scraped_kontenjan"], s.get("stated_kontenjan"),
                         ok, time.time() - t0), flush=True)
            return po

        if args.period_workers > 1 and len(todo) > 1:
            with ThreadPoolExecutor(max_workers=args.period_workers) as ex:
                futs = {ex.submit(work, p): p for p in todo}
                for fut in as_completed(futs):
                    p = futs[fut]
                    try:
                        period_objs.append(fut.result())
                    except Exception as e:  # noqa
                        print("  [HATA] %s -> %s" % (p["id"], e), flush=True)
        else:
            for p in todo:
                try:
                    period_objs.append(work(p))
                except Exception as e:  # noqa
                    print("  [HATA] %s -> %s" % (p["id"], e), flush=True)

    idx = build_combined(period_objs)
    tot_k = sum(r["scraped_kadro"] for r in idx)
    tot_ko = sum(r["scraped_kontenjan"] for r in idx)
    mism = [r["id"] for r in idx if not (r["kadro_match"] and r["kontenjan_match"])]
    print("\n=== OZET ===")
    print("Donem: %d | Toplam kadro: %d | Toplam kontenjan: %d" %
          (len(idx), tot_k, tot_ko))
    print("Uyusmayan donemler: %s" % (", ".join(mism) if mism else "yok"))


if __name__ == "__main__":
    main()
