# zerOS — Day 02: Architecture Decision Preparation

Sənəd tarixi: **2026-11-07** (Day 02 planı). Araşdırma: **2026-11-06**, Asia/Baku.  
Status: **təklif; arxitektura qərarı və implementasiya təsdiqi deyil**.  
Əsas: [Day 01 texniki auditi](../audits/2026-11-06-technical-audit.md); baza commit `b1aa32f713baf2570cfdd21eae364447402a0e49`.

## 1. Tövsiyə edilən istiqamət

İlk Alpha üçün **Debian 13 Trixie / amd64 / GNOME / live-only / persistence-siz** profil seçmək tövsiyə olunur. Məqsəd Azərbaycan dili, masaüstü və hardware təcrübəsini qiymətləndirməkdir. Installer, diskə quraşdırma, daimi şəxsi məlumat saxlama və Rust mikrokernel bu Alpha-nın əhatəsinə daxil edilməsin. Təklif olunan public profil administrator hesabı verməsin.

Bu sənəddə uyğunluq “paket mövcuddur”, “mexanizm ehtimalən portativdir” və “zerOS-da testlə təsdiqlənib” səviyyələrinə ayrılır. Sonuncu səviyyədə yeni sübut **yoxdur**: build, boot, paket həlli, GDM sessiyası və sudo testi aparılmayıb. Paket quraşdırılmayıb, root əmri icra edilməyib, məhsul kodu dəyişdirilməyib. Başlanğıcdakı `.gitignore` və `config/common` dəyişiklikləri saxlanılıb.

Mürəkkəblik: **Aşağı** ≈ 0.5–1 mühəndis günü; **Orta** ≈ 1–3 gün; **Yüksək** ≈ 3–5+ gün. Bunlar implementasiya və fokuslu yoxlama üçün təxmindir; build növbəsi, hardware əldə edilməsi və tam tərcümə daxil deyil. Sətirlərin vaxtları toplanaraq zəmanətli təqvim müddəti hesablanmamalıdır.

## 2. Debian 12 və Debian 13 müqayisəsi

