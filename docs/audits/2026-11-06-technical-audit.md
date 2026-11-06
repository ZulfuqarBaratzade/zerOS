# zerOS — Day 01: Technical Audit

Tarix: 2026-11-06 (Asia/Baku)  
Baza commit: `b1aa32f713baf2570cfdd21eae364447402a0e49`  
Əhatə: repository, build resepti, paketlər, hook-lar, lokallaşdırma, brendinq, təhlükəsizlik və buraxılışa hazırlıq.

## 1. Executive Summary

zerOS Debian Bookworm/amd64 və GNOME əsasında ilkin live distributiv reseptinə malikdir. İlk ictimai stabil buraxılışa hazır olduğu təsdiqlənmir. Buraxılışdan əvvəl locale hook konflikti, istifadəçi/sudo siyasəti, hostdan asılı build resepti və build/boot sübutlarının çatışmazlığı aradan qaldırılmalıdır. İndiki vəziyyət development və məhdud live preview mərhələsinə uyğundur.

Əsas nəticələr:

- Azərbaycan locale-i generasiya edilir, lakin sonrakı standart hook `/etc/default/locale` faylını `LANG=C.UTF-8` ilə əvəz edir. Normal live boot parametrinin bunu düzəltməsi mümkündür; boot testi yoxdur.
- `zeros/zeros` hesabı image daxilində yaradılır və sudo qrupuna salınır. Live-config-in ayrıca istifadəçi və parolsuz sudo mexanizmi ilə uyğunlaşdırılmayıb.
- Standart hook-lar repository daxilində məzmun kimi saxlanmır: hostun `/usr/share/live/build/hooks/` ağacına mütləq symlink-lərdir. Toolchain, paket versiyaları və snapshot tarixi pinlənməyib.
- BIOS Syslinux və UEFI GRUB nəzərdə tutulub. Mövcud qalıqlarda hər ikisinin faylları var; boot, Secure Boot və USB uyğunluğu yoxlanılmayıb.
- Tərcümələr çox məhduddur; GDM background mexanizmi uyğun deyil; chroot GRUB ayarı live ISO menyusunu brendləşdirmir.
- Installer yoxdur. Debian APT və security/updates konfiqurasiyası var; ayrıca zerOS yeniləmə/release sistemi yoxdur.

### Metod və məhdudiyyətlər

Yalnız təhlükəsiz statik oxuma, Git inventarı, `bash -n`, Python standart kitabxanası ilə GNU MO oxuma və rəsmi Debian mənbələrinin yoxlanması aparılıb. Paket quraşdırılmayıb, root əmri, build, boot, chroot icrası, installer və şəbəkə yeniləmə testi aparılmayıb. Məhsul kodu dəyişdirilməyib.

Audit başlanğıcında `.gitignore` və `config/common` artıq dəyişmişdi; onlar toxunulmadan saxlanılıb. Workspace-də ISO, `binary/`, `chroot/`, `cache/`, `.build/` və manifestlər var. Bunlar əvvəlki əməliyyatdan qalan, hazırkı commit ilə uyğunluğu və mənşəyi təsdiqlənməmiş əlavə sübutlardır. ISO mount edilməyib və daxili məzmunu ayrıca çıxarılmayıb. `chroot/etc/sudoers` oxuma icazəsi vermədiyi üçün faktiki sudoers təsdiqlənmir. Məhdud icazəli alt qovluqlar üçün yüksəldilmiş giriş tələb edilməyib.

## 2. Mövcud funksiyalar və struktur

**Status mənası:** “Təsdiqlənmiş” yalnız statik məzmunun mövcudluğunu bildirir; işlək build/boot mənasını daşımır. “Qismən” konfiqurasiya var, lakin konflikt və ya test boşluğu mövcuddur. “Mövcud deyil” audit olunan repository-də tətbiq tapılmayıb.

