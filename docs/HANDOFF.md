# HANDOFF

Oturumlar arası not. Her anlamlı oturumun sonunda güncelle (bkz. `CLAUDE.md` → Oturum sonu).

## 2026-10-23 — hata taraması ve düzeltmeler

22 Ekim'de `docs/index.html` script'i, `sw.js` ve `firestore.rules` baştan sona okundu; şüpheliler
yerelde canlı veriyle ölçüldü (veritabanına yazılmadı). 23 Ekim'de ilk üçü düzeltildi.

1. **Arama Türkçe harfe takılıyordu — düzeltildi.** `toLowerCase()` "İ"yi "i" + U+0307 yapıyordu;
   "istanbul", "ISTANBUL", "izmir", "canakkale" 0 sonuç veriyordu. Artık `foldSearch()` iki tarafı
   NFD'ye çevirip birleşik işaretleri atıyor ve ı→i yapıyor. Ölçüm: istanbul/ISTANBUL/İstanbul 36,
   izmir/İZMİR 29, canakkale/çanakkale 14, sanliurfa/şanlıurfa 3. ("igdir" 0 — veride Iğdır yok.)
2. **Dijital röleler analog kanal olarak dışa aktarılıyordu — düzeltildi.** CHIRP ve Anytone
   (analog FM kanal yazan biçimler) artık DMR / NXDN / D-STAR rölelerini dışarıda bırakıyor ve
   sihirbaz kaç tane bırakıldığını yazıyor (`wiz-dig-note`, şu an 9). C4FM bırakılmadı: çoğu AMS
   ile analog da geçiriyor. Genel CSV / GPX / KML hepsini içermeye devam ediyor.
3. **CSV Excel'de bozuk görünüyordu — düzeltildi.** Genel CSV artık UTF-8 BOM (U+FEFF) ile
   başlıyor. CHIRP/Anytone CSV'lerine bilerek eklenmedi: içerikleri ASCII ve içe aktarıcıları
   ilk başlığı adıyla eşliyor, BOM onu bozabilir. Aynı fonksiyonda: bütün metin alanları
   tırnak-kaçışlı (`q()`), `offset` 0 artık boş değil "0" (167 simplex kayıt).
