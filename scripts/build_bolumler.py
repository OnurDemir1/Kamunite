# -*- coding: utf-8 -*-
"""bolumler.json'u TUM veriden eksiksiz yeniden cikarir.
Kural: bir nitelik aciklamasi BOLUM'dur eger bir SART-FIILI icermiyorsa
(olmak/bilmek/sahip/bakiniz/aranmaktadir/uygulan... = sart; degil = bolum adi).
'/' ile ayrilmis alternatifler ayri bolum olarak eklenir. Mevcut liste ile birlestirilir (kayip olmasin)."""
import json, glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

def norm(s):
    s=(s or '').replace('I','ı').replace('İ','i').lower()
    for a,b in [('ç','c'),('ğ','g'),('ı','i'),('ö','o'),('ş','s'),('ü','u'),('â','a'),('î','i'),('û','u')]:
        s=s.replace(a,b)
    return s.strip()

SART = ['olmak','bilmek','sahip','bakiniz','aranmaktadir','aranir','uygulan',
        'yapmis','gormus','edilmis','edilir','tahkikat','sertifika','belgesi',
        'gerekmekte','sinifi surucu','vardiya']
def is_dept(ac):
    an = norm(ac)
    if len(an) < 3: return False
    if any(w in an for w in SART): return False
    if 'program' in an and 'birinden' in an: return False   # 'asagidaki ... programlarindan birinden'
    if an.startswith('(') or an.startswith('bu kadro'): return False
    return True

# tek basina gercek bolum olmayan genel kelimeler (cok-kelimeli varyantlari kalir)
GENERIC = {"guvenlik", "personel", "yonetim", "bilgisayar"}
def is_junk(b):
    """cikan aday bolum-ADI degil de junk/cumle/genel-kelime mi? (cleanup_bolumler.py ile ayni kural)"""
    n = norm(b)
    if n in GENERIC: return True
    if n == '---' or n.isdigit() or len(n) < 4: return True   # ayirac/kod artigi(5009)/cok kisa — "Yapi"/"Orme"(4) KALIR
    if re.search(r'[.!?]$', b.strip()): return True        # cumle
    if re.search(r'belgele|bildigini|oldugunu|yaptigini|sonuclanmas|uygulanmakta|'
                 r'bakiniz|okumak ve|tahkikat|vardiya|sertifikasina sahip', n): return True
    return False

# mevcut listeyi koru
try: existing = set(json.load(open(os.path.join(DATA,"bolumler.json"),encoding="utf-8")))
except: existing = set()

found = set()
for f in glob.glob(os.path.join(DATA,"json","*.json")):
    for k in json.load(open(f,encoding="utf-8"))["kadrolar"]:
        for n in k.get("nitelikler",[]):
            ac = (n.get("aciklama","") or "").strip()
            if not ac or not is_dept(ac): continue
            for part in ac.split("/"):
                p = part.strip()
                if len(p) >= 3 and not p.startswith("("):
                    found.add(p)

allb = found | existing
# temizle: cift kayit (normalize bazli) -> DUZGUN YAZIMI tercih et (hepsi-BUYUK olani degil)
def _score(s):
    return (1 if any(c.islower() for c in s) else 0, -len(s))   # once kucuk-harf iceren, sonra kisa
seen = {}
for b in allb:
    key = norm(b)
    if not key: continue
    if key not in seen or _score(b) > _score(seen[key]):
        seen[key] = b
out = sorted((b for b in seen.values() if not is_junk(b)), key=lambda s: norm(s))
json.dump(out, open(os.path.join(DATA,"bolumler.json"),"w",encoding="utf-8"), ensure_ascii=False)

print("ONCE:", len(existing), "| YENI cikan:", len(found), "| TOPLAM (birlesik):", len(out))
for tb in ["Makine Mühendisliği","Elektrik-Elektronik Mühendisliği","Hemşirelik ve Sağlık Hizmetleri",
           "Acil Bakım Teknikerliği","Siyaset Bilimi ve Uluslararası İlişkiler","İstatistik","Sosyal Hizmet",
           "İşletme-Ekonomi","Ebelik","Yönetim Bilişim Sistemleri"]:
    print(("  VAR   " if tb in seen.values() or norm(tb) in seen else "  YOK!  ")+tb)