| Funksiya | Status | Sübut və məhdudiyyət |
|---|---|---|
| Debian 12 / amd64 / live image resepti | Təsdiqlənmiş, statik | `auto/config:4–10`, `config/bootstrap:4–28`, `config/chroot:4–25` |
| GNOME, GDM, Firefox, NetworkManager | Təsdiqlənmiş, paket istəyi | `config/package-lists/desktop.list.chroot:1–19`; install/işləmə ayrıca test olunmayıb |
| BIOS + UEFI hybrid ISO | Qismən | `config/binary:4,22–28`; qalıqlarda `binary/isolinux/isolinux.bin`, `binary/EFI/boot/bootx64.efi` var |
| Secure Boot | Qismən / təsdiqlənməyib | `config/binary:119` = `auto`; imza və firmware sınağı yoxdur |
| Azərbaycan dili | Qismən | `0006-locale.hook.chroot:4–13` ilə `1020-create-locales-files.hook.chroot:7` konfliktlidir |
| `az,us` klaviatura | Qismən | `auto/config:10`; GNOME input sources/switch shortcut tətbiqi yoxdur |
| GNOME tərcüməsi | Qismən | İki MO kataloqu: Settings 15, Nautilus 14 mesaj |
| Dark theme / wallpaper | Qismən | `0004-dconf-apply.hook.chroot:6–25`; user profile və sistem default-ları var, vizual test yoxdur |
| GDM brendinqi | Qismən, problemli | `0002-gdm-theme.hook.chroot:6–11`; sxemdə olmayan açar |
| Plymouth | Qismən | Tema və PNG var, `0005-plymouth.hook.chroot:4–5`; yalnız statik şəkil skripti |
| ISO GRUB/Syslinux zerOS mövzusu | Mövcud deyil | `config/bootloaders/` boşdur; chroot GRUB faylı ISO şablonu deyil |
| Machine-id / SSH key sanitizasiyası | Təsdiqlənmiş resept, runtime yox | `8020`, `8050`, `8060` hook-ları; host hook versiyasından asılıdır |
| Installer | Mövcud deyil | `auto/config:8`, `config/binary:53`; paket siyahılarında Calamares yoxdur |
| Debian APT/security updates | Təsdiqlənmiş resept, tətbiq testi yox | `config/common:19`, `config/chroot:19,28–31`, `config/bootstrap:34–64` |
| zerOS update kanalı / first-boot onboarding | Mövcud deyil | Tracked config və scripts inventarında tətbiq yoxdur |
| CI, release imzası, test matrisi | Mövcud deyil | Tracked fayllar arasında workflow/release/test infrastrukturu yoxdur |

### Struktur inventarı

53 tracked fayl/link var. `auto/config` konfiqurasiya girişidir; `scripts/build.sh` clean/config/build ardıcıllığıdır; `config/{common,bootstrap,chroot,binary,source}` generasiya olunmuş live-build parametrləridir. `config/package-lists/` iki siyahı saxlayır. `config/hooks/normal/` beş yerli icraolunan hook və 24 host symlink-i, `config/hooks/live/` iki host symlink-i saxlayır. `config/includes.chroot/` GRUB, GDM, wallpaper, gettext kataloqları və Plymouth fayllarıdır. Kökdə `Readme.md`, ignor edilən `Road.md` və `zeros_linux_wallpaper.svg` var; SVG-dən istifadə olunan JPG/PNG-lərə çevirmə prosesi yoxdur.

`config/apt`, `archives`, `bootloaders`, `debian-installer`, `preseed`, `packages*`, `includes.*` kimi əlavə qovluqlar mövcuddur, lakin inventarda əlavə fayl yoxdur. `binary/`, `cache/`, `chroot/`, `.build/`, `local/`, ISO və manifestlər build qalıqlarıdır; təmiz checkout məzmunu sayılmır. `.gitignore:1–7,18–23` əsas qalıqları gizlədir. `Readme.md:3` production istifadəsinə hazır olmadığını açıq bildirir.

## 3. Kritik texniki problemlər

### B01 — P0: Locale sonrakı hook tərəfindən əvəz edilir

- **Sübut:** `config/hooks/normal/0006-locale.hook.chroot:4–13` locale yaradır və LANG/LANGUAGE/LC_ALL yazır. `config/hooks/normal/1020-create-locales-files.hook.chroot:7` sonradan `LANG=C.UTF-8` yazır. Bu linkin audit hostundakı hədəfi də həmin əmri saxlayır. Host `/usr/lib/live/build/chroot_hooks:58` normal hook-ları glob ardıcıllığı ilə emal edir. Qalıq `chroot/etc/default/locale:1` də `LANG=C.UTF-8` göstərir.
- **Risk:** Azərbaycan dili image-in etibarlı default-u deyil. `auto/config:10` normal live boot zamanı locale tətbiq edə bilər; bu, konfliktin runtime həll olunduğunu sübut etmir. Failsafe parametrində locale yoxdur (`config/binary:19`).
- **Tövsiyə:** Locale tətbiqini standart reset-dən sonraya keçirmək, vahid mənbə saxlamaq; daimi LC_ALL ehtiyacını yenidən qiymətləndirmək; locale.gen əlavəsini idempotent etmək. Normal/failsafe/GDM sessiyalarını ayrıca yoxlamaq.

### B02 — P0: Build hostdan asılıdır, resept tam pinlənməyib

