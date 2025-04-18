#!/usr/bin/env python3

# pylint: disable=logging-fstring-interpolation, broad-exception-caught

import argparse
import logging
import subprocess as sp
import sys
from pathlib import Path


class FedoraSetup:
    """
    Class to set up a Fedora instance after installation.
    """

    # Configuration file paths
    CONFIG_FILES = {
        "ssh_config": "/etc/ssh/ssh_config",
        "sshd_config": "/etc/ssh/sshd_config",
        "remove_packages": "remove_packages.csv",
        "install_packages": "install_packages.csv",
    }

    # Installation scripts
    INSTALL_SCRIPTS = [
        "install_rust.sh",
        "install_i3status_rust.sh",
        "install_jetbrainsmono_nerd_font.sh",
        "install_keepassxc.sh",
        "install_keyd.sh",
    ]

    def __init__(
        self,
        backup_dir: Path | str | None,
        debug: bool = False,
    ):
        """
        Initialize a `FedoraSetup` instance.

        :param backup_dir: Directory containing backup files to restore.
        :param debug: Enable debug logging.
        """
        self.home_dir = Path().home()
        self.backup_dir = Path(backup_dir) if backup_dir is not None else Path(__file__).parent
        self.repo_dir = Path(__file__).parent
        self.debug = debug

        # Configure logging
        self._configure_logger()

        # Validate paths
        if not self.home_dir.exists():
            self.log.error(f"Home directory does not exist: {self.home_dir}")
            sys.exit(1)
        if not self.backup_dir.exists():
            self.log.error(f"Backup directory does not exist: {self.backup_dir}")
            sys.exit(1)
        for file_key in ("remove_packages", "install_packages"):
            file_path = self.repo_dir / self.CONFIG_FILES[file_key]
            if not file_path.exists():
                self.log.warning(f"Package list not found at {file_path}")

        # Clone the shell-scripts repository
        scripts_repo = self.repo_dir / "shell-scripts"
        if not scripts_repo.exists():
            self.log.info("Cloning shell-scripts repository")
            self._run_command(
                [
                    "git",
                    "clone",
                    "https://github.com/cameronperot/shell-scripts.git",
                    str(scripts_repo),
                ]
            )
        self.scripts_dir = scripts_repo / "scripts"

        # Get the fedora version
        self.fedora_version = sp.run(
            ["rpm", "-E", "%fedora"], check=True, capture_output=True, text=True
        ).stdout.strip()
        self.log.info(f"Detected Fedora version: {self.fedora_version}")

    def _load_package_list(self, relative_path: str) -> list[str]:
        """
        Load a list of packages from a file.

        :param relative_path: Path to the file relative to repo_dir.
        :return: List of package names.
        """
        file_path = self.repo_dir / relative_path
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return [y for x in f.readlines() if (y := x.strip())]
        except FileNotFoundError:
            self.log.warning(f"Package file not found: {file_path}")
            return []

    def _run_command(self, command: list[str] | str, **kwargs) -> bool:
        """
        Run a command with logging.

        :param command: Command to execute.
        :param **kwargs: Additional kwargs to pass to `subprocess.run()`.
        :return: `True` if successful, `False` otherwise.
        """
        command_str = command
        if isinstance(command, list):
            command_str = " ".join(command)

        self.log.debug(f"Running command: {command_str}")
        result = sp.run(command, check=False, capture_output=True, text=True, **kwargs)
        if result.returncode != 0:
            self.log.error(f"Command failed\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
            return False

        self.log.debug("Command succeeded")
        return True

    def configure_packages(self, install_tlp: bool = False) -> None:
        """
        Configure the packages using `dnf`.

        :param install_tlp: Flag to install TLP packages for advanced power management.
        """
        self.log.info("Configuring packages")

        # Load the packages to remove/install
        remove_packages = self._load_package_list(
            relative_path=self.CONFIG_FILES["remove_packages"]
        )
        install_packages = self._load_package_list(
            relative_path=self.CONFIG_FILES["install_packages"]
        )

        # Set up RPM Fusion URLs
        rpm_fusion_urls = (
            f"https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-{self.fedora_version}.noarch.rpm",
            f"https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{self.fedora_version}.noarch.rpm",
        )

        # Execute package operations
        if install_tlp:
            install_packages += ["tlp", "tlp-rdw", "powertop"]
        commands = []
        if remove_packages:
            commands.append(["sudo", "dnf", "remove", "-y", *remove_packages])
            commands.append(["sudo", "dnf", "autoremove", "-y"])
        commands += [
            ["sudo", "dnf", "install", "-y", *rpm_fusion_urls],
            ["sudo", "dnf", "upgrade", "-y"],
        ]
        if install_packages:
            commands.append(["sudo", "dnf", "install", "-y", *install_packages])
        for command in commands:
            self._run_command(command)

        self.log.info("Packages configured successfully")

    def configure_etc(self) -> None:
        """
        Configure `/etc` files and update SSH moduli.
        """
        self.log.info("Configuring /etc")

        # Copy over config files
        config_files = (self.CONFIG_FILES["ssh_config"], self.CONFIG_FILES["sshd_config"])
        for config_file in config_files:
            source_path = self.repo_dir / config_file[1:]
            if not source_path.exists():
                self.log.warning(f"Source file {source_path} does not exist, skipping")
                continue
            self._run_command(["sudo", "cp", "-a", str(source_path), config_file])
            self._run_command(["sudo", "chown", "root:root", config_file])
            self._run_command(["sudo", "chmod", "644", config_file])
            self._run_command(["sudo", "restorecon", config_file])

        # Remove small primes from SSH moduli
        self.log.info("Removing small primes from SSH moduli")
        self._run_command(
            ["sudo", "bash", str(self.scripts_dir / "remove_small_ssh_moduli_primes.sh")]
        )

    def configure_home(self) -> None:
        """
        Configure home directory and set SSH permissions.
        """
        self.log.info(f"Configuring {self.home_dir}")

        # Set the source directory
        source_dir = self.backup_dir / "home"
        if not source_dir.exists():
            source_dir = self.repo_dir / "environment-setup/dotfiles"
            if not source_dir.parent.exists():
                self.log.info("Cloning environment-setup repository")
                self._run_command(
                    [
                        "git",
                        "clone",
                        "https://github.com/cameronperot/environment-setup.git",
                        str(source_dir.parent),
                    ]
                )

        # Copy over user files
        self.log.info(f"Copying files from {source_dir} to {self.home_dir}")
        self._run_command(["rsync", "-a", "--progress", f"{source_dir}/", f"{self.home_dir}/"])

        # Set SSH directory permissions
        self.log.info("Setting ~/.ssh permissions")
        ssh_dir = self.home_dir / ".ssh"
        if not ssh_dir.exists():
            ssh_dir.mkdir(mode=0o700)
            self.log.info(f"Created {ssh_dir}")
        self._run_command(["bash", str(self.scripts_dir / "set_ssh_dir_permissions.sh")])

    def run_install_scripts(self) -> None:
        """
        Install packages from source using the installation scripts.
        """
        self.log.info("Installing packages from scripts")

        # Run the install scripts
        for script_name in self.INSTALL_SCRIPTS:
            script_path = self.scripts_dir / script_name
            if not script_path.exists():
                self.log.warning(f"Script {script_path} not found, skipping")
                continue

            self.log.info(f"Running {script_path.name}")
            self._run_command(["bash", str(script_path)])

    def _configure_logger(self) -> None:
        """
        Configure the logger for this class.
        """
        # Set log file and format
        log_file = self.repo_dir / "fedora_setup.log"
        formatter = logging.Formatter(
            "[%(asctime)s - %(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create logger
        self.log = logging.getLogger("fedora_setup")
        self.log.setLevel(logging.DEBUG)

        # Create a console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG if self.debug else logging.INFO)
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

        # Create file handler and set level to DEBUG
        try:
            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self.log.addHandler(fh)
            self.log.info(f"Logging to {log_file}")
        except PermissionError:
            print(f"Warning: Could not create log file at {log_file}")


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Fedora setup script", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Basic configuration options
    parser.add_argument(
        "--backup_dir",
        type=str,
        default=None,
        help="Directory containing backup files to restore",
    )
    parser.add_argument("--debug", "-v", action="store_true", help="Enable debug logging")

    # Configuration steps flags
    parser.add_argument(
        "--configure_packages",
        action="store_true",
        help="Run packages configuration step",
    )
    parser.add_argument(
        "--install_tlp", action="store_true", help="Install TLP for power management"
    )
    parser.add_argument(
        "--configure_etc", action="store_true", help="Run /etc configuration step"
    )
    parser.add_argument(
        "--configure_home",
        action="store_true",
        help="Run home directory configuration step",
    )
    parser.add_argument(
        "--run_install_scripts",
        action="store_true",
        help="Run installation of packages from scripts",
    )
    parser.add_argument("--all", action="store_true", help="Run all configuration steps")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    try:
        fs = FedoraSetup(backup_dir=args.backup_dir, debug=args.debug)

        if args.all or args.configure_packages:
            fs.configure_packages(install_tlp=args.install_tlp)
        if args.all or args.configure_etc:
            fs.configure_etc()
        if args.all or args.configure_home:
            fs.configure_home()
        if args.all or args.run_install_scripts:
            fs.run_install_scripts()

        print("\nFedora setup completed successfully!")
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nSetup failed: {e}")
        sys.exit(1)
