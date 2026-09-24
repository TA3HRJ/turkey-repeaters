# HANDOFF

Oturumlar arası not. Her anlamlı oturumun sonunda güncelle (bkz. `CLAUDE.md` → Oturum sonu).

## Son durum — 2026-09-24

Master temiz, `origin/master` ile aynı çizgide. Yarım kalmış kod ya da veri değişikliği yok.

Bu oturumda yapılanlar:

- **HANDOFF ilk kez oluşturuldu.** Önceki oturumların notu hiç yoktu. Depo daha önce
  `C:/HAM/turkey-repeaters` altındaydı; o klasör silinmiş, eski notlar varsa onunla gitti.
- **CHANGELOG'a `[Unreleased]` eklendi.** Önceden yalnızca 0.1.0 vardı ve orada
  `scrape.py` hâlâ iki siteden veri çekiyormuş gibi görünüyordu. 0.1.0 girdisi tarihsel
  olarak doğru olduğu için ona dokunulmadı; dış çekmenin kaldırılması ve sonrasında eklenen
  her şey (PWA, harita, oylama, filtreler, AT_530-532) yeni bölümde.
- **CLAUDE.md'deki eski not düzeltildi.** `settings.local.json` için "takipsiz duruyor"
  yazıyordu; 9adc242'den beri `.gitignore`'da (`launch.json` ile birlikte).
- **Ölü worktree temizlendi:** `git worktree prune`, `claude/gifted-cray-51db39` dalı silindi
  (master'da olmayan commit'i yoktu, 1fd685f'te duruyordu). `.claude/worktrees/` altındaki
  kopya da silindi; önce 1fd685f ile karşılaştırıldı, fark yalnızca CRLF'ti.

## Açık kalanlar

- Belirli bir sonraki iş tanımlı değil. Veri tarafı elle bakılıyor; yeni röle/düzeltme
  gelirse `data/overrides.json` → `python scripts/scrape.py` (bu, `build_compact.py`'yi de
  çağırıyor) → commit.
- `firestore.rules` ve `FIREBASE_SETUP.md` bu oturumda incelenmedi; oylama özelliğinin canlıda
  çalışıp çalışmadığı doğrulanmadı.

## Tuzaklar

- **Windows'ta CRLF:** Eski worktree kopyasındaki dosyalar `cmp` ile commit'ten "farklı"
  göründü; hepsi satır sonu farkıydı. Bir kopyayı commit ile karşılaştırırken `\r`'yi at.
- **Oturumun kendi dizinini silmek:** Claude oturumunun çalışma dizini silinecek klasörün
  içindeyse Windows "Device or resource busy" veriyor. Önce oturumu repo köküne taşı.
- **`scrape.py` adı yanıltıcı:** Ağ çağrısı yapmıyor. CLAUDE.md'de ayrıntısı var.
