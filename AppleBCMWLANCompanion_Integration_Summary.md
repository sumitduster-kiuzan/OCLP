# AppleBCMWLANCompanion Integration with OpenCore Legacy Patcher

## Overview

This document summarizes the integration of AppleBCMWLANCompanion support into OpenCore Legacy Patcher (OCLP). AppleBCMWLANCompanion is a kernel extension by FireWolf that enables legacy Broadcom Wi-Fi cards to work on macOS Sonoma, Sequoia, and Tahoe **without requiring root patches**.

## What is AppleBCMWLANCompanion?

AppleBCMWLANCompanion (BCMC) is a macOS kernel extension that:
- Supports BCM43602 and BCM4350 Wi-Fi chips on modern macOS versions
- Works without disabling System Integrity Protection (SIP) or Apple Mobile File Integrity (AMFI)
- Provides a cleaner alternative to OCLP's current root patching approach
- Requires proper firmware files and device configuration

### Supported Devices

| Chip Name | Device ID      | Card Names                                       |
|-----------|----------------|--------------------------------------------------|
| BCM43602  | 0x14E4, 0x43BA | BCM943602BAED, BCM943602CDP, BCM943602CS, DW1830 |
| BCM4350   | 0x14E4, 0x43A3 | BCM94350ZAE, DW1820A                             |

## Integration Changes Made

### 1. PCI Data Updates (`oclp_r/datasets/pci_data.py`)

Added new device category for AppleBCMWLANCompanion supported devices:

```python
# AppleBCMWLANCompanion supported devices
# These devices can use AppleBCMWLANCompanion kext instead of root patches
AppleBCMWLANCompanion = [
    0x43BA,  # BCM43602 - BCM943602BAED, BCM943602CDP, BCM943602CS, DW1830
    0x43A3,  # BCM4350 - BCM94350ZAE, DW1820A
]
```

### 2. Device Probe Updates (`oclp_r/detections/device_probe.py`)

- Added new chipset type: `AppleBCMWLANCompanion = "AppleBCMWLANCompanion supported"`
- Updated detection logic to prioritize AppleBCMWLANCompanion over legacy AirPortBrcmNIC detection

### 3. New Hardware Detection Class (`oclp_r/sys_patch/patchsets/hardware/networking/apple_bcmwlan_companion.py`)

Created comprehensive hardware detection class with:
- **Device Detection**: Identifies compatible BCM43602 and BCM4350 devices on Sonoma+
- **Requirements Checking**: Validates system integrity, firmware presence, and IOMMU settings
- **Device Properties**: Automatically configures firmware paths, hashes, and SROM settings
- **Boot Arguments**: Adds required `wlan.pcie.detectsabotage=0` argument
- **Limitations Tracking**: Documents known issues and device-specific limitations

### 4. Patchset Integration (`oclp_r/sys_patch/patchsets/detect.py`)

Integrated AppleBCMWLANCompanion into the main hardware detection system.

### 5. Modern Wireless Conflict Resolution (`oclp_r/sys_patch/patchsets/hardware/networking/modern_wireless.py`)

Updated ModernWireless class to avoid conflicts:
- Excludes AppleBCMWLANCompanion devices on Sonoma+ to prevent root patch conflicts
- Maintains backward compatibility for older macOS versions

### 6. EFI Builder Integration (`oclp_r/efi_builder/networking/wireless.py`)

Added `_apple_bcmwlan_companion()` method that:
- Enables AppleBCMWLANCompanion kext injection
- Configures device-specific firmware properties
- Sets required boot arguments automatically
- Handles country code configuration

### 7. Constants Updates (`oclp_r/constants.py`)

Added AppleBCMWLANCompanion version and path constants:
```python
# Third Party - FireWolf
self.apple_bcmwlan_companion_version: str = "1.0.0"  # AppleBCMWLANCompanion

@property
def apple_bcmwlan_companion_path(self):
    return self.payload_kexts_path / Path(f"FireWolf/AppleBCMWLANCompanion-v{self.apple_bcmwlan_companion_version}-{self.kext_variant}.zip")
```

