# Debian 13 Build VM — locale və məhdud live profil hazırlığı

Tarix: 2026-11-06. Baza: Day 03 `bd806c3ed57c789b1826ebdcf591b5e23eed2f7f` və qəbul edilmiş [Day 04 readiness](day04-readiness.md).

## Bu mərhələnin dəyişiklikləri

Locale/live-profile kodu artıq `b75ecae` commit-inə daxildir. Aşağıdakı bundle həmin commit-i ehtiva edən branch-dən hazırlanır; patch-i yenidən tətbiq etməyin. [Portativ patch](patches/live-profile.patch) yalnız tarixi Day 03 bazasına tətbiq edilən review nüsxəsidir; əvvəlki istifadəçi dəyişikliklərini və Day 01/02 sənədlərini daşımır.

Patch SHA256: `8934bc3daf0eda7b9d6ed07d5b05f098574afb40c793518de92b9c7b460c0281`. Eyni SHA portativ patch üçün yanında saxlanıb.

### Locale

- Erkən `0006-locale.hook.chroot` əvəzində `1100-zeros-locale.hook.chroot` əlavə edilib. 26 vendor hook və onların hash-ləri dəyişməyib; 1020 default reset-dən sonra Azərbaycan ayarı tətbiq olunur.
- Python helper locale.gen-də az entry-lərini idempotent aktivləşdirir; digər locale-ləri saxlayır; `locale-gen` uğursuz olarsa build dayanır.
- Final `/etc/default/locale`: `LANG=az_AZ.UTF-8`, `LANGUAGE=az:en`. Qlobal LC_ALL yoxdur.
- Rəsmi snapshot-dan hash-i yoxlanmış **live-config 11.0.5** komponenti də yoxlanıb: `0050-locales` runtime-da faylı yalnız LANG ilə əvəz edir. Buna görə bu komponent də nocomponents siyahısına salınıb; locale build-də tam hazırlanır. GDM/PAM/session-un həmin default-u oxuması gələcək boot gate-dir.

### İstifadəçi və privilege siyasəti

- zeros UID 1000 build-də əvvəlcədən yaradılır, password field `!` olur. `zeros/zeros` və live-config-in standart `user/live` parolu istifadə edilmir.
- Mövcud zeros hesabı yalnız UID 1000 olduqda qəbul edilir; başqa hesabın UID 1000-ini mənimsəmək cəhdi fail edir. Root parolu da `!` ilə əvəz edilir; işlək köhnə hash lock işarəsinin arxasında saxlanmır.
- zeros-un əsas qrupu zeros, əlavə qrupları boşdur. Media/seat girişlərinin logind ilə işləməsi ayrıca test tələb edir. sudo paketi hələ mövcuddur, lakin istifadəçiyə səlahiyyət verilmir. Gözlənilməyən `/etc/sudoers.d/live` qrantı build-i dayandırır.
- Normal və failsafe boot eyni `LIVE_POLICY` istifadə edir: `username=zeros noroot nottyautologin` və `user-setup,live-debconfig_passwd,sudo,locales,policykit,gdm3,xinit` istisnaları. Bir neçə writer yerinə build-time account/locale və statik GDM config məsuldur.
- GDM yalnız zeros üçün qrafik autologin edir; timed autologin bağlıdır. Mövcud WaylandEnable=false qorunub. Console autologin nottyautologin ilə bağlıdır. Standart gdm3/xinit komponentləri statik config-i əvəz etməsin deyə söndürülüb.
- `00-zeros-live.rules` zeros üçün bütün PolicyKit sorğularına NO qaytarır. Bu sərt daxili demo siyasətidir: bəzi Wi-Fi, removable disk və shutdown/restart əməliyyatları işləməyə bilər. Hər hansı rahatlıq üçün universal sudo və ya blanket YES əlavə edilməməlidir; ehtiyaclar ayrıca review edilməlidir.
- Parolsuz disposable sessiyada avtomatik lock/idle bağlanıb. İstifadəçinin əl ilə lock etməsi, suspend və logout sonrası GDM autologin/PAM davranışı ayrıca yoxlanmalıdır. Geri giriş mümkün olmazsa VM reset/reboot yolu istifadə edilir; saxlanmayan sessiya məlumatı itir.

