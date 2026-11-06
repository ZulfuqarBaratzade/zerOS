# zerOS Trixie Alpha — daxili eksperimental build

Build exit code: 0. Status: BUILD_SUCCESS_BOOT_UNTESTED.

ISO: `/home/baratzade/Desktop/zerOS/artifacts/zeros-alpha-20261106t183343z/zerOS-Trixie-Alpha.iso`  
Ölçü: 1944256512 bayt (1.811 GiB).  
SHA256: `0381f91cadebc5355fd66c494185fafc352b1221ae10a225dbeef3776255ddc6`  
Source: `e83d8f1c9b37aa07e5eb246092add31e5ace4d44`.

Build log, console.log, paket manifesti, host-packages.tsv, Docker run parametrləri və SHA256SUMS bu qovluqdadır. ISO/Git cache stage və push edilməyib. Container və Docker volume saxlanılıb; heç bir köhnə ISO-nun üzərinə yazılmayıb.

ISO BIOS/UEFI El Torito boot qeydləri və hybrid partition strukturu xorriso ilə oxunub. Squashfs daxilində LANG=az_AZ.UTF-8, LANGUAGE=az:en, zeros UID/GID 1000, root/zeros parol sahələri !, boş supplemental group siyahısı və boş machine-id yoxlanıb. Bu statik nəticələr boot və ya GDM/PAM uğuru deyil.

Məlum məhdudiyyətlər: PolicyKit deny bəzi şəbəkə/disk/power axınlarını bloklaya bilər; GNOME tərcüməsi qisməndir; ISO volume label Debian trixie olaraq qalır; squashfs POSIX ACL xattr prefix warning verib. Yalnız daxili test üçün, public release deyil.

VirtualBox testini istifadəçi aparacaq: ayrıca test VM-də ISO optical disk kimi seçilir; BIOS və sonra ayrıca EFI rejimində boot, zeros qrafik autologin, az/us klaviatura, locale, sudo rəddi və əsas desktop axınları yoxlanmalıdır. Host şəxsi diskləri test VM-yə əlavə edilməsin. Secure Boot uyğunluğu təsdiqlənməyib.
