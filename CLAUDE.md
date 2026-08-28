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
python scripts/scrape.py           # repeaters.json'u yeniden üret + override uygula
python scripts/build_compact.py    # repeaters.min.json'u tek başına yeniden üret
python scripts/merge_repeaterbook.py path/to/export.csv
```

`build_compact.py` sitenin gerçekte yüklediği dosyayı üretir — veri değiştiyse bunu çalıştırmadan
yayın eksik kalır. Haftalık workflow da bunu çağırıyor.

## Veri elle bakılıyor — otomatik çekme yok

`scripts/scrape.py` adına rağmen dışarıdan veri çekmiyor; dosyada tek bir ağ çağrısı yok.
Yaptığı iş, mevcut `repeaters.json`'ı okuyup `data/overrides.json`'daki elle düzeltmeleri
uygulayarak yeniden yazmak. Kendi docstring'i de bunu söylüyor: *"External scraping has been
disabled. The database is now manually maintained."*

`.github/workflows/update-data.yml` yalnızca `workflow_dispatch` ile çalışıyor — **zamanlanmış
tetikleyici yok**, yani kendiliğinden hiçbir şey güncellenmiyor. Elle tetiklendiğinde
`build_compact.py` çalıştırıp değişiklik varsa commit'liyor.

README bir süre bunun tersini iddia ediyordu ("weekly automated data refresh", "aggregated from
multiple Turkish amateur radio sources", "refreshes automatically every Monday") ve düzeltildi.
İleride gerçek bir otomatik çekme eklenirse README'nin de birlikte güncellenmesi gerekir.

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

## Git kimliği

Bu depoda kimlik **yerel** olarak ayarlı (`.git/config`); makinede global `.gitconfig` yok
ve olmamalı:

```
user.name  = TA3HRJ
user.email = TA3HRJ@users.noreply.github.com
```

Yerel olması kasıtlı — klasör başka bir makineye taşındığında commit atmak için hiçbir
kurulum gerekmiyor. Özel e-posta adresi kullanma; noreply adresi hem gerçek adresi gizler
hem de commit'lerin GitHub hesabına düzgün atfedilmesini sağlar.
