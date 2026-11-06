# Day 03 final review

Branch: `codex/day03-trixie-build-foundation`. Review tarixi: 2026-11-06.

## Diff və scope

`git status`, tracked diff, bütün yeni Day 03 faylları və boş başlanğıc index yoxlanılıb. auto/config Trixie/amd64/bootloader seçimlərini açıq edir; build.sh dağıdıcı in-place clean/build əvəzinə ayrıca sahədə işləyən runner çağırır. 26 hook üçün dəyişiklik məzmun redaktəsi deyil, Git mode 120000 symlink-dən 100755 lokal fayla keçiddir. Lock, image recipe, lisenziya, test və provenance sənədləri əlavə edilir.

### Yeni Day 03 faylları (11)

- `.dockerignore`
- `build/Dockerfile`
- `build/GPL-3.txt`
- `build/hooks.lock.json`
- `build/live-build.COPYRIGHT`
- `build/versions.json`
- `scripts/build.py`
- `tests/test_build_foundation.py`
- `docs/build/day03-foundation.md`
- `docs/build/day03-inventory.json`
- `docs/build/day03-final-review.md`

### Dəyişdirilmiş Day 03 faylları (28)

- `auto/config`
- `scripts/build.sh`
- `config/hooks/live/0010-disable-kexec-tools.hook.chroot`
- `config/hooks/live/0050-disable-sysvinit-tmpfs.hook.chroot`
- `config/hooks/normal/1000-create-mtab-symlink.hook.chroot`
- `config/hooks/normal/1010-enable-cryptsetup.hook.chroot`
- `config/hooks/normal/1020-create-locales-files.hook.chroot`
- `config/hooks/normal/5000-update-apt-file-cache.hook.chroot`
- `config/hooks/normal/5010-update-apt-xapian-index.hook.chroot`
- `config/hooks/normal/5020-update-glx-alternative.hook.chroot`
- `config/hooks/normal/5030-update-plocate-database.hook.chroot`
- `config/hooks/normal/5040-update-nvidia-alternative.hook.chroot`
- `config/hooks/normal/5050-dracut.hook.chroot`
- `config/hooks/normal/8000-remove-adjtime-configuration.hook.chroot`
- `config/hooks/normal/8010-remove-backup-files.hook.chroot`
- `config/hooks/normal/8020-remove-dbus-machine-id.hook.chroot`
- `config/hooks/normal/8030-truncate-log-files.hook.chroot`
- `config/hooks/normal/8040-remove-mdadm-configuration.hook.chroot`
- `config/hooks/normal/8050-remove-openssh-server-host-keys.hook.chroot`
- `config/hooks/normal/8060-remove-systemd-machine-id.hook.chroot`
- `config/hooks/normal/8070-remove-temporary-files.hook.chroot`
- `config/hooks/normal/8080-reproducible-glibc.hook.chroot`
- `config/hooks/normal/8090-remove-ssl-cert-snakeoil.hook.chroot`
- `config/hooks/normal/8100-remove-udev-persistent-cd-rules.hook.chroot`
- `config/hooks/normal/8110-remove-udev-persistent-net-rules.hook.chroot`
- `config/hooks/normal/9000-remove-gnome-icon-cache.hook.chroot`
- `config/hooks/normal/9010-remove-python-pyc.hook.chroot`
- `config/hooks/normal/9020-remove-man-cache.hook.chroot`

## Qorunan və commit-dən çıxarılan fayllar

- `.gitignore`: əvvəlki diff yalnız boş sətrin `Road.md` ilə əvəz edilməsidir. SHA256: `300d00bd404aed56e880f2d2b978751e5613e9a65cd5c2a9f69e2dd451773d8f`.
- `config/common`: əvvəlki diff yalnız regenerasiya şərhinin silinməsidir. SHA256: `5d5b9784b0284a4a353a016b60c8d64fd83d603aa8d9f9b9360e01b6c8b714b3`.
- `docs/audits/2026-11-06-technical-audit.md` və `docs/planning/2026-11-07-alpha-decisions.md`: əvvəlki untracked sənədlərdir; stage/commit siyahısında yoxdur.
- Köhnə ISO və inventardakı digər artifact-lərin ölçü/mtime göstəriciləri ilkin inventarla uyğun gəlir; directory ağacının bütün məzmununa hash hesablanmayıb.

