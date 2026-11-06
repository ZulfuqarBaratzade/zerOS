# Mount API failure — concrete permission gate

Yeni diaqnostika əvvəl təsdiqlənmiş eyni SYS_ADMIN/SYS_CHROOT və docker-default/seccomp ilə icra edildi; exit 32. Əlavə capability və device verilməyib, ISO başlamayıb.

CapEff/CapBnd 0x240000: SYS_ADMIN və SYS_CHROOT effektivdir. Mountinfo-da /scratch/probe yoxdur. fsopen/tmpfs, fsconfig və fsmount keçir; mount_setattr keçir; move_mount(to=/scratch/probe) Permission denied verir. util-linux bundan sonra read-only retry edir və fsconfig Device or resource busy qaytarır. Son EBUSY mesajı ilkin permission failure-ı maskalayır. Tam log mount-api-debug.txt daxilindədir.

AppArmor enforce-dadır; görünən audit entry yoxdur. Buna görə AppArmor ən əsas şübhədir, amma audit trace olmadan tək günahkar olduğu təsdiqlənmir. Mövcud default siyasətini söndürmək əvəzinə ayrıca named profil hazırlanıb: build/apparmor/zeros-smoke. Mount üçün yalnız tmpfs -> /scratch/probe/ və həmin path-in umount-u icazəlidir; proc/sys qoruma qaydaları saxlanır. Bu default-like xüsusi profildir, daemon-un yüklənmiş profilinin byte-for-byte surəti deyil.

Offline `apparmor_parser --skip-kernel-load --skip-cache` keçdi; profil kernel-ə yüklənməyib. scoped-policy-smoke.sh də yalnız bash -n yoxlamasından keçib, run edilməyib. Profilin özünü və konkret run-u review etmək lazımdır.

Təsdiq tələb edən iki dəqiq əməliyyat:

1. Hostda yeni profili əlavə etmək: `sudo apparmor_parser --add /home/baratzade/Desktop/zerOS/build/apparmor/zeros-smoke` (mövcud docker-default dəyişmir; eyni named profile artıq varsa add uğursuz olmalı və avtomatik replace edilməməlidir).
2. `bash /home/baratzade/Desktop/zerOS/docs/build/review/scoped-policy-smoke.sh` — eyni image/source/capabilities/devices, yalnız AppArmor named profile seçimi dəyişir; yeni container/log adı köhnələri qoruyur.

Bu profil tam ISO build mount-larını açmır və smoke approval ISO üçün əlavə capability icazəsi deyil. Uğurlu olsa belə build üçün daha geniş /work daxilində mount və target package əməliyyatları ayrıca review ediləcək. SYS_ADMIN shared host kernel riskini saxlayır; seccomp deaktiv edilməyəcək. Heç bir profil yükləmə/siyasət yumşaltma, privileged run, fayl silmə və push bu mərhələdə aparılmayıb.
