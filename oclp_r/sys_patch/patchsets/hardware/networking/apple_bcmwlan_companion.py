"""
apple_bcmwlan_companion.py: AppleBCMWLANCompanion support for BCM43602 and BCM4350
"""

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants  import Constants
from .....detections import device_probe

from .....datasets.os_data import os_data


class AppleBCMWLANCompanion(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: AppleBCMWLANCompanion"


    def present(self) -> bool:
        """
        Targeting BCM43602 and BCM4350 chips that support AppleBCMWLANCompanion
        """
        return isinstance(self._computer.wifi, device_probe.Broadcom) and (
            self._computer.wifi.chipset in [
                device_probe.Broadcom.Chipsets.AppleBCMWLANBusInterfacePCIe,
            ]
        )


    def native_os(self) -> bool:
        """
        AppleBCMWLANCompanion is designed for macOS Sonoma, Sequoia, and Tahoe
        """
        return self._xnu_major >= os_data.sonoma.value


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.NETWORKING


    def patches(self) -> dict:
        """
        Patches for AppleBCMWLANCompanion
        """
        if self.native_os() is False:
            return {}

        return {
            "AppleBCMWLANCompanion": {
                PatchType.ADD_KEXT: {
                    "AppleBCMWLANCompanion.kext": {
                        "Enabled": True,
                        "Order": 1,  # Must load after Lilu
                    },
                },
            },
        }


    def device_properties(self) -> dict:
        """
        Device properties for AppleBCMWLANCompanion
        """
        if self.present() is False:
            return {}

        # Get the WiFi device path
        wifi_device_path = self._get_wifi_device_path()
        if not wifi_device_path:
            return {}

        # Determine chip type and firmware
        chip_type = self._get_chip_type()
        firmware_info = self._get_firmware_info(chip_type)
        
        if not firmware_info:
            return {}

        device_properties = {
            wifi_device_path: {
                "bcmc-firmware-path": firmware_info["path"],
                "bcmc-firmware-hash": firmware_info["hash"],
            }
        }

        # Add SROM slide for BCM4350
        if chip_type == "BCM4350":
            device_properties[wifi_device_path]["bcmc-srom-slide"] = "40000000"
        else:  # BCM43602
            device_properties[wifi_device_path]["bcmc-srom-slide"] = "00000000"

        return device_properties


    def _get_wifi_device_path(self) -> str:
        """
        Get the PCI device path for the WiFi card
        """
        if not hasattr(self._computer.wifi, 'pci_path'):
            return None
        
        # Convert PCI path to OpenCore format
        # This is a simplified implementation - in practice, you'd need to
        # parse the actual PCI path and convert it to PciRoot format
        return f"PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)"  # Placeholder


    def _get_chip_type(self) -> str:
        """
        Determine the chip type based on device ID
        """
        if not hasattr(self._computer.wifi, 'device_id'):
            return None
        
        device_id = self._computer.wifi.device_id
        
        if device_id == 0x43BA:
            return "BCM43602"
        elif device_id == 0x43A3:
            return "BCM4350"
        
        return None


    def _get_firmware_info(self, chip_type: str) -> dict:
        """
        Get firmware path and hash for the specified chip type
        """
        if chip_type == "BCM43602":
            return {
                "path": "/usr/local/share/firmware/wifi/brcmfmac43602-pcie_7.35.177.61.bin",
                "hash": "bf4cfc23ee952a3d82ef33a0f5f87853201c98f1bed034876a910f354f37862d"
            }
        elif chip_type == "BCM4350":
            return {
                "path": "/usr/local/share/firmware/wifi/brcmfmac4350-pcie_7.35.180.119.bin",
                "hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567890"  # Placeholder
            }
        
        return None