4. **Firestore kuralları oyu doğrulamıyordu — düzeltildi, yayında ve canlıda doğrulandı (aşağıda "Sonra olanlar").** Eski kural:
   anonim oturum açan herkes `aggregates/votes`'u istediği değere yazabilir ya da silebilir.
   Yeni `firestore.rules`: bir yazma yalnızca tek rölenin tek sorusunun iki sayacına
   (`{id}.wy`+`{id}.wn` ya da `{id}.ly`+`{id}.ln`) dokunabilir, her biri en çok ±1 değişir,
   0'ın altına inmez, alan silinemez, kimlik `^A[TK]_[0-9]+$` (574 kimliğin hepsi uyuyor; bu
   oturumluk RepeaterBook satırlarına `RB_s_n` verilen oyları da reddeder). Belge oluşturma
   kapalı (FIREBASE_SETUP adım 4'te elle oluşturuluyor). Script'le tekrar tekrar ±1 oy vermeyi
   durduramaz; bunun için Cloud Function gerekir. **Kural dosyası test edilmedi** (Firebase CLI /
   emülatör yok). Yayınlamak için: Firebase Console → Firestore → Rules → dosyanın içeriğini
   yapıştır → Rules Playground'da önce bir oy (ör. `AT_1.wy` 0→1, `AT_1.wn` 0→0) ve bir saldırı
   (ör. `AT_1.wy` → 999) dene → Publish.
   **Sonra olanlar (2026-10-23):** Yayındaki eski kural kullanıcıdan alındı: repo'daki eski
   kuralla aynı (yorumsuz) — açık canlıda da vardı. İlk taslak kullanıcı tarafından yayınlandı;
   Playground "An unknown error occurred" verdi; canlıda sitenin biçimindeki meşru bir oy
   (`AT_1.wy` +1) `permission-denied` aldı → o taslak BÜTÜN oyları engelliyordu. Muhtemel neden:
   `affectedKeys()` bir Set döndürüyor ve Set'te `toList()` yok (belgeyle doğrulanamadı: Firebase
   rules referans sayfaları fetch ile yalnızca gezinme menüsü döndürüyor). Hiçbir şey yazılmadı.
   **İkinci taslak:** site her oya `_last: "AT_1.w"` ekliyor; kural yalnızca `get`,
   `affectedKeys().hasOnly([...])`, `removedKeys().size()`, `matches` ve `+` kullanıyor (`let`,
   `toList`, `split` yok). Doğru sıra: (1) konsolda eski kurala dön, oylar çalışsın; (2) `_last`
   gönderen site kodu yayına çıksın (eski kural bunu da kabul eder); (3) yeni kural yayınlansın;
   (4) canlıda: meşru +1/−1 geçmeli, `AT_530.wy`→5, `TEST_1.wy`, alan silme reddedilmeli.
   **Dört adım da yapıldı, ikinci kural YAYINDA ve canlıda doğrulandı (2026-10-23, 4bfcf8b):**
   `TEST_1.wy` reddedildi; meşru `AT_1.wy` +1 ve −1 (sitenin `_last`'lı biçimi) geçti;
   `AT_530.wy`=5, `AT_1.ly` silme, `_last: AT_1.w` ile `AT_2.wy` +1 reddedildi. `_last`
   gönderilmeyen +1 geçti, çünkü belgedeki mevcut `_last` kullanılıyor — yine yalnızca o
   sorunun iki sayacında ±1, açık değil. Belgeyi merge'süz değiştiren yazma bilerek denenmedi
   (kural bozuksa bütün oyları silerdi); alanları silen yazmanın reddedildiği 4. deneme onu da
   kapsıyor. Son durum başlangıçla aynı (44 alan; 43 + `_last`). Repo'daki `firestore.rules`
   yayındakiyle aynı. Eski (açık) kural metni bu bölümde yukarıda; geri dönmek gerekirse
   konsolda Rules geçmişinden de alınabilir.
5. **Küçükler — düzeltildi (2026-10-23).** CROSS bandı (3 kayıt, kayma 0, diğer banttaki giriş
   frekansı veride yok): ana filtrede, harita lejantında (`--series-6`) ve sihirbazda (varsayılan
   işaretsiz) seçilebiliyor; CHIRP/Anytone'dan dijitallerle birlikte dışarıda bırakılıyor ve not
   bunu yazıyor. Anytone: CTCSS decode "Off", encode ton. Sıralama: boş hücreler iki yönde de
   sonda (`sortData` içindeki `key()`), metinler `localeCompare(…,"tr")`. Oy: `myVotesLoaded`
   bayrağı — `user_votes` okunmadan `castVote` hiçbir şey yapmıyor (çift sayım yok);
   `isVotableId` — yalnızca `^A[TK]_[0-9]+$` kimliklerine oy düğmesi (kural da yalnızca bunları
   kabul ediyor). RepeaterBook içe aktarımı `parseCSV()` ile: tırnaklı alanda virgül, çift tırnak,
   satır sonu; BOM'lu başlık; eksik sütunda çökmeden boş. Yerelde test edildi (tırnaklı virgüllü
   örnek dosya, sıralama uçları, CROSS filtresi = 3, sihirbaz notu, Anytone sütunları).
6. Hata değil, not: `sw.js` veri JSON'unu stale-while-revalidate ile veriyor; veri güncellenince
   geri dönen ziyaretçi ilk açılışta eski listeyi ve eski "Son güncelleme" tarihini görür, ikinci
   açılışta yenisini. Çağrı işaretine göre artan sıralamada 494 boş kayıt başa geliyor.

Aynı commit'te, contacts oturumunun isteğiyle aile standardı 1.4: baştaki tema betiği, koyu
seçmiş ziyaretçide `meta[name=theme-color]`'ı ilk boyamada `#1b1a16` yapıyor (family.css koyu
`--bg`). Test: betik yalnız başına çalıştırıldı — koyu → #1b1a16, açık/seçimsiz → #f6f3ea.

