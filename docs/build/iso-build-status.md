# Daxili Trixie ISO build statusu

Tarix: 2026-11-06. **BLOCKED: uyğun izolə Debian 13 build mühiti yoxdur.**

Yeni ISO yaradılmayıb: path, ölçü və SHA256 mövcud deyil. `zerOS-Trixie-Alpha.iso` adı altında köhnə ISO kopyalanmayıb və uğur iddiası verilməyib.

Cari host Kali GNU/Linux Rolling-dir. Yalnız Docker default context-i görünür: `unix:///var/run/docker.sock`. Sandbox xaricində read-only `docker info` daemon OS-ni `Kali GNU/Linux Rolling`, OSType-ni linux, architecture-ni x86_64 göstərdi; `docker ps` işləyən container qaytarmadı. Remote Debian endpoint və ya giriş məlumatı yoxdur. Debian container-i Kali daemon-da privileged işlətmək host kernel/mount privilege sərhədini dəyişmir və istifadəçi bunu qadağan edib. Buna görə builder image, privileged smoke və root live-build başladılmayıb. VirtualBox-a müraciət edilməyib.

`bash scripts/build.sh --preflight`: PASS. `python3 -B -m unittest discover -s tests -v`: 18/18 PASS. `--check-environment`: `Missing build dependency: xorriso` ilə rədd edildi. Kali OS özü də dəstəklənən Debian Trixie environment kontraktına uyğun deyil; təkcə çatışmayan paketi hosta quraşdırmaq həll deyil. Paket quraşdırılmayıb.

Repository filesystem-də təxminən 329 GiB boş yer var. Köhnə ISO/cache silinməsinə ehtiyac yoxdur; ilkin artifact ölçü/mtime-ləri qorunub. /tmp tmpfs-dir, təxminən 7.6 GiB boşdur; gələcək real build VM-də çıxış sahəsinin ölçüsü ayrıca uyğun olmalıdır.

## Daxil edilmiş source

- Day 03 foundation: bd806c3ed57c789b1826ebdcf591b5e23eed2f7f.
- Day 04 readiness/sübutlar: d944777 (ayrı commit).
- Locale/live-profile/security və testlər: b75ecae (ayrı commit).
- 26 vendor hash dəyişməyib; Day 04 Trixie müqayisəsi 26/26 eynilik göstərir.
- Live-profile tarixi patch-inin reverse-apply yoxlaması commit-dən əvvəl iş ağacındakı dəyişikliklərlə uyğunluğu təsdiqləyib; yeni source-da həmin düzəlişlər artıq commit edilib, patch yenidən tətbiq edilməməlidir.

## Qalan məlum problemlər

GDM/PAM locked-account autologin, faktiki sudo/PolicyKit, sessiya locale-i və BIOS/UEFI boot test edilməyib. PolicyKit deny Wi-Fi, mount və power əməliyyatlarını məhdudlaşdıra bilər. Binary mərhələsi aktual mirror-lardan istifadə edir; tam snapshot reproducibility iddiası verilmir. Bu source yalnız daxili eksperiment üçündür.

Uyğun Debian 13 build endpoint təqdim olunmadan ISO hasil etmək mümkün deyil. Gələcək uğurlu build-də yalnız yeni run-un ISO-su `zerOS-Trixie-Alpha.iso` adı ilə ayrıca çıxışa kopyalanmalı, ölçü/SHA256 və manifest eyni nəticə qovluğunda saxlanmalıdır. Köhnə `live-image-amd64.hybrid.iso` toxunulmaz qalır.
