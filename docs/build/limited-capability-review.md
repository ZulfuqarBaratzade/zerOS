# Məhdud capability smoke — icra öncəsi review

Tarix: 2026-11-06. **PREPARED, NOT EXECUTED.** Elevated smoke və ISO üçün icazə verilməyib. Bu sənəddəki əmrlər yalnız review üçündür; heç bir elevated container işə salınmayıb.

## Dəqiq input-lar

- Immutable builder: `sha256:d1bab47128ad1679d1ed00f032c4dedc0517b506913dd823f3b4eb3d689c0789`.
- Source commit: `e83d8f1c9b37aa07e5eb246092add31e5ace4d44`.
- Hazırlanmış clean clone: `/tmp/zeros-smoke-review-zt1_720a/source`.
- Checkout qeydi: `/tmp/zeros-smoke-review-zt1_720a/checkout.json`.
- Clone `--no-local --no-hardlinks` ilə hazırlanıb, detached commit seçilib və `git status --porcelain` boşdur. Əsas iş ağacındakı şəxsi/untracked fayllar, Day 01/02 sənədləri, ISO/cache clone-a daşınmayıb. Clone ayrıca `.git`-ə malikdir; əsas repository-nin `.git` qovluğuna link deyil.
- Host bind kimi yalnız bu xüsusi source altqovluğu `/src`-ə read-only/rprivate veriləcək. Host `/`, `/home`, Docker socket, SSH agent, /dev ağacı və şəxsi qovluqlar mount edilməyəcək. `.git/config` clone-un lokal origin path-ini metadata kimi daşıyır, həmin origin qovluğu container-də mount olunmur.

/tmp-dəki source reboot və ya tmp təmizlənməsi ilə itə bilər; yoxdursa eyni commit-dən yeni clean clone hazırlanmalı və dəqiq komanda yenidən təqdim edilməlidir. Heç bir mövcud checkout/container/volume silinmir.

## Risk və təhlükəsizlik sərhədi

`SYS_ADMIN` geniş capability-dir: yalnız “mount icazəsi” kimi dar təhlükəsizlik sərhədi deyil. Shared Kali kernel-i əlavə attack surface-ə açılır; Debian userspace kernel isolation yaratmır. `SYS_CHROOT` prosesin root dəyişməsinə imkan verir. Read-only source və capability-lərin qalanının çıxarılması riski azaldır, tam host təhlükəsizliyinə zəmanət vermir.