Rəsmi live-config paketi: snapshot `pool/main/l/live-config/live-config_11.0.5_all.deb`, SHA256 `2fba42fd76b60455714f23cfdd2998fcc632de9dd4c3d16f81b5e31855004304`. Yoxlama Day 04-də doğrulanmış Packages.xz record-u ilə aparılıb; paket yalnız /tmp-yə çıxarılıb, install edilməyib. Komponent davranışı [Debian live-config manualı](https://manpages.debian.org/trixie/live-config-doc/live-config.7.en.html) ilə birlikdə qiymətləndirilib.

**Təhlükə sərhədi:** autologin fiziki girişdən qoruma deyil. ISO/rootfs və boot parametrlərinə nəzarət edən şəxs sistemi dəyişə bilər. Bu patch browser/session prosesinə avtomatik admin verməməyi hədəfləyir; public release təhlükəsizlik attestasiyası deyil. Helper CLI yalnız live-build-in `/live-build/config` marker-i olan chroot-da işləyir; marker izolasiya attestasiyası deyil. Heç bir helper-i Kali-də əl ilə root kimi işə salmayın.

## VirtualBox VM hazırlığı

1. Təmiz Debian 13 amd64 VM yaradın. Başlanğıc profil: 4 vCPU, 8 GiB RAM, ən az 40 GiB boş disk; bunlar ölçülmüş minimum deyil.
2. NAT şəbəkə seçin. İnternet Debian snapshot və Docker Hub üçün lazımdır. Host disk passthrough, shared home, shared clipboard, drag/drop və SSH agent forwarding aktivləşdirməyin.
3. Source transfer üçün SSH lazım olarsa yalnız host loopback port forwarding yaradın: məsələn host 127.0.0.1:2222 → guest 22. SSH serveri yalnız build VM-yə qurun; target live ISO-ya əlavə etməyin. Host fingerprint-i yoxlayın.
4. Debian-da ayrıca sudo səlahiyyətli **VM operatoru** yaradın. Bu hesab ISO daxilindəki məhdud zeros istifadəçisi ilə əlaqəli deyil.
5. Install tamamlandıqdan sonra təmiz VM snapshot-u saxlayın. Kali-də Docker/privileged build başlamasın.

## Source paketi — yalnız source hostda

Aşağıdakı əmrlər gələcək transfer üçündür. Patch artıq `docs/build/patches/live-profile.patch` daxilində hazırlanıb. Yeni dəyişiklik edilsə patch yenidən yaradılmalı və bazaya tətbiqi yoxlanmalıdır.

```bash
cd /home/baratzade/Desktop/zerOS
TRANSFER_DIR="$(mktemp -d /tmp/zeros-vm-transfer.XXXXXX)"
git bundle create "$TRANSFER_DIR/source.bundle" codex/day03-trixie-build-foundation
git bundle verify "$TRANSFER_DIR/source.bundle"
cp docs/build/patches/live-profile.patch "$TRANSFER_DIR/live-profile.patch"
cp docs/build/vm-preparation.md docs/build/day04-readiness.md "$TRANSFER_DIR/"
cd "$TRANSFER_DIR"
sha256sum source.bundle live-profile.patch > SHA256SUMS
```

Bundle branch-i `b75ecae` live-profile commit-ini ehtiva etməlidir. VM-də ancestor yoxlaması bunu təsdiqləyir. Başqa terminalda həmin TRANSFER_DIR-in çap edilmiş real yolunu və SSH operator adını istifadə edin:

```bash
# Əvvəlki terminalda TRANSFER_DIR yolunu öyrənin:
printf '%s\n' "$TRANSFER_DIR"
# VM operator adını və real transfer yolunu əvəz edin:
scp -P 2222 /tmp/zeros-vm-transfer.REPLACE/* VM_OPERATOR@127.0.0.1:/tmp/
```

Bu xüsusi transfer qovluğunda yalnız bundle, patch və prosedur sənədləri var. Repository-ni rekursiv köçürməyin: köhnə ISO/cache və dirty istifadəçi fayllarını daşımaq lazım deyil. SHA256SUMS-ni hostda saxlayıb VM-də müqayisə edin; bu checksum rəqəmsal imza deyil.

## Yalnız Debian 13 VM-də — Docker, patch və yoxlamalar

Aşağıdakı paket/service əmrləri bu tapşırıqda icra edilməyib. Operator onları yalnız disposable VM-də yerinə yetirməlidir. Təmiz VM üçün Debian docker.io ailəsi seçilib; Docker CE ilə qarışdırmayın.

```bash
bash
set -euo pipefail
. /etc/os-release
test "$ID" = debian
test "$VERSION_CODENAME" = trixie
test "$(dpkg --print-architecture)" = amd64
sudo apt-get update
sudo apt-get install --yes docker.io docker-cli docker-buildx git python3 ca-certificates
sudo systemctl enable --now docker
mkdir -p "$HOME/zeros-build-session/results"
cd /tmp
sha256sum --check SHA256SUMS
cd "$HOME/zeros-build-session"
git clone /tmp/source.bundle source
cd source
git checkout --detach origin/codex/day03-trixie-build-foundation
git merge-base --is-ancestor b75ecae HEAD
test -z "$(git status --porcelain)"
test -f config/includes.chroot/usr/lib/zeros/live_profile.py
cp /tmp/vm-preparation.md /tmp/day04-readiness.md docs/build/
bash scripts/build.sh --preflight
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
RESULT_DIR="$HOME/zeros-build-session/results"
cp /tmp/live-profile.patch "$RESULT_DIR/"
sha256sum /tmp/live-profile.patch > "$RESULT_DIR/profile-patch.sha256"
git rev-parse HEAD > "$RESULT_DIR/source-base-commit.txt"
git status --short > "$RESULT_DIR/source-status.txt"
dpkg-query -W > "$RESULT_DIR/vm-packages.tsv"
sudo docker version > "$RESULT_DIR/docker-version.txt"
sudo docker info > "$RESULT_DIR/docker-info.txt"
df -h > "$RESULT_DIR/vm-disk.txt"
```

Live-profile artıq commit-dədir; əlavə patch tətbiq edilmir. Transfer edilmiş sənədlərin kopyası dirty status yarada bilər, lakin source kodunun əsası seçilmiş commit-dir. Commit SHA, source status və runner input kopyaları saxlanılır. Tarixi patch-in checksum-u yalnız review provenance üçündür.

## Builder image və environment gate — yalnız VM, ISO build deyil

Day 04-də doğrulanmış amd64 digest istifadə olunur. Bu mərhələ target ISO-nu qurmur; yalnız builder mühitinə paketlər quraşdırır.

```bash
cd "$HOME/zeros-build-session/source"
set -euo pipefail
RESULT_DIR="$HOME/zeros-build-session/results"
BASE_IMAGE='debian:trixie@sha256:bfc36aecdece0387418759dba474aa856c026ca8087da3606b41b90ab0509c99'
sudo docker pull --platform linux/amd64 "$BASE_IMAGE"
sudo docker image inspect "$BASE_IMAGE" > "$RESULT_DIR/base-image-inspect.json"
sudo docker build --platform linux/amd64 --build-arg BASE_IMAGE="$BASE_IMAGE" -f build/Dockerfile -t zeros-builder:profile . 2>&1 | tee "$RESULT_DIR/builder-image.log"
BUILDER_ID="$(sudo docker image inspect --format '{{.Id}}' zeros-builder:profile)"
printf '%s\n' "$BUILDER_ID" > "$RESULT_DIR/builder-id.txt"
sudo docker image inspect "$BUILDER_ID" > "$RESULT_DIR/builder-image-inspect.json"
sudo docker run --rm --mount "type=bind,src=$PWD,dst=/src,readonly" "$BUILDER_ID" --check-environment 2>&1 | tee "$RESULT_DIR/environment-check.log"
```

Burada dayanın və `builder-image.log`, `environment-check.log`, image ID və VM paket manifestini təqdim edin. Mount/chroot smoke testi Day 04 prosedurunda var, lakin ayrıca operator təsdiqi ilə yalnız VM-də aparılmalıdır. **ISO `--build` əmri bu mərhələnin icra siyahısına daxil deyil.**

## Test nəticələri və sonrakı gate-lər

Hazırkı source hostda: **18/18 test**, statik preflight və shell syntax keçib. Testlər tempfile fixture-lərinə yazır; useradd/usermod/locale-gen mock edilib. Başqa cwd-dən preflight və portativ patch-in təmiz baza üstündə tətbiqi ayrıca yoxlanıb. Vendor hook-ların 26 hash-i, istifadəçi faylları və köhnə artifact ölçü/mtime-ləri qorunub. Testlərin detalları [profile yoxlama qeydlərində](profile-checks.txt) saxlanılır.

GDM/PAM autologin, faktiki shadow/group/sudoers, PolicyKit JS-in runtime yükü, locale session environment və şəbəkə axınları **test edilməyib**. Bu səbəbdən “təhlükəsiz işlək Alpha” təsdiqi verilmir. Builder image-in hazırlanması və environment gate də hələ gözlənilir. Day 04 binary mirror reproducibility riski bu patch-in scope-u xaricindədir və qalır.

İlk ISO yalnız ayrıca başlanğıc göstərişindən sonra hazırlanmalıdır. Sonrakı boot protokolunda bunlar məcburidir:

- Normal/failsafe daxilində LANG az_AZ.UTF-8 və LANGUAGE az:en; `locale -a` daxilində Azərbaycan locale-i; az/us keyboard.
- zeros UID 1000, əsas qrup zeros, əlavə admin/disk qrupları yoxdur; zeros/root shadow password field dəqiq `!`; password/tty girişləri rədd edilir.
- `sudo -n true` uğursuz; sudoers-də live NOPASSWD qrantı yoxdur; PolicyKit admin əməliyyatları rədd edilir.
- GDM qrafik autologin açılır, timed login yoxdur; logout/lock/suspend sonrası davranış və reset/reboot yolu sənədləşdirilir. PAM locked hesabı autologin-ə buraxmasa universal parol əlavə edilməsin; profil review-a qaytarılsın.
- PolicyKit deny altında lazım olan Ethernet/Wi-Fi/power axınları ölçülür. Sərt profil lazım olan işi bloklayırsa hər əməliyyat ayrıca siyasət review-suna çıxarılır.
- Machine-id iki təmiz boot-da fərqlidir; host key/credential sızması yoxdur. BIOS/UEFI boot nəticəsi konkret ISO SHA256 ilə qeyd edilir.

Uğur və ya xətadan sonra container-dən nəticələrin çıxarılması və checksum yoxlanması [Day 04 bölmə 7E](day04-readiness.md#e-uğur-və-ya-xətadan-sonra-nəticələrin-çıxarılması) üzrə aparılmalıdır. Bu mərhələ container və ya köhnə artifact silməyi tələb etmir.