## Yoxlamaların nəticəsi

- Hook sayı və SHA256: **26/26 keçdi**. Fayllar lokal regular fayllardır; hazırda əvvəlki host hədəfləri ilə də byte-for-byte eynidir. Bu, Trixie upstream uyğunluğu deyil.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: **6/6 keçdi**.
- `bash scripts/build.sh --preflight`: **keçdi**. Başqa çalışma qovluğundan absolute script çağırışı da yoxlanır.
- `bash -n`: auto/config, build.sh və 31 hook üçün **33/33 keçdi**.
- Python mənbələrinin yaddaşda compile yoxlaması: **keçdi**, pycache yazılmadı.
- `git diff --check`: **keçdi**; stage sonrası `git diff --cached --check` də commit-dən əvvəl tələb olunur.
- `--check-environment`: **uğurlu deyil**, `Missing build dependency: xorriso` ilə dayandı. Sonrakı environment yoxlamaları işləmədiyindən OS/marker/versiya uyğunluğu təsdiqlənmir.
- Docker build/lint tool, snapshot paket həlli, root/mount, tam ISO build və boot testləri aparılmayıb. Dockerfile/lock uyğunluq testi Docker build testi deyil.

## Trixie hook müqayisəsi üçün açıq yoxlamalar

1. Dəqiq `live-build 1:20250505+deb13u1` Debian paketini imzalanmış archive metadata/hash vasitəsilə doğrulayıb izolə sahəyə çıxarmaq; bu review-da paket endirilməyib və çıxarılmayıb.
2. Trixie paketinin normal/live hook inventarını bu 26 faylla müqayisə etmək: əlavə/silinmiş/adı dəyişmiş hook-lar, məzmun, executable mode və copyright fərqləri.
3. Hər fərqin funksional təsirini review etmək; xüsusən 1020 locale reset, 8020/8050/8060 ID/key təmizliyi, 5050 dracut və 8090 sertifikat sanitizasiyası.
4. Seçilmiş Trixie `lb config`-in vendor faylları saxladığını, gözlənilməyən əlavə link/hook yaratmadığını və bütün hook icra sırasını yoxlamaq. Hazırkı post-config hash testi yalnız lock-da olan 26 path-i yoxlayır; əlavə hook-lar üçün tam inventar müqayisəsi hələ yoxdur.
5. Məlum dəyişiklikləri versiyalı diff/əsaslandırma ilə qeydə almaq; yalnız review-dan sonra import mənşəyini və lock-u yeniləmək. Kali məzmununu Trixie mənşəli kimi yenidən etiketləməmək.

## Qalan risklər

- Vendor hook-lar host asılılığından çıxarılıb, lakin Kali mənşəli davranışın Debian Trixie uyğunluğu test edilməyib.
- Konkret base-image digest seçilməyib; snapshot-da pinned paket həlli və HTTPS bootstrap/live-build davranışı təsdiqlənməyib. Bit-identical ISO zəmanəti yoxdur.
- Disposable copy-də generated config-in yenidən yaradılması əvvəlki ISO metadata/cache/Secure Boot default-larını dəyişə bilər; resolved-config diff və boot matrisi tələb olunur.
- Unit testlər tam build, manifest/log uğur-xəta yollarını və container privilege sərhədini icra etmir. Setup metadata yazılması try/finally-dən əvvəl uğursuz ola bilər; uzun build-in interruption/process cleanup davranışı ayrıca test edilməlidir.
- Locale konflikti, məlum default istifadəçi/sudo siyasəti və GDM/translation problemləri scope-a uyğun olaraq saxlanılıb. Bu commit public təhlükəsiz Alpha buraxılışı deyil.
- Privileged Docker yalnız disposable VM daxilində planlaşdırılıb; marker təkbaşına həqiqi izolə mühit attestasiyası deyil. Nəticələr /tmp-dən daimi storage-a köçürülməlidir.

Yalnız yuxarıdakı Day 03 allowlist stage/commit edilməlidir. Push, paket install, root build və artifact silinməsi bu review-a daxil deyil. Commit SHA commit yaradıldıqdan sonra istifadəçiyə ayrıca təqdim edilir.
