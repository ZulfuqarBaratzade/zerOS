# Kali development host + Debian 13 Docker builder

Tarix: 2026-11-06. Bu qərar əvvəlki məcburi Debian VM siyasətini əvəz edir. Day 04 və əvvəlki bloklanmış build qeydləri tarixi nəticələrdir; indiki image/environment yoxlamasının nəticəsi aşağıdadır. ISO build hələ aparılmayıb.

## Host və container sərhədi

Əvvəlki `scripts/build.py --check-environment` əslində icra olunduğu userspace-in `/etc/os-release` faylını yoxlayırdı. Kali hostda onu birbaşa çağırmaq Kali-ni yoxlayırdı; Docker container daxilində isə Debian-ı yoxlayır. VM tələbi həmin yoxlamanın mətnində və workflow sənədlərində idi; Linux host distributivinin mütləq Debian olması Docker userspace üçün texniki tələb deyil.

İndi:

- Host check: `scripts/docker-builder.py` Linux/amd64, explicit local Unix Docker context, işlək Linux/amd64 daemon və təhlükəsizlik metadata-sını yoxlayır. Kali qəbul edilir; hosta paket quraşdırılmır, sysctl/LSM və Docker ayarları dəyişdirilmir.
- Container check: Debian Trixie userspace, amd64, Docker marker-i, environment lock eyniliyi, bütün tələb olunan əmrlər və dəqiq live-build/debootstrap versiyaları tələb olunur. Host OS yoxlaması burada təkrarlanmır.
- Docker shared-kernel modelidir: Debian userspace Kali kernel-ini dəyişmir. Image/environment check-in uğuru mount/chroot/loop/boot uyğunluğunu təsdiqləmir.
- `build.py --build` əlavə `--allow-container-build` acknowledgement tələb edir; bu flag capability vermir və istifadəçinin ayrıca təsdiqini əvəz etmir. Root icrası container daxilində olmalıdır. Yeni host wrapper-də build və smoke action ümumiyyətlə yoxdur.

## İcra edilmiş nəticə

- Builder image **uğurla yaradıldı**: `zeros-builder:trixie`.
- Immutable image ID: `sha256:d1bab47128ad1679d1ed00f032c4dedc0517b506913dd823f3b4eb3d689c0789`.
- Base: `debian:trixie@sha256:bfc36aecdece0387418759dba474aa856c026ca8087da3606b41b90ab0509c99`.
- Image daxilində live-build `1:20250505+deb13u1`, debootstrap `1.0.141` və digər tələb olunan dependency-lər quraşdırıldı. Host paketləri dəyişdirilmədi.
- Read-only filesystem, UID/GID 65534, `--cap-drop=ALL`, `no-new-privileges`, network none, 512 MiB memory və 128 PID limiti ilə **environment check keçdi**. /tmp yalnız 64 MiB məhdud tmpfs-dir. Source bind read-only-dir; Docker socket container-ə verilməyib.
- 21/21 unit test və statik preflight keçib.
- `--privileged`, mount/chroot smoke və ISO build **işlədilməyib**.
- Image recipe-də məcburi BASE_IMAGE ARG üçün BuildKit `InvalidDefaultArgInFrom` warning verdi; explicit pinned argument ilə build uğurlu oldu. Floating base fallback yoxdur.

[Image build log](kali-docker-evidence/image-build.txt), [environment log](kali-docker-evidence/environment-check.txt), [nəticə](kali-docker-evidence/result.json), [host metadata](kali-docker-evidence/docker-host.json), [image summary](kali-docker-evidence/builder-image-summary.json).

## Təkrar istifadə əmrləri — ISO yaratmır

Repository kökündə, local Docker socket-ə icazəsi olan operator üçün:

```bash
bash scripts/build.sh --preflight
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/docker-builder.py host-check
python3 scripts/docker-builder.py prepare
python3 scripts/docker-builder.py check
```

`prepare` standart Docker image build edir, sonra sərtləşdirilmiş privilegesiz environment check aparır. Heç bir xəta privilegesiz run-dan privileged run-a avtomatik keçid yaratmır. Image tag inspect-dən sonra immutable ID ilə işlədilir. Hər action `/tmp/zeros-docker-check-...` daxilində log və result.json saxlayır. Docker daemon storage-da image/cache yaranır; köhnə zerOS ISO/cache silinmir. Source context `.dockerignore` ilə yalnız Dockerfile və lock-a məhdudlaşdırılıb.

