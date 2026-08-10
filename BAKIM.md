# Kamunite — Bakım / Düzenleme Kılavuzu

Bu uygulama **veri-güdümlü** çalışır: "hangi kadro neyi istiyor" bilgisi kodda değil,
düzenlenebilir birkaç veri dosyasındadır. Bir kadro için ayrı ayar YOKTUR — kurallar
170 bin kadronun tamamına aynı anda uygulanır.

## Neyi nereden düzenlersin

| İstediğin | Dosya | Not |
|---|---|---|
| Bölüm ekle/çıkar | `data/bolumler.json` | Düz liste. Eklediğin bölüm otomatik eşleşir (açıklama adıyla). |
| Bir bölümün öğrenim seviyesi | `data/bolum_kod.json` → `bolumLevel` | `{"Bölüm Adı": ["Lisans","Onlisans"]}`. |
| Sertifika ekle/çıkar | `data/sertifikalar.json` → `list` | `{"kod","ad","tam"}`. `tam` = kadrodaki tam açıklama (eşleşme buna göre). |
| Ham kadro verisi | `data/json/<yil>-<donem>.json` | ÖSYM/memurlar.net'ten gelen asıl veri. |
| Dönem listesi | `data/index.json` | Her dönem için bir satır. |

> Cinsiyet, ehliyet ve YDS tespiti küçük ve %100 doğrulanmış desenlerle yapılır
> (`index.html` içinde `ydsReqOf`, `ehliyetOk`, `_cinsiyet`). Nadiren dokunulur.

## Yeni KPSS dönemi eklemek

1. Yeni dönemi çek: `python scripts/kpss_scraper.py` (veya ilgili çekme scripti) →
   `data/json/<yil>-<donem>.json` oluşur.
2. `data/index.json`'a o dönemin satırını ekle.
3. **Tek komut** ile türetilmiş verileri güncelle:
   ```
   python scripts/rebuild_all.py
   ```
   Bu; bölüm listesini, bölüm→seviye haritasını ve sertifika listesini ham veriden
   yeniden üretir.
4. Masaüstü uygulamasını yeniden paketle (isteğe bağlı):
   ```
   python scripts/build_exe.py
   ```

## Elle bir düzeltme yaptıysan

`data/bolumler.json` / `data/sertifikalar.json` gibi bir dosyayı elle düzenlediysen
uygulama zaten onları doğrudan okur — sadece `python scripts/make_demo.py` ile demoyu,
`python scripts/build_exe.py` ile .exe'yi tazelemen yeterli. `rebuild_all.py` ham veriden
yeniden ürettiği için **elle eklediğin bölümleri de korur** (mevcut listeyle birleştirir).

## Türetilmiş dosyaları üreten scriptler

- `build_bolumler.py` — ham nitelik açıklamalarından bölüm listesini çıkarır
  (kural: şart-fiili içermeyen = bölüm; "…mezun olmak", "…sertifikası", "erkek olmak" vb. = bölüm değil).
- `build_bolum_level.py` — her bölümün geçtiği öğrenim seviyelerini bulur (isim eşleşmesiyle).
- `build_sertifika.py` — kadrolarda istenen tüm sertifikaları temiz adlarla çıkarır.
- `rebuild_all.py` — yukarıdakileri doğru sırayla, tek komutta çalıştırır.

## Neden kod değil de veri?

Nitelik **kodları** dönemden döneme yeniden atandığı için (aynı kod farklı dönemde
farklı anlam) eşleştirme **açıklama (isim) bazlıdır** — dönemden bağımsız ve güvenilir.
Bu yüzden bir şeyi düzeltmek çoğu zaman sadece bir liste dosyasını düzenlemektir.