- **Sübut:** `config/hooks/normal/1000-…9020-*.hook.chroot` və iki `config/hooks/live/*` Git-də `120000` rejimli mütləq `/usr/share/live/build/hooks/...` symlink-ləridir. `config/common:4` format versiyası `20250214` olsa da, versiya kilidi deyil. Audit hostunda `live-build=1:20250814+kali3`, `debootstrap=1.0.145` oxunub; bu, Debian Bookworm toolchain-i ilə eyni mühit deyil.
- **Risk:** Başqa hostda link itə, hook məzmunu dəyişə və clean/config fərqli nəticə verə bilər. Təhlükəsizlik təmizliyi də xarici hook məzmunundan asılıdır.
- **Tövsiyə:** Dəstəklənən izolyasiya edilmiş build mühiti və dəqiq toolchain versiyaları təyin etmək; standart hook asılılıqlarını versiyalı və yoxlanılan etmək. Təmiz checkout-dan ayrıca build tələb olunur.

### B03 — P1: Build skripti çalışma qovluğunu və tələbləri yoxlamır

- **Sübut:** `scripts/build.sh:4–11` yalnız EUID yoxlayır, sonra nisbi qovluqda `lb clean --purge`, `bash auto/config`, `lb build` işlədir. Repository kökünə keçid, toolchain yoxlaması və log/artifact metadata saxlanması yoxdur. `auto/config:4–11` bir neçə parametr müəyyən edir, architecture, archive areas, bootloader və metadata digər config fayllarından gəlir.
- **Risk:** Səhv qovluqdan çağırış xətası və arzuolunmaz build ağacının təmizlənməsi; əsas parametrlərin clean/config davranışına bağlılığı. `set -e` əmr xətasını saxlayır, lakin tələblərin düzgünlüyünü yoxlamır.
- **Tövsiyə:** Repository kökünü deterministik tapmaq, preflight və versiya yoxlamaları, build log-u/commit/konfiqurasiya manifesti saxlamaq; əsas parametrlərin vahid mənbəsini müəyyən etmək. Bunlar auditdə dəyişdirilməyib.

### B04 — P1: Bit səviyyəsində təkrarlana bilmə təmin olunmur

- **Sübut:** `config/bootstrap:34–64` dəyişən Debian mirror-ları; paket siyahılarında versiya pinləri yoxdur. `config/common:16,25–34,76` recommends, cache və `LB_UTC_TIME=false`; `config/binary:83` dəyişən `@ISOVOLUME_TS@`. `0100-create-default-user.hook.chroot:8` hər icrada chpasswd çağırır və parol hash salt-ı dəyişə bilər. SOURCE_DATE_EPOCH/snapshot/build mühiti kilidi tapılmayıb.
- **Risk:** Müxtəlif tarixlərdə fərqli paketlər, dependency-lər, timestamp-lər və hash-lər. Mövcud manifest əvvəlki nəticəni təsvir edir, gələcək həlli kilidləmir.
- **Tövsiyə:** Təhlükəsizlik yeniləmələri üçün idarə olunan snapshot yeniləmə siyasəti, SOURCE_DATE_EPOCH, sabit timezone və toolchain, imzalı paket manifesti; iki müstəqil build müqayisəsi. `8080-reproducible-glibc` yalnız bir cache-ni silir, tam reproducibility sübutu deyil.

### B05 — P1: Paket əhatəsi və boot uyğunluğu ayrıca təsdiq tələb edir

- **Sübut:** `desktop.list.chroot:12–14` ilə `live.list.chroot:1–3` təkrarlanır; zərərli konflikt sübutu deyil. `desktop.list.chroot:19` firmware-linux istəyir və `config/bootstrap:28` non-free-firmware-i aktivləşdirir. Kernel `config/chroot:22–25` ilə gəlir. `config/binary:22–28` BIOS/EFI ayrı parametrləri və boş LB_BOOTLOADERS saxlayır.
- **Risk:** Toolchain versiyasına bağlı bootloader seçimi; bütün Wi-Fi/GPU cihazlarının firmware-linux ilə əhatə olunduğu iddia edilə bilməz. Secure Boot `auto` nəticəsi bilinmir.
- **Tövsiyə:** Dəqiq live-build versiyasında bu parametrləri təsdiqləmək; BIOS/UEFI, Secure Boot açıq/bağlı, USB və hardware matrisi yaratmaq. Qalıq manifestdə firmware-linux və GNOME var, openssh-server/Calamares yoxdur; bunu yeni ISO zəmanəti saymamaq.

## 4. Lokallaşdırma və brendinq tapıntıları

### L01 — P1: Klaviatura yalnız live kernel parametrində müəyyən edilib

