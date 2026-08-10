# Kamunite

KPSS'ye girip de "ben hangi kadrolara başvurabilirim, bunların hangisi bana uyar" diye tercih kılavuzlarında boğulanlar için yaptığım kişisel bir araç. Elinle yüzlerce sayfayı tek tek taramak yerine, profilini bir kere giriyorsun; gerisini uygulama süzüyor.

İki işi var: geçmiş KPSS kadrolarını sorgulamak, ve şu an açık olan memur/sözleşmeli ilanlarından sana uyanları bulmak. Girdiğin bilgiler yalnızca kendi bilgisayarında durur, hiçbir yere gönderilmez.

## Ne yapıyor

### 1. Geçmiş kadro sorgulama
2012'den bugüne kadar 72 dönemin bütün KPSS kadroları burada; 170 binden fazla kayıt. Yıla, ile, kuruma, unvana, taban puana göre filtreleyebilir; kart ya da liste olarak görebilirsin. Bir kadroya tıkladığında aranan bütün nitelikler, taban–tavan puan, kontenjan ve boş kadro sayısı açılıyor.

Asıl işe yarayan kısım "Bana uygun" düğmesi. Profilini bir kez doldurduğunda (öğrenim, bölüm, KPSS puanın, ehliyet, sertifika, tercih ettiğin iller) sana açık olan kadroları işaretliyor:

- "Yalnızca bölümümü isteyenleri göster" dersen, sadece senin bölümünü özellikle arayan kadrolar kalır.
- Bunu kapatırsan, seviyendeki herkese açık kadroları da görürsün (örneğin "herhangi bir lisans mezunu" arayan memurluklar).
- Puanın o kadronun geçen taban puanını tutuyorsa yeşil "puanın yeter", tutmuyorsa "puan düşük" yazıyor.
- Bir kadro sertifika istiyorsa ve sende yoksa, kadroyu gizlemek yerine "sertifika ister" diye uyarıyor; çünkü çoğu zaman sertifika sonradan alınabiliyor.

Bölüm, öğrenim düzeyini de belli ediyor; yani önlisans bir bölüm seçtiysen puanın önlisans kadrolarıyla karşılaştırılır, ortaöğretim kadrolarına karışmaz.

### 2. Güncel iş ilanları
Kariyer Kapısı'nda o an açık olan ilanları çekip profiline uyan unvanları buluyor. Her ilanı açtığında aranan bölümleri, öğrenim şartını ve KPSS puan barajını görürsün; "Tüm şartları göster" ile ilanın kendi metnini okuyabilirsin. İlan sitesindeki bağlantıya da tek tıkla gidiyorsun.

İlanlar sürekli değişip yenilendiği için uygulama bunu senin yerine takip ediyor. Programı her açtığında arka planda güncel listeyi çekiyor (veri bayatsa), ayrıca İlanlar sayfasına girdiğinde de kontrol ediyor. Yani sen uğraşmadan, yeni açılan ilanlar kendiliğinden geliyor.

Not: üniversitelerin toplu sözleşmeli ilanlarında bir "unvan" satırı çoğu zaman birçok farklı pozisyonu birden içeriyor. Uygulama, bölümün o ilanda açıkça geçtiğinde sana gösteriyor; yine de başvurmadan önce ilanın kendi metnini okumakta fayda var.

## Nasıl çalıştırılır

En kolayı: `dist/Kamunite` klasöründeki **Kamunite.exe**'ye çift tıklamak (masaüstünde kısayol varsa oradan). Kurulum yok, direkt açılıyor.

Tek dikkat edilecek şey: exe tek başına çalışmaz, yanındaki `_internal`, `index.html` ve `data` klasörüne ihtiyacı var. Başka bir yere taşıyacaksan `dist\Kamunite` klasörünü bütün olarak taşı, tek exe'yi değil.

## Kendin çalıştırmak / geliştirmek

Python ile kaynaktan açmak:

```bash
pip install pywebview
python app.py
```

Exe'yi yeniden derlemek:

```bash
pip install pywebview pyinstaller
python scripts/build_exe.py
```

Çıktı `dist/Kamunite` klasörüne gelir.

## Veriyi güncelleme

Aktif ilanları elle tazelemek istersen:

```bash
python scripts/fetch_ilanlar.py
```

(Uygulamadaki "↻ Yenile" düğmesi de aynı işi yapıyor.)

ÖSYM yeni bir dönem yayınladığında: o dönemin JSON dosyasını `data/json` içine koy, `data/index.json`'a bir satır ekle, sonra şunu çalıştır:

```bash
python scripts/rebuild_all.py
```

Bölüm listesi, öğrenim seviyeleri ve sertifika tabloları gibi türetilmiş veriler böylece yeniden üretilir.

## Dosyalar ne işe yarıyor

- **`index.html`** — arayüzün ve eşleştirme mantığının tamamı tek dosyada. Uygulamanın kalbi burası.
- **`app.py`** — masaüstü penceresini açan sarmalayıcı. Küçük bir yerel sunucu kurup arayüzü onun içinde gösteriyor; canlı ilan çekmeyi ve profili diske kaydetmeyi de bu yönetiyor.
- **`scripts/`** — veriyi hazırlayan ve exe'yi paketleyen yardımcı betikler.
- **`data/`** — KPSS dönem verisi (`json` klasörü), ondan türetilmiş tablolar (bölümler, seviyeler, sertifikalar) ve son çekilen aktif ilanlar.
- **`BAKIM.md`** — hangi dosyanın neyi kontrol ettiğine dair kısa notlar.

## Notlar

Veri kaynağı ÖSYM'nin tercih kılavuzları; sayılar resmî rakamlarla eşleşiyor. Yine de bu bir yardımcı araç, resmî belge değil; kesin başvuru kararında her zaman ÖSYM kılavuzunu esas al.

Profilindeki bilgiler bilgisayarının kendi hafızasında tutuluyor, internete çıkmıyor. Uygulama yalnızca güncel ilanları çekmek için Kariyer Kapısı'na bağlanıyor, senin bilgilerini hiçbir yere göndermiyor.
