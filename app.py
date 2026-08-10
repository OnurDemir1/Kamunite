#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KPSS Tercih Robotu — Windows masaüstü uygulaması.

Hazır glassmorphism arayüzünü (index.html) native bir pencerede açar.
Tarayıcı yok; veri (data/) uygulamanın yanındaki klasörden okunur.
Küçük bir yerel HTTP sunucusu 127.0.0.1'de sadece bu uygulamaya hizmet verir
(böylece tarayıcının fetch güvenlik kısıtı sorun çıkarmaz).
"""
import os
import sys
import socket
import threading
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

import webview


def base_dir():
    """index.html ve data/ klasörünün bulunduğu kök."""
    if getattr(sys, "frozen", False):        # PyInstaller ile paketlendiyse
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def pick_port(pref=47615):
    """Once SABIT bir portu dene: origin (host:port) sabit kalinca WebView2
    localStorage'i (gorunum vb.) acilislar arasi korur. Doluysa serbest porta dus."""
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", pref)); s.close(); return pref
    except OSError:
        try: s.close()
        except Exception: pass
        return free_port()


def profil_path():
    """Kullanici profilinin diskteki yolu — porttan/rebuild'den bagimsiz kalici konum."""
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    d = os.path.join(base, "Kamunite")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        d = base_dir()
    return os.path.join(d, "profil.json")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *a):            # konsolu kirletme
        pass

    def _host_ok(self):                   # DNS-rebinding'e karsi: yalniz localhost Host'u kabul et
        h = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        return h in ("127.0.0.1", "localhost", "::1", "")

    def do_GET(self):
        if not self._host_ok():
            self.send_error(403); return
        return super().do_GET()

    def do_HEAD(self):
        if not self._host_ok():
            self.send_error(403); return
        return super().do_HEAD()


def start_server(root, port):
    handler = partial(QuietHandler, directory=root)
    httpd = HTTPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


class Api:
    """JS'ten cagrilan Python koprusu (CORS olmadan canli veri cekmek icin)."""
    def yenileIlanlar(self):
        """Kariyer Kapisi'ndan guncel aktif ilanlari cek -> data/aktif_ilanlar.json.
        JS: window.pywebview.api.yenileIlanlar()"""
        try:
            base = base_dir()
            sp = os.path.join(base, "scripts")
            if sp not in sys.path:                # her cagride tekrar eklenmesin
                sys.path.insert(0, sp)
            import fetch_ilanlar
            g = fetch_ilanlar.run(os.path.join(base, "data"))
            return {"ok": True, "guncelleme": g}
        except Exception as e:
            return {"ok": False, "hata": str(e)}

    def profilKaydet(self, s):
        """JS profilini (JSON string) diske yazar. Bos string => sil.
        JS: window.pywebview.api.profilKaydet(json)"""
        try:
            p = profil_path()
            if not s:
                if os.path.exists(p):
                    os.remove(p)
            else:
                tmp = p + ".tmp"                  # atomik yaz: yarim/bozuk profil birakma
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(s)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, p)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "hata": str(e)}

    def profilOku(self):
        """Diskteki profili JSON string olarak dondur; yoksa None.
        JS: await window.pywebview.api.profilOku()"""
        try:
            p = profil_path()
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    return f.read()
        except Exception:
            pass
        return None


def main():
    root = base_dir()
    index = os.path.join(root, "index.html")
    if not os.path.exists(index):
        # veri/arayüz bulunamadıysa kullanıcıya net mesaj
        print("HATA: index.html bulunamadı: %s" % index)
        sys.exit(1)

    try:
        port = int(os.environ.get("KPSS_PORT") or 0) or pick_port()
    except ValueError:                            # KPSS_PORT sayisal degilse serbest porta dus
        port = pick_port()
    start_server(root, port)
    url = "http://127.0.0.1:%d/index.html" % port

    if os.environ.get("KPSS_SERVE_ONLY") == "1":
        # test modu: pencereyi açmadan sunucuyu ayakta tut
        print("SERVE_ONLY %s" % url)
        import time
        time.sleep(float(os.environ.get("KPSS_SERVE_SECONDS", "6")))
        return

    webview.create_window(
        "Kamunite — KPSS Tercih Robotu",
        url,
        width=1200, height=820,
        min_size=(420, 620),
        background_color="#0c0c0e",   # native cerceve; koyu tema zemini
        js_api=Api(),                 # JS'ten canli ilan yenileme koprusu
    )
    webview.start()   # native pencere; kapatılınca döner


if __name__ == "__main__":
    main()
