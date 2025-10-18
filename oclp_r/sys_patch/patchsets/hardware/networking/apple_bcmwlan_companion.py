"""
apple_bcmwlan_companion.py: AppleBCMWLANCompanion detection and configuration
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
        Targeting AppleBCMWLANCompanion compatible devices
        
        AppleBCMWLANCompanion supports:
        - BCM43602 (0x43BA): BCM943602BAED, BCM943602CDP, BCM943602CS, DW1830
        - BCM4350 (0x43A3): BCM94350ZAE, DW1820A
        
        Only available on macOS Sonoma (14.0) and newer
        """
        return (
            isinstance(self._computer.wifi, device_probe.Broadcom) 
            and self._computer.wifi.chipset == device_probe.Broadcom.Chipsets.AppleBCMWLANCompanion
            and self._xnu_major >= os_data.sonoma.value
        )


    def native_os(self) -> bool:
        """
        AppleBCMWLANCompanion is designed for macOS Sonoma and newer
        These devices are not natively supported on Sonoma+
        """
        return False


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.NETWORKING


    def _get_device_properties(self) -> dict:
        """
        Generate device properties for AppleBCMWLANCompanion based on device ID
        """
        device_id = self._computer.wifi.device_id
        
        # Firmware mapping based on device ID
        firmware_map = {
            0x43BA: {  # BCM43602
                "firmware_name": "brcmfmac43602-pcie_7.35.177.61.bin",
                "firmware_hash": "bf4cfc23ee952a3d82ef33a0f5f87853201c98f1bed034876a910f354f37862d",
                "srom_slide": "00000000"  # Not required for BCM43602 but can be set
            },
            0x43A3: {  # BCM4350
                "firmware_name": "brcmfmac4350-pcie_7.35.180.119.bin", 
                "firmware_hash": "TBD",  # Hash would need to be calculated from actual firmware
                "srom_slide": "40000000"  # Required for BCM4350
            }
        }
        
        if device_id not in firmware_map:
            return {}
            
        fw_info = firmware_map[device_id]
        
        return {
            "bcmc-firmware-path": f"/usr/local/share/firmware/wifi/{fw_info['firmware_name']}",
            "bcmc-firmware-hash": bytes.fromhex(fw_info['firmware_hash']).hex() if fw_info['firmware_hash'] != "TBD" else "",
            "bcmc-srom-slide": bytes.fromhex(fw_info['srom_slide']).hex()
        }


    def patches(self) -> dict:
        """
        AppleBCMWLANCompanion configuration
        
        Instead of root patches, this provides kext injection and device properties
        """
        if self.native_os() is True:
            return {}

        # Generate device properties for the Wi-Fi card
        device_props = self._get_device_properties()
        
        # Get device path - this would need to be determined at runtime
        # For now, using a placeholder that would be filled by the EFI builder
        device_path = "PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)"  # Example path
        
        return {
            "AppleBCMWLANCompanion": {
                # Kext injection will be handled by EFI builder
                PatchType.KEXT_INJECTION: {
                    "AppleBCMWLANCompanion.kext": "latest"
                },
                # Device properties for the Wi-Fi card
                PatchType.DEVICE_PROPERTIES: {
                    device_path: device_props
                },
                # Boot arguments required for AppleBCMWLANCompanion
                PatchType.BOOT_ARGUMENTS: [
                    "wlan.pcie.detectsabotage=0"  # Required to prevent Wi-Fi driver from checking the chip
                ]
            }
        }


    def requirements(self) -> dict:
        """
        Requirements for AppleBCMWLANCompanion to function properly
        """
        device_id = self._computer.wifi.device_id
        
        firmware_map = {
            0x43BA: "brcmfmac43602-pcie_7.35.177.61.bin",
            0x43A3: "brcmfmac4350-pcie_7.35.180.119.bin"
        }
        
        firmware_name = firmware_map.get(device_id, "unknown")
        
        return {
            "system_integrity": {
                "sip_enabled": True,
                "amfi_enabled": True,
                "description": "AppleBCMWLANCompanion requires SIP and AMFI to remain enabled"
            },
            "firmware": {
                "path": f"/usr/local/share/firmware/wifi/{firmware_name}",
                "description": f"Firmware file {firmware_name} must be present in /usr/local/share/firmware/wifi/"
            },
            "iommu": {
                "vt_d_enabled": True,
                "description": "VT-d must be enabled in BIOS for AppleVTD and IOMapper support"
            },
            "incompatible_patches": {
                "modern_wireless": False,
                "legacy_wireless": False,
                "description": "Root Wi-Fi patches must be removed before using AppleBCMWLANCompanion"
            }
        }


    def limitations(self) -> dict:
        """
        Known limitations of AppleBCMWLANCompanion
        """
        device_id = self._computer.wifi.device_id
        
        general_limitations = [
            "AWDL (Apple Wireless Direct Link) not available - affects AirDrop and Continuity features",
            "Internet Sharing to Wi-Fi adapter may not work properly", 
            "Sleep/wake may trigger kernel panics"
        ]
        
        device_specific = {}
        if device_id == 0x43A3:  # BCM4350
            device_specific["BCM4350"] = [
                "WPA/WPA2 protected networks not currently supported"
            ]
        elif device_id == 0x43BA:  # BCM43602
            device_specific["BCM43602"] = [
                "Wi-Fi menu shows incorrect transmit rate (24 Mbps) when actual rate is higher"
            ]
            
        return {
            "general": general_limitations,
            "device_specific": device_specific,
            "status": "Beta - Not recommended for daily use"
        }