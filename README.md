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

### Copy Backed Up Home Files
```bash
cp -a ../backup/home/* ~/
```

### Install intel-undervolt from Source
https://github.com/kitsunyan/intel-undervolt
```bash
sudo bash shell-scripts/setup-scripts/intel-undervolt.sh
```

### Install KeePassX from Source
https://www.keepassx.org/
```bash
sudo bash shell-scripts/setup-scripts/keepassx-fedora.sh
```

### Install Firejail from Source
https://firejail.wordpress.com/
```bash
sudo bash shell-scripts/setup-scripts/firejail.sh
```

### Install Source Code Pro font
```bash
bash shell-scripts/miscellaneous/source-code-pro-font.sh
```

### Install Veracrypt
https://www.veracrypt.fr/en/Downloads.html

### Configure i3 to Lock on Suspend
```bash
cp -a backup/etc/systemd/system/i3lock@.service /etc/systemd/system/i3lock@.service
sudo systemctl daemon-reload
sudo systemctl enable i3lock@user.target
```

### Configure Browsers

#### Firefox
* Log into firefox sync
* Set `browser.sessionstore.interval` to `3600000`
* Go through privacytools.io [about:config tweaks](https://www.privacytools.io/browsers/#about_config)
* Change privacy settings

#### Chromium
* Install add-ons: privacy badger, ublock origin, https everywhere
* Change privacy settings

### Install Sublime
https://www.sublimetext.com/
```bash
sudo rpm -v --import https://download.sublimetext.com/sublimehq-rpm-pub.gpg
sudo dnf config-manager --add-repo https://download.sublimetext.com/rpm/stable/x86_64/sublime-text.repo
sudo dnf install sublime-text
```

### Install Atom
https://atom.io/
```bash
cd ~
git clone https://github.com/cameronperot/.atom.git
cd .atom
./atom-setup.sh
```

### Set up lm_sensors
https://github.com/lm-sensors/lm-sensors
```bash
sudo sensors-detect
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

### Install youtube-dl
https://ytdl-org.github.io/youtube-dl/
```bash
sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
sudo chmod a+rx /usr/local/bin/youtube-dl
```

### Install translate-shell
https://github.com/soimort/translate-shell
```bash
git clone https://github.com/soimort/translate-shell.git
cd translate-shell/
make
sudo make install
```

### Install proxychains-ng
https://github.com/rofl0r/proxychains-ng
```bash
git clone https://github.com/rofl0r/proxychains-ng.git
./configure
make
sudo make install
```