Rəsmi məlumatlara görə Bookworm tam dəstəyi 11 iyul 2026-da bitib; LTS 30 iyun 2028-dəkdir. Trixie tam dəstəyi 9 avqust 2028-dək, LTS 30 iyun 2030-dək göstərilir. amd64 hər iki baza üçün uyğundur. [Bookworm həyat dövrü](https://www.debian.org/releases/bookworm/), [Trixie həyat dövrü](https://www.debian.org/releases/trixie/).

| Meyar | Debian 12 Bookworm | Debian 13 Trixie | zerOS qərarına təsir |
|---|---|---|---|
| Cari resept | Hazırda seçilib: `auto/config:6`, `config/bootstrap:7–22` | Konfiqurasiya və paket həlli yenilənməlidir | Bookworm-a qalmaq ilkin diff-i azaldır, audit P0-larını həll etmir |
| Dəstək | Artıq LTS; paket əhatəsi ayrıca izlənməlidir | Daha uzun baza ömrü və tam dəstək mərhələsi | Yeni ictimai məhsul üçün Trixie üstünlükdür |
| Desktop | GNOME 43; indiki qalıqlar bu versiyadandır | GNOME 48 | Mövzular, dconf, GDM və mesaj kataloqları yenidən yoxlanmalıdır |
| Kernel | 6.1 seriyası | 6.12 seriyası | Yeni hardware üçün daha yaxşı namizəd; konkret cihaz uyğunluğu zəmanəti deyil |
| Toolchain | Mövcud host Kali variantlı live-build istifadə edir | Debian Trixie toolchain-i ilə standartlaşdırmaq mümkündür | Host və target versiyaları ayrı kilidlənməlidir |
| Tərcümə | Kiçik mövcud overlay-lər belə tam yoxlanılmayıb | Dəyişmiş msgid/context/plural ilə əhatə azala bilər | İki baza üçün paralel kataloq saxlamaq əvəzinə bir target seçmək |
| Qısa müddətli risk | Az port işi; köhnə problemləri saxlamaq riski | Daha böyük ilkin port/test işi | Trixie sınağına vaxt ayırmaq; təqvim naminə test gate-lərini azaltmamaq |

GNOME/kernel müqayisəsi rəsmi [Trixie yenilikləri və paket cədvəlinə](https://www.debian.org/releases/trixie/release-notes/whats-new.en.html) əsaslanır. Yeni kernel-in zerOS hardware əhatəsini artırması texniki gözləntidir, ölçülmüş nəticə deyil.

| Variant / tövsiyə | Texniki əsas | Risk | Mürəkkəblik |
|---|---|---|---|
| **D01: Trixie-ni Alpha üçün əsas namizəd seçmək** | Yeni desktop bazası üzərində bir dəfə lokallaşdırma; daha uzun dəstək | GNOME/GDM və boot regressiyaları | Yüksək; ayrıca test mərhələsi |
| Bookworm-u diaqnostik müqayisə üçün saxlamaq | Eyni P0 düzəlişlərini əvvəlki bazada müqayisə etmək olur | İki public baza saxlanarsa yük ikiqat artır | Orta; public paralel buraxılış tövsiyə edilmir |
| Yalnız ölçülmüş Trixie blocker-i varsa Bookworm Alpha fallback | Geri dönüş texniki problemin təcridinə kömək edir | LTS əhatəsi və sonrakı miqrasiya borcu qalır | Orta; ayrıca qərar və bütün gate-lər tələb olunur |

Fallback avtomatik deyil: blocker, təkrar yaratma addımları, Trixie həll xərci, Bookworm təhlükəsizlik əhatəsi və keçid vaxtı sənədləşdirilməlidir. Köhnə ISO-nu sadəcə Alpha adlandırmaq qəbuledilməzdir.

## 3. Debian 13 uyğunluq qiymətləndirməsi

### 3.1. Komponentlər

| Komponent və mövcud sübut | Trixie qiymətləndirməsi | Tövsiyə / texniki əsas | Risk və mürəkkəblik |
|---|---|---|---|
| GNOME: `desktop.list.chroot:4–5`; dark dconf `0004-dconf-apply.hook.chroot:13–23` | GNOME 48 mövcuddur; zerOS override-ları təsdiqlənməyib | **D02:** prefer-dark və wallpaper-i dəstəklənən schema ilə saxlamaq; GTK3/GTK4/libadwaita-nı ayrıca yoxlamaq | gtk-theme bütün tətbiqləri idarə etmir; Orta |
| GDM: `0002-gdm-theme.hook.chroot:6–11`, `daemon.conf:2` | [gdm3 48.0-2](https://packages.debian.org/trixie/gdm3) var; hazırkı background mexanizmi port ediləcək sağlam əsas deyil | **D03:** Alpha-da standart GDM görünüşü + yalnız təsdiqlənmiş logo/banner; Debian profile yolunu paketdən yoxlamaq | Greeter schema/profile uyğunsuzluğu; Orta |
| Session: `WaylandEnable=false` | Bu ayarın GNOME 48-də saxlanması üçün layihədə əsas yoxdur | **D04:** əvvəlcə Debian default session-u sınaqdan keçirmək; X11 məcburiyyətini yalnız reproduksiya olunan problem əsasında seçmək | GPU/VM/ekran paylaşma fərqləri; Orta |
| live-build: `config/common:4`, host symlink-ləri | [Trixie paketi 1:20250505+deb13u1](https://packages.debian.org/trixie/live-build) var; audit hostunun Kali variantı ilə eyni deyil | **D05:** Debian mənşəli dəqiq versiya və asılılıqlarla təmiz resept yaratmaq | Köhnə generated config yeni default-ları bloklaya bilər; Yüksək |
| BIOS/UEFI: `config/binary:22–28,119` | Trixie manualında `--bootloaders` və Secure Boot seçimi var | **D06:** seçilmiş toolchain-də `--bootloaders "syslinux grub-efi"` namizədini yoxlamaq; Secure Boot-u açıq qərar etmək | Köhnə ayrı LB_BOOTLOADER_* dəyişənlərini kor-koranə daşımamaq; Orta |
| Firmware: `desktop.list.chroot:19`, `bootstrap:28` | [firmware-linux 20250410-2](https://packages.debian.org/trixie/firmware-linux) non-free-firmware-də var | **D07:** main/contrib/non-free-firmware siyasətini saxlamaq; hədəf cihazlara görə Wi-Fi/GPU/microcode paket xəritəsi yaratmaq | Metapaket bütün cihazları əhatə etmir; ölçü/lisenziya artımı; Orta |
| Plymouth: `0005-plymouth.hook.chroot:4–5`, `zeros.script:1–6` | Sadə script konsepti portativ namizəddir; Trixie plugin/initramfs testi yoxdur | **D08:** mövcud initramfs-tools/live-boot xəttini ilk Alpha-da saxlamaq, dracut keçidini ayrıca iş etmək; initramfs-də asset-ləri yoxlamaq | İkinci initramfs keçidi debugging-i çətinləşdirər; Orta |

D05/D06 üçün əsas: [Trixie lb_config manualı](https://manpages.debian.org/trixie/live-build/lb_config.1.en.html) mövcud generated config ilə yenidən konfiqurasiya etməyin ziddiyyətli nəticələr verə biləcəyini bildirir. İmplementasiya zamanı disposable checkout-da yalnız generated beş config faylı yenidən yaradılmalı, custom includes/hook/package-list məzmunu qorunmalıdır. Bu sənəd silmə və ya build əmri icra etmir.

D02 üçün [GNOME sistem default-ları](https://help.gnome.org/system-admin-guide/dconf-custom-defaults.html) profile və system database mexanizmini izah edir. Bu mexanizm user desktop və GDM greeter üçün eyni profil demək deyil. `dconf update` uğuru açarın tətbiq tərəfindən dəstəkləndiyini sübut etmir.

### 3.2. Tərcümə overlay-ləri

Day 01 L02: `config/includes.chroot/usr/share/locale/az/LC_MESSAGES/gnome-control-center.mo` 15, `nautilus.mo` 14 qeyri-header giriş daşıyır. `naut.po:7–50` Settings terminləri saxlayır. Trixie-də [Settings 48.4](https://packages.debian.org/trixie/gnome-control-center) və [Nautilus 48.3](https://packages.debian.org/trixie/nautilus) paketləri mövcuddur. Paket mövcudluğu kataloq uyğunluğu deyil.

**D09 — Tövsiyə:** mövcud MO-ları GNOME 48-ə təsdiqlənmiş tərcümə kimi köçürməmək. Seçilən paket versiyasının mənbə PO/POT-ları ilə mesajları müqayisə etmək; domain, msgctxt və plural formaları qorumaq; `msgmerge` sonrası fuzzy girişləri insan review-suna göndərmək; `msgfmt --check` ilə MO generasiya etmək. Settings və Nautilus üçün düzgün adlandırılmış ayrı PO mənbələri repository-də saxlanmalıdır. Upstream Azərbaycan kataloqu varsa onu baza götürmək, 14–15 mesajlıq faylla bütöv kataloqu əvəz etməmək.

**Texniki əsas:** gettext fayl formatının oxuna bilməsi yalnız parse uyğunluğudur; UI uyğunluğu msgid/context/plural uyğunluğundan asılıdır. **Risk:** səssiz ingilis dili fallback-ı, zəngin upstream tərcüməsinin itməsi, paket yeniləməsinin overlay-i silməsi. **Mürəkkəblik:** Orta pipeline işi; linqvistik tamlıq ayrıca, daha uzun işdir.

**D10 — Alpha alternativi:** hədəf paketlərlə yoxlanmış kiçik, düzgün birləşdirilmiş kataloq buraxmaq və UI əhatəsini açıq göstərmək; yoxlanılmayan overlay-i çıxarıb upstream fallback-ını saxlamaq. Əsas: yanlış tərcümə əvəzinə proqnozlaşdırılan davranış. Risk: Alpha-nın Azərbaycan dilində əhatəsi azalır; Aşağı–Orta. Sonrakı mərhələdə tərcümə/branding-i versiyalı Debian paketinə keçirmək tövsiyə olunur; Orta, paket ownership və update inteqrasiyası tələb edir. Alpha üçün avtomatik paket upgrade-dən sonra branding-in qalacağı vəd edilməməlidir.

## 4. Live-only Alpha istifadəçi, autologin və sudo siyasəti

### 4.1. Tövsiyə olunan public profil — D11

**Təhdid modeli:** ISO hamı üçün oxuna biləndir; image daxilində saxlanan ümumi parol sirr deyil. Autologin fiziki istifadəçiyə sessiya verir. Bu profil təhlükəsiz şəxsi workstation və ya hostile fiziki girişdən qorunma iddiası daşımır. Bununla belə adi browser/desktop prosesinə avtomatik root vermək lazım deyil.

| Sahə | Konkret təklif | Texniki əsas | Risk / mürəkkəblik |
|---|---|---|---|
| Tək hesab sahibi mexanizm | `username=zeros` ilə live-config istifadəçi yaradılmasını idarə etsin; build-time `0100-create-default-user` mexanizmi əvəz edilsin | UID 1000 yarışı və ikinci default user aradan qalxır | Hook və runtime ardıcıllığı dəqiq yoxlanmalıdır; Orta |
| Şifrə | Image-də `zeros/zeros`, `user/live` və boş parol qalmasın; root və zeros password authentication locked olsun | Ümumi parolun publik olma problemini aradan qaldırır | GDM PAM locked hesabı autologin-ə buraxmaya bilər; test blocker-dir; Orta |
| Qrafik autologin | Yalnız disposable GDM sessiyası üçün zeros autologin; console autologin bağlı | Alpha-nı parol paylaşmadan açır | Fiziki giriş sessiyaya tam girişdir; Orta |
| Sudo | Public profildə sudo səlahiyyəti və `NOPASSWD: ALL` yoxdur; sudo/adm üzvlüyü verilməsin | Məlum parollu və ya parolsuz admin riskini kəsir | Texniki tester bəzi əmrləri işlədə bilməz; Aşağı–Orta |
| live-config shortcut | Normal və failsafe girişlərində `noroot nottyautologin username=zeros` namizəd parametrləri | `noroot` sudo/PolicyKit-i, `nottyautologin` console autologin-i idarə edir | PolicyKit ilə işləyən desktop əməliyyatları pozula bilər; Orta |
| Qruplar və PolicyKit | Root/disk/sudo/adm əlavə edilməsin; yalnız sessiyaya lazım olan qruplar; effektiv PolicyKit qaydaları yoxlanılsın | Təkcə sudo-nu bağlamaq başqa yüksəltmə yollarını yox etmir | Wi-Fi, removable media və power əməliyyatlarının işləməsi ayrıca testdir; Orta |
| Uzaq xidmətlər | SSH/RDP/VNC serveri public profilə əlavə edilməsin; gözlənilməyən listener olmasın | Autologin hesabının şəbəkə girişini məhdudlaşdırır | Dependency vasitəsilə xidmət əlavə oluna bilər; Aşağı + test |
| Disk və persistence | Installer və persistence dəstəyi yoxdur; daxili disklər avtomatik yazma üçün mount edilməsin | Disposable Alpha sərhədi qorunur | Browser və fayl meneceri əl ilə məlumat yaza bilər; bu profil disk isolation deyil; Orta |
| Logout/lock | Parol bərpası axını vəd edilməsin; lock/suspend davranışı əvvəlcədən seçilsin, çıxılmaz vəziyyətdə aydın reboot yolu olsun | Locked parolla ekranı yenidən açmaq mümkün olmaya bilər | Sessiya məlumatı itir; bunun UI/release notes-da izahı tələb olunur; Orta |

[Debian live-config manualı](https://manpages.debian.org/trixie/live-config-doc/live-config.7.en.html) bu parametrləri sənədləşdirir. `noroot` mövcud pre-created sudo hesabını təmizləyən universal mexanizm kimi qəbul edilmir: köhnə hook və əvvəlki sudoers/qruplar ayrıca aradan qaldırılmalıdır. Root və user parolunun boot-time kilidlənməsi üçün seçilmiş live-config komponentlərindən sonra, display manager-dən əvvəl işləyən lokal, yoxlanılan addım planlaşdırılmalıdır; yalnız build-time lock user-setup tərəfindən əvəz edilə bilər.

GDM autologin-in dəstəklənən `[daemon]` açarları [GNOME sənədində](https://help.gnome.org/system-admin-guide/login-automatic.html) verilir; Debian-da yol paketə görə yoxlanmalıdır. Hazırkı `/etc/gdm3/daemon.conf` bütöv faylı overlay edir. GDM autologin üçün iki ayrı writer yaratmaq əvəzinə live-config-in GDM komponentini əsas götürmək, nəticəni test etmək tövsiyə olunur.

**Vacib gate:** `noroot` altında Wi-Fi və əsas sessiya əməliyyatları uğursuz olarsa universal sudo əlavə edilməsin. İki seçim review edilsin: əvvəlcədən işləyən şəbəkə konfiqurasiyası ilə məhdud public demo, yaxud sudo komponenti söndürülmüş və yalnız dəqiq ehtiyaclara icazə verən PolicyKit siyasəti. İkinci seçim Orta–Yüksək mürəkkəblik və ayrıca privilege testləri tələb edir. Hazırkı araşdırma hansı variantın Trixie-də işləyəcəyini təsdiqləmir.

### 4.2. Digər variantlar

| Variant | Əsas | Risk | Mürəkkəblik / qərar |
|---|---|---|---|
| Autologin bağlı, ilk boot-da şəxsi parol | Real autentifikasiya sərhədi yaradır | Onboarding/GDM inteqrasiyası, keyring və recovery işi | Yüksək; sonrakı release üçün namizəd |
| Autologin + ümumi parol + password sudo | İmplementasiyası asandır | Ümumi parol admin qoruması vermir | Aşağı; public Alpha üçün rədd edilir |
| Autologin + universal NOPASSWD sudo | Tester üçün rahatdır | Sessiyadakı istənilən proses root ala bilər | Aşağı; public profil üçün rədd edilir |
| Ayrı developer image | Hardware diaqnostikasında admin lazım ola bilər | Public ISO ilə qarışdırılma riski | Orta; yalnız ayrıca artifact/ad/hash və açıq admin etiketi ilə gələcək seçim |

## 5. Locale konfliktinin konkret həll variantları

Problem: `0006-locale.hook.chroot:4–13` locale yaradır, sonrakı `1020-create-locales-files.hook.chroot:7` isə `LANG=C.UTF-8` yazır (Day 01 B01). Includes faylı yazmaq təkbaşına həll deyil: cari pipeline-də includes-after-packages hook-lardan əvvəl köçürülür.

| Variant | Mexanizm və texniki əsas | Risk | Mürəkkəblik / seçim |
|---|---|---|---|
| **D12-A: Son locale hook-u** | Məsələn `1100-zeros-locale.hook.chroot`: standart 1020-dən sonra idempotent locale.gen aktivləşdirməsi, locale-gen, update-locale; daha sonrakı writer olmadığını yoxlamaq | Host hook sırası pinlənməsə yenə dəyişə bilər | Aşağı; Alpha üçün tövsiyə |
| D12-B: Standart 1020 hook-un lokal əvəzi | Upstream hook-un `/etc/environment` yaratmasını qoruyub az default-u birbaşa yazmaq | Upstream yenilikləri fork-a avtomatik gəlmir; lb config yenidən link yarada bilər | Orta; hook vendor siyasəti ilə uyğundur |
| D12-C: Yalnız runtime live-config | Locale və keyboard-u boot/config parametrləri ilə tətbiq etmək | Failsafe və komponent sırası; build rootfs default-u fərqli qalır; boot vaxtı generasiya | Aşağı; tək həll kimi seçilmir |

D12-A-nın hədəf nəticəsi: `/etc/default/locale` daxilində `LANG=az_AZ.UTF-8`, `LANGUAGE=az:en`; daimi `LC_ALL` təyin edilməsin. Əsas: LC_ALL bütün kateqoriyaları məcbur etməsin, istifadəçi override-ları qalsın. `locale.gen`-ə hər build-də yeni dublikat append edilməsin. Bu dəyərlər təklifdir, hazırkı kod deyil.

**D13:** Normal və failsafe boot girişləri üçün eyni locale, keyboard və hesab siyasətini bir mənbədən generasiya etmək; failsafe yalnız hardware/recovery parametrləri ilə fərqlənsin. GNOME üçün `org.gnome.desktop.input-sources` altında `az`, `us` mənbələrini və Super+Space keçidini hədəf schema ilə yoxlamaq. Əsas: kernel keyboard parametri Wayland/GDM/GNOME nəticəsinin zəmanəti deyil. Risk: console/GDM fərqli sıra; Orta. `LANGUAGE` fallback və Ə/ə, İ/i, I/ı simvolları üzrə runtime test tələb olunur.

## 6. Hostdan asılı hook-ların həll variantları

Problem: standart hook-lar Git-də absolute `/usr/share/live/build/hooks/...` symlink-ləridir (Day 01 B02). Linklərin silinməsi sanitizasiya funksiyalarını itirə bilər; yalnız beş custom hook-u saxlamaq yetərli deyil.

| Variant | Texniki əsas və konkret tədbir | Risk | Mürəkkəblik |
|---|---|---|---|
| **D14-A: Versiyalı hook məzmunu + pinlənmiş mühit** | Seçilmiş Debian live-build-dən istifadə olunan hook-ları normal fayl kimi vendor etmək; upstream versiya/path/SHA256/lisenziya inventarı; generated hook siyahısını yoxlamaq | Təhlükəsizlik düzəlişlərini vaxtında upstream-dən almaq yükü | Orta; Alpha üçün tövsiyə |
| D14-B: Paket hook-ları yalnız sabit build image daxilində | Absolute link-ləri yalnız dəqiq toolchain paketində həll etmək; manifestlə məzmun hash-lərini yoxlamaq | Repo standalone deyil; uyğun image olmadan işləməz | Orta; idarə olunan alternativ |
| D14-C: Minimal zerOS hook dəsti yazmaq | Lazımsız cache/alternative hook-ları azaltmaq, sanitizasiyanı özümüz saxlamaq | Gizli upstream davranışları və təhlükəsizlik təmizliyini itirmək | Yüksək; ilk Alpha üçün seçilmir |

**D15 — A ilə birlikdə mühit kontraktı:** disposable Debian Trixie VM/build image; dəqiq live-build/debootstrap və boot/image aləti versiyaları, image digest və ya VM manifesti; target snapshot tarixi, archive signatures və paket manifesti. `build-with-chroot=true` saxlanmalıdır. Repository kökünü yoxlayan preflight və clean/config mərhələsindən sonra hook inventarının təsdiqi planlaşdırılmalıdır. Əsas: vendoring təkbaşına xarici toolchain asılılığını aradan qaldırmır. Risk: köhnə snapshot təhlükəsizlik yeniləmələrini dondurur; release öncəsi idarə olunan refresh və təkrar gate tələb olunur. Mürəkkəblik: Yüksək ilkin qurulum, sonradan Orta saxlanma.

`lb config`-in standart symlink-ləri yenidən yaratması/əvəz etməsi seçilmiş versiyada ayrıca yoxlanmalıdır; təkrar config-dən sonra checksum inventarı dəyişirsə build dayansın. 8020/8050/8060 ID/key təmizləmə, log/temp sanitizasiya və locale hook davranışları qəbul meyarlarına bağlanmalıdır. Bit-identical ISO Alpha üçün məcburi deyil; iki təmiz build arasında paket/konfiqurasiya fərqləri izahsız qalmamalıdır. Risk: zəif provenance; Orta əlavə yoxlama.

## 7. P0 icra ardıcıllığı və asılılıqlar

Bu sıra implementasiya planıdır; P0-ların həll olunduğu iddiası deyil. Alpha scope ilə auditdəki stabil release tələbləri ayrılır: installer və tam GNOME tərcüməsi Alpha blocker-i deyil, hesab/locale/boot təhlükəsizliyi blocker-dir.

| Sıra | İş və Day 01 əlaqəsi | Asılılıq | Çıxış sübutu | Risk / mürəkkəblik |
|---|---|---|---|---|
| 0 | D01/D11 scope, baza və public privilege profili | Yoxdur | Qısa təsdiqlənmiş qərar qeydi | Yanlış baza üzərində təkrar iş; Aşağı qərar işi |
| 1 | D05/D14/D15 build mühiti və hook mənşəyi — B02 | 0 | Toolchain/hook lock, preflight, təmiz config diff | Hostdan çirklənmə; Yüksək |
| 2a | D12/D13 locale və boot profilləri — B01 | 1 | Hook sırası, final default və bütün boot entry-lərin statik yoxlaması | Locale overwrite; Aşağı–Orta |
| 2b | D11 istifadəçi, UID, parol, sudo — S01/S02 | 0, 1 | User-setup və final security addımının vahid kontraktı | İkinci hesab və ya admin qalması; Orta |
| 3 | Minimal Trixie paket/firmware + desktop uyğunluğu — B05/L01–L03 | 1, 2a, 2b | Paket həlli, schema/PO/MO yoxlaması, service inventarı | UI/şəbəkə regressiyası; Orta–Yüksək |
| 4 | Təmiz Alpha candidate ISO və rootfs yoxlaması | 3 | Build log, manifest, final filesystem və initramfs yoxlamaları | Köhnə qalıqların artifact-ə qarışması; Orta |
| 5 | BIOS/UEFI boot, təhlükəsizlik və locale gate-ləri | 4 | Test edilmiş konkret ISO SHA256-na bağlı protokol | Yoxlanmayan ISO-nun yayımlanması; Yüksək test işi |
| 6 | Release hash/imza, notes və Alpha qərarı — R02 | 5-də bütün blocker-lər keçib | İmzalı artifact + nəticələr + known issues | Autentiklik/mənşə boşluğu; Orta |

Asılılıq qrafı: `scope → toolchain/hooks → {locale, account policy} → paket/desktop → candidate → gate-lər → release`. 2a və 2b məntiqi olaraq müstəqildir; eyni final boot konfiqurasiyasına təsirləri birlikdə review edilməlidir. Sənəd paralel agent və ya sistem əməliyyatı başlatmır.

## 8. İlk Alpha ISO üçün minimum qəbul meyarları

Aşağıdakıların **heç biri bu araşdırmada icra edilməyib**. Hər test qeydində ISO SHA256, commit, toolchain, VM/cihaz, boot rejimi, tarix, nəticə və log/screenshot yolu olmalıdır. Mandatory gate keçməyibsə public Alpha yayımlanmasın. Mürəkkəblik gate-in hazırlanması və icrasına aiddir.

| Gate | Minimum ölçülən qəbul şərti | Texniki əsas / yoxlanmazsa risk | Mürəkkəblik |
|---|---|---|---|
| A01 Build/provenance | Təmiz checkout-dan fatal xəta olmadan ISO; paket/toolchain/hook manifesti və tam build log; ikinci təmiz build-də fərqlər izah olunub | Köhnə artefakt və host drift-i aşkarlanır | Yüksək |
| A02 Final rootfs | ISO-dan yoxlanmış rootfs-də az locale generasiya edilib; default-lar düzgündür; köhnə zeros/zeros hesab siyasəti yoxdur; hook sanitizasiyası görünür | Chroot qalıqları final ISO sübutu deyil | Orta |
| A03 Boot | Legacy BIOS VM və UEFI VM-də normal giriş GNOME sessiyasına çatır; failsafe sənədləşdirilmiş recovery sessiyası açır; bir real amd64 cihaz USB-dən uğurla boot edir | Hər iki firmware yolu və real USB yoxlanır | Yüksək |
| A04 Secure Boot scope | Ya açıq Secure Boot ilə test keçib və dəstək göstərilib, ya da “Alpha-da dəstəklənmir, söndürülməlidir” açıq yazılıb; `auto` uğur sayılmır | İmza zənciri config ilə sübut olunmur | Orta; dəstək iddiası varsa mandatory test |
| A05 Hesab/autologin | Tək gözlənilən zeros hesabı; yalnız GDM autologin; tty parolsuz giriş yoxdur; root/zeros parol auth locked; logout/lock/reboot axını çıxılmaz vəziyyət yaratmır | Default live-config parolu və ikinci user qalmır | Orta |
| A06 Privilege | `sudo -n true` adi istifadəçidə uğursuz; faktiki sudoers və qruplar review edilib; `su` ilə root parol girişi yoxdur; GUI vasitəsilə disk/istifadəçi idarəsi admin bypass etmir | Sudo qrupunu silmək bütün privilege yollarını bağlamır | Orta |
| A07 Şəbəkə/xidmətlər | Seçilmiş VM-də Ethernet, test cihazında dəstək vəd edilən Wi-Fi işləyir; DNS/HTTPS browsing uğurludur; SSH/RDP/VNC və gözlənilməyən remote listener yoxdur | noroot/PolicyKit desktop şəbəkəsini poza bilər | Orta |
| A08 Locale/keyboard | Normal və failsafe-də LANG az_AZ.UTF-8; GNOME/GDM-də az/us keçidi və Azərbaycan simvolları işləyir; kritik mətnlərdə mojibake yoxdur | Kernel parametrinin mövcudluğu runtime nəticə deyil | Orta |
| A09 Tərcümə/UI | Target GNOME versiyası ilə PO lint/compile keçir; saxlanılan xüsusi mesajlar UI-də görünür; dəqiq əhatə və ingilis fallback known issues-da yazılıb; Settings/Files açılır | Kiçik MO ilə tam GNOME tərcüməsi iddiasının qarşısı alınır | Orta |
| A10 Sanitizasiya | Final image-də sistem machine-id boş, D-Bus ID və SSH host private key yoxdur; iki təmiz boot-da machine-id fərqlidir; history/credential/build state sızması tapılmayıb | Klon ID və sirr sızması riski | Orta |
| A11 Live-only davranış | Installer yoxdur; persistence avtomatik aktivləşmir; daxili disk avtomatik yazma mount-u yoxdur; reboot-dan sonra live user dəyişiklikləri qalmır | İstifadəçi məlumatı/disk riski və yanlış gözlənti | Orta |
| A12 Update bazası | Final sources yalnız seçilmiş Trixie/security/updates siyasətinə uyğundur; imza yoxlaması aktivdir; texniki testdə APT metadata yenilənməsi uğurludur | Public istifadəçiyə sudo vermədən repo sağlamlığı yoxlanır | Orta |
| A13 Minimum təcrübə | Browser, Files, Settings və terminal açılır; restart/shutdown işləyir; wallpaper/dark görünüş oxunaqlıdır; 30 dəqiqəlik əsas sınaqda sessiya çökmür | Bu test uzunmüddətli stabillik zəmanəti deyil | Orta |
| A14 Yayımlama | ISO üçün xarici SHA256SUMS + detached signature yoxlanır; Alpha/live-only/persistence-siz status, hardware matrisi, privilege məhdudiyyəti, Secure Boot qərarı, known issues, feedback yolu və asset/mənbə mənşə qeydi var | İstifadəçi nəyi yüklədiyini və nəyi gözləməli olduğunu bilir | Orta |

A12 public profilə admin qaytarmaq üçün səbəb deyil: ayrıca test harness/izolyasiya edilmiş analiz mühiti vasitəsilə yoxlanmalıdır. A10-da SSH server daxil edilməyibsə key regenerasiyası testi N/A kimi səbəbi ilə qeyd edilə bilər; təsadüfi server əlavə olunarsa siyasət yenidən review edilməlidir.

Təklif olunan ilk VM sınaq profili: amd64, 2 vCPU, 4 GiB RAM, emulyasiya olunan Ethernet və qrafika; bu, ölçülmüş minimum sistem tələbi deyil. Real cihazın CPU/GPU/Wi-Fi modeli nəticələrlə dərc edilməlidir. Tam GNOME tərcüməsi, xüsusi GDM fonu, Plymouth animasiyası, installer, persistence, bütün hardware və bit-identical ISO Alpha qəbuluna şərt deyil; yalnız yoxlanmış imkanlara dəstək iddiası verilməlidir.

## 9. Qərar verilməli açıq məsələlər

1. D01 Trixie və D11 məhdud public profil qəbul edilirmi? Admin diaqnostikasına ehtiyac ayrıca developer artifact-i tələb edirmi?
2. `noroot` ilə GNOME 48-də Wi-Fi/power/removable media axınları işləyirmi? İşləməzsə hansı məhdud PolicyKit əməliyyatları əsas scope-dur?
3. GDM locked-password autologin-i seçilmiş PAM qaydaları ilə qəbul edirmi? Ekran kilidi üçün reboot yolu əvəzinə ilk boot parolu tələb olunurmu?
4. Alpha Secure Boot dəstəyi vəd edəcəkmi? Birinci real test cihazları və firmware matrisi hansılardır?
5. Tərcümə terminologiyasına, lisenziya/mənşə inventarına və release imza açarına kim cavabdehdir?
6. Seçilmiş snapshot və toolchain versiyaları hansılar olacaq? Yuxarıda göstərilən paket versiyaları araşdırma anının məlumatıdır, qəbul edilmiş lock deyil.

Növbəti implementasiya yalnız bu təkliflər üzrə scope qərarından sonra ayrıca iş kimi aparılmalıdır. Bu sənəd məhsul dəyişikliyi və ya release icazəsi deyil.
