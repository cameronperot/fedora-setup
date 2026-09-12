# Fedora Setup

Useful scripts and snippets for configuring Fedora.

## Usage

```bash
cd ~
git clone https://github.com/cameronperot/fedora-setup.git
cd fedora-setup
./fedora_setup.py --help
```

## Recommended Setup

### intel-undervolt (needs configuring)

Install from [source](https://github.com/kitsunyan/intel-undervolt); see the [Arch Wiki page on undervolting](https://wiki.archlinux.org/title/Undervolting_CPU) for guidance.

```bash
sudo bash shell-scripts/scripts/install_intel_undervolt.sh
```

### VeraCrypt

Download and install from [veracrypt.fr](https://www.veracrypt.fr/en/Downloads.html).

### Browsers

#### Firefox

- Log into Firefox Sync
- Set `browser.sessionstore.interval` to `3600000`
- Go through the [privacytools.io `about:config` tweaks](https://www.privacytools.io/browsers/#about_config)
- Change privacy settings

#### Chromium

- Install add-ons: Privacy Badger, uBlock Origin, HTTPS Everywhere
- Change privacy settings

### lm_sensors

See the [lm-sensors repository](https://github.com/lm-sensors/lm-sensors).

```bash
sudo sensors-detect
```

### Number of Old Kernels to Keep

Set `installonly_limit=n` in `/etc/dnf/dnf.conf` to keep `n` old kernels.

### SDDM Background

Add the following to `/usr/share/sddm/themes/03-sway-fedora/theme.conf`:

```ini
[General]
background=/usr/share/backgrounds/background.png
```

### OpenSnitch

See the [OpenSnitch repository](https://github.com/evilsocket/opensnitch).

### Snapper

```bash
# Triggers hourly snapshots (governed by TIMELINE_CREATE="yes")
sudo systemctl enable --now snapper-timeline.timer

# Triggers scheduled cleanup/pruning (governed by TIMELINE_CLEANUP, NUMBER_CLEANUP, etc.)
sudo systemctl enable --now snapper-cleanup.timer
```

## Manual Configuration

- Cron jobs
- VPN
- NextCloud
- Syncthing

### Fingerprint Login

```bash
sudo authselect enable-feature with-fingerprint
sudo authselect apply-changes
```

### FFMPEG

```bash
sudo dnf swap ffmpeg-free ffmpeg --allowerasing
```

## Framework Laptop 13 (AMD) Fixes

### WiFi

See the [Arch Wiki on the mt7921 driver](https://wiki.archlinux.org/title/Network_configuration/Wireless#mt7921) and this [Framework community thread](https://community.frame.work/t/responded-poor-wi-fi-performance-with-amd-rz616/42901/20).

#### WiFi Backend

Add the following to `/etc/NetworkManager/conf.d/wifi_backend.conf`:

```ini
[device]
wifi.backend=iwd
```

#### WiFi Power Saving

Add the following to `/etc/modprobe.d/mt7921e.conf`:

```bash
options mt7921e disable_aspm=1
```

### Blank Screen on Boot (SDDM)

```bash
sudo grubby --update-kernel=ALL --remove-args="rhgb"
```

### Screen Flickering

```bash
sudo grubby --update-kernel=ALL --args="amdgpu.dcdebugmask=0x10"
sudo grubby --update-kernel=ALL --args="amdgpu.sg_display=0"
sudo grubby --update-kernel=ALL --args="amdgpu.abmlevel=0"
```

To also disable Panel Replay (PR), use `0x410` instead:

```bash
sudo grubby --update-kernel=ALL --args="amdgpu.dcdebugmask=0x410"
sudo grubby --update-kernel=ALL --args="amdgpu.sg_display=0"
sudo grubby --update-kernel=ALL --args="amdgpu.abmlevel=0"
```

## Disable

### PPD

```bash
sudo systemctl enable --now power-profiles-daemon
powerprofilesctl set power-saver
```
