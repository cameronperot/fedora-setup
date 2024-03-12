#!/usr/bin/env python3

import logging
from pathlib import Path
from subprocess import run


class FedoraSetup:
    def __init__(
        self,
        rsync_dir,
        backup_dir=None,
        user="user",
        install_tlp=False,
        julia_version=None,
    ):
        # Set attributes
        self.user = user
        self.rsync_dir = Path(rsync_dir)
        self.home_dir = Path(f"/home/{user}")
        self.script_dir = Path(__file__)
        self.install_tlp = install_tlp
        self.julia_version = julia_version

        # Set backup directory (contains home and etc subdirectories)
        if backup_dir is None:
            backup_dir = self.rsync_dir / "nix/fedora/backup"
        self.backup_dir = backup_dir

        # Ensure directories exist
        assert self.home_dir.exists()
        assert self.rsync_dir.exists()
        assert self.backup_dir.exists()
        assert self.julia_version is not None

        # Get the fedora version (used for adding repos)
        self.fedora_version = run(
            ["rpm", "-E", "%fedora"], capture_output=True, check=True, encoding="ascii"
        ).stdout.strip()

        # Configure the logger
        self._configure_logger()

    def configure_packages(self):
        self.log.info("----------------------------------------")
        self.log.info("Configuring packages")
        self.log.info("----------------------------------------")

        # Get packages to erase/install from list files
        with open(self.script_dir / "erase_packages.list", "r") as f:
            erase_packages = [x.strip() for x in f.readlines() if x.strip()]
        with open(self.script_dir / "install_packages.list", "r") as f:
            install_packages = [x.strip() for x in f.readlines() if x.strip()]

        rpm_fusion_urls = [
            f"https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-{self.fedora_version}.noarch.rpm",
            f"https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{self.fedora_version}.noarch.rpm",
        ]

        # Erase packages
        self.log.info("Erasing packages")
        run(["sudo", "dnf", "erase", "-y", *erase_packages], check=True)
        # Install rpm fusion
        self.log.info("Installing RPM Fusion")
        run(["sudo", "dnf", "install", "-y", *rpm_fusion_urls], check=True)
        # Upgrade packages
        self.log.info("Upgrading packages")
        run(["sudo", "dnf", "upgrade", "-y"], check=True)
        # Install packages
        self.log.info("Installing packages")
        run(["sudo", "dnf", "install", "-y", *install_packages], check=True)

        # Install tlp
        if self.install_tlp:
            run(
                ["sudo", "dnf", "install", "-y", "tlp", "tlp-rdw", "powertop"],
                check=True,
            )

    def configure_etc(self):
        self.log.info("----------------------------------------")
        self.log.info("Configuring /etc")
        self.log.info("----------------------------------------")

        # Copy over config files
        self.log.info("Copying over config files")
        config_files = [
            "/etc/ssh/ssh_config",
            "/etc/ssh/sshd_config",
            "/etc/intel-undervolt.conf",
            "/etc/systemd/system/i3lock.service",
        ]
        for config_file in config_files:
            run(
                ["sudo", "cp", "-a", self.backup_dir / config_file[1:], config_file],
                check=True,
            )
            run(["sudo", "chown", "root:root", config_file], check=True)
            run(["sudo", "chmod", "644", config_file], check=True)
            run(["sudo", "restorecon", config_file], check=True)

        # Enable i3lock on sleep
        run(["sudo", "systemctl", "daemon-reload"], check=True)
        run(["sudo", "systemctl", "enable", "i3lock"], check=True)

        # Remove small primes from SSH moduli
        self.log.info("Removing small primes from SSH moduli")
        moduli_fix = """
            awk '$5 > 3000' /etc/ssh/moduli > "${HOME}/moduli"
            wc -l "${HOME}/moduli"
            sudo mv -f "${HOME}/moduli" /etc/ssh/moduli
            sudo chown root:root /etc/ssh/moduli
            sudo chmod 644 /etc/ssh/moduli
        """
        run(moduli_fix, shell=True, check=True)

    def configure_home(self):
        self.log.info("----------------------------------------")
        self.log.info(f"Configuring {self.home_dir}")
        self.log.info("----------------------------------------")

        # Copy over user files
        self.log.info("Copying over user files")
        run(
            [
                "rsync",
                "-a",
                "--progress",
                f"{self.backup_dir / 'home'}/",
                f"{self.home_dir}/",
            ],
            check=True,
        )

        # Set SSH directory permissions
        self.log.info("Setting ~/.ssh permissions")
        if not (self.home_dir / ".ssh").exists():
            run(["mkdir", self.home_dir / ".ssh"], check=True)
        ssh_permissions = """
            chmod 700 ${HOME}/.ssh
            chmod 600 ${HOME}/.ssh/*
            chmod 644 ${HOME}/.ssh/*.pub
            chown -R ${USER}:${USER} ${HOME}/.ssh
        """
        run(ssh_permissions, shell=True, check=True)

    def install_packages_from_scripts(self):
        self.log.info("----------------------------------------")
        self.log.info("Installing packages from source")
        self.log.info("----------------------------------------")

        # Scripts to be run, keys are directories, values are lists of script names
        dirs_scripts = {
            self.rsync_dir
            / "nix/scripts/setup-scripts": [
                "intel-undervolt.sh",
                "juliamono.sh",
                "keepassxc.sh",
                "keyd.sh",
            ],
            self.rsync_dir
            / "programming/environment/python-environment": [
                "miniconda-setup.sh",
                "jupyter-setup.sh",
            ],
        }

        # Install Julia if specified
        if self.julia_version is not None:
            dirs_scripts[self.rsync_dir / "programming/environment/julia-environment"] = [
                "julia-setup.sh"
            ]

        # Run install scripts
        for dir, scripts in dirs_scripts.items():
            for script in scripts:
                script = dir / script
                self.log.info(f"Running {script.name}")

                command = ["bash", script]
                if script.name == "julia-setup.sh":
                    command.extend(self.julia_version.split("."))

                out = run(
                    command,
                    capture_output=True,
                )
                self._check_for_failure(out, script.stem)

    def disable_ipv6(self):
        disable_ipv6 = """
            cat <<EOT >> /etc/sysctl/sysctl.d/99-sysctl
            net.ipv6.conf.all.disable_ipv6 = 1
            net.ipv6.conf.default.disable_ipv6 = 1
            net.ipv6.conf.lo.disable_ipv6 = 1
            EOT
        """
        run(disable_ipv6, shell=True, check=True)

    def enable_iptables(self):
        enable_iptables = """
            sudo chown root:root /etc/sysconfig/ip*tables
            sudo chmod 600 /etc/sysconfig/ip*tables
            sudo systemctl disable firewalld
            sudo systemctl enable iptables
            sudo systemctl enable ip6tables
            sudo systemctl stop firewalld
            sudo systemctl start iptables
            sudo systemctl start ip6tables
        """
        run(enable_iptables, shell=True, check=True)

    def _check_for_failure(self, out, name):
        if out.returncode != 0:
            self.log.error(f"Installation failed for {name}")
            with open(self.home_dir / f"fedora_setup-failure-{name}.stdout", "wb") as f:
                f.write(out.stdout)
            with open(self.home_dir / f"fedora_setup-failure-{name}.stderr", "wb") as f:
                f.write(out.stderr)

    def _configure_logger(self):
        # Set log file and format
        logfile = self.home_dir / "fedora_setup.log"
        formatter = logging.Formatter(
            "[%(asctime)s] - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create logger
        self.log = logging.getLogger("fedora_setup")
        self.log.setLevel(logging.DEBUG)

        # Create a console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)

        # Create file handler and set level to DEBUG
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        # Add handlers to logger
        self.log.addHandler(ch)
        self.log.addHandler(fh)


if __name__ == "__main__":
    fs = FedoraSetup(
        rsync_dir=Path("/backup/rsync"),
        user="user",
        install_tlp=True,
        julia_version="1.7.3",
    )
    fs.configure_packages()
    fs.configure_etc()
    fs.configure_home()
    fs.install_packages_from_scripts()
