# Doğrulama Raporu

Bu veri seti iki katmanda doğrulanmıştır.

## 1) Her dönem: çekilen ↔ beyan edilen (memurlar.net başlık toplamı)

Scraper her dönemde çektiği kadro sayısını (`scraped_kadro`) ve kontenjan toplamını
(`scraped_kontenjan`), o dönemin sayfasındaki resmî beyanla (*"Bu alımda X kadro için
toplam Y kontenjan açıldı…"*) karşılaştırır. Tam liste: `index.csv`.

**Sonuç: 72 dönemin 71'inde birebir eşleşme.**

| Durum | Dönem sayısı |
|-------|-------------|
| Kadro + kontenjan tam eşleşme | 71 |
| Kısmi (kaynak eksiği) | 1 → `2019-2` |

### 2019-2 hakkında (tek istisna)
- Beyan: **1142 kadro / 1749 kontenjan** — Çekilen: **1130 kadro / 1735 kontenjan** (12 kadro eksik).
- Neden **scraper hatası değil**: memurlar.net'in bu döneme ait robotunda öğrenim
  düzeyi (Ortaöğretim 64 + Önlisans 341 + Lisans 725 = 1130) **ve** il bazlı arama da
  aynı 1130 kadroyu döndürüyor. Yani kaynak, başlığında 1142 yazmasına rağmen kendi
  verisinde yalnızca 1130 kadro barındırıyor. Eksik 12 kadro kaynakta hiçbir arama
  yöntemiyle görünmüyor.
- **Tamamlama seçeneği:** Bu 12 kadro yalnızca ÖSYM'nin 2019/2 resmî tercih kılavuzu
  PDF'inden alınabilir (istenirse eklenebilir).

## 2) Resmî ÖSYM çapraz kontrolü (örnek dönem)

memurlar.net verisinin ÖSYM ile birebir aynı olduğunu doğrulamak için ÖSYM'nin kendi
"Yerleştirme Sonuçlarına İlişkin Sayısal Bilgiler" belgesi indirilip kıyaslandı.

### KPSS-2024/1 — ÖSYM resmî PDF ↔ bizim veri
Kaynak: `osym_resmi/kpss_2024-1_sayisalbilgiler.pdf`
(https://dokuman.osym.gov.tr/pdfdokuman/2024/KPSS/TERCIH1/sayisalbil29072024.pdf)

| Öğrenim | ÖSYM kontenjan | Bizim kontenjan | ÖSYM yerleşen | Sonuç |
|---------|---------------:|----------------:|--------------:|:-----:|
| Lisans | 1.046 | 1.046 | 1.046 | ✅ |
| Önlisans | 615 | 615 | 615 | ✅ |
| Ortaöğretim | 155 | 155 | 155 | ✅ |
| **TOPLAM** | **1.816** | **1.816** | **1.816** | ✅ |

Tercih yapan aday: ÖSYM 98.526 = bizim `stated_basvuran` 98.526. ✅

**Sonuç:** memurlar.net verisi ÖSYM resmî rakamlarıyla hem toplamda hem öğrenim
düzeyi kırılımında birebir aynıdır; öğrenim etiketlemesi (BranchType) doğrudur.

## Kadro detayları ve nitelik kapsamı

Her kadro için indirilen detaylar: `kadro_kodu`, `kurum`, `unvan`, `il`, `ogrenim`,
`kontenjan`, `bos_kadro`, `min_puan`, `max_puan`, **aranan nitelikler** (kod + açıklama)
ve `kadro_guid`.

- **Nitelik kapsamı: %99,4** — 170.627 kadronun 169.549'unda aranan nitelik(ler) mevcut.
- Nitelik alanı boş olan **1.078 kadro (%0,6)**: tamamı **ortaöğretim** düzeyi sağlık/teknik
  kadrolar (Hemşire 472, Sağlık Memuru 409, Teknisyen 127, Ebe 70). Yoğunlaştığı dönemler:
  2015-3 (636), 2016-3 (310), 2025-5 (127), 2020-8 (5).
- Bunlar **scraper eksiği değildir**: memurlar.net'in bu kadrolar için *kadro detay
  sayfası da* (`/kadro/{guid}/`) boş; kaynakta nitelik verisi yok. Tam nitelik yalnızca
  ÖSYM resmî kılavuz PDF'inden gelebilir.

### Kadro detay sayfasındaki ek alan
memurlar.net kadro detay sayfasında satırda olmayan tek ek alan **"Sınıf / Derece"**
(ör. *Sağlık Hizmetleri (SH)*). İstenirse bu alan tüm kadrolar için ayrıca toplanabilir
(kadro başına 1 istek gerektirir). **Puan türü** (KPSSP3/P93/P94…) memurlar.net'te hiçbir
sayfada yer almaz; gerekirse ÖSYM kılavuzundan çıkarılır (öğrenim düzeyi iyi bir yaklaşıktır).

## Son denetimde bulunan ve düzeltilen hata (kodlama)

Son detaylı denetimde **7 dönemde** (2025-5, 2025-4, 2022-11, 2024-5, 2024-4,
2012-5, 2021-10 — ~18.248 satır) Türkçe karakterlerin (ğ, ş, İ…) çift-kodlandığı
(mojibake) tespit edildi.
- **Kök neden:** `BeautifulSoup` + `lxml`, zaten çözümlenmiş (unicode) bir metni
  `<meta charset=iso-8859-9>` etiketiyle görünce yeniden kodluyordu (belirleyici
  değildi; sadece bazı büyük dönemleri etkiledi).
- **Düzeltme:** parser artık HTML'i UTF-8 bayta çevirip `from_encoding="utf-8"` ile
  besliyor (`make_soup`). Ham önbellek (`data/raw/`) doğru olduğu için **yeniden
  indirmeye gerek kalmadan** 72 dönem önbellekten yeniden işlendi.
- **Doğrulama:** düzeltme sonrası tüm alanlarda mojibake taraması **0**; farklı il
  değeri 112'den gerçek **81** ile değişti; tam denetim **33 PASS / 0 FAIL / 0 WARN**.

## Genel toplam
- **72 dönem**, **170.627 kadro**, **457.395 kontenjan**, **2.391 benzersiz nitelik kodu**.
- Kaynağa göre eksiksiz (kaynağın gösterdiği her satır çekildi); tek fark 2019-2'nin
  kaynak kaynaklı 12 kadrolık açığı.
