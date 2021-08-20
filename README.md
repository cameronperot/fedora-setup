# Fedora Setup
This repository contains useful scripts and snippets I use when configuring Fedora on my workstations.

## Usage
```bash
cd ~
git clone https://github.com/cameronperot/fedora-setup.git
cd fedora-setup
./fedora-setup.sh
```

## Recommended

### Restore dotfiles
```bash
git clone https://github.com/cameronperot/dotfiles
```

### Copy Backed Up Home Files
```bash
cp -a ../backup/home/* ~/
```

### Install intel-undervolt from Source (needs configuring)
https://github.com/kitsunyan/intel-undervolt
https://wiki.archlinux.org/title/Undervolting_CPU
```bash
sudo bash shell-scripts/setup-scripts/intel-undervolt.sh
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

#### Set up temp monitoring for status bar
Place the `cpu_temp1_input` script in `/usr/local/bin` and edit crontab to include:
```bash
@reboot bash /usr/local/bin/cpu_temp1_input
```

### Set Number of Old Kernels to Keep
Change `installonly_limit=n` in `/etc/dnf/dnf.conf` to keep `n` old kernels.

### Import GPG Keys
```bash
gpg --import <PUBLIC_KEY>
gpg --allow-secret-key-import --import <PRIVATE_KEY>
```

## Optional

### Install Mathematica
https://user.wolfram.com/portal/requestSystemTransfer.html
```bash
sudo bash Mathematica_11.0.1_LINUX.sh
```
Set Mathematica screen resolution `SetOptions[$FrontEnd, FontProperties -> {"ScreenResolution" -> 180}]`

#### Mathematica Fix
Requires moving/renaming of `libfreetype.so`, `libfreetype.so.6` and `libz.so` as stated in https://mathematica.stackexchange.com/questions/189306/cant-launch-mathematica-11-on-fedora-29