Bu yoxlamada source bind bütün repository-ni read-only göstərir, lakin container non-root, şəbəkəsiz və capability-sizdir. Gələcək elevated run üçün ayrıca təmiz committed checkout istifadə edilməli, şəxsi/untracked fayllar və köhnə artifact-lər paylaşılmamalıdır. Rootful Docker socket-ə giriş host root-a yaxın etibar tələb edir; istifadəçini docker qrupuna avtomatik əlavə edən kod yoxdur.

## Privileged run riski və alternativlər

[Docker runtime privilege sənədi](https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities) privileged rejimin bütün capability-ləri, cihaz girişini və zəifləmiş LSM məhdudiyyətlərini verdiyini izah edir. Debian image bu riski aradan qaldırmır. Zərərli hook/paket skripti host storage-a və kernel attack surface-ə çata bilər; source-un read-only olması tam təhlükəsizlik sərhədi deyil. Docker socket, host /dev, /, /home və SSH agent paylaşılmamalıdır.

| Variant | Qiymətləndirmə |
|---|---|
| Standart Docker image/environment yoxlaması | İcra edilib və keçib; ISO build üçün lazımi mount imkanlarını vermir |
| Yalnız tələb olunan capability/device-lər | SYS_ADMIN/SYS_CHROOT və ehtiyac yaranarsa dəqiq loop device mapping araşdırıla bilər. SYS_ADMIN özü geniş səlahiyyətdir; AppArmor/seccomp policy-si ayrıca audit edilməlidir. Minimum işlək dəst hələ test edilməyib; geniş unconfined fallback avtomatik verilməsin |
| Rootless Docker / user namespaces | [Docker rootless](https://docs.docker.com/engine/security/rootless/) host root riskini azaldır. live-build mount/device tələbləri burada avtomatik həll olunmur; yeni pipeline və test tələb edə bilər |
| mmdebstrap/fakechroot + userspace image assembly | Daha az privilege üçün araşdırma namizədidir; mövcud live-build-in drop-in təsdiqlənmiş əvəzi deyil |
| Bir dəfə qurulmuş disposable VM və ya remote worker | Kernel sərhədini ayıran güclü alternativdir; hər build üçün yeni VM yaratmaq məcburi deyil, snapshot bərpası istifadə oluna bilər. Əsas workflow üçün tələb deyil |
| Full privileged Docker | Rahat, lakin Kali hostuna geniş təsir riski var; **ayrıca təsdiqsiz qadağandır** |

## Növbəti gate — ayrıca qərar tələb edir

1. İstifadəçi risk profilini seçməli: məhdud capability sınağı, ayrıca worker və ya full privileged smoke.
2. Elevated smoke üçün konkret immutable image, mount/device/capability siyahısı və təmiz source planı göstərilib ayrıca təsdiq alınmalıdır. Cari task bu icazəni vermir.
3. Smoke uğurlu olarsa ISO build ayrıca scope/başlanğıc göstərişi ilə aparılır; build result/log və paket manifesti saxlanılır. Kernel/rootfs uyğunluğu həmin zaman ölçülür.
4. Source çıxışları və nəticələr disk üzərində ayrıca sahədə saxlanmalıdır; host /tmp tmpfs-i tam ISO üçün uyğun ölçüdə olmaya bilər. Hazırkı wrapper yalnız kiçik image/environment log-larını /tmp-də saxlayır.

Locale/live-profile dəyişiklikləri qorunub. PolicyKit deny/GDM/PAM və real boot testləri hələ açıqdır. Binary mərhələsində aktual mirror istifadə olunduğu üçün tam snapshot və bit-identical ISO iddiası verilmir. Köhnə ISO yeni image uğuruna görə hazır ISO sayılmır.

## Artifact inventarı üzrə müşahidə

Son yoxlamada əvvəlki inventardakı `live-image-amd64.hybrid.iso` repository kökündə tapılmadı. Bu task-da host ISO/artifact-lərini silən və ya köçürən əmr icra edilməyib; faylın başqa proses tərəfindən daşınıb/silinməsi müəyyən edilməyib. Kökdəki chroot.files, chroot.packages.install/live, live-image-amd64.contents/files/packages və binary.modified_timestamps də tapılmadı. Mövcud binary/cache/chroot/.build/local qovluqlarının metadata-sı dəyişməyib; daxilindəki bütün fayllar rekursiv hash edilməyib. Yeni ISO yaradılmayıb.
