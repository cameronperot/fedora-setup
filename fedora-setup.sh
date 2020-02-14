#!/usr/bin/env bash
set -eu -o pipefail

# Ensure script is run as root
if [ "$USER" != "root" ]
then
	echo "You must run this script as root!"
	exit 1
fi

# Username, SSH keys, and location of user's home directory
new_user=user
home_dir=/home/$new_user
setup_dir=$home_dir/setup

# Copy over bash aliases
cp -a $setup_dir/home/. $home_dir/
chown -R $new_user:$new_user $home_dir

# Set up the new user's ~/.ssh directory and authorized_keys
mkdir $home_dir/.ssh
chmod 700 $home_dir/.ssh
cp -a $setup_dir/home/.ssh/. $home_dir/.ssh/
chmod 600 $home_dir/.ssh/*
chmod 644 $home_dir/.ssh/*.pub
chown -R $new_user:$new_user $home_dir/.ssh

# Edit the moduli file to remove small primes
awk '$5 > 2000' /etc/ssh/moduli > "${HOME}/moduli"
wc -l "${HOME}/moduli"
mv "${HOME}/moduli" /etc/ssh/moduli

# # Replace sshd_config and ssh_config files
cp $setup_dir/etc/ssh/*_config /etc/ssh/
chmod 644 /etc/ssh/*_config

# Remove/install packages
dnf erase -y \
	galculator \
	pragha \
	parole \
	enumerator \
	abiword \
	claws-mail \
	geany xfburn \
	xscreensaver-base \
	gnumeric \
	orage \
	asunder
dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
dnf upgrade -y
dnf install -y \
	iptables-services \
	rsync \
	htop \
	tmux \
	ncdu \
	git \
	vim \
	nload \
	wireshark \
	fakeroot \
	make \
	automake \
	gcc \
	gcc-c++ \
	libtool \
	curl \
	ca-certificates \
	VirtualBox \
	kernel-devel \
	light-locker \
	vlc \
	lm_sensors \
	gimp \
	qalculate-gtk \
	redshift-gtk \
	pidgin \
	pidgin-otr \
	hexchat \
	texlive-scheme-basic \
	texlive-collection-latexextra \
	dvipng \
	pandoc \
	chromium \
	libreoffice \
	transmission-gtk \
	p7zip \
	p7zip-plugins \
	gvfs-mtp \
	perl-Image-ExifTool \
	ImageMagick \
	soundconverter \
	hdf5-devel \
	libgnome-keyring

# Enable tlp if laptop arg
if [ "$1" == "laptop" ]
then
	dnf install -y install tlp tlp-rdw powertop
fi

# Copy over OpenVPN files
cp -a $setup_dir/etc/openvpn/. /etc/openvpn/
chmod -R 400 /etc/openvpn/client/*.crt
chmod -R 400 /etc/openvpn/client/*.key
chmod -R 600 /etc/openvpn/client/*.auth
chmod -R 644 /etc/openvpn/client/*.ovpn
chown -R root:openvpn /etc/openvpn

# Configure Networking and DNS
cp $setup_dir/etc/NetworkManager/NetworkManager.conf /etc/NetworkManager/NetworkManager.conf
chmod 644 /etc/NetworkManager/NetworkManager.conf
cp $setup_dir/etc/resolv.conf /etc/resolv.conf
chmod 644 /etc/resolv.conf

# Disable IPv6
cat <<EOT >> /etc/sysctl/sysctl.d/99-sysctl
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
EOT

# Enable iptables if arg
if [ "$2" == "iptables" ]
then
	cp $setup_dir/etc/sysconfig/ip*tables /etc/sysconfig/
	chmod 600 /etc/sysconfig/ip*tables
	systemctl disable firewalld
	systemctl enable iptables
	systemctl enable ip6tables
	systemctl stop firewalld
	systemctl start iptables
	systemctl start ip6tables
fi
