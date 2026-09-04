# zerOS

> ⚠️ This project is currently under active development. Not ready for production use.

**zerOS** — [live-build](https://manpages.debian.org/live-build/) vasitəsilə **Debian Bookworm (12)** əsasında qurulmuş Linux distributividir. GNOME masaüstü mühiti, xüsusi dark tema, Azərbaycan dili (Azərbaycanca) lokalizasiyası və fərdi Plymouth boot animasiyası ilə gəlir.

**zerOS** is a Linux distribution built on top of **Debian Bookworm (12)** using `live-build`. It ships with the GNOME desktop, a custom dark theme, Azerbaijani localization, and a custom Plymouth boot theme.

## Features

- 🎨 **Fərdi brendinq** — xüsusi GRUB menyusu, GDM giriş ekranı, Plymouth boot animasiyası və divar kağızı
- 🇦🇿 **Azərbaycan lokalizasiyası** — `az_AZ.UTF-8` locale, `az,us` klaviatura layout-ları, qismən tərcümə olunmuş GNOME
- 🌙 **Default dark tema** (Adwaita-dark)
- 💻 **Live ISO** — hybrid image (BIOS `syslinux` + UEFI `grub-efi` dəstəyi)
- 🔐 **Təmiz ilk boot** — machine-id, SSH host key-ləri, log-lar build zamanı təmizlənir

## Build

Tələblər: Debian-based sistem, root icazəsi və `live-build` paketi.

```bash
sudo apt install live-build debootstrap
sudo bash scripts/build.sh
```

Nəticə fayl: `live-image-amd64.hybrid.iso`

## Default istifadəçi

| Sahə | Dəyər |
|------|-------|
| username | `zeros` |
| password | `zeros` |

> İstifadəçi `sudo` qrupundadır.

## Layihə strukturu

| Yol | Məqsəd |
|-----|--------|
| `auto/config` | `lb config` giriş nöqtəsi |
| `config/package-lists/` | Paket siyahıları (desktop, live) |
| `config/hooks/` | Fərdi build hook-ları (`normal`, `live`) |
| `config/includes.chroot/` | Root fayl sisteminə köçürülən fayllar (GRUB, GDM, tema, tərcümələr) |
| `scripts/build.sh` | Tək əmrlə build skripti |

## Yol xəritəsi (Roadmap)

- [x] Əsas live ISO (Debian Bookworm + GNOME)
- [x] Fərdi brendinq (divar kağızı, Plymouth, GRUB, GDM)
- [x] Azərbaycan locale-i və qismən GNOME tərcüməsi
- [ ] GNOME-un tam Azərbaycanca tərcüməsi
- [ ] Quraşdırıcı (məs. Calamares)
- [ ] Paket meneceri / yeniləmə sistemi
- [ ] CI/CD avtomatik build (GitHub Actions)