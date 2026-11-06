# Build/run ONLY in a disposable VM: live-build requires mount/chroot privileges.
# Caller must supply a verified debian:trixie@sha256:... reference.
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
COPY build/versions.json /opt/zeros/versions.json
ARG BASE_IMAGE
RUN case "$BASE_IMAGE" in debian:trixie@sha256:*) ;; *) echo "Require pinned Debian Trixie digest" >&2; exit 1 ;; esac
# Python is deliberately bootstrapped via APT, not assumed in the base image.
RUN rm -f /etc/apt/sources.list /etc/apt/sources.list.d/debian.sources \
 && printf '%s\n' \
 'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/20261106T000000Z/ trixie main' \
 'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20261106T000000Z/ trixie-security main' \
 > /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
 live-build=1:20250505+deb13u1 debootstrap=1.0.141 \
 python3 git ca-certificates debian-archive-keyring gpgv wget rsync cpio \
 xorriso squashfs-tools dosfstools mtools syslinux-common isolinux \
 grub-pc-bin grub-efi-amd64-bin mount util-linux file \
 && sed -i s,http://snapshot.debian.org,https://snapshot.debian.org,g /etc/apt/sources.list \
 && printf '%s\n' "$BASE_IMAGE" > /etc/zeros-build-environment
WORKDIR /src
ENTRYPOINT ["bash", "scripts/build.sh"]
CMD ["--check-environment"]