**Tuzak:** Bash heredoc'undan Python'a `\u0300` ya da Edit aracına `\uFEFF` yazmak dosyaya
kaçış metni değil gerçek görünmez karakteri koydu (regex'te U+0300-U+036F, CSV'de BOM). Düzeltme:
Python'da `chr(92)+'u0300'` ile kurmak. Bu tür satırları yazdıktan sonra `od -c` ya da
`ascii()` ile bayt düzeyinde kontrol et.

## 2026-10-15 — Leaflet unpkg'den çıktı

Harita kütüphaneleri (Leaflet 1.9.4, leaflet.markercluster 1.5.3) artık `docs/assets/vendor/`
altından, siteyle aynı adresten yükleniyor; unpkg.com'a istek gitmiyor. Dosyalar npm sürümlerinin
birebir aynısı (unpkg ve jsDelivr'deki baytlar aynı; Leaflet'in SRI özetleri tutuyor).
`.gitattributes` bu klasörü `-text` tutuyor: leaflet.css CRLF ile geliyor, git normalleştirirse
SRI bozulur. Yerelde harita sekmesi açıldı: L 1.9.4, markerClusterGroup var, 47 işaret,
18 karo, istekler yalnızca `assets/vendor/`. SW önbellek sürümü değişmedi (precache listesi
aynı; vendor dosyaları çalışma anında önbelleğe giriyor). Kalan üçüncü taraflar: Firebase
(gstatic.com + Firestore, oylama) ve OpenStreetMap karoları; aprsagent.com/privacy.html
bunları yazıyor.

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

## Ek — 2026-10-10: yasal bölüm hizası

`#legal` bölümü sola hizalı değil, sayfanın ortasına kaymıştı. Sebep standarttaki kalıp:
`<div class="wrap legal">` — `.legal`'in `max-width:78ch` değeri `.wrap`'ın genişliğini ezip
`margin:auto` ile kutuyu ortalıyordu. Standart 1.1'de satır sınırı `.legal>*`'a taşındı.

**Bu kopyaya yalnızca o düzeltme yamalandı; "yerinde düzenleme" kuralından bilinçli sapma.**
Standarttaki `family.css` aynı "1.1" etiketi altında iki değişiklik daha aldı:

