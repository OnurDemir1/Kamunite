# -*- coding: utf-8 -*-
"""TEK KOMUT: eşleştirme için gereken tüm türetilmiş veri dosyalarını
ham dönem JSON'larından (data/json/*.json) yeniden üretir.

    python scripts/rebuild_all.py

Yeni bir KPSS dönemi eklediğinde (data/json/ içine yeni <yil>-<donem>.json koyup
data/index.json'a satır ekledikten sonra) sadece bunu çalıştır; sonra istersen
python scripts/build_exe.py ile .exe'yi yeniden paketle.
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
# SIRA ÖNEMLİ: bolumler önce (bolum_level onu okur)
STEPS = [
    ("Bolum listesi (bolumler.json)",           "build_bolumler.py"),
    ("Bolum-seviye haritasi (bolum_kod.json)",  "build_bolum_level.py"),
    ("Sertifika listesi (sertifikalar.json)",   "build_sertifika.py"),
    ("Unvan listesi (unvanlar.json)",           "normalize_unvan.py"),
]

def main():
    for baslik, script in STEPS:
        print("\n=== %s ===" % baslik)
        subprocess.check_call([sys.executable, os.path.join(HERE, script)])
    print("\nTAMAM — tüm türetilmiş veri güncellendi. Uygulama bunları otomatik okur.")
    print("(.exe için: python scripts/build_exe.py)")

if __name__ == "__main__":
    main()
