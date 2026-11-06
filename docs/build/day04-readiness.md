# zerOS — Day 04: Trixie Build Readiness

Tarix: **2026-11-06**, Asia/Baku. Status: **NOT READY — real ISO build-in başlaması üçün mühit gate-i hələ keçilməyib**.

## 1. Commit və qorunan iş ağacı

Day 03 commit-i mövcuddur: **`bd806c3ed57c789b1826ebdcf591b5e23eed2f7f`**, `build: establish isolated Debian Trixie build foundation`. Branch `codex/day03-trixie-build-foundation`-dir. Commit yaratmaq/tamamlamaq ehtiyacı olmadı.

Day 03 diff-i yalnız əvvəlki allowlist-dən 39 fayl saxlayır. Cari `.gitignore` və `config/common` istifadəçi dəyişiklikləri, Day 01/02 untracked sənədləri qorunub. Bu mərhələdə build məhsul kodu, hook və lock-lar dəyişdirilməyib; Day 04 yalnız docs/build altında hesabat və doğrulama sübutları əlavə edir. Commit/push edilməyib.

İstifadəçi fayllarının SHA256-ləri Day 03 review ilə eynidir:

| Fayl | SHA256 |
|---|---|
| `.gitignore` | `300d00bd404aed56e880f2d2b978751e5613e9a65cd5c2a9f69e2dd451773d8f` |
| `config/common` | `5d5b9784b0284a4a353a016b60c8d64fd83d603aa8d9f9b9360e01b6c8b714b3` |

Köhnə ISO və Day 03 inventarındakı build qalıqları silinməyib; ölçü/mtime uyğunluğu yenidən yoxlanılıb. Ağacdakı bütün faylların rekursiv content hash-i yoxdur. Cari host **Kali 2026.3**-dür; burada root build, Docker image build və privileged container başladılmayıb.

## 2. Rəsmi Trixie hook müqayisəsi

Rəsmi Debian snapshot-un InRelease imzaları Debian archive keyring ilə `gpgv` vasitəsilə doğrulandı. İmzalı Release-dən Packages.xz SHA256 götürüldü; endirilmiş index həmin hash-ə uyğun gəldi. Index record-larındakı SHA256 ilə iki .deb doğrulandı. `live-build.deb` yalnız `/tmp/zeros-day04/trixie-live-build` altına `dpkg-deb -x` ilə çıxarıldı; install və maintainer script icrası olmadı.

