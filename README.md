# Fedora Setup
This repository contains useful scripts and snippets I use when configuring Fedora on my workstations.

## Usage
```bash
cd ~
git clone https://github.com/cameronperot/fedora-setup.git
cd fedora-setup
```
```bash
./fedora_setup.py --help
```

## Recommended

### Install intel-undervolt from Source (needs configuring)
https://github.com/kitsunyan/intel-undervolt
https://wiki.archlinux.org/title/Undervolting_CPU
```bash
sudo bash shell-scripts/scripts/install_intel_undervolt.sh
```

### Install Veracrypt
https://www.veracrypt.fr/en/Downloads.html

### Configure xfce-notifyd
https://forum.xfce.org/viewtopic.php?id=14228

### Configure Browsers

#### Firefox
* Log into firefox sync
* Set `browser.sessionstore.interval` to `3600000`
* Go through privacytools.io [about:config tweaks](https://www.privacytools.io/browsers/#about_config)
* Change privacy settings

#### Chromium
* Install add-ons: privacy badger, ublock origin, https everywhere
* Change privacy settings

### Set up lm_sensors
https://github.com/lm-sensors/lm-sensors
```bash
sudo sensors-detect
```

### Set Number of Old Kernels to Keep
Change `installonly_limit=n` in `/etc/dnf/dnf.conf` to keep `n` old kernels.

### Set the background for SDDM
Add the following to `/usr/share/sddm/themes/03-sway-fedora/theme.conf`.
```
[General]
background=/usr/share/backgrounds/background.png
```

### Additional Manual Configuration
- VPN
- NextCloud
- Syncthing
