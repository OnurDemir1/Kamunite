# -*- coding: utf-8 -*-
"""Kariyer Kapısı'ndaki AKTİF iş alım ilanlarını PUBLIC API'den çeker ->
data/aktif_ilanlar.json. (Giriş gerekmez.) Her unvan için: öğrenim, KPSS puan türü,
asgari puan, kontenjanlar, aranan bölümler (bizim bolumler.json ile eşlenmiş) ve şart metni.

    python scripts/fetch_ilanlar.py
"""
import urllib.request, ssl, json, re, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
API = "https://api.kariyerkapisi.gov.tr/api"
CTX = ssl.create_default_context()   # TLS sertifika dogrulamasi ACIK (MITM veri-zehirlemeye karsi; endpoint gecerli sertifika kullaniyor)
HDR = {"User-Agent": "Mozilla/5.0 Chrome/120", "Content-Type": "application/json"}

def norm(s):
    s = (s or "").replace("I", "ı").replace("İ", "i").lower()
    for a, b in [("ç","c"),("ğ","g"),("ı","i"),("ö","o"),("ş","s"),("ü","u"),("â","a"),("î","i"),("û","u")]:
        s = s.replace(a, b)
    return s

def post(path, obj, tries=3):
    for t in range(tries):
        try:
            req = urllib.request.Request(API+path, data=json.dumps(obj).encode(), headers=HDR, method="POST")
            return json.loads(urllib.request.urlopen(req, context=CTX, timeout=45).read().decode("utf-8","replace"))
        except Exception as e:
            if t == tries-1: raise
            time.sleep(1.5)

# aranan bolumleri eslemek icin bizim tam listemiz (run() icinde data_dir'den yuklenir)
BOLN = []

def temizle(t):
    t = re.sub(r"\[/?[a-zA-Z]+\]", " ", t or "")   # [justify] vb. etiketleri at
    return re.sub(r"[ \t]+", " ", t).strip()

def puan_ogrenim(metin):
    m = norm(metin)
    turu = None; ogr = None
    # puan turu: "kpssp94" / "kpss p94" / "p94" / "p-94" ... (bosluklu/bitisik hepsi)
    if re.search(r"kpssp94|\bp\s*94\b|p-94", m):   turu, ogr = "KPSSP94", "Ortaogretim"
    elif re.search(r"kpssp93|\bp\s*93\b|p-93", m): turu, ogr = "KPSSP93", "Onlisans"
    elif re.search(r"kpssp3|\bp\s*3\b|p-3", m):    turu, ogr = "KPSSP3", "Lisans"
    if ogr is None:                                # puan turu yoksa metinden ogrenim
        if re.search(r"\bon\s?lisans\b", m):        ogr = "Onlisans"
        elif re.search(r"\blisans\b", m) and "onlisans" not in m: ogr = "Lisans"
        elif re.search(r"orta\s?ogretim|\blise\b", m): ogr = "Ortaogretim"
        else:                                       # yedek cikarim: yuksek guvenli, tek sinyal varsa
            myo = bool(re.search(r"meslek yuksekokul|\bmyo\b", m))   # MYO = onlisans
            fak = ("fakulte" in m and "mezun" in m)                  # fakulte mezunu = lisans
            if   myo and not fak: ogr = "Onlisans"
            elif fak and not myo: ogr = "Lisans"
            # iki sinyal birden (karma duzey) veya hicbiri -> None birak (yanlis elemeyi onle)
    # asgari puan: "en az 60 puan", "asgari 50", "50 ve daha yukari", "60 puana sahip"
    # ONCE puan-TURU rakamini (KPSSP94/P93/P3) metinden temizle -> '94/93' yanlislikla puan sanilmasin;
    # (?<!\d) ile yil-benzeri token'lari (2050 -> 50) ele.
    ms = re.sub(r"kpssp\s*9[34]|kpssp\s*3|\bp\s*9[34]\b|\bp\s*3\b|p-9[34]|p-3", " ", m)
    mp = None
    for pat in (r"(?:en az|asgari|minimum)\s*(?<!\d)(\d{2,3})\s*(?:puan|ve|kpss|['\"]?d[ae]n)",
                r"(?<!\d)(\d{2,3})\s*(?:ve (?:daha )?(?:yukari|uzeri|fazla)|puan)"):
        mm = re.search(pat, ms)
        if mm and 30 <= int(mm.group(1)) <= 100:
            mp = int(mm.group(1)); break
    if turu and mp == {"KPSSP94": 94, "KPSSP93": 93, "KPSSP3": 3}.get(turu):
        mp = None                                # emniyet: turu-soneki asla asgari puan degildir
    return turu, ogr, mp

def bolumleri_bul(metin):
    mn = norm(metin)
    out = []
    for b, bn in BOLN:
        st = 0
        while True:                              # TUM occurrence'lari dene: ilki cekimli kelime
            i = mn.find(bn, st)                   # icinde (or. 'personeli') olsa bile sonraki tam eslesmeyi yakala
            if i < 0:
                break
            a = mn[i-1] if i > 0 else " "
            z = mn[i+len(bn)] if i+len(bn) < len(mn) else " "
            if not a.isalnum() and not z.isalnum():
                out.append(b); break
            st = i + 1
    return sorted(set(out), key=lambda s: norm(s))

