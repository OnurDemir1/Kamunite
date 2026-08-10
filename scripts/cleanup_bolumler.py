# -*- coding: utf-8 -*-
"""bolumler.json + bolum_kod.json'dan bolum-OLMAYAN girdileri temizler:
junk kodlar, tam-cumle sart metinleri ve tek-basina gercek bolum olmayan
genel kelimeler (Guvenlik/Personel/Yonetim/Bilgisayar). Cok-kelimeli gercek
programlar (Bilgisayar Programciligi, Yonetim Bilisim Sistemleri ...) KORUNUR.

    python scripts/cleanup_bolumler.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# tek basina gercek bolum olmayan genel kelimeler (cok-kelimeli varyantlari kalir)
GENERIC = {"guvenlik", "personel", "yonetim", "bilgisayar"}


def norm(s):
    s = (s or "").replace("I", "ı").replace("İ", "i").lower()
    for a, b in [("ç","c"),("ğ","g"),("ı","i"),("ö","o"),("ş","s"),("ü","u"),("â","a"),("î","i"),("û","u")]:
        s = s.replace(a, b)
    return s.strip()


def is_junk(b):
    """b bir bolum ADI degil de junk/cumle/genel-kelime mi?"""
    n = norm(b)
    if n in GENERIC:
        return True
    if n == "---" or n.isdigit() or len(n) < 4:  # ayirac / kod artigi (5009) / cok kisa — ama "Yapi"/"Orme" (4) KALIR
        return True
    if re.search(r"[.!?]$", b.strip()):         # cumle (nokta ile biter)
        return True
    if re.search(r"belgele|bildigini|oldugunu|yaptigini|sonuclanmas|uygulanmakta|"
                 r"bakiniz|okumak ve|tahkikat|vardiya|sertifikasina sahip", n):
        return True
    return False


def main():
    bp = os.path.join(DATA, "bolumler.json")
    BOL = json.load(open(bp, encoding="utf-8"))
    rem = [b for b in BOL if is_junk(b)]
    kal = [b for b in BOL if not is_junk(b)]
    json.dump(kal, open(bp, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("bolumler.json: %d -> %d  (%d silindi)" % (len(BOL), len(kal), len(rem)))

    # bolum_kod.json/bolumLevel icindeki ayni anahtarlari da at
    kp = os.path.join(DATA, "bolum_kod.json")
    if os.path.exists(kp):
        bk = json.load(open(kp, encoding="utf-8"))
        lvl = bk.get("bolumLevel", {})
        remset = set(rem)
        atilan = [k for k in lvl if k in remset]
        for k in atilan:
            del lvl[k]
        bk["bolumLevel"] = lvl
        json.dump(bk, open(kp, "w", encoding="utf-8"), ensure_ascii=False)
        print("bolum_kod.json/bolumLevel: %d anahtar atildi" % len(atilan))


if __name__ == "__main__":
    main()
