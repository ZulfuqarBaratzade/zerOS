# Day 04 doğrulama sübutları

2026-11-06, Asia/Baku. Paket quraşdırılmayıb, downloaded .deb-lər icra edilməyib.

Debian trust chain: hostdakı `/usr/share/keyrings/debian-archive-keyring.gpg` → snapshot InRelease GPG imzaları → main/binary-amd64/Packages.xz SHA256 → paket SHA256 → `dpkg-deb -x` ilə yalnız /tmp-yə çıxarılmış hook-lar.

- Snapshot: https://snapshot.debian.org/archive/debian/20261106T000000Z/
- Index: dists/trixie/main/binary-amd64/Packages.xz
- Paket path-ları və hash-lər: packages-verified.json.
- Security: https://snapshot.debian.org/archive/debian-security/20261106T000000Z/dists/trixie-security/InRelease
- Updates: https://snapshot.debian.org/archive/debian/20261106T000000Z/dists/trixie-updates/InRelease
- Packages.xz və .deb-lər repository-yə əlavə edilməyib; eyni URL-lərdən yenidən alınaraq saxlanmış imzalı index hash-i və package record hash-ləri ilə yoxlanmalıdır. `packages-verified.json` özlüyündə imzalı metadata deyil.
- Əsas imzalar: Debian Archive Automatic Signing Key (13/trixie), Debian Stable Release Key (13/trixie); fingerprint-lər gpgv çıxışındadır. Tarixi metadata Valid-Until yoxlaması ilə cari repo freshness-i təsdiqləmir.

Docker trust chain: TLS ilə Docker Hub `registry-1.docker.io/v2/library/debian/manifests/trixie` → index body SHA256 və Docker-Content-Digest → linux/amd64 descriptor → manifest body SHA256 → config blob SHA256 və os/architecture. `auth.docker.io` anonymous token-i yalnız yaddaşda istifadə edilib və saxlanılmayıb.

Digest-lər image-verified.json daxilindədir; raw index/manifest/config saxlanıb. Image layer-ləri endirilməyib, image run edilməyib; runtime/rootfs uyğunluğu yoxlanmayıb. Registry/TLS mənşə yoxlaması ayrıca publisher signature attestasiyası deyil.

Hook comparison bütün 26 normal/live upstream hook-u əhatə edir. Byte-for-byte uyğunluq runtime uyğunluğu demək deyil. SHA256SUMS bu qovluqdakı alınmış sübutların bütövlüyü üçündür, detached release signature deyil.