- **Sübut:** `auto/config:10`, `config/binary:13` = `keyboard-layouts=az,us`; `0004-dconf-apply.hook.chroot:13–23` input-sources təyin etmir. Qalıq `chroot/etc/default/keyboard:6` yalnız `us` göstərir. Failsafe parametrində layout yoxdur (`config/binary:19`).
- **Risk:** Runtime live-config konsolu/X11-i dəyişə bilər, lakin GNOME/GDM daxilində sıra, keçid və parol yazılması təsdiqlənmir. Azərbaycan simvolları ilə istifadə axını pozula bilər.
- **Tövsiyə:** Console, GDM, GNOME və installed sistem üçün vahid keyboard siyasəti; Ə/ə, I/ı, İ/i, Ö/ö, Ü/ü, Ğ/ğ, Ş/ş, Ç/ç və layout keçidinin testi.

### L02 — P1: Tərcümə çox kiçikdir və yenidən generasiya edilmir

- **Sübut:** `config/includes.chroot/usr/share/locale/az/LC_MESSAGES/gnome-control-center.mo` Python GNUTranslations ilə 15 qeyri-header giriş (1-i orijinal ilə eyni), `nautilus.mo` 14 giriş verir. Bunlar ümumi GNOME coverage faizi deyil. Yeganə PO `.../naut.po:1–50` Settings terminləri saxlayır; adı Nautilus təəssüratı yaradır, lakin control-center kataloquna uyğun məzmundur. PO→MO build addımı, POT, versiya metadata-sı və control edilən Nautilus PO mənbəyi yoxdur.
- **Risk:** Cəmi 29 kataloq girişi GNOME-un tam Azərbaycan dilində olması demək deyil. Paketə məxsus MO faylının overlay ilə əvəz edilməsi həmin domendə mövcud daha geniş tərcümələri itirə bilər; paket yeniləməsi overlay-i əvəz edə bilər. Gettext uyğunluğu faylların oxunması ilə məhdud təsdiqlənib.
- **Tövsiyə:** GNOME 43 mənbələrinə uyğun POT/PO-lar, düzgün domain adları, msgfmt yoxlaması/compilation, plural/context/fuzzy və linqvistik review. Shell, Settings, Files və əsas tətbiqlər üzrə ölçülən coverage və fallback testi; az_AZ→az fallback-ını runtime yoxlamaq.

### L03 — P1: GDM hook-u uyğun olmayan açardan istifadə edir

- **Sübut:** `config/hooks/normal/0002-gdm-theme.hook.chroot:6–11` `org/gnome/login-screen` altında `background` yazır. Qalıq `chroot/usr/share/glib-2.0/schemas/org.gnome.login-screen.gschema.xml:3–101` bu açarı daşımır; `logo` və banner açarları var. Hook GDM üçün profile yaratmır; qalıqda `/etc/dconf/profile/gdm` yoxdur, Debian-ın `/usr/share/gdm/greeter-dconf-defaults` mexanizmi var.
- **Risk:** `dconf update` uğuru GNOME-un açarı istifadə etdiyi mənasına gəlmir; gözlənilən fon tətbiq olunmaya bilər. `config/includes.chroot/etc/gdm3/daemon.conf:2` Wayland-ı səbəbi sənədləşmədən söndürür.
- **Tövsiyə:** Debian GDM-in dəstəklənən profile/default mexanizmini və GNOME versiyasına uyğun branding üsulunu seçmək; X11 qərarını əsaslandırmaq; login/lock ekranını ayrıca yoxlamaq.

### L04 — P1: Chroot GRUB ilə ISO boot menyusu qarışdırılıb

- **Sübut:** `config/includes.chroot/etc/default/grub:1–4` distributor, timeout və PNG göstərir; `config/bootloaders/` daxilində şablon yoxdur. Qalıq `binary/boot/grub/grub.cfg:4,8` və `binary/isolinux/live.cfg:2,9` ingiliscə standart menyudur. `binary/boot/grub/theme.cfg:4–5` `splash.png` və `live-theme/theme.txt` seçir.
- **Risk:** Rootfs-dəki `/etc/default/grub` live-build-in ISO GRUB/Syslinux menyusunu avtomatik brendləşdirmir; BIOS ümumiyyətlə Syslinux istifadə edir.
- **Tövsiyə:** Hər iki ISO bootloader üçün versiyalı şablon, Azərbaycan dili/font və recovery menyusu; installed GRUB-u installer qərarından sonra ayrıca qurmaq.

### L05 — P2: Dark theme və Plymouth mövcuddur, vizual nəticə təsdiqlənməyib