def bolum_sarti(metin, bolumler):
    """liste = belirli bolumler var | genel = herhangi bir program/lise | ilgili = 'ilgili bolum' (metinde listelenmemis) | belirsiz."""
    if bolumler: return "liste"
    m = norm(metin)
    if "herhangi bir" in m and ("program" in m or "alan" in m or "bolum" in m): return "genel"
    # ortaogretim/lise mezunu olmak (bolum belirtmeden) = genel
    if re.search(r"(orta ?ogretim|lise)[^.]{0,28}mezunu ol", m): return "genel"
    if re.search(r"en az.*(lise|ilkogretim|ilkokul|ortaokul).*(mezun|dengi)", m): return "genel"
    if "ilgili" in m and ("bolum" in m or "program" in m or "alan" in m): return "ilgili"
    return "belirsiz"

def kontenjan_parse(klist):
    iller = []
    tot = 0
    for k in (klist or []):
        il = temizle(k.get("il", "") if isinstance(k, dict) else str(k))
        m = re.search(r"KONTENJAN\s*\((\d+)\)\s*$", il) or re.search(r"\((\d+)\)\s*$", il)
        say = int(m.group(1)) if m else (k.get("kontenjan") if isinstance(k, dict) and isinstance(k.get("kontenjan"), int) else 1)
        il = re.sub(r"\s*KONTENJAN\s*\(\d+\)\s*$", "", il).strip()
        iller.append({"yer": il, "kontenjan": say}); tot += say
    return iller, tot

def run(data_dir=DATA):
    """Aktif ilanlari cek, parse et, data_dir/aktif_ilanlar.json'a yaz. guncelleme string'i dondur.
    (app.py bunu 'Yenile' icin cagirir; main() de bunu kullanir.)"""
    global BOLN
    with open(os.path.join(data_dir, "bolumler.json"), encoding="utf-8") as f:
        BOL = json.load(f)
    BOLN = [(b, norm(b)) for b in BOL if len(norm(b)) >= 5]
    print(">> Aktif ilanlar cekiliyor...")
    liste = post("/ilan/SearchIlanPublic", {"krM_ID": 0, "searchText": "", "il": "0", "ilanTuru": "0"})
    if isinstance(liste, dict):                   # zarf sekli gelirse ({data:[...]}) diziyi cek
        liste = liste.get("data") or liste.get("list") or liste.get("result") or []
    if not isinstance(liste, list):
        raise RuntimeError("SearchIlanPublic beklenmeyen sekil: %r" % type(liste))
    # norm() ile karsilastir -> "Aktif"/"AKTIF"/"aktif" (Turkce buyuk-I sorunu) hepsi tutar
    liste = [i for i in liste if isinstance(i, dict) and norm(i.get("sonDurumu", "")).startswith("aktif")]
    print("   aktif ilan:", len(liste))
    ilanlar = []
    eksik = 0
    for idx, il in enumerate(liste, 1):
        guid = il.get("guid")
        try:
            alt = post("/altilan/GetAltIlanInfoByIlanIdPublic", {"ilanGuid": guid})
        except Exception as e:
            eksik += 1; print("   ! %s alinamadi: %s" % (guid, e)); continue
        if not isinstance(alt, list):             # None/zarf -> bos gec, TUM cekimi cokertme
            alt = alt.get("data") if isinstance(alt, dict) else None
            if not isinstance(alt, list):
                alt = []
        unvanlar = []
        for a in alt:
            if not isinstance(a, dict):
                continue
            metin = temizle(a.get("ilanMetni", ""))
            turu, ogr, mp = puan_ogrenim(metin)
            iller, tot = kontenjan_parse(a.get("kontenjanList"))
            bols = bolumleri_bul(metin)
            unvanlar.append({
                "unvan": (a.get("unvan") or "").strip(),
                "baslik": (a.get("ilanBaslik") or "").strip(),
                "ogrenim": ogr, "puanTuru": turu, "minPuan": mp,
                "kontenjan": tot, "iller": iller,
                "bolumler": bols,
                "bolumSarti": bolum_sarti(metin, bols),
                "metin": metin,
            })
        ilanlar.append({
            "guid": guid, "kurum": (il.get("kurumAdi") or "").strip(), "birim": (il.get("birimAdi") or "").strip(),
            "baslik": (il.get("ilanBaslik") or "").strip(), "tur": il.get("ilanTuru"),
            "bas": il.get("basTarih"), "bit": il.get("bitTarih"),
            "link": "https://kariyerkapisi.gov.tr/IlanDetay?i=" + str(guid),
            "toplamKontenjan": sum(u["kontenjan"] for u in unvanlar),
            "unvanlar": unvanlar,
        })
        print("   [%d/%d] %s — %d unvan" % (idx, len(liste), (il.get("kurumAdi") or "")[:34], len(unvanlar)))
        time.sleep(0.3)
    out = {"guncelleme": time.strftime("%Y-%m-%d %H:%M"), "ilanSayisi": len(ilanlar), "ilanlar": ilanlar}
    hedef = os.path.join(data_dir, "aktif_ilanlar.json")
    tmp = hedef + ".tmp"                           # atomik yaz: yarim/bozuk dosya birakma
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    os.replace(tmp, hedef)
    print("TAMAM -> %s (%d ilan, %d eksik, %.2f MB)" % (hedef, len(ilanlar), eksik, os.path.getsize(hedef)/1048576))
    return out["guncelleme"]

if __name__ == "__main__":
    run(DATA)
