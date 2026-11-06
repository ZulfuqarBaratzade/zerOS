# Day 03 — Debian 13 build foundation

Tarix: 2026-11-06; Day 03 iş mərhələsi. Branch: `codex/day03-trixie-build-foundation`.

## İnventar və qorunan məlumatlar

Başlanğıc commit `b1aa32f713baf2570cfdd21eae364447402a0e49`, branch `main` idi. `.gitignore` və `config/common` istifadəçi dəyişiklikləri, əvvəlki iki audit/planning sənədi untracked idi. Bunlar dəyişdirilməyib. Əvvəlki artifact-lərin path, ölçü, mtime və ownership qeydləri `day03-inventory.json` daxilindədir. Directory ölçüləri rekursiv hesablanmayıb; icazəsi olmayan ağaclara giriş artırılmayıb.

Mövcud `live-image-amd64.hybrid.iso` 1,393,684,480 baytdır. `binary/`, `cache/`, `chroot/`, `.build/`, `local/` və paket/file manifestləri saxlanılıb. Köhnə build-in təmizlənməsi və ya onun davam etdirilməsi planlaşdırılmır. Yeni nəticə ayrıca `/tmp/zeros-build-...` qovluğuna yazılır; VM-də bu qovluq sonradan qorunan storage-a köçürülməlidir. `/tmp` daimi arxiv deyil.

## İzolyasiya və versiya kontraktı

Dəstəklənən dizayn: disposable **amd64 Debian Trixie VM** daxilində digest ilə seçilmiş Debian Trixie container image. live-build mount/chroot səlahiyyətləri istədiyi üçün privileged container yalnız bu VM daxilində işlədilməlidir. Adi hostda privileged Docker işə salmaq izolyasiya sərhədi sayılmır. Source repository container-ə read-only mount edilir; bütün yazılar container-in ayrıca iş sahəsinə gedir.

`build/versions.json`:

- target: `trixie`, `amd64`;
- live-build: `1:20250505+deb13u1`;
- debootstrap: `1.0.141`;
- dependency snapshot: `20261106T000000Z`;
- SOURCE_DATE_EPOCH: 2026-11-06 00:00:00 UTC.

Versiyalar rəsmi [live-build](https://packages.debian.org/trixie/live-build) və [debootstrap](https://packages.debian.org/trixie/debootstrap) səhifələrindən seçilib. Snapshot-da dəqiq paket həlli və container image build-i **yoxlanılmayıb**; paket yoxdursa APT uğursuz dayanmalıdır, versiya avtomatik genişləndirilməməlidir. Dockerfile-də eyni versiyaların lock ilə uyğunluğu unit testlə yoxlanılır.

`BASE_IMAGE` məcburidir və `debian:trixie@sha256:...` formatında olmalıdır. Konkret digest bu mərhələdə seçilib yoxlanılmayıb. Təkrarlanan build-lərdə eyni digest istifadə edilməlidir; floating `debian:trixie` qəbul edilmir. Docker image ID-si və base reference gələcək nəticələrlə saxlanmalıdır. Base reference environment marker-də, bütün quraşdırılmış host paketləri nəticə manifestində saxlanılır. Marker təhlükəsizlik attestasiyası deyil; səhv hostda təsadüfi icranın qarşısını alan kontrakt yoxlamasıdır.

APT bootstrap mərhələsində minimal Debian image-də CA sertifikatının olmaması nəzərə alınaraq snapshot signed HTTP ilə oxunur; imza yoxlaması söndürülmür. CA paketi qurulandan sonra builder sources HTTPS-ə çevrilir. Tarixi snapshot üçün yalnız Valid-Until müddət yoxlaması söndürülür; APT signature yoxlaması aktiv qalır. Snapshot köhnəldikcə təhlükəsizlik borcu yaranır; release-dən əvvəl idarə olunan refresh və təkrar yoxlama lazımdır.

ISO target paketləri də tarixli Debian/security snapshot-dan gəlir. Final live sistemin APT mirror-ları isə aktual Trixie yeniləmələri üçün rəsmi HTTPS ünvanlarıdır. Tam dependency graph ayrıca versiya pinləri ilə yazılmayıb: snapshot + base digest + paket manifesti ilə bərpa edilir. Bit-identical ISO nəticəsi iddia edilmir.

## Hook-lar və scope

26 absolute host symlink-i eyni path-də **byte-for-byte lokal icraolunan fayllara** çevrilib. `build/hooks.lock.json` əvvəlki hədəfi, SHA256 və import mənşəyini saxlayır. Mənbə mövcud hostdakı `live-build 1:20250814+kali3` paketidir; bu fayllar Debian Trixie upstream versiyası kimi təqdim edilmir. Məqsəd hazırkı davranışı dəyişmədən host asılılığını kəsməkdir. GPL-3+ copyright və GPL mətni build qovluğuna əlavə edilib. Sonradan upstream ilə müqayisə ayrıca review tələb edir.

Beş custom hook dəyişməyib. Locale reset hook-u da dəyişməyib: məlum locale konflikti və `zeros/zeros` siyasəti **həll edilməyib**. Bu infrastruktur public təhlükəsiz Alpha buraxılışı demək deyil. GNOME/GDM/Plymouth branding fayllarına toxunulmayıb. Bu P0-lar növbəti ayrıca işdir.

`auto/config` Trixie/amd64, archive areas və BIOS+UEFI bootloader seçimini açıq verir; `--binary-image` canonical option-dan istifadə edir. Mövcud boot locale/keyboard və installer-none parametrləri qorunur. Əsas repository-dəki generated config faylları, xüsusən istifadəçinin dəyişmiş `config/common` faylı olduğu kimi qalır. Skript yalnız disposable copy-də beş generated config-i atır və pinned toolchain ilə yenidən generasiya edir. Buna görə köhnə config-dəki ISO metadata/cache/default parametr fərqləri gələcək resolved-config review-sunda yoxlanmalıdır; custom GNOME branding isə includes/hook-larda saxlanır.

## Build runner davranışı

`scripts/build.sh` qovluqdan asılı olmayaraq repository root-u tapır, Python runner-i çağırır. Default və `--preflight` yalnız read-only statik yoxlamadır. `--check-environment` əlavə olaraq OS, amd64, dependency, marker, lock və dəqiq paket versiyalarını yoxlayır. `--build` həmin yoxlamalardan və root yoxlamasından sonra tam build başlada bilər; bu mərhələdə çağırılmayıb.

Yeni build `lb clean --purge` işləmir və mövcud ISO-ya yazmır. Unikal mkdtemp sahəsinə yalnız source config/auto köçürülür; köhnə cache/chroot/binary heç vaxt köçürülmür. `lb config` hook-ları yenidən dəyişərsə checksum yoxlaması `lb build`-dən əvvəl dayanır. Yanlış toolchain ilə davam etmə seçimi yoxdur. Source root üçün Git safe.directory yalnız həmin Git çağırışına verilir, global Git konfiqurasiyası dəyişdirilmir.

Hər build nəticə qovluğunda bunları saxlayır:

- commit SHA, Git status, tracked diff; dirty tree gizlədilmir;
- faktiki input config/auto/scripts, foundation lock və hook provenance;
- host OS, base image reference və host paket manifesti;
- resolved config, tam stdout/stderr `build.log`;
- uğurda final `.packages` manifesti və ISO SHA256SUMS;
- uğur/xətada `result.json`, mövcuddursa aralıq chroot paket manifestləri və bütöv work sahəsi.

Commit SHA dirty və untracked input-u tam təsvir etmir; buna görə input kopyaları ayrıca saxlanılır. Build log streaming edilir və pipeline exit kodu maskalanmır. Paket manifesti olmayan build uğurlu sayılmır. Build-in uğurlu çıxışı belə `build-complete-boot-untested` kimi yazılır. Setup zamanı (məsələn disk dolması) metadata yazılması da uğursuz ola bilər; CLI xətası qorunur, boş metadata uğur kimi qəbul edilmir.

## Yoxlama nəticələri

- Default/static preflight: keçdi; `/tmp` qovluğundan absolute script yolu ilə də keçdi.
- 6 unit test: keçdi — lokal hook bütövlüyü, Dockerfile/lock uyğunluğu, çatışmayan dependency-nin rəddi, dəyişmiş hook hash-inin rəddi, default rejimin build başlatmaması və environment gate xətasında build-in çağırılmaması.
- `bash -n`: wrapper, auto/config və hook-lar preflight daxilində keçdi.
- Cari hostda environment check: gözlənilən rədd, `Missing build dependency: xorriso`. Qalan mühit tələbləri bu çağırışda təsdiqlənmir.
- Docker build, snapshot paket həlli, root/mount imkanları, real ISO build və BIOS/UEFI boot: **icra edilməyib**.
- Məhdudiyyət: versiya kilidi və mətn testləri işlək Trixie ISO sübutu deyil.

## Növbəti əmrlər

İndi root-suz və dəyişikliksiz yoxlama:

```bash
bash scripts/build.sh --preflight
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Aşağıdakı əmrlər **gələcək üçün təlimatdır; icra edilməyib**. Image hazırlamaq paket quraşdırır, privileged build root/mount əməliyyatları edir. Bunlar yalnız ayrıca icazədən sonra disposable VM daxilində icra olunmalıdır. Dəqiq, yoxlanmış amd64 base digest ilə placeholder-i əvəz edin və həmin reference-i release manifestində saxlayın:

```bash
BASE_IMAGE='debian:trixie@sha256:REPLACE_WITH_VERIFIED_AMD64_DIGEST'
docker build --build-arg BASE_IMAGE="$BASE_IMAGE" -f build/Dockerfile -t zeros-builder:day03 .
docker image inspect zeros-builder:day03 > /tmp/zeros-builder-image.json
docker run --rm --mount "type=bind,src=$PWD,dst=/src,readonly" zeros-builder:day03 --check-environment
```

Tam build üçün ayrıca icazədən sonra, eyni disposable VM-də:

```bash
docker run --name zeros-day03-build --privileged --mount "type=bind,src=$PWD,dst=/src,readonly" zeros-builder:day03 --build
```

Sonuncu container `--rm` ilə silinmir ki, uğursuzluqda da log və nəticələr qalsın. CLI-də göstərilən dəqiq qovluğu kopyalayın:

```bash
docker cp zeros-day03-build:/tmp/zeros-build-REPLACE_WITH_PRINTED_SUFFIX ./zeros-day03-result
```

Copy və SHA256 yoxlamasından əvvəl container/VM silinməsin. Çıxış repository-dən kənarda da saxlanıla bilər. İndiki mərhələdə branch yaradılıb, commit və push edilməyib. Day 01/02 sənədləri və istifadəçi dəyişiklikləri ayrıca staging/commit qərarı üçün saxlanılır.