- **Sübut:** `0004-dconf-apply.hook.chroot:6–25` user/local dconf profili, prefer-dark, Adwaita-dark, wallpaper və dark wallpaper müəyyən edir. `zeros.plymouth:4–8` script modulunu seçir; `zeros.script:1–6` PNG-ni ekran ölçüsünə dartır. `0005-plymouth.hook.chroot:4–5` həm `-R`, həm `update-initramfs -u` çağırır.
- **Risk:** Adwaita-dark seçimi ayrıca yaradılmış custom GTK tema deyil. Plymouth skriptində animasiya, progress və parol prompt callback-ları yoxdur; aspect ratio pozula bilər. `-R` sonrakı initramfs əməliyyatını təkrarlaya bilər. Real boot görünüşü bilinmir.
- **Tövsiyə:** Müxtəlif ekranlarda GTK3/GTK4/libadwaita, wallpaper və boot nəticələrini yoxlamaq; initramfs-də tema mövcudluğunu təsdiqləmək; “animasiya/custom theme” iddialarını faktiki imkanlarla uyğunlaşdırmaq.

## 5. Təhlükəsizlik riskləri və baza dəstəyi

### S01 — P0: Məlum parollu administrator hesabı

- **Sübut:** `config/hooks/normal/0100-create-default-user.hook.chroot:5–8` zeros hesabını sudo/adm və digər qruplarla yaradır, hər dəfə `zeros:zeros` verir; `Readme.md:28–35` bunu ictimailəşdirir. Qalıq `chroot/etc/passwd:32` zeros UID 1000 hesabını göstərir. First-boot parol dəyişmə məcburiyyəti və installed-user ayrılması yoxdur.
- **Risk:** Fiziki giriş və ya sonradan açılan uzaq xidmət vasitəsilə məlum parolla admin səlahiyyəti əldə etmək mümkündür. SSH serverin hazırda aktiv olması sübut edilməyib; birbaşa uzaq exploit iddiası yoxdur.
- **Tövsiyə:** Live mühit üçün açıq sənədləşdirilmiş müvəqqəti hesab; installed sistemdə default hesabın silinməsi və istifadəçinin öz parolunu seçməsi; şəbəkə xidmətlərinin minimumlaşdırılması. Stabil buraxılışdan əvvəl hesab siyasəti release gate olmalıdır.

### S02 — P0: Live-config istifadəçisi və sudo siyasəti uyğunsuzluğu

- **Sübut:** `auto/config:10` username/noroot göstərmir; tracked live-config override yoxdur. Qalıq `chroot/usr/lib/live/config/0030-user-setup:30–32,51–55,75–82` LIVE_USERNAME əsasında istifadəçi yaratmağa çalışır və UID 1000 istəyir; UID artıq zeros-a məxsusdur. `0040-sudo:62–74` seçilmiş live istifadəçisi üçün `NOPASSWD: ALL` yaradır. Faktiki `/etc/sudoers` icazə səbəbilə oxunmayıb.
- **Risk:** Default live istifadəçisi, GDM seçimi və zeros hesabı bir-birindən ayrıla bilər; user-setup uğursuzluğu və gözlənilməyən parolsuz admin siyasəti mümkündür. Bunlar boot edilmədən təsdiqlənmiş runtime nəticəsi deyil. Öz hook-larında NOPASSWD yazılmaması live-config-in bunu etmədiyi demək deyil.
- **Tövsiyə:** Username/UID, autologin, live sudo və installed sudo üçün vahid siyasət; ilk boot-da faktiki passwd/group/sudoers və `sudo -l` testi. `noroot` parametrinin pre-created zeros sudo üzvlüyünü təkbaşına aradan qaldıracağını fərz etməmək.

### S03 — P1: Sanitizasiya var, lakin unikal ilk boot sübutu yoxdur

- **Sübut:** `8020-remove-dbus-machine-id.hook.chroot:9`, `8050-remove-openssh-server-host-keys.hook.chroot:10`, `8060-remove-systemd-machine-id.hook.chroot:9–12` ID/key-ləri silir və systemd ID-ni boşaldır. Qalıqda `/etc/machine-id` 0 baytdır, D-Bus ID yoxdur və `/etc/ssh/ssh_host_*` tapılmayıb. `8030:6–8` log-ları truncate edir; `8070:6–15` temp faylları silir. `8090` snakeoil sertifikatını silir.
- **Risk:** Bunlar host symlink-lərindən asılıdır və ISO rootfs/ilk boot ayrıca yoxlanılmayıb. SSH key olmaması server quraşdırılmadığı üçün də ola bilər. İki maşında yeni ID/key yaranması təsdiqlənmir. Log truncate bütün build sirrlərinin təmizlənməsi zəmanəti deyil.
- **Tövsiyə:** Final rootfs sanitizasiya yoxlaması, iki təmiz boot müqayisəsi, lazım gələrsə SSH key regenerasiyası və xidmət siyasəti; root/user history, credential və build state üçün ayrıca yoxlama.