## How It Works

### Detection Priority

1. **AppleBCMWLANCompanion** (Sonoma+ with supported devices)
2. **ModernWireless** (root patches for older systems or unsupported devices)
3. **LegacyWireless** (very old devices)

### Configuration Process

When AppleBCMWLANCompanion is detected:

1. **Kext Injection**: AppleBCMWLANCompanion.kext is added to OpenCore configuration
2. **Device Properties**: Firmware path, hash, and SROM slide values are configured
3. **Boot Arguments**: `wlan.pcie.detectsabotage=0` is added automatically
4. **Firmware Check**: System validates firmware file presence and integrity

### Device Properties Generated

For **BCM43602**:
```
bcmc-firmware-path: /usr/local/share/firmware/wifi/brcmfmac43602-pcie_7.35.177.61.bin
bcmc-firmware-hash: <SHA-256 hash>
bcmc-srom-slide: 00000000
```

For **BCM4350**:
```
bcmc-firmware-path: /usr/local/share/firmware/wifi/brcmfmac4350-pcie_7.35.180.119.bin
bcmc-srom-slide: 40000000 (required for BCM4350)
```

## Requirements for Users

### System Requirements
- macOS Sonoma (14.0) or newer
- System Integrity Protection (SIP) **enabled**
- Apple Mobile File Integrity (AMFI) **enabled**
- VT-d enabled in BIOS settings

### Firmware Requirements
Users must manually download and install firmware files:
- BCM43602: `brcmfmac43602-pcie_7.35.177.61.bin`
- BCM4350: `brcmfmac4350-pcie_7.35.180.119.bin`

Files should be placed in: `/usr/local/share/firmware/wifi/`

### Incompatible Configurations
- **Root Wi-Fi patches must be removed** before using AppleBCMWLANCompanion
- Cannot be used alongside `AMFIPass.kext`, `IOSkywalkFamily.kext`, or `IO80211FamilyLegacy.kext`

## Known Limitations

### General Issues
- **AWDL not available**: AirDrop and Continuity features won't work
- **Internet Sharing**: May not work properly with Wi-Fi adapter
- **Sleep/Wake**: May trigger kernel panics

### Device-Specific Issues
- **BCM4350**: WPA/WPA2 networks not currently supported
- **BCM43602**: Wi-Fi menu shows incorrect transmit rate (24 Mbps)

## Benefits Over Root Patches

1. **System Integrity**: No system file modifications required
2. **Security**: SIP and AMFI remain enabled
3. **Stability**: Cleaner integration with Apple's networking stack
4. **Updates**: System updates won't break Wi-Fi functionality
5. **Future-Proof**: Works with latest macOS versions

## Implementation Status

✅ **Completed**:
- Device detection and classification
- Hardware detection class with full feature set
- EFI builder integration
- Patchset system integration
- Conflict resolution with existing patches

🔄 **Pending**:
- AppleBCMWLANCompanion kext integration in payload system
- Firmware download automation
- GUI integration for user configuration
- Testing and validation on real hardware

## Next Steps

1. **Kext Payload**: Add AppleBCMWLANCompanion kext to OCLP's payload system
2. **Firmware Management**: Implement automatic firmware download and verification
3. **User Interface**: Add GUI options for AppleBCMWLANCompanion configuration
4. **Documentation**: Update user guides with AppleBCMWLANCompanion setup instructions
5. **Testing**: Validate functionality across supported hardware configurations

## Conclusion

This integration provides OCLP users with a modern, secure alternative to root patches for supported Broadcom Wi-Fi cards. The implementation maintains OCLP's philosophy of automated hardware detection while offering the benefits of AppleBCMWLANCompanion's clean, SIP-compatible approach.

The integration is designed to be:
- **Automatic**: No user configuration required for basic functionality
- **Safe**: Prevents conflicts with existing patches
- **Informative**: Provides clear requirements and limitations
- **Future-Ready**: Supports the latest macOS versions without system modifications