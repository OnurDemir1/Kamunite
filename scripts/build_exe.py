#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KPSS Tercih Robotu'nu tek .exe olarak paketler (Windows).

Gereksinim:  pip install pywebview pyinstaller
Çalıştır:    python scripts/build_exe.py
Çıktı:       dist/KPSS Tercih Robotu/KPSS Tercih Robotu.exe  (+ index.html + data/)
Dağıtım:     bu klasörü olduğu gibi zip'le/taşı (exe tek başına çalışmaz, yanındaki
             _internal, index.html ve data klasörüne ihtiyaç duyar).
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "Kamunite"
DEST = os.path.join(ROOT, "dist", NAME)


def run():
    os.chdir(ROOT)
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--onedir",
           "--windowed", "--name", NAME, "--collect-all", "webview",
           "--paths", os.path.join(ROOT, "scripts"), "--hidden-import", "fetch_ilanlar"]
    ico = os.path.join(ROOT, "assets", "logo.ico")
    if os.path.exists(ico):
        cmd += ["--icon", ico]
    cmd += ["app.py"]
    print(">>", " ".join(cmd))
    subprocess.check_call(cmd)

    # arayüz + veri (raw HARİÇ) exe'nin yanına
    shutil.copy(os.path.join(ROOT, "index.html"), DEST)
    data_dst = os.path.join(DEST, "data")
    os.makedirs(os.path.join(data_dst, "json"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "data", "index.json"), data_dst)
    for extra in ("unvanlar.json", "il_kodlari.json", "bolumler.json", "nitelik_list.json", "bolum_kod.json", "sertifikalar.json", "aktif_ilanlar.json", "bolum_esanlam.json"):
        sp = os.path.join(ROOT, "data", extra)
        if os.path.exists(sp):
            shutil.copy(sp, data_dst)
    src_json = os.path.join(ROOT, "data", "json")
    for f in os.listdir(src_json):
        if f.endswith(".json"):
            shutil.copy(os.path.join(src_json, f), os.path.join(data_dst, "json", f))

    print("\nTAMAM ->", os.path.join(DEST, NAME + ".exe"))


if __name__ == "__main__":
    run()
