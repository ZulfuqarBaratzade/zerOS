# zerOS

> ⚠️ This project is currently under active development. Not ready for production use.

**zerOS** — [live-build](https://manpages.debian.org/live-build/) vasitəsilə **Debian Trixie (13)** əsasında qurulmuş Linux distributividir. GNOME masaüstü mühiti, xüsusi dark tema, Azərbaycan dili (Azərbaycanca) lokalizasiyası və fərdi Plymouth boot animasiyası ilə gəlir.

**zerOS** is a Linux distribution built on top of **Debian Trixie (13)** using `live-build`. It ships with the GNOME desktop, a custom dark theme, Azerbaijani localization, and a custom Plymouth boot theme.

## Features

- 🎨 **Fərdi brendinq** — xüsusi GRUB menyusu, GDM giriş ekranı, Plymouth boot animasiyası və divar kağızı
- 🇦🇿 **Azərbaycan lokalizasiyası** — `az_AZ.UTF-8` locale, `az,us` klaviatura layout-ları, qismən tərcümə olunmuş GNOME
- 🌙 **Default dark tema** (Adwaita-dark)
- 💻 **Live ISO** — hybrid image (BIOS `syslinux` + UEFI `grub-efi` dəstəyi)
- 🔐 **Təmiz ilk boot** — machine-id, SSH host key-ləri, log-lar build zamanı təmizlənir

## Build

Build bazası: Debian 13 Trixie/amd64. Build yalnız disposable Debian VM-də hazırlanmış pinned mühitdə aparılır.

[VM hazırlıq proseduru](docs/build/vm-preparation.md). ISO build üçün ayrıca başlanğıc göstərişi tələb olunur.

```bash
bash scripts/build.sh --preflight
```

Bu əmr yalnız statik preflight aparır, ISO yaratmır. Gələcək build nəticələri ayrıca `/tmp/zeros-build-...` sahəsində saxlanılır.

## Default istifadəçi

| Sahə | Dəyər |
|------|-------|
| username | `zeros` |
| password | Parol girişi kilidlidir; yalnız qrafik autologin nəzərdə tutulur |

> Məhdud daxili Alpha profili: istifadəçi sudo/adm qruplarında deyil; PolicyKit sorğuları rədd edilir. Wi-Fi, disk və power əməliyyatları məhdudlaşa bilər. GDM/PAM və boot uyğunluğu hələ test edilməyib.

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