Mənbə: [20261106 snapshot](https://snapshot.debian.org/archive/debian/20261106T000000Z/), paket `live-build 1:20250505+deb13u1`. [Rəsmi paket məlumatı](https://packages.debian.org/trixie/live-build).

| Yoxlama | Nəticə |
|---|---|
| Lokal vendor hook-ların lock ilə SHA256 uyğunluğu | **26/26** |
| Trixie paketində eyni normal/live path-in mövcudluğu | **26/26** |
| Vendor ↔ Trixie byte-for-byte uyğunluğu | **26/26** |
| Fərqli və ya çatışmayan hook | **0** |
| Bu upstream normal/live dəstində əlavə hook | **0** |

Tam path/hash cədvəli: [hook-comparison.json](day04-evidence/hook-comparison.json). Vendor manifestində Kali import mənşəyi doğrudur və dəyişdirilməyib; indi əlavə olaraq həmin məzmunun seçilmiş Debian versiyası ilə eyni olduğu sübut edilib.

**Funksional/təhlükəsizlik nəticəsi:** bu paket versiyasına keçid üçün hook məzmunu düzəlişi lazım deyil. Mövcud ID/key sanitizasiyası upstream ilə eynidir; locale reset də eyni şəkildə qalır. Bu, custom hook-larla birlikdə işləmənin təsdiqi deyil: `0006-locale` ardınca `1020` yenə LANG-ı dəyişir; `0100` məlum parollu sudo hesabını yaradır. `5050` dracut şərti işə düşərsə davranışı ayrıca test tələb edir.

Rəsmi paketin `usr/lib/live/build/config:1360–1370` kodu mövcud normal/live hook path-i varsa onu symlink ilə əvəz etmir. Bu, vendor strategiyasını statik əsaslandırır; real `lb config` icrası və sonra bütün hook inventarının yoxlanması VM-də aparılmalıdır. Upstream `chroot_hooks:58` sırası normal hook-lardan sonra live hook-ları icra edir. Runtime uyğunluğu, sanitizasiya və boot nəticəsi **test edilməyib**.

## 3. Base image digest

Docker Hub-un rəsmi `library/debian:trixie` namespace-indən anonymous Registry API vasitəsilə əldə edildi:

| Obyekt | Digest |
|---|---|
| Multi-platform index | `sha256:9c6e381421d0f48d1b8133e573f33c185ee16cbf505eda9c4a8a4791b25ea8a6` |
| **linux/amd64 image manifest** | **`sha256:bfc36aecdece0387418759dba474aa856c026ca8087da3606b41b90ab0509c99`** |
| Image config | `sha256:51e269e6af18ae477f7880a0820f34863e34366c621d93b0dd939260ea62e59b` |

Index body SHA256 serverin Docker-Content-Digest başlığı ilə, amd64 manifest və config blob hash-ləri descriptor-larla uyğun gəldi. Config `os=linux`, `architecture=amd64` göstərir. Image yaradılma metadata-sı 2026-11-04-dür. Layer-lər endirilməyib və image işlədilməyib.

Build üçün **index digest deyil, yuxarıdakı amd64 manifest digest-i** istifadə ediləcək:

```bash
BASE_IMAGE='debian:trixie@sha256:bfc36aecdece0387418759dba474aa856c026ca8087da3606b41b90ab0509c99'
```

[Raw manifestlər və config](day04-evidence/README.md), [maşınla oxunan digest qeydi](day04-evidence/image-verified.json), [env faylı](day04-evidence/base-image.env) saxlanılıb. Tag zamanla dəyişə bilər; bu qeyd həmin araşdırma anına aiddir. Registry/TLS yoxlaması publisher signature və ya işlək image attestasiyası kimi təqdim edilmir. Digest ilə image istifadəsi [Docker sənədində](https://docs.docker.com/engine/containers/run/#image-references) izah olunur.

## 4. Snapshot paketləri

İmzalı `dists/trixie/main/binary-amd64/Packages.xz` SHA256:
`7778d3e3f303b7ddb8ce0fe7c8d57473a076c6bf2e8f241f75421d2396352498`.

| Pin | Snapshot-da versiya | Endirilmiş .deb SHA256 | Nəticə |
|---|---|---|---|
| live-build | `1:20250505+deb13u1` | `58e09779881cbcc631c49ceb703413e0247a87db01823e597b2a1c40a2afd8f4` | Mövcuddur, hash uyğun |
| debootstrap | `1.0.141` | `8c02cb8ad712eb67afb0d23fab175c562804cc97eda70b70cb0f3bc2a21732d7` | Mövcuddur, hash uyğun |

İki paket `Architecture: all`-dır və amd64 index-dədir. Dockerfile-də açıq sadalanan digər 19 paket adı da həmin index-də tapıldı: [paket cədvəli](day04-evidence/recipe-package-availability.json). Bu yoxlama **APT dependency resolution testi deyil**. Transitive dependency-lər, base image ilə versiya əlaqəsi, downloads və bütün RUN addımlarının uğuru yalnız VM-də builder image hazırlananda təsdiqlənəcək.

`trixie-security` və `trixie-updates` snapshot InRelease URL-ləri də endirildi və GPG imzaları yoxlandı. Security paket indekslərinin dependency həlli ayrıca aparılmayıb. [Paket record-ları](day04-evidence/packages-verified.json), [trust chain və təkrar doğrulama məlumatı](day04-evidence/README.md) saxlanılıb. Deb və 9.7 MB Packages.xz repository-yə əlavə edilməyib.

## 5. Ayrı review üçün düzəliş və qərar siyahısı

Hook-larda upstream fərqi olmadığı üçün süni hook patch-i hazırlanmadı. Aşağıdakılar mövcud məhsul koduna avtomatik tətbiq edilməyib:

| ID / prioritet | Review üçün konkret variant | Əsas və risk | Bağlanma şərti |
|---|---|---|---|
| R1 / P0 build gate | VM-də digest ilə builder image-i hazırlamaq və `--check-environment` işlətmək | Paket mövcudluğu image-in işləməsi demək deyil | Image ID, paket manifesti və environment log-u |
| R2 / P1 reproducibility | `scripts/build.py:94–97` binary mirror-larını da tarixli mirror-lara yönəltmək; final live APT sources üçün ayrıca aydın siyasət seçmək | Hazırda bootstrap/chroot snapshot-dur, binary mərhələsi isə aktual Debian mirror-larına keçir. `build-with-chroot=true` səbəbilə əlavə boot/image paketləri həmin mərhələdə dəyişə bilər | Bütün mərhələlərin resolved sources və paket manifesti; runtime update siyasəti ilə qarışdırılmayan review edilmiş diff |
| R3 / P1 preflight | Post-config-də yalnız 26 hash deyil, bütün normal/live inventarı və symlink-ləri yoxlamaq | Gələcək toolchain əlavə hook yarada bilər | Əlavə/silinmiş hook üçün negative test |
| R4 / P0 public Alpha | Locale-i 1020-dən sonra tətbiq etmək; zeros/zeros və sudo/autologin siyasətini ayrıca dəyişmək | Məlum əvvəlki P0-lar qalır | Day 02 qəbul meyarları üzrə ayrıca implementasiya və boot testi |
| R5 / P1 runtime validation | Generated-config fərqləri, initramfs və Secure Boot nəticəsini review etmək | Köhnə config sıfırlanması branding/boot default-larını dəyişə bilər | Resolved-config review + BIOS/UEFI protokolu |

R2 ilk **daxili eksperimental build** üçün qaçılmaz blocker deyil, lakin “tam snapshot ilə sabit nəticə” iddiasını bloklayır. R4 release blocker-dir; izolyasiya edilmiş daxili build-i özlüyündə qadağan etmir. Build-start readiness ilə public-release readiness ayrıdır.

## 6. Cari yoxlamalar və bloklayıcılar

| Yoxlama | Faktiki nəticə |
|---|---|
| Day 03 commit | Təsdiqləndi |
| Vendor lock və rəsmi Trixie müqayisəsi | 26/26 uyğun |
| Unit testlər | 6/6 keçdi |
| Static preflight, başqa cwd-dən çağırış | Keçdi |
| Shell syntax | 33/33 keçdi |
| Python compile / diff whitespace | Keçdi |
| Sənəddəki bash blokları | Syntax keçdi; əmrlər icra edilməyib |
| Cari host `--check-environment` | **Uğursuz: Missing build dependency: xorriso** |
| VM daxilində environment check | **Aparılmayıb** |
| Builder image hazırlanması / APT dependency həlli | **Aparılmayıb** |
| Mount/chroot capability smoke test | **Aparılmayıb** |
| ISO build / boot | **Aparılmayıb** |

### ISO build-in başlamasından əvvəl mandatory gate-lər

1. Disposable amd64 Debian 13 VM seçilməli, yalnız VM-də Docker qurulmalı; VM-də kifayət qədər disk/RAM təsdiqlənməlidir.
2. Yoxlanmış commit VM-yə köçürülməli; məxfi məlumat, köhnə ISO/cache və istifadəçinin dəyişiklikləri transfer paketinə daxil edilməməlidir.
3. Doğrulanmış digest ilə builder image hazırlanmalı; exit status və image metadata saxlanmalıdır. Paket dependency həlli burada yoxlanacaq.
4. Həmin image və read-only source ilə `--check-environment` uğurla keçməlidir.
5. VM-də build container-in minimal mount/chroot sınağı keçməlidir; Kali-də privileged container işlədilməməlidir.
6. İlk run-un daxili test olduğu, locale/istifadəçi riskləri ilə public yayılmayacağı və nəticə extraction proseduru təsdiqlənməlidir.
7. Bu işdə verilən “hələ ISO build başlatma” məhdudiyyəti sonrakı açıq başlanğıc göstərişi ilə götürülməlidir.

Əsas hazırkı blocker-lər 1, 3, 4 və 5-dir: uyğun VM və real builder execution sübutu yoxdur. Root əməliyyatlarını cari Kali hostda icra etmək bu boşluğu həll etmir.

## 7. Dəqiq build VM proseduru

Aşağıdakılar **gələcək icra üçün təlimatdır; bu araşdırmada icra edilməyib**. Root/paket install və privileged smoke/build əmrləri ayrıca başlanğıc göstərişindən sonra yalnız disposable VM-də icra olunmalıdır. İlkin tövsiyə: 4 vCPU, 8 GiB RAM, ən az 40 GiB boş disk; bu ölçülər ölçülmüş minimum deyil. VM-də şəxsi data, host disk passthrough, shared home, SSH agent forwarding və Docker socket mount olmasın.

### A. Yalnız lazımi commit-in ötürülməsi — source host

Aşağıdakı Git bundle yalnız commit tarixçəsini daşıyır; dirty `.gitignore`, `config/common`, untracked Day 01/02 və köhnə artifact-lər daxil olmur. Day 04 sənədləri uncommitted qaldığından build source bundle-a daxil deyil; digest bu sənəddə açıq verilib.

```bash
cd /home/baratzade/Desktop/zerOS
git rev-parse codex/day03-trixie-build-foundation
# Nəticə bd806c3ed57c789b1826ebdcf591b5e23eed2f7f olmalıdır.
git bundle create /tmp/zeros-day03.bundle codex/day03-trixie-build-foundation
git bundle verify /tmp/zeros-day03.bundle
sha256sum /tmp/zeros-day03.bundle
scp /tmp/zeros-day03.bundle BUILD_VM_USER@BUILD_VM_IP:/tmp/
```

`BUILD_VM_USER` və `BUILD_VM_IP` real VM identifikatorları ilə əvəz edilməlidir. Bundle SHA256-ni ayrıca qeydə alıb VM-də müqayisə edin. SCP üçün SSH host fingerprint-i yoxlanmalıdır; agent forwarding aktivləşdirilməsin.

### B. Debian 13 VM — Docker və source hazırlığı

Bu prosedur yalnız təmiz Debian VM-də **Debian-ın docker.io/docker-cli/docker-buildx paketlərindən** istifadə edir; Docker CE repository-si ilə qarışdırılmır. [Trixie docker.io paketi](https://packages.debian.org/trixie/docker.io). Mövcud başqa runtime quraşdırılmış VM-də avtomatik uninstall etməyin; yeni disposable VM seçin.

```bash
. /etc/os-release
test "$ID" = debian
test "$VERSION_CODENAME" = trixie
test "$(dpkg --print-architecture)" = amd64
sudo apt-get update
sudo apt-get install --yes docker.io docker-cli docker-buildx git python3 ca-certificates
sudo systemctl enable --now docker
sudo docker version
sudo docker info
sha256sum /tmp/zeros-day03.bundle
mkdir -p "$HOME/zeros-build-session"
cd "$HOME/zeros-build-session"
git clone /tmp/zeros-day03.bundle source
cd source
git checkout --detach bd806c3ed57c789b1826ebdcf591b5e23eed2f7f
test -z "$(git status --porcelain)"
bash scripts/build.sh --preflight
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
mkdir -p ../results
dpkg-query -W > ../results/vm-packages.tsv
sudo docker version > ../results/docker-version.txt
sudo docker info > ../results/docker-info.txt
df -h > ../results/vm-disk.txt
```

Bu VM install-i hələ pinlənmiş Docker runtime deyil; faktiki paket/runtime versiyaları nəticələrlə saxlanır. Docker CE tələb olunarsa ayrıca [rəsmi Debian install proseduru](https://docs.docker.com/engine/install/debian/) seçilməli, iki paket ailəsi qarışdırılmamalıdır.

### C. Builder image və environment check — yalnız VM

Hər blokda xəta olduqda dayanın. Loglama üçün bash/pipefail lazımdır; pipeline içində docker xətası tee uğuru ilə maskalanmamalıdır.

```bash
bash
set -euo pipefail
cd "$HOME/zeros-build-session/source"
RESULT_DIR="$HOME/zeros-build-session/results"
BASE_IMAGE='debian:trixie@sha256:bfc36aecdece0387418759dba474aa856c026ca8087da3606b41b90ab0509c99'
sudo docker pull --platform linux/amd64 "$BASE_IMAGE"
sudo docker image inspect "$BASE_IMAGE" > "$RESULT_DIR/base-image-inspect.json"
sudo docker build --platform linux/amd64 --build-arg BASE_IMAGE="$BASE_IMAGE" -f build/Dockerfile -t zeros-builder:day04 . 2>&1 | tee "$RESULT_DIR/builder-image.log"
BUILDER_ID="$(sudo docker image inspect --format '{{.Id}}' zeros-builder:day04)"
printf '%s\n' "$BUILDER_ID" > "$RESULT_DIR/builder-id.txt"
sudo docker image inspect "$BUILDER_ID" > "$RESULT_DIR/builder-image-inspect.json"
sudo docker run --rm --mount "type=bind,src=$PWD,dst=/src,readonly" "$BUILDER_ID" --check-environment 2>&1 | tee "$RESULT_DIR/environment-check.log"
```

Sonrakı run-larda mutable tag əvəzinə **BUILDER_ID** istifadə olunur. `--check-environment` mount capability yoxlamır. Ayrı, kiçik smoke test (privileged, **yalnız VM**; ISO build deyil):

```bash
sudo docker run --rm --privileged --entrypoint /bin/sh "$BUILDER_ID" -ec 'mkdir -p /tmp/zeros-mount-smoke; mount -t tmpfs tmpfs /tmp/zeros-mount-smoke; trap "umount /tmp/zeros-mount-smoke" EXIT; touch /tmp/zeros-mount-smoke/ok; chroot / /bin/true' 2>&1 | tee "$RESULT_DIR/mount-smoke.log"
```

Bu smoke test bütün live-build loop/device əməliyyatlarını təsdiqləmir; yalnız ilk capability gate-dir. Nəticəsi uğursuzdursa ISO build-ə keçilməsin.

### D. Ayrı başlanğıc göstərişindən sonra ilk daxili ISO build — yalnız VM

Bu hissə hazırda **icra edilməməlidir**. C mərhələsinin bütün gate-ləri və yeni başlanğıc göstərişi tələb olunur.

```bash
cd "$HOME/zeros-build-session/source"
set -euo pipefail
sudo docker run --name zeros-alpha-01 --privileged --mount "type=bind,src=$PWD,dst=/src,readonly" "$BUILDER_ID" --build 2>&1 | tee "$RESULT_DIR/iso-build-console.log"
```

`--rm` verilmir: uğursuz build-də də container/log/work saxlanmalıdır. Nonzero çıxışdan sonra da ayrıca extraction mərhələsini işlədin. Container adını təkrar istifadə etmək üçün köhnə nəticəni silmək əvəzinə növbəti cəhdə başqa ad verin. Run mount-ları arasında host data diski və Docker socket yoxdur.

### E. Uğur və ya xətadan sonra nəticələrin çıxarılması

```bash
sudo docker inspect zeros-alpha-01 > "$RESULT_DIR/build-container-inspect.json"
sudo docker logs zeros-alpha-01 > "$RESULT_DIR/build-container.log" 2>&1
mkdir -p "$RESULT_DIR/container-tmp"
sudo docker cp zeros-alpha-01:/tmp/. "$RESULT_DIR/container-tmp/"
sudo chown -R "$(id -u):$(id -g)" "$RESULT_DIR/container-tmp"
find "$RESULT_DIR/container-tmp" -maxdepth 2 -name result.json -print
```

Container log-undakı `Build output: /tmp/zeros-build-...` sətrinə uyğun dəqiq qovluğu seçin; bir neçə run-u qarışdırmayın. Məsələn aşağıdakı placeholder-i həmin suffix ilə əvəz edin:

```bash
BUILD_RESULT="$RESULT_DIR/container-tmp/zeros-build-REPLACE_WITH_PRINTED_SUFFIX"
cat "$BUILD_RESULT/result.json"
cd "$BUILD_RESULT"
sha256sum --check SHA256SUMS
```

Build uğursuz olubsa SHA256SUMS olmaya bilər; bunu uğur kimi qəbul etməyin. `build.log`, commit.txt, foundation lock-lar, host-packages.tsv, resolved-config, .packages və bütün work sahəsini saxlayın. Metadata yaratmadan əvvəl xəta varsa container log və inspect əsas diaqnostikadır. `build-complete-boot-untested` yalnız build nəticəsidir; boot təsdiqi deyil.

Nəticələri VM-dən başqa terminalda çıxarın:

```bash
scp -r BUILD_VM_USER@BUILD_VM_IP:zeros-build-session/results ./zeros-day04-results
```

Transfer sonrası ISO-nun SHA256-sını çıxarılmış SHA256SUMS ilə yenidən müqayisə edin. Yoxlama və backup bitmədən container/VM silinməsin. Kali-dəki köhnə ISO və build ağaclarına heç bir clean/remove əmri verilməsin.

## 8. Yekun qərar

**NOT READY.** Rəsmi hook müqayisəsi, iki pinned paketin snapshot mövcudluğu və amd64 manifest digest-i artıq sübut olunub. Lakin uyğun VM-də builder image-in hazırlanması, dependency həlli, environment check və minimal mount/chroot gate-i hələ keçilməyib. Bunlar tamamlanandan və ayrıca ISO başlanğıc göstərişi veriləndən sonra yalnız **daxili test build** üçün READY qərarı verilə bilər. Public Alpha üçün locale, istifadəçi/sudo və boot təhlükəsizliyi gate-ləri ayrıca qalır.