[Docker seccomp](https://docs.docker.com/engine/security/seccomp/) və [AppArmor](https://docs.docker.com/engine/security/apparmor/) siyasətləri saxlanılır. `seccomp=unconfined`, `apparmor=unconfined`, `--privileged`, host PID/network/IPC və wildcard device rule yoxdur. Mövcud daemon metadata-sı AppArmor və builtin seccomp göstərir. `docker-default` mount-u rədd edə bilər; ilk smoke həm də bu sərhədin diaqnostikasıdır. Belə rədd gözlənilən mümkün nəticədir, avtomatik siyasət yumşaltma səbəbi deyil. Xəta olarsa dayanılacaq, log təqdim ediləcək; mount-a uyğun xüsusi AppArmor/seccomp siyasəti ayrıca review və təsdiq tələb edəcək.

## Smoke üçün səlahiyyət və mount cədvəli

| Resurs | Dəqiq seçim / səbəb |
|---|---|
| UID/GID | Container daxilində 0:0; chroot/mount üçün |
| Capabilities | Əvvəl ALL çıxarılır, yalnız SYS_ADMIN və SYS_CHROOT əlavə edilir |
| Devices | Əlavə host device mapping **yoxdur**; Docker-in standart məhdud /dev-i qalır; loop device istifadə edilmir |
| Source | Yalnız xüsusi clean clone → /src, readonly, rprivate |
| Rootfs | Read-only |
| /tmp | Container-local 64 MiB tmpfs, nosuid,nodev,noexec |
| /scratch | Container-local 16 MiB tmpfs, nosuid,nodev,noexec |
| Test mount | /scratch/probe daxilində əlavə 1 MiB tmpfs; host filesystem deyil |
| Network | none |
| Limits | 512 MiB RAM, 128 PID; private cgroup namespace |
| Security | no-new-privileges, docker-default AppArmor, builtin seccomp |
| Saxlanma | --rm yoxdur; uğursuz/stopped container saxlanılır; stdout/stderr xüsusi review qovluğuna tee edilir |

## İcra olunacaq dəqiq smoke komanda

Tam komanda və dəyişməz input-lar [review/limited-smoke.sh](review/limited-smoke.sh) daxilindədir. **Fayl icra edilməyib.** Təsdiqdən sonra yalnız bu script-in icrası nəzərdə tutulur:

```bash
bash /home/baratzade/Desktop/zerOS/docs/build/review/limited-smoke.sh
```

Hostda script yalnız clean SHA/status-u yoxlayır və Docker çağırır; root live-build icra etmir. Container əvvəl environment check aparır, sonra tmpfs mount/read/write/umount və `chroot / /usr/bin/true` yoxlayır. Chroot burada yalnız container-in öz rootfs-i üzərindədir; tam Debian target chroot hazırlığı, debootstrap və loop əməliyyatları yoxlanmır. Uğur üçün həm exit 0, həm `SMOKE_PASS` sətri tələb olunur. Cleanup yalnız test tmpfs-ni unmount edir, heç bir fayl/container silmir.

## Smoke keçərsə ISO üçün minimal-permission namizəd prosedur

**Bu hissə də icra edilməyib və smoke təsdiqi ISO build təsdiqi deyil.** İki capability-li smoke tam live-build üçün minimum dəsti sübut etmir. Aşağıdakı dəst ilk məhdud build cəhdi üçün namizəddir; “təsdiqlənmiş minimum” deyil.

Əlavə capability-lər: CHOWN (target ownership), DAC_OVERRIDE (target fayl girişləri), FOWNER/FSETID (metadata), SETUID/SETGID (target user/group əməliyyatları), SETFCAP (paket file capability-ləri), MKNOD (target device node-ları). SYS_ADMIN/SYS_CHROOT saxlanır. Host block/loop device-ləri və device-cgroup wildcard-ları verilmir. Device və ya syscall lazım olduğu sübut olunarsa build dayanmalı, dəqiq əlavə resurs ayrıca təsdiqə çıxmalıdır.

Build source eyni clean clone-dur. /work üçün **yeni, ayrıca adlı Docker volume** istifadə olunur; host disk/kök qovluğu bind verilmir. TMPDIR=/work sayəsində runner-in unikal iş sahəsi host /tmp tmpfs-inə sığmağa məcbur olmur. Paket download-ları üçün ayrıca default bridge network lazımdır; host networking yoxdur. DNS/HTTPS repo girişi açıq olacaq. Package maintainer script-ləri bu capability-lərlə işləyəcəyinə görə risk smoke-dan daha yüksəkdir.

Aşağıdakı komanda yalnız smoke nəticəsi review edilib ISO üçün ayrıca təsdiq alındıqdan sonra istifadə oluna bilər:

```bash
SOURCE=/tmp/zeros-smoke-review-zt1_720a/source
IMAGE=sha256:d1bab47128ad1679d1ed00f032c4dedc0517b506913dd823f3b4eb3d689c0789
# Volume adı mövcuddursa dayan; köhnə volume silinmir və təkrar istifadə edilmir.
if docker --context default volume inspect zeros-alpha-e83d8f1-work >/dev/null 2>&1; then
  echo 'Volume already exists; select and review a fresh name' >&2
  exit 1
fi
docker --context default volume create zeros-alpha-e83d8f1-work
docker --context default run --name zeros-alpha-e83d8f1-limited \
  --user 0:0 --read-only --network bridge --cgroupns private \
  --cap-drop ALL \
  --cap-add SYS_ADMIN --cap-add SYS_CHROOT \
  --cap-add CHOWN --cap-add DAC_OVERRIDE --cap-add FOWNER --cap-add FSETID \
  --cap-add SETUID --cap-add SETGID --cap-add SETFCAP --cap-add MKNOD \
  --security-opt no-new-privileges --security-opt apparmor=docker-default \
  --pids-limit 2048 --memory 8g \
  --tmpfs /tmp:rw,nosuid,nodev,size=256m \
  --tmpfs /run:rw,nosuid,nodev,noexec,size=64m \
  --mount "type=bind,src=$SOURCE,dst=/src,readonly,bind-propagation=rprivate" \
  --mount type=volume,src=zeros-alpha-e83d8f1-work,dst=/work \
  --env TMPDIR=/work \
  "$IMAGE" --build --allow-container-build
```

8 GiB memory limit hostun RAM ehtiyatı ilə yenidən yoxlanmalıdır; hazırda run edilmədiyindən uyğunluq iddiası yoxdur. Read-only builder rootfs-də əlavə host-tool quraşdırılması lazım olarsa build dayanacaq; image dependency düzəlişi ayrıca ediləcək. AppArmor-un nested target mount-ları rədd etməsi də mümkündür. Heç bir xəta full privileged fallback-a səbəb olmur.

Nəticə çıxarılması üçün build container-i saxlanılır. Gələcək çıxış `docker logs` və `docker cp ...:/work/.` ilə ayrıca artifact qovluğuna kopyalanmalı; result.json, paket manifesti və SHA256SUMS yoxlanmalıdır. Yalnız uğurlu run-un yeni ISO-su `zerOS-Trixie-Alpha.iso` kimi təqdim edilə bilər. Bu review-da ISO və yeni build volume yaradılmayıb.

## Faktiki aparılmış yoxlamalar

Yalnız clean clone hazırlanıb, committed SHA/status və untracked faylların daşınmadığı yoxlanıb. Təklif olunan shell script və sənəddəki shell bloklarına `bash -n` tətbiq edilir; bu əmrləri icra etmir. Elevated smoke, mount, chroot və ISO build **NOT RUN**. Əsas iş ağacının şəxsi dəyişiklikləri saxlanılıb; push və silmə əmri verilməyib.
