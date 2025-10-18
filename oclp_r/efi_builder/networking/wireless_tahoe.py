"""
wireless_tahoe.py: Class for handling Wireless Networking Patches for Tahoe, invocation from build.py
"""

import logging
import shutil

from .. import support

from ... import constants

from ...detections import device_probe

from ...datasets import (
    smbios_data,
    cpu_data,
    os_data
)


class BuildWirelessNetworkingTahoe:
    """
    Build Library for Wireless Networking Support on macOS Tahoe (15.x)
    Supports AppleBCMWLANCompanion for legacy Broadcom Wi-Fi cards

    Invoke from build.py
    """

    def __init__(self, model: str, global_constants: constants.Constants, config: dict) -> None:
        self.model: str = model
        self.config: dict = config
        self.constants: constants.Constants = global_constants
        self.computer: device_probe.Computer = self.constants.computer

        self._build()


    def _build(self) -> None:
        """
        Kick off Wireless Build Process for Tahoe
        """

        # Check if detected OS is Tahoe or newer
        if self.constants.detected_os < os_data.os_data.tahoe:
            logging.info("- Skipping AppleBCMWLANCompanion (requires macOS Tahoe or newer)")
            return

        # Check if WiFi was detected
        if not self.constants.custom_model and self.constants.computer.wifi:
            self._on_model()
        else:
            # For custom models or prebuilt, optionally enable based on user preference
            if self.constants.enable_wireless_tahoe:
                self._enable_bcmwlancompanion()


    def _on_model(self) -> None:
        """
        On-Model Hardware Detection Handling
        """

        if not self.computer.wifi:
            return

        wifi_chipset = self.computer.wifi.chipset

        # Supported Broadcom chipsets for AppleBCMWLANCompanion
        # BCM43602 and BCM4350 both use AirportBrcmNIC chipset
        supported_chipsets = [
            device_probe.Broadcom.Chipsets.AirportBrcmNIC,  # BCM43602, BCM4350
        ]

        if wifi_chipset in supported_chipsets:
            logging.info(f"- Detected supported Broadcom Wi-Fi chipset: {wifi_chipset}")
            logging.info("  Supported cards: BCM43602, BCM4350 (AirportBrcmNIC)")
            self._enable_bcmwlancompanion()
        else:
            logging.info(f"- Unsupported Wi-Fi chipset for AppleBCMWLANCompanion: {wifi_chipset}")
            logging.info("  Supported: AirportBrcmNIC (BCM43602, BCM4350)")


    def _enable_bcmwlancompanion(self) -> None:
        """
        Enable AppleBCMWLANCompanion kext for Broadcom Wi-Fi support on Tahoe
        """

        logging.info("- Enabling AppleBCMWLANCompanion for Broadcom Wi-Fi on macOS Tahoe")
        logging.info("  Note: This is BETA software from 0xFireWolf")
        logging.info("  GitHub: https://github.com/0xFireWolf/AppleBCMWLANCompanion")
        
        # Add the kext entry to config (since it's not in the base template)
        kext_entry = {
            "Arch": "Any",
            "BundlePath": "AppleBCMWLANCompanion.kext",
            "Comment": f"AppleBCMWLANCompanion {self.constants.bcmwlancompanion_version} - Broadcom Wi-Fi for Tahoe",
            "Enabled": True,
            "ExecutablePath": "Contents/MacOS/AppleBCMWLANCompanion",
            "MaxKernel": "",
            "MinKernel": "23.0.0",  # macOS Sonoma and newer
            "PlistPath": "Contents/Info.plist"
        }
        
        # Add to config
        self.config["Kernel"]["Add"].append(kext_entry)
        
        # Copy the kext file
        logging.info(f"- Adding AppleBCMWLANCompanion.kext {self.constants.bcmwlancompanion_version}")
        shutil.copy(self.constants.bcmwlancompanion_path, self.constants.kexts_path)

        # Add optional debug boot arguments if debug mode is enabled
        if self.constants.kext_debug:
            logging.info("- Adding AppleBCMWLANCompanion debug boot arguments")
            self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -bcmcdbg"
        
        # Add beta features boot argument
        self.config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"] += " -bcmcbeta"

        logging.info("- AppleBCMWLANCompanion configuration complete")
        logging.info("  Supported cards: BCM43602, BCM4350 (AirportBrcmNIC)")
        logging.info("  Status: Beta (Test thoroughly before daily use)")

