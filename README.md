# Kamunite — KPSS Tercih Asistanı

KPSS adayları için kişisel bir tercih aracı. İki özellik:

1. **Kadro Sorgulama** — 72 dönemlik **170.627** geçmiş KPSS kadrosunu filtrele; profiline göre **"Bana uygun"** olanları bul (öğrenim, bölüm, puan, cinsiyet, ehliyet, YDS, sertifika, il).
2. **Güncel İş Alım İlanları** — [Kariyer Kapısı](https://kariyerkapisi.gov.tr)'ndaki **aktif** ilanları çeker ve profiline uyan unvanları bulur. Uygulama açılışında ve İlanlar sayfasına girişte **otomatik tazelenir** (yeni ilanlar kendiliğinden yakalanır).

Koyu, cam/katı-yüzeyli arayüz; sayılar monospace. Tüm veri **yalnızca cihazda** saklanır, hiçbir yere gönderilmez.

## Çalıştırma

**Hazır uygulama (Windows):** `dist/Kamunite/` klasörünü indir, `Kamunite.exe`'yi çift tıkla. (exe tek başına çalışmaz; yanındaki `_internal`, `index.html` ve `data/` gerekir — klasörü bütün taşı.)

**Kaynaktan (geliştirme):**
```bash
pip install pywebview
python app.py
```

## Yeniden derleme (exe)
```bash
pip install pywebview pyinstaller
python scripts/build_exe.py   # -> dist/Kamunite/
```

## Veriyi güncelleme
- **Aktif ilanlar:** `python scripts/fetch_ilanlar.py` (uygulama içindeki "↻ Yenile" de aynısını yapar).
- **Yeni KPSS dönemi eklendiğinde:** dönem JSON'unu `data/json/`'a koy, `data/index.json`'a satır ekle, sonra `python scripts/rebuild_all.py`.

## Yapı
| Yol | Açıklama |
|---|---|
| `index.html` | Tüm arayüz + eşleştirme motoru (tek dosya, vanilla JS) |
| `app.py` | Masaüstü sarmalayıcı (pywebview + yerel HTTP sunucu + canlı-çekim köprüsü) |
| `scripts/` | Veri hattı + build betikleri |
| `data/` | KPSS dönem verisi (`json/`) + türetilmiş tablolar + aktif ilanlar |
| `BAKIM.md` | Bakım/güncelleme notları |

> Veri kaynağı: ÖSYM tercih kılavuzları. Bu araç kişisel kullanım içindir; kesin bilgi için ÖSYM kılavuzunu esas alın.
