# AppleBCMWLANCompanion Integration

This document describes the integration of AppleBCMWLANCompanion into OpenCore Legacy Patcher (OCLP-R) for providing native Wi-Fi support on macOS Sonoma, Sequoia, and Tahoe.

## Overview

AppleBCMWLANCompanion (BCMC) is a macOS kernel extension designed for selected Broadcom FullMAC Wi-Fi cards. It consists of a device driver that configures legacy Wi-Fi chips and a Lilu plugin that ensures compatibility with Apple's new Wi-Fi driver.

## Supported Systems

- macOS Tahoe (26.0+)
- macOS Sequoia (15.7+)
- macOS Sonoma (14.6+)

## Supported Wi-Fi Chips

| Chip Name | Device ID      | Card Names                                       |
|-----------|----------------|--------------------------------------------------|
| BCM43602  | 0x14E4, 0x43BA | BCM943602BAED, BCM943602CDP, BCM943602CS, DW1830 |
| BCM4350   | 0x14E4, 0x43A3 | BCM94350ZAE, DW1820A                             |

## Features

- Native Wi-Fi support without root patches
- Works with System Integrity Protection (SIP) enabled
- Supports WPA Wi-Fi and Personal Hotspot
- Compatible with Apple's new Wi-Fi driver stack
- No firmware patching required

## Requirements

### Hardware Requirements
- BCM43602 or BCM4350 Wi-Fi chip
- VT-d enabled in BIOS settings
- IOMapper support

### Software Requirements
- macOS Sonoma, Sequoia, or Tahoe
- OpenCore Legacy Patcher (OCLP-R)
- Lilu kext (automatically included)

## Installation

### Automatic Installation (Recommended)

1. Run OpenCore Legacy Patcher
2. Select "Post-Install Root Patch"
3. The patcher will automatically detect BCM43602/BCM4350 chips
4. AppleBCMWLANCompanion will be automatically enabled
5. Required firmware files will be installed to `/usr/local/share/firmware/wifi/`

### Manual Installation

If automatic installation fails, you can manually install the firmware:

```bash
# Create firmware directory
sudo mkdir -p /usr/local/share/firmware/wifi/

# Install BCM43602 firmware
sudo cp payloads/Firmwares/BCMWLAN/BCM43602/brcmfmac43602-pcie_7.35.177.61.bin /usr/local/share/firmware/wifi/

# Install BCM4350 firmware
sudo cp payloads/Firmwares/BCMWLAN/BCM4350/brcmfmac4350-pcie_7.35.180.119.bin /usr/local/share/firmware/wifi/
```

## Configuration

### Boot Arguments

The following boot argument is automatically added by OCLP-R:

```
wlan.pcie.detectsabotage=0
```

### Device Properties

OCLP-R automatically adds the following device properties for detected Wi-Fi cards:

#### BCM43602
```plist
<key>PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)</key>
<dict>
    <key>bcmc-firmware-path</key>
    <string>/usr/local/share/firmware/wifi/brcmfmac43602-pcie_7.35.177.61.bin</string>
    <key>bcmc-firmware-hash</key>
    <data>v0z8I+6VKj2C7zOg9fh4UyAcmPG+0DSHapEPNU83hi0=</data>
    <key>bcmc-srom-slide</key>
    <data>AAAAAA==</data>
</dict>
```

#### BCM4350
```plist
<key>PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)</key>
<dict>
    <key>bcmc-firmware-path</key>
    <string>/usr/local/share/firmware/wifi/brcmfmac4350-pcie_7.35.180.119.bin</string>
    <key>bcmc-firmware-hash</key>
    <data>oRrM3U5fZ4kQNFZ4kQNFZ4kQNFZ4kQNFZ4kQNFZ4kQ=</data>
    <key>bcmc-srom-slide</key>
    <data>QAAAAA==</data>
</dict>
```

## Verification

### Check Kext Loading

To verify that AppleBCMWLANCompanion is loaded:

```bash
kextstat | grep bcmc
```

You should see:
```
science.firewolf.bcmc
```

### Check Logs

To view AppleBCMWLANCompanion logs:

```bash
sudo dmesg | grep bcmc
```

Expected output:
```
[    1.136079]: bcmc: void AppleBCMWLANCompanion::start() PInfo: AppleBCMWLANCompanion 1.0.0 (3369554) starts on Darwin 25.0.0.
[    1.139448]: bcmc: void AppleBCMWLANCompanion::start() PInfo: Build Date: Wed Sep 17 08:34:03 UTC 2025.
[    1.142183]: bcmc: void AppleBCMWLANCompanion::start() PInfo: Copyright (C) 2023-2025 FireWolf @ FireWolf Pl. All Rights Reserved.
```

## Troubleshooting

### Common Issues

1. **Wi-Fi not working after installation**
   - Ensure VT-d is enabled in BIOS
   - Check that firmware files are installed correctly
   - Verify device properties are added to config.plist

2. **Kext not loading**
   - Ensure Lilu is loaded before AppleBCMWLANCompanion
   - Check that the kext is in the correct location
   - Verify macOS version compatibility

3. **Firmware hash verification failed**
   - Re-download firmware files
   - Check file permissions
   - Verify file integrity

### Debug Mode

To enable debug logging, add the following boot argument:

```
-bcmcdbg
```

### Beta Mode

To enable on unsupported systems, add:

```
-bcmcbeta
```

## Compatibility Notes

- **OpenCore Legacy Patcher Users**: If you have applied Wi-Fi-related root patches, you must revert them first before using AppleBCMWLANCompanion
- **System Integrity Protection**: AppleBCMWLANCompanion works with SIP enabled
- **FileVault**: Compatible with FileVault 2
- **Secure Boot**: Works with .im4m Secure Boot

## Credits

- **0xFireWolf**: Original AppleBCMWLANCompanion developer
- **Acidanthera**: Lilu framework
- **OpenCore Legacy Patcher Team**: Integration and testing

## License

AppleBCMWLANCompanion is licensed under BSD-3-Clause.
Copyright (C) 2023-2025 FireWolf @ FireWolf Pl. All Rights Reserved.

## Support

For issues related to AppleBCMWLANCompanion integration in OCLP-R:
- Open an issue on the OCLP-R GitHub repository
- Include system information and logs

For issues related to AppleBCMWLANCompanion itself:
- Visit the [original repository](https://github.com/0xFireWolf/AppleBCMWLANCompanion)
- Join the [InsanelyMac discussion thread](https://www.insanelymac.com/forum/topic/361710-broadcom-fullmac-wi-fi-support-on-macos-sonoma-sequoia-and-tahoe-without-root-patches/)