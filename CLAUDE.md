# turkey-repeaters

Türkçe konuş. Kullanıcı Türkçe çalışıyor.

Türkiye amatör telsiz röle veritabanı — GitHub Pages üzerinde statik site.
Canlı: <https://ta3hrj.github.io/turkey-repeaters> · Depo: `TA3HRJ/turkey-repeaters`

## Yapı

```
docs/            # GitHub Pages kökü — yayınlanan her şey burada
├── index.html   # tüm site tek dosyada
├── data/        # repeaters.json + repeaters.min.json (site bunu yükler)
├── sw.js        # service worker (PWA)
└── manifest.json
scripts/         # Python araçları
data/            # overrides.json (elle düzeltmeler), location_aliases_draft.json
.github/workflows/update-data.yml
```

## Veri hattı

```bash
python scripts/scrape.py           # veriyi yeniden üret (aşağıdaki nota bak)
python scripts/build_compact.py    # repeaters.min.json'u tek başına yeniden üret
python scripts/merge_repeaterbook.py path/to/export.csv
```

`build_compact.py` sitenin gerçekte yüklediği dosyayı üretir — veri değiştiyse bunu çalıştırmadan
yayın eksik kalır. Haftalık workflow da bunu çağırıyor.

## Bilinen tuzak — README gerçeği tam yansıtmıyor

Son commit'lerden biri dış kaynaklı otomatik çekmeyi kaldırdı (*"Remove external scraping;
database is now manually maintained"*) ve `scripts/scrape.py` artık dışarıdan veri çekmiyor;
mevcut `repeaters.json`'ı `data/overrides.json` ile birleştirip yeniden yazıyor.

Ama `README.md` hâlâ *"Data is aggregated from multiple Turkish amateur radio sources"* ve
*"weekly automated data refresh"* diyor. Workflow haftalık çalışmaya devam ediyor ama gerçek
scraping yapmıyor, sadece override uyguluyor.

Bu ifadeleri düzeltmek açık bir iş. Düzeltmeden önce `scrape.py`'yi okuyup bugünkü davranışı
teyit et — yukarıdaki tespit commit mesajı ve koda dayanıyor, ama son durum değişmiş olabilir.

## Konvansiyonlar

- Elle düzeltmeler koda değil `data/overrides.json`'a yazılır — böylece yeniden üretimde kaybolmaz.
- Şüpheli kayıtlar için `find_suspicious.py`, konum takma adları için `find_similar_locations.py`
  ve `apply_location_aliases.py` var; elle JSON düzenlemeden önce bunlara bak.
- `.claude/settings.local.json` kişisel yerel ayardır, `.gitignore`'a girmelidir — şu an takipsiz
  duruyor.

## Oturum sonu

Anlamlı bir iş yaptıysan — bir karar verildi, bir şey kırılıp düzeldi, bir varsayım ölçüldü —
bitirmeden önce `docs/HANDOFF.md`'yi güncelle: nerede kalındı, ne açık kaldı, hangi tuzağa
düşüldü ve neden. Dosya yoksa oluştur.

Sohbet geçmişi kalıcı değildir. Repoda yazılı olmayan her şey oturumla birlikte gider.
