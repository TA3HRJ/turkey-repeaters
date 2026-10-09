# HANDOFF

Oturumlar arası not. Her anlamlı oturumun sonunda güncelle (bkz. `CLAUDE.md` → Oturum sonu).

## Son durum — 2026-10-10

Site aprsagent.com ailesinin görünümüne geçirildi. Adres artık https://repeaters.aprsagent.com
(`docs/CNAME`). Standart: `C:\Claude Projects\_shared\aprsagent-site-standardi\` (README, family.css,
snippets.html). 11f558f push'landı, Pages derlendi; canlıda family.css, başlık çubuğu, 574 kayıt
ve SW v2 doğrulandı, konsolda hata yok.

Bu oturumda yapılanlar:

- **Tema:** `docs/assets/family.css` standarttan kopyalandı ve `<head>`'de bağlı. Sitenin kendi
  `<style>` bloğu artık yalnızca family değişkenlerinden türeyen token'lar kullanıyor (eski
  `--primary/--surface/--muted…` paleti tamamen kalktı). Bant renkleri `--series-1..4`
  (VHF lacivert, UHF kırmızı, APRS bakır, EchoLink yeşil); harita pinleri bunları `cssVar()` ile
  canlı okuyor, böylece koyu temada da doğru.
- **Başlık çubuğu:** APRS-Agent işareti (`docs/assets/aprsagent-mark.svg`, standart klasördeki
  kopyadan; ağdan indirilmedi) + `aprsagent.com` → `/#tools` + `REPEATERS` + tema düğmesi +
  EN/TR grubu + GitHub ↗. Dil düğmesi tek "TR/EN" anahtarından `setLang()` + `aria-pressed`
  grubuna çevrildi.
- **Alt bilgi:** "Telsizci araçları" satırı (Röleler `aria-current="page"`), lisans satırı,
  Hakkında / RepeaterBook / GitHub, "İşleten: TA3HX", kısa yasal not + `#legal` bağlantısı.
- **Hakkında sekmesi (yeni):** Liste/Harita yanına üçüncü sekme. Hakkında metni + `#legal`
  (ticari markalar, APRS® cümlesi, sorumluluk reddi, standarttaki "repeaters" maddesi).
  Yeni metinler `data-i` öznitelikli; `applyStrings()` bunları `STRINGS[lang]`'dan genel bir
  döngüyle dolduruyor. `?tab=about` ve `#legal` URL'den açılıyor.
- **Emoji → SVG:** 🌙/☀️ (tema), 📍 (En Yakın), ✕ (pencere kapat), ⚠ (yaklaşık koordinat notu).
- **PWA:** `sw.js` önbelleği `v1` → `v2`, precache'e family.css ve işaret eklendi. manifest
  renkleri `#f6f3ea`. `icon-192/512.png` aynı paletle yeniden çizildi (kâğıt + ızgara, mürekkep
  anten, kırmızı dalga, lacivert nokta); eskiler mavi yuvarlak kareydi.
- **README:** "Trademarks and disclaimer" bölümü; lisans satırı "kod MIT, veri kişisel kullanım,
  markalar üzerinde hak vermez".
- Yan düzeltmeler: "Tüm şehirler" çevrilmiyordu; RepeaterBook İçe Aktar paneli ilk tıkta açılmıyordu.

### Bilinçli sapmalar (standarttan)

- **İçerik genişliği 1440px**, standartta 1040px. 17 sütunlu tablo 1040'a sığmıyor; başlık,
  araç çubuğu, tablo ve alt bilgi aynı hizada kalsın diye hepsi `.wrap{max-width:1440px}`.
- **Koyu tema korundu** (standart izin veriyor), yalnızca family.css `[data-theme="dark"]`
  değerleriyle. Başlık çubuğunda bu yüzden fazladan bir tema düğmesi var.
- **EchoLink, RepeaterBook, CHIRP, AnyTone için ® yok** — sahiplerinin belgesinden kanıt
  bakılmadı; genel "olabilir" cümlesi kapsıyor. Kanıt bulunursa `lgTm2` (EN/TR) ve README'ye eklenir.
- Kaynak siteler (amatortelsizcilik, AKRAD) adıyla anılmadı; b216ea1'de alt bilgiden bilerek
  kaldırılmışlardı. Metin "Türk amatör telsiz kaynakları" diyor.

### Kontrol listesi (standart §5)

- [x] family.css kopyalandı, renkler oradan · [x] başlık çubuğu · [x] airmail şeridi + ızgara
- [x] h2/h3 mono BÜYÜK HARF, `.btn.p/.btn.s`, ortak kenarlı tablo · [x] alt bilgi satırları
- [x] `#legal` · [x] README · [x] emoji → SVG · [x] 375px'te yatay kaydırma yok (ölçüldü:
  `scrollWidth == 375`), şerit/başlık çakışmıyor · [x] SW sürümü · [x] aprsagent.com ile 375px
  yan yana bakıldı; başlık çubuğu düzeni aynı.

## Açık kalanlar

- **Eski ziyaretçiler:** v1 SW'si kurulu tarayıcılarda yeni görünüm ilk açılışta değil, bir
  yenilemeden sonra gelir (navigasyon network-first olduğu için genelde ilk açılışta da gelir).
  Temiz tarayıcıda doğrulandı; v1 kurulu bir cihazda bakılmadı.
- **family.css bir kopya.** Standart değişirse önce `_shared/aprsagent-site-standardi/family.css`,
  sonra buraya kopyala ve SW sürümünü artır. `docs/assets/family.css`'i yerinde düzenleme.
- Firebase oylama özelliğinin canlıda çalışıp çalışmadığı hâlâ doğrulanmadı.
- Veri tarafı: `data/overrides.json` → `python scripts/scrape.py` (build_compact'ı da çağırır) → commit.

## Tuzaklar

- **`.wrap` padding'i `main`'i eziyor:** `main{padding…}` yerine `main.wrap{padding-top…}`
  gerekiyor (sınıf seçici öğe seçicisini yener). Lejant sekme çizgisine yapışınca fark edildi.
- **`stateToURL()` her filtre değişiminde URL'yi yeniden yazıyor**; `#legal` hash'ini silmesin
  diye Hakkında sekmesindeyken hash korunuyor. URL koduna dokunursan bunu kırma.
- **Body satır aralığı 1.62 tabloya da geçiyor;** `table#rt{line-height:1.35}` ve oy hücresini
  tek satıra almak satırı 82px'ten 33px'e indirdi.
- **Tarayıcı paneli ekran görüntüsü** sık sık "did not finish rendering" ile zaman aşımına düşüyor;
  2 sn bekleyip tekrar denemek ya da JS ile ölçmek işe yarıyor.
- **Windows'ta CRLF:** bir kopyayı commit ile karşılaştırırken `\r`'yi at.
- **Oturumun kendi dizinini silmek** "Device or resource busy" verir; önce oturumu repo köküne taşı.
- **`scrape.py` adı yanıltıcı:** ağ çağrısı yapmıyor (CLAUDE.md).

## Önceki oturum — 2026-09-24

HANDOFF ilk kez oluşturuldu (eski notlar `C:/HAM/turkey-repeaters` ile kaybolmuştu). CHANGELOG'a
`[Unreleased]` eklendi, CLAUDE.md'deki eski gitignore notu düzeltildi, ölü worktree ve
`claude/gifted-cray-51db39` dalı temizlendi.
