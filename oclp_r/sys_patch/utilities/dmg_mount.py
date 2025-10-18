"""
dmg_mount.py: PatcherSupportPkg DMG Mounting. Handles Universal-Binaries and sumitdusterInternalResources DMGs.
"""

import logging
import subprocess
import applescript

from pathlib import Path

from ... import constants

from ...support import subprocess_wrapper


class PatcherSupportPkgMount:

    def __init__(self, global_constants: constants.Constants) -> None:
        self.constants: constants.Constants = global_constants
        self.icon_path = str(self.constants.app_icon_path).replace("/", ":")[1:]


    def _mount_universal_binaries_dmg(self) -> bool:
        """
        Mount PatcherSupportPkg's Universal-Binaries.dmg
        """
        if not Path(self.constants.payload_local_binaries_root_path_dmg).exists():
            logging.info("- PatcherSupportPkg resources missing, Patcher likely corrupted!!!")
            return False

        output = subprocess.run(
            [
                "/usr/bin/hdiutil", "attach", "-noverify", f"{self.constants.payload_local_binaries_root_path_dmg}",
                "-mountpoint", Path(self.constants.payload_path / Path("Universal-Binaries")),
                "-nobrowse",
                "-shadow", Path(self.constants.payload_path / Path("Universal-Binaries_overlay")),
                "-passphrase", "password"
            ],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        if output.returncode != 0:
            logging.info("- Failed to mount Universal-Binaries.dmg")
            subprocess_wrapper.log(output)
            return False

        logging.info("- Mounted Universal-Binaries.dmg")
        return True


    def _mount_sumitduster_internal_resources_dmg(self) -> bool:
        """
        Mount PatcherSupportPkg's sumitdusterInternalResources.dmg (if available)
        """
        if not Path(self.constants.overlay_psp_path_dmg).exists():
            return True
        if not Path("~/.sumitduster_developer").expanduser().exists():
            return True
        if self.constants.cli_mode is True:
            return True

        logging.info("- Found sumitdusterInternal resources, mounting...")

        for i in range(3):
            key = self._request_decryption_key(i)
            output = subprocess.run(
                [
                    "/usr/bin/hdiutil", "attach", "-noverify", f"{self.constants.overlay_psp_path_dmg}",
                    "-mountpoint", Path(self.constants.payload_path / Path("sumitdusterInternal")),
                    "-nobrowse",
                    "-passphrase", key
                ],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            if output.returncode != 0:
                logging.info("- Failed to mount sumitdusterInternal resources")
                subprocess_wrapper.log(output)

                if "Authentication error" not in output.stdout.decode():
                    self._display_authentication_error()

                if i == 2:
                    self._display_too_many_attempts()
                    return False
                continue
            break

        logging.info("- Mounted sumitdusterInternal resources")
        return self._merge_sumitduster_internal_resources()


    def _merge_sumitduster_internal_resources(self) -> bool:
        """
        Merge sumitdusterInternal resources with Universal-Binaries
        """
        result = subprocess.run(
            [
                "/usr/bin/ditto", f"{self.constants.payload_path / Path('sumitdusterInternal')}", f"{self.constants.payload_path / Path('Universal-Binaries')}"
            ],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        if result.returncode != 0:
            logging.info("- Failed to merge sumitdusterInternal resources")
            subprocess_wrapper.log(result)
            return False

        return True


    def _request_decryption_key(self, attempt: int) -> str:
        """
        Fetch the decryption key for sumitdusterInternalResources.dmg
        """
        # Only return on first attempt
        if attempt == 0:
            if Path("~/.sumitduster_developer_key").expanduser().exists():
                return Path("~/.sumitduster_developer_key").expanduser().read_text().strip()

        password = ""
        msg = "Welcome to the sumitdusterInternal Program, please provide the decryption key to access internal resources. Press cancel to skip."
        if attempt > 0:
            msg = f"Decryption failed, please try again. {2 - attempt} attempts remaining. "

        try:
            password = applescript.AppleScript(
                f"""
                set theResult to display dialog "{msg}" default answer "" with hidden answer with title "OCLP-R" with icon file "{self.icon_path}"

                return the text returned of theResult
                """
            ).run()
        except Exception as e:
            pass

        return password


    def _display_authentication_error(self) -> None:
        """
        Display authentication error dialog
        """
        try:
            applescript.AppleScript(
                f"""
                display dialog "Failed to mount sumitdusterInternal resources, please file an internal radar." with title "OCLP-R" with icon file "{self.icon_path}"
                """
            ).run()
        except Exception as e:
            pass


    def _display_too_many_attempts(self) -> None:
        """
        Display too many attempts dialog
        """
        try:
            applescript.AppleScript(
                f"""
                display dialog "Failed to mount sumitdusterInternal resources, too many incorrect passwords. If this continues with the correct decryption key, please file an internal radar." with title "OCLP-R" with icon file "{self.icon_path}"
                """
            ).run()
        except Exception as e:
            pass


    def mount(self) -> bool:
        """
        Mount PatcherSupportPkg resources

        Returns:
            bool: True if all resources are mounted, False otherwise
        """
        # If already mounted, skip
        if Path(self.constants.payload_local_binaries_root_path).exists():
            logging.info("- Local PatcherSupportPkg resources available, continuing...")
            return True

        if self._mount_universal_binaries_dmg() is False:
            return False

        if self._mount_sumitduster_internal_resources_dmg() is False:
            return False

        return True