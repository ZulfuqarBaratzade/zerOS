# Limited smoke mount diaqnostikası

Tarix: 2026-11-06. Əsas elevated container yenidən başladılmayıb. Yeni elevated smoke, əlavə capability/device və ISO build aparılmayıb. Mövcud container-lər/fayllar silinməyib; push yoxdur.

## Təsdiqlənmiş nəticələr

- Mövcud container `zeros-mount-smoke-e83d8f1`, ID `2dc71157eafe7703ef68379b80449ddcc42dbe805c38a9102ffb84790492a92f`.
- State exited, exit code **32**, Pid 0, OOMKilled false, State.Error boşdur. Environment check keçib; SMOKE_PASS yoxdur. Şərti mounted flag real mount uğurundan sonra yazıldığı üçün xəta zamanı cleanup umount çağırmayıb.
- Start 2026-11-06 18:14:08.114 UTC (22:14:08.114 Asia/Baku), finish 18:14:08.399 UTC. Tam timestamp log existing-logs.txt-dədir.
- Privileged false, readonly rootfs true, network none, CapDrop ALL, yalnız SYS_ADMIN və SYS_CHROOT, AppArmor docker-default. Seccomp override göstərilməyib; daemon metadata-sında builtin seccomp var. Runtime CapEff və syscall trace əvvəlki run-da yazılmayıb: config capability-nin istəndiyini təsdiqləyir, effektiv dəsti ayrıca qeydə almır.
- Əlavə device mapping yoxdur. /scratch ayrıca 16 MiB tmpfs-dir; /scratch/probe üçün Docker mount/bind təyin edilməyib. mkdir əmri set -e altında keçib: probe əvvəlcədən mövcud olmayıb. Script-də mount komandasının sintaksisi düzgündür. zeros-smoke tmpfs üçün source label-dir, mövcud block device axtarışı tələb etmir.

## Busy ilə permission fərqi

util-linux v2.41.5 libmount kodunda bu konkret “already mounted or mount point busy” mətni EBUSY budağından gəlir; exit 32 isə ümumi mount failure kodudur, errno 32 deyil. EPERM üçün həmin mənbədə ayrıca permission-denied budağı var:
https://raw.githubusercontent.com/util-linux/util-linux/v2.41.5/libmount/src/context_mount.c (1595–1625).

Buna görə hazırkı mətni birbaşa “SYS_ADMIN çatmır” və ya “AppArmor rədd etdi” kimi təqdim etmək düzgün deyil. EBUSY mesajı konkret probe-un əvvəldən mount olduğunu da sübut etmir. util-linux mount(2) və yeni mount API əməliyyatlarını istifadə edə bilər; əvvəlki run dəqiq syscall/errno trace saxlamayıb.

Container stopped olduğundan əvvəlki process mount namespace-i artıq əlçatan deyil (Pid 0). Inspect yalnız başlanğıc konfiqurasiyasıdır, uğursuz syscall anının mountinfo-su deyil. Əvvəlki probe-un həqiqətən busy olmasını retrospektiv təsdiqləmək mümkün olmadı.

## Yalnız privilegesiz əlavə yoxlama

Ayrıca `zeros-smoke-readonly-diag-e83d8f1` container-i saxlanılıb. UID/GID 65534, CapEff/CapBnd 0, no-new-privileges=1, Seccomp=2 və docker-default enforce ilə işləyib. Source/host bind mount yoxdur; yalnız Docker-local tmpfs-lər var. Non-root mkdir üçün /scratch mode=1777 seçilib; bu, köhnə elevated run-un tam replay-i deyil.

- Probe əvvəlcə yoxdur; yaradıldıqdan sonra directory-dir, symlink və mountpoint deyil.
- mountinfo-da yalnız /scratch tmpfs görünür, /scratch/probe üçün entry yoxdur.
- Eyni mount arqumentləri `mount --fake` ilə exit **0** verir; probe sonra da mountpoint deyil. Bu, options/target hazırlığında aşkar sintaktik problem tapmadı, real mount icazəsi və ya kernel uğuru demək deyil.
- Heç bir real mount/chroot istənməyib. Non-root container exit **0**. Tam komanda unprivileged-command.json, çıxış unprivileged-diag.txt-dədir.
- Müvafiq üç saniyəlik kernel journal sorğusu entry qaytarmadı. Dmesg oxuna bildi, lakin scratch/probe, container ID və hadisənin vaxtı ilə uyğun AppArmor/seccomp/audit entry görünmədi. Görünən audit sübutunun olmaması LSM/seccomp ehtimalını qəti istisna etmir.

## Səbəb və ən kiçik dəyişiklik

**Təsdiqlənmiş failure sinfi:** mount/libmount EBUSY nəticəsi; üst səbəb hazırkı sübutlarla müəyyən edilmir. Path preparation və əvvəlcədən mount/busy konflikti yeni privilegesiz mühitdə təkrarlanmadı. Capability və LSM/seccomp problemi də sübut olunmadı. Heç bir permission artırılması əsaslandırılmır.

Ən kiçik əsaslandırılmış dəyişiklik təhlükəsizlik bypass-ı deyil, uğursuz syscall-dan əvvəl mountinfo/effective capabilities/LSM və LIBMOUNT_DEBUG log-u əlavə etməkdir. proposed-diagnostic.patch yalnız review üçündür, orijinal script-ə tətbiq edilməyib. Yeni container/log adı köhnə sübutların üzərinə yazmamaq üçündür. findmnt mövcud mount aşkar edərsə overmount əvəzinə dayanır. Eyni capability, device və security seçimləri saxlanılır.

Bu patch gələcəkdə ayrıca təsdiqlənmiş elevated diaqnostik run üçün lazım olan məlumatı toplayır; mount problemini həll etdiyi iddia edilmir. Path-i dəyişmək, source label-i tmpfs etmək, --privileged əlavə etmək və AppArmor/seccomp-u söndürmək hazırkı faktlarla əsaslandırılmır. Yeni elevated test aparılmayıb. Patch yalnız bash -n ilə sintaksis yoxlamasından keçib.