- Başlık çubuğunun iç kutusu `.bar` → `.fam-row` (coax'ta ilerleme çubuğu `.bar` ile çakışmış).
  Bu sitenin HTML'i `<div class="wrap bar">` kullanıyor; dosya olduğu gibi kopyalansa başlık
  çubuğu düzenini kaybederdi.
- `--series-*` renkleri değişti (8 seri, dataviz doğrulayıcısıyla ölçülmüş). Harita pinleri ve
  bant rozetleri bunları kullanıyor; kopyalamak sitenin renklerini değiştirirdi.

Standarda tam eşitlemek için: `index.html`'de `wrap bar` → `wrap fam-row`, yeni `--series-*`
renklerini haritada/rozetlerde gözle kontrol et, sonra `family.css`'i olduğu gibi kopyala ve
SW sürümünü artır. Bu yapılana kadar dosyanın başındaki sürüm notu kopyanın tam 1.1
olmadığını söylüyor.

SW `v2` → `v3`. Yerelde temiz tarayıcıda ölçüldü: yasal başlık Hakkında başlığıyla aynı
hizada (1280'de 24px, 375'te 16px), `scrollWidth == 375`, önbellek `ta-repeaters-v3`.
Bu düzeltme oylama düzeltmesiyle (`b283710`) aynı anda, ayrı bir oturumda yapıldı; ikisi
birlikte push'landı (2026-10-10, `47c781b`). Pages derlemesi başarılı; canlıda `family.css`'te
`.legal>*` ve `sw.js`'te `v3` var.

## Açık kalanlar

- **Eski ziyaretçiler:** v1 SW'si kurulu tarayıcılarda yeni görünüm ilk açılışta değil, bir
  yenilemeden sonra gelir (navigasyon network-first olduğu için genelde ilk açılışta da gelir).
  Temiz tarayıcıda doğrulandı; v1 kurulu bir cihazda bakılmadı.
- **family.css bir kopya.** Standart değişirse önce `_shared/aprsagent-site-standardi/family.css`,
  sonra buraya kopyala ve SW sürümünü artır. `docs/assets/family.css`'i yerinde düzenleme.
- **Firebase oylama — düzeltme yayında (`b283710`, 2026-10-10'da `47c781b` ile push'landı;
  canlı sayfada `unflattenVotes` var). Canlı sayfada tarayıcıda doğrulandı (2cd06e7 derlemesi):
  11 rölede 42 sayaç görünüyor, örn. AT_197 "Çalışıyor? ✗2", konsolda hata yok; SW güncellemesi
  önbelleği `ta-repeaters-v3`'e geçirip v2'yi sildi.**
  Not: sayfadan `fetch('sw.js')` SW'nin stale-while-revalidate önbelleğinden eski sürümü döndürebilir;
  canlı sürümü `curl` ile ya da `registration.update()` sonrası `caches.keys()` ile ölç.
  Canlıda ölçülen: SDK yükleniyor, anonim oturum açılıyor, `aggregates/votes` okunuyor, kendi
  `user_votes/{uid}` okunuyor; kurallar doğru. Yazma da çalışıyor (gerçek kullanıcılardan 42 sayaç
  birikmiş, 11 röle). **Ama hiçbir oy sayfada görünmüyordu:** `castVote`, `batch.set(ref,
  {"AT_1.wy": increment(1)}, {merge:true})` ile yazıyor; `set()` noktayı yol saymaz, belgede
  düz `"AT_1.wy"` alanları duruyor. Okuma iç içe `data.AT_1.wy` arıyordu → hep 0; kendi oyunun
  vurgusu yoktu ve oy değiştirince eskisi düşülmüyordu (çift sayım mümkün — mevcut sayaçlarda
  bundan kalma şişme olabilir, ayıklanamaz). Düzeltme okuma tarafında: `unflattenVotes()`
  düz alanları iç içe nesneye katlıyor; veri taşıma gerekmedi, yazma koduna dokunulmadı.
  Yerelde canlı Firestore'dan okuyarak doğrulandı (11 rölede sayılar görünüyor). Test oyu
  verilmedi — canlı veriye yazmamak için.
- **Yazma biçimini değiştirme** (`update()`'e ya da iç içe nesneye geçmek): eski düz alanlarla
  yeni iç içe alanlar karışır; `unflattenVotes` ikisini de okur ama aynı rölede ikisi birden
  varsa biri diğerinin üstüne yazılır (toplanmaz). Geçilecekse önce veriyi taşı.
- Veri tarafı: `data/overrides.json` → `python scripts/scrape.py` (build_compact'ı da çağırır) → commit.

## Tuzaklar

- **Firebase hataları sessizce yutuluyor** (`.catch(()=>{})` her yerde): bir şey bozulursa sayfa
  hiçbir iz vermez. Kontrol için konsolda `firebaseReady`, `fbUid`, `voteAggregates`'e bak.
- **Gizli sekmede Firebase hiç yüklenmez:** `loadFirebase` `requestIdleCallback` ile çağrılıyor,
  tarayıcı gizli sekmede bunu çalıştırmıyor. Tarayıcı panelinde test ederken `loadFirebase()`'i
  elle çağır; bu canlı bir hata değil.
- **Liste tablosu geniş (17 sütun, 1024px'te ~1336px):** yatay kaydırma kaçınılmaz. Bu yüzden
  tablo `.table-scroll` içinde ekran yüksekliğiyle sınırlı (`max-height:calc(100dvh - 80px)`,
  kaydırma çubuğu hep ulaşılır), başlık satırı `position:sticky;top:0`, Topluluk sütunu
  `position:sticky;right:0` — oylama her genişlikte görünür. Sütun ekler/çıkarırsan sabit
  sütunun arka planını (hover/seçili satır) ve `renderTable`'daki `cells[i]` indekslerini kontrol
  et: plaka sütunu eklenince `loc-cell` sınıfı Konum yerine Şehir'e kaymıştı (i===6 → 7).
  Sticky başlıkta `border-collapse` kenarlığı yapışmaz; alt çizgi `box-shadow` ile.
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
