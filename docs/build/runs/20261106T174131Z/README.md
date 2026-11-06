# İlk ISO build cəhdi — VM əlçatanlığı gate-i

Status: BLOCKED_VM_UNAVAILABLE. Cari host Kali-dir. İşləyən Build VM və SSH endpoint təsdiqlənməyib. `/dev/vboxdrv` yoxdur; VBoxManage warning mətnində VMs cannot start bildirilirdi. Sandbox xaricində read-only runningvms çağırışı exit 0 ilə boş siyahı qaytardı.

İstifadəçi VM-ə özü qoşulacağını bildirdi. Builder image, environment check, mount/chroot smoke və ISO build başladılmayıb. Yeni ISO və SHA256 yoxdur. Root, driver/paket quraşdırılması və privileged container icra edilməyib. Köhnə ISO/artifact ölçü/mtime uyğunluğu qorunub.

Davam: Debian 13 VM açıldıqdan sonra SSH host/port/operator və uyğun giriş yolu təqdim edilməlidir. Sonra docs/build/vm-preparation.md üzrə patch transferi → builder image → environment check → VM-only smoke → ilk daxili build ardıcıllığı icra olunacaq. İlk xəta ilə dayanılacaq.

Gələcək VirtualBox ISO testi: ayrıca disksiz test VM; ISO optical drive kimi bağlanır; əvvəl BIOS, sonra ayrıca EFI rejimi; zeros graphical autologin, LANG/LANGUAGE/az-us, sudo rəddi, şəbəkə və iki boot machine-id testi. Mövcud ZerosLinux VM-in disk/ISO konfiqurasiyası dəyişdirilməyib.