### S04 — P1: APT bazası var; məhsulun update siyasəti yoxdur

- **Sübut:** `config/common:19` APT secure yoxlamasını aktiv saxlayır; `config/chroot:19,28–31` Debian keyring, security və updates seçir. `config/bootstrap:34–64` HTTP Debian mirror-ları göstərir. Qalıq `chroot/etc/apt/sources.list:1–6` bookworm, bookworm-security, bookworm-updates saxlayır. Öz repository/keyring, unattended-upgrades və paket overlay update siyasəti tapılmayıb. Qalıq manifestdə GNOME Software var.
- **Risk:** HTTP təkbaşına paket imzalarının söndürüldüyü demək deyil; APT imzaları əsas qorunmadır, HTTPS əlavə transport məxfiliyi/qorunması verir. Mirror əlçatanlığı və update UI işləkliyi yoxlanılmayıb. Debian paket yeniləmələri əl ilə overlay edilmiş MO və digər branding fayllarını əvəz edə bilər. Live overlay yeniləmələri persistence olmadan reboot-da itə bilər.
- **Tövsiyə:** HTTPS və final sources yoxlaması; live/installed update davranışını sənədləşdirmək; zerOS dəyişikliklərini versiyalı paketlərdə yaymaq; security yeniləmələrinə cavab müddəti, ISO refresh və rollback siyasəti müəyyən etmək. APT mövcud olduğuna görə “paket meneceri yoxdur” demək düzgün deyil (`Readme.md:54` ayrıca məhsul roadmap-i kimi dəqiqləşdirilməlidir).

### S05 — P1: Debian 12 artıq LTS mərhələsindədir

