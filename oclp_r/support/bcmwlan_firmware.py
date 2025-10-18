"""
bcmwlan_firmware.py: AppleBCMWLANCompanion firmware management
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any

from ..constants import Constants


class BCMWLANFirmwareManager:
    """
    Manages AppleBCMWLANCompanion firmware files
    """
    
    def __init__(self, constants: Constants):
        self.constants = constants
        self.firmware_dir = Path("/usr/local/share/firmware/wifi")
        self.source_dir = constants.payload_firmwares_path / "BCMWLAN"
        
        # Firmware information
        self.firmware_info = {
            "BCM43602": {
                "file": "brcmfmac43602-pcie_7.35.177.61.bin",
                "hash": "bf4cfc23ee952a3d82ef33a0f5f87853201c98f1bed034876a910f354f37862d",
                "srom_slide": "00000000"
            },
            "BCM4350": {
                "file": "brcmfmac4350-pcie_7.35.180.119.bin",
                "hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567890",  # Placeholder
                "srom_slide": "40000000"
            }
        }
    
    def install_firmware(self, chip_type: str) -> bool:
        """
        Install firmware for the specified chip type
        
        Args:
            chip_type: Either "BCM43602" or "BCM4350"
            
        Returns:
            True if installation successful, False otherwise
        """
        if chip_type not in self.firmware_info:
            print(f"Error: Unknown chip type: {chip_type}")
            return False
        
        firmware_data = self.firmware_info[chip_type]
        source_file = self.source_dir / chip_type / firmware_data["file"]
        dest_file = self.firmware_dir / firmware_data["file"]
        
        # Check if source file exists
        if not source_file.exists():
            print(f"Error: Source firmware file not found: {source_file}")
            return False
        
        # Create destination directory if it doesn't exist
        self.firmware_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy firmware file
            shutil.copy2(source_file, dest_file)
            print(f"Installed firmware: {dest_file}")
            
            # Verify hash if not placeholder
            if not firmware_data["hash"].startswith("a1b2c3d4"):  # Not placeholder
                if self._verify_firmware_hash(dest_file, firmware_data["hash"]):
                    print("Firmware hash verification successful")
                else:
                    print("Warning: Firmware hash verification failed")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error installing firmware: {e}")
            return False
    
    def _verify_firmware_hash(self, file_path: Path, expected_hash: str) -> bool:
        """
        Verify the SHA-256 hash of a firmware file
        
        Args:
            file_path: Path to the firmware file
            expected_hash: Expected SHA-256 hash
            
        Returns:
            True if hash matches, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash.lower() == expected_hash.lower()
        except Exception as e:
            print(f"Error verifying hash: {e}")
            return False
    
    def get_firmware_info(self, chip_type: str) -> Optional[Dict[str, Any]]:
        """
        Get firmware information for the specified chip type
        
        Args:
            chip_type: Either "BCM43602" or "BCM4350"
            
        Returns:
            Dictionary with firmware information or None if not found
        """
        if chip_type not in self.firmware_info:
            return None
        
        firmware_data = self.firmware_info[chip_type].copy()
        firmware_data["path"] = str(self.firmware_dir / firmware_data["file"])
        return firmware_data
    
    def is_firmware_installed(self, chip_type: str) -> bool:
        """
        Check if firmware is installed for the specified chip type
        
        Args:
            chip_type: Either "BCM43602" or "BCM4350"
            
        Returns:
            True if firmware is installed, False otherwise
        """
        if chip_type not in self.firmware_info:
            return False
        
        firmware_data = self.firmware_info[chip_type]
        dest_file = self.firmware_dir / firmware_data["file"]
        return dest_file.exists()
    
    def uninstall_firmware(self, chip_type: str) -> bool:
        """
        Uninstall firmware for the specified chip type
        
        Args:
            chip_type: Either "BCM43602" or "BCM4350"
            
        Returns:
            True if uninstallation successful, False otherwise
        """
        if chip_type not in self.firmware_info:
            print(f"Error: Unknown chip type: {chip_type}")
            return False
        
        firmware_data = self.firmware_info[chip_type]
        dest_file = self.firmware_dir / firmware_data["file"]
        
        try:
            if dest_file.exists():
                dest_file.unlink()
                print(f"Uninstalled firmware: {dest_file}")
            else:
                print(f"Firmware not found: {dest_file}")
            return True
        except Exception as e:
            print(f"Error uninstalling firmware: {e}")
            return False
    
    def list_installed_firmware(self) -> list:
        """
        List all installed BCMWLAN firmware files
        
        Returns:
            List of installed firmware files
        """
        installed = []
        for chip_type in self.firmware_info:
            if self.is_firmware_installed(chip_type):
                installed.append(chip_type)
        return installed