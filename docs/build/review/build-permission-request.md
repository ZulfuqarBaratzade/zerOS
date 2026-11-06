# ISO build permission delta — not executed

Smoke: scoped AppArmor + classic mount(2) exited 0 with SMOKE_PASS. New mount API failed move_mount Permission denied; classic API succeeded without reducing protection. Log: ../smoke-diagnostics/scoped-mount2-passed.txt.

Proposed build: same immutable image sha256:d1bab47128ad1679d1ed00f032c4dedc0517b506913dd823f3b4eb3d689c0789 and clean e83d8f1 source checkout. Keep SYS_ADMIN/SYS_CHROOT and add CHOWN,DAC_OVERRIDE,FOWNER,FSETID,SETUID,SETGID,SETFCAP,MKNOD for target package/account/filesystem operations. No new host device, wildcard device rule or privileged mode. Bridge networking replaces network none for signed Debian package downloads.

Proposed named AppArmor policy: build/apparmor/zeros-build. Only tmpfs/proc/sysfs/devpts and bind/remount/propagation operations targeting /work/** are permitted. Existing proc/sys protections remain. This is a candidate scoped policy, not a demonstrated minimum; no block filesystem type is granted. No global profile is changed; docker-default remains intact. Seccomp stays builtin, no-new-privileges remains enabled. Offline parser validation passed; profile NOT loaded.

Use a new Docker-managed volume at /work, set TMPDIR=/work and LIBMOUNT_FORCE_MOUNT2=always, keep image rootfs and source read-only. Only clean source bind, no host /,/home,/dev,Docker socket or SSH agent. Requested resources: 8 GiB memory and 2048 PIDs, private cgroup namespace. Preserve container, volume and all outputs on failure; no automatic privilege/profile/device fallback.

Risk: SYS_ADMIN and target package scripts still share host kernel. The expanded target mount/ownership/user permissions increase attack surface compared with smoke. This permission request must be accepted before profile loading or build run.

Next approved host operation would be: sudo apparmor_parser --add /home/baratzade/Desktop/zerOS/build/apparmor/zeros-build. Currently no load/build has run and no ISO has been created.