- **Sübut:** Baza `auto/config:6`, `config/bootstrap:7–22` ilə Bookworm-dur. Audit tarixinə rəsmi [Debian Bookworm release məlumatı](https://www.debian.org/releases/bookworm/) tam dəstəyin 11 iyul 2026-da bitdiyini, LTS-in 30 iyun 2028-dək davam etdiyini bildirir. [12 iyul 2026 elanında](https://www.debian.org/News/2026/20260712) təhlükəsizlik dəstəyinin LTS komandasına keçdiyi təsdiqlənir. [LTS Bookworm wiki](https://wiki.debian.org/LTS/Bookworm) başlanğıcı 11 iyun kimi göstərir; tarix fərqi səbəbilə tam dəstəyin sonu üçün release səhifəsi və rəsmi elan əsas götürülüb. Hər halda 2026-11-06-da LTS statusu dəyişmir.
- **Risk:** LTS bütün paketlərə eyni əhatə zəmanəti vermir; GNOME desktop, brauzer və digər seçilmiş paketlərin dəstəyi ayrıca izlənməlidir. Yeni məhsul üçün baza ömrü məhduddur.
- **Tövsiyə:** `debian-security-support` məlumatı ilə paket səviyyəli dəstək review-su planlaşdırmaq; ilk ictimai stabil buraxılışdan əvvəl Debian 13/Trixie-yə keçidin xərci və testini qiymətləndirmək. [Trixie release səhifəsi](https://www.debian.org/releases/trixie/) ilkin buraxılışı 9 avqust 2025, tam dəstəyi 9 avqust 2028, LTS sonunu 30 iyun 2030 göstərir. Sadəcə suite adını dəyişmək kifayət deyil: GNOME, GDM, live-build, firmware və tərcümələr yenidən yoxlanmalıdır.

## 6. İlk ictimai buraxılış üçün çatışmayanlar

### R01 — P1: Installer və buraxılış sərhədi

- **Sübut:** `auto/config:8`, `config/binary:53` Debian Installer-i söndürür; iki paket siyahısında Calamares və installer settings yoxdur. Standart `5050-dracut.hook.chroot:24–54` daxilindəki Calamares istinadları yalnız şərti uyğunlaşdırmadır, installer quraşdırmır. `Readme.md:53` installer-i açıq iş kimi göstərir.
- **Risk:** İstifadəçi install edilə bilən distributiv gözləyərsə proses yoxdur; default live hesabını diskə köçürən qeyri-rəsmi üsullar təhlükəli ola bilər.
- **Tövsiyə:** Birinci buraxılışın live-only preview, yoxsa install edilən stabil sistem olduğunu seçmək. Live-only üçün installer tələb deyil; bunun açıq yazılması tələbdir. Install edilən buraxılışda partition/UEFI/BIOS, encryption, user creation, live hesabının silinməsi və bootloader testləri release gate olmalıdır.

### R02 — P1: Release sübutları və distributiv metadata-sı yoxdur

- **Sübut:** `config/binary:31` SHA256 daxili yoxlamalarını seçir; qalıqda `binary/sha256sum.txt` var. Tracked fayllarda ISO üçün imzalı SHA256SUMS, CI workflow, release manifesti, versiya siyasəti, test protokolu, LICENSE və üçüncü tərəf asset/tərcümə mənşə sənədi yoxdur. `config/source:4` source image yaratmağı söndürür. `config/includes.chroot/` daxilində os-release/issue override yoxdur; ISO metadata-sı isə `config/binary:74–83` ilə brendləşdirilir.
- **Risk:** Daxili checksums yüklənən ISO-nun autentikliyini sübut etmir; build mənşəyi, mənbə uyğunluğu, brend hüquqları və istifadəçiyə görünən distro kimliyi qeyri-müəyyəndir. Source ISO-nun olmaması təkbaşına lisenziya pozuntusu hökmü deyil, yayım öhdəlikləri ayrıca yoxlanmalıdır.
- **Tövsiyə:** Versiyalı RC, commit/toolchain/paket manifesti, ISO hash və detached signature, açar paylaşımı, changelog/known issues/minimum requirements/support kanalı. Asset və dəyişdirilmiş proqramların mənşə/lisenziya inventarı, uyğun mənbə əldə etmə yolu; Debian uyğunluğunu saxlayan distro metadata-sı.

## 7. P0/P1/P2 backlog

P0 = stabil ictimai buraxılışı bloklayır; P1 = RC-dən əvvəl həll və ya açıq scope qərarı; P2 = keyfiyyət və saxlanma işi. Heç biri bu auditdə implement edilməyib.

| Prioritet | İş / tapıntı | Qəbul meyarı |
|---|---|---|
| P0 | Locale konflikti — B01 | Final rootfs və normal/failsafe sessiyada az_AZ.UTF-8; gözlənilən dil fallback-ı |
| P0 | Hesab/sudo siyasəti — S01/S02 | Faktiki login hesabı/UID/sudo siyasəti sənədlə uyğundur; installed sistemdə məlum parol yoxdur |
| P0 | Build reseptinin host asılılığı — B02 | Versiyalı toolchain, mövcud hook hədəfləri və təmiz checkout build sübutu |
| P0 | Stabil release üçün build/boot sübutu — B05/R02 | BIOS və UEFI normal boot; Secure Boot üçün açıq dəstək qərarı; log və imzalı artifact |
| P1 | Build preflight və reproducibility — B03/B04 | Sabit girişlər və provenance; iki build müqayisəsi, fərqlər izah edilir |
| P1 | Keyboard və GNOME tərcümə pipeline-ı — L01/L02 | GDM/GNOME klaviatura testi; PO mənbələrindən yoxlanan MO; ölçülən dil əhatəsi |
| P1 | GDM və ISO boot branding — L03/L04 | Dəstəklənən schema/profile; BIOS/UEFI screenshot review |
| P1 | Sanitizasiya və update testi — S03/S04 | İki boot-da unikal ID; gözlənilən key/service davranışı; APT update sübutu |
| P1 | Baza seçimi — S05 | Bookworm LTS risk qərarı və ya sınaqdan keçmiş Trixie keçid planı |
| P1 | Installer/scope və release paketi — R01/R02 | Live-only qərarı və ya sınaqlı installer; hash/imza, release notes, mənbə/lisenziya inventarı |
| P2 | Theme/Plymouth və iddiaların dəqiqləşməsi — L05 | Aspect ratio, dark app coverage, recovery/parol axını; README faktlarla uyğundur |
| P2 | Paket siyahılarının sadələşdirilməsi — B05 | Təkrarsız, əsaslandırılmış desktop/hardware paketləri və ölçü büdcəsi |

## 8. Tövsiyə olunan növbəti 7 günlük plan

Bu plan gələcək iş təklifidir; sistem dəyişən və root tələb edən testlər bu auditdə icra edilməyib.

| Gün | Fokus | Gözlənilən nəticə |
|---|---|---|
| 1 — 7 noyabr | Live-only/install scope, Bookworm/Trixie və release gate qərarları | Qısa qərar sənədi, hardware və security tələbləri |
| 2 — 8 noyabr | Pinlənmiş build mühiti, hook və config girişləri | Təmiz checkout üçün yoxlanılan build resepti, preflight/logging |
| 3 — 9 noyabr | Locale konflikti, keyboard, username/UID və sudo | Review edilmiş dəyişikliklər, statik yoxlamalar |
| 4 — 10 noyabr | PO/MO pipeline, GDM və boot branding | Versiyalı tərcümə mənbələri, əsas UI sözlüyü, branding RC |
| 5 — 11 noyabr | İzolyasiya edilmiş təmiz build və ikinci build müqayisəsi | Log, paket/toolchain manifesti, ISO hash, fərq hesabatı |
| 6 — 12 noyabr | BIOS/UEFI/Secure Boot, live login, locale, update və ID testləri | Reproduksiya olunan test protokolu və blocker siyahısı; installer seçilibsə ayrıca test |
| 7 — 13 noyabr | Blocker review, release sənədləri və məhdud icma RC-si | İmzalı RC və known issues; P0 qalırsa stabil buraxılış təxirə salınır |

Tam installer əlavə etmək və baza köçürməsi yeddi günə keyfiyyətli tamamlanmaya bilər. Məqsəd müddətə görə “stabil” etiketi vermək deyil, yoxlanılan RC və açıq qərarlar əldə etməkdir. Rust mikrokernel və AI OS istiqamətini ilk Debian/GNOME release-dən ayrı tədqiqat xətti kimi saxlamaq tövsiyə olunur.

## 9. Açıq suallar və əlavə test ehtiyacları

- İlk ictimai buraxılış live-only preview olacaq, yoxsa diskə install edilən stabil sistem? Persistence dəstəyi nəzərdə tutulurmu?
- Bookworm-da qalmaq üçün konkret səbəb varmı; Trixie miqrasiyası üçün hansı hardware/tətbiq məhdudiyyəti var?
- Live hesab zeros olmalıdırmı; autologin, parolsuz sudo və installed hesabın tələb olunan davranışı nədir?
- Azərbaycan dilində minimum qəbul edilən ekranlar hansılardır; terminologiya və tərcümə review-suna kim cavabdehdir?
- Wayland-ın söndürülməsinə səbəb hansı təsdiqlənmiş problemdir? BIOS, UEFI və Secure Boot dəstəyinin minimum hardware matrisi nədir?
- Mövcud ISO hansı commit/toolchain ilə yaranıb? Qalıq manifestlər final ISO ilə eynidirmi? Build qalıqları buna cavab vermir.
- Wallpaper/boot şəkilləri və MO-ların müəllifliyi/lisenziyası nədir? Mənbə PO/asset çevirmə prosesi haradadır?
- Paket dəstəyini, security ISO refresh-lərini, imza açarlarını və istifadəçi problem hesabatlarını kim idarə edəcək?

### İcra edilən yoxlamalar

- Tracked fayllar və symlink rejimləri, bütün yerli build config/hook mətnləri və həll olunan standart hook hədəfləri oxunub.
- `bash -n`: `auto/config`, `scripts/build.sh` və 31 hook üçün cəmi **33 sintaksis yoxlaması uğurludur**. Bu, əmrlərin mövcudluğunu və build nəticəsini yoxlamır.
- GNU MO parser ilə iki kataloq oxunub; gettext compile/lint alətləri mövcud olmadığı üçün msgfmt yoxlaması aparılmayıb.
- Qalıq boot config, paket manifesti, locale/keyboard, GDM schema və açıq sanitizasiya faylları statik oxunub. Sudoers oxuma məhdudiyyəti qeyd olunub.
- Build, ISO daxili rootfs yoxlaması, boot və vizual test, network update, installer və iki build reproducibility testi **aparılmayıb**.

### Sonrakı test protokolu

1. Təmiz, versiyalı mühitdə build; commit, toolchain, snapshot, log və SHA256 qeyd etmək.
2. ISO hybrid partition/El Torito və final squashfs məzmununu ayrıca yoxlamaq; initramfs Plymouth asset-lərini təsdiqləmək.
3. BIOS və UEFI normal/failsafe boot; Secure Boot açıq/bağlı, real USB və seçilmiş Wi-Fi/GPU hardware testi.
4. `locale`, klaviatura, GDM/login/lock, GNOME input sources, tərcümə/dark theme screenshot-ları; az_AZ və az fallback-ları.
5. Faktiki istifadəçi/UID/group, autologin, sudoers və açıq xidmətlər; iki müstəqil boot-da machine-id və SSH key davranışı.
6. APT imza/sources və yeniləmə axını; branding fayllarının upgrade-dən sonra qalması; live persistence davranışı.
7. Installer seçilərsə boş disk, UEFI/BIOS, istifadəçi yaradılması, default live hesabının silinməsi, encryption və installed reboot.
8. İki müstəqil build-in ISO və filesystem fərqlərini müqayisə etmək; izahsız fərqlər qalarsa bit-identical reproducibility iddiası verməmək.
