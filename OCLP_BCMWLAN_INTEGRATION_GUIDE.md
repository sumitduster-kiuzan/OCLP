# 📶 AppleBCMWLANCompanion Integration Guide

## Overview
This guide explains how AppleBCMWLANCompanion has been integrated into OpenCore Legacy Patcher 3.0.1+ for automatic Broadcom Wi-Fi support on macOS Tahoe.

## 🎉 What's Been Added

### 1. **Constants Configuration** (`oclp_r/constants.py`)

Added version tracking and path configuration:

```python
## 0xFireWolf
## https://github.com/0xFireWolf/AppleBCMWLANCompanion
self.bcmwlancompanion_version: str = "1.0.0"  # AppleBCMWLANCompanion

# Enable/disable Wi-Fi support
self.enable_wireless_tahoe: bool = True  # Enable AppleBCMWLANCompanion for Tahoe

# Path configuration
@property
def bcmwlancompanion_path(self):
    return self.payload_kexts_path / Path(f"Wifi/AppleBCMWLANCompanion-v{self.bcmwlancompanion_version}.zip")
```

### 2. **Wireless Tahoe Module** (`oclp_r/efi_builder/networking/wireless_tahoe.py`)

New module that handles Broadcom Wi-Fi detection and configuration:

**Features:**
- Automatic detection of supported Broadcom chipsets (BCM43602, BCM4350)
- Intelligent OS version checking (requires Tahoe or newer)
- Automatic kext enabling with proper configuration
- Debug boot argument support
- Comprehensive logging

**Supported Chipsets:**
- `AirPortBrcm43602` (BCM43602) - DW1830, BCM943602BAED, BCM943602CDP, BCM943602CS
- `AirPortBrcm4350` (BCM4350) - DW1820A, BCM94350ZAE

### 3. **Build System Integration** (`oclp_r/efi_builder/build.py`)

Updated build process to include wireless support:

```python
from .networking import (
    wired,
    wireless_tahoe,  # Broadcom Wi-Fi for Tahoe (AppleBCMWLANCompanion)
)

# Build process includes wireless_tahoe.BuildWirelessNetworkingTahoe
```

## 🔧 How It Works

### **Automatic Detection Flow:**

1. **OS Version Check**
   - Verifies detected OS is macOS Tahoe (15.x) or newer
   - Skips if running older macOS versions

2. **Hardware Detection**
   - Detects Wi-Fi chipset if running on actual hardware
   - Checks if chipset is supported (BCM43602 or BCM4350)

3. **Kext Configuration**
   - Enables AppleBCMWLANCompanion.kext
   - Sets minimum kernel version to 23.0.0 (macOS Sonoma+)
   - Adds `-bcmcbeta` boot argument
   - Adds `-bcmcdbg` if debug mode is enabled

4. **Logging**
   - Provides clear feedback about Wi-Fi support
   - Shows detected chipset information
   - Warns about beta status

### **Manual Control:**

Users can control Wi-Fi support through constants:

```python
# Disable Wi-Fi support
self.constants.enable_wireless_tahoe = False

# Enable Wi-Fi support (default)
self.constants.enable_wireless_tahoe = True
```

## 📦 Kext Placement

The kext should be placed at:
```
payloads/Kexts/Wifi/AppleBCMWLANCompanion-v1.0.0.zip
```

**Directory structure:**
```
OCLP/
└── payloads/
    └── Kexts/
        └── Wifi/
            ├── AppleBCMWLANCompanion-v1.0.0.zip
            ├── corecaptureElCap-v1.0.2.zip
            ├── IO80211ElCap-v2.0.1.zip
            └── ...
```

## 🚀 Usage

### **For End Users:**

1. **Automatic Mode** (Recommended)
   - Simply build OpenCore through OCLP-R GUI or CLI
   - System will automatically detect supported Wi-Fi cards
   - AppleBCMWLANCompanion will be enabled if:
     - Running macOS Tahoe or newer
     - Supported Broadcom card is detected
     - `enable_wireless_tahoe` is True (default)

2. **Manual Mode**
   - Edit configuration before building
   - Set `constants.enable_wireless_tahoe = True/False`
   - Rebuild OpenCore configuration

### **For Developers:**

**Download the kext:**
```bash
# Download from GitHub
wget https://github.com/0xFireWolf/AppleBCMWLANCompanion/releases/download/1.0.0/AppleBCMWLANCompanion-1.0.0-RELEASE.zip

# Place in correct location
mkdir -p payloads/Kexts/Wifi
cp AppleBCMWLANCompanion-1.0.0-RELEASE.zip payloads/Kexts/Wifi/AppleBCMWLANCompanion-v1.0.0.zip
```

**Build with Wi-Fi support:**
```bash
cd /path/to/OCLP
python3 Build-Project.command
```

## 🎯 Boot Arguments

### **Automatically Added:**

- **`-bcmcbeta`**: Enable beta features (always added)
- **`-bcmcdbg`**: Enable debug logging (added if `kext_debug` is True)

### **User-Configurable:**

Additional boot arguments can be added via OCLP-R GUI or config.plist:

```
-bcmcoff          # Disable AppleBCMWLANCompanion
-bcmcbeta         # Enable beta features (default)
-bcmcdbg          # Enable debug logging
```

## 📊 Configuration Example

### **OpenCore config.plist entry:**

```xml
<dict>
    <key>Arch</key>
    <string>Any</string>
    <key>BundlePath</key>
    <string>AppleBCMWLANCompanion.kext</string>
    <key>Comment</key>
    <string>AppleBCMWLANCompanion 1.0.0 - Broadcom Wi-Fi for Tahoe</string>
    <key>Enabled</key>
    <true/>
    <key>ExecutablePath</key>
    <string>Contents/MacOS/AppleBCMWLANCompanion</string>
    <key>MinKernel</key>
    <string>23.0.0</string>
    <key>MaxKernel</key>
    <string></string>
    <key>PlistPath</key>
    <string>Contents/Info.plist</string>
</dict>
```

## 🔍 Troubleshooting

### **Wi-Fi Not Detected:**

1. **Check OS Version:**
   ```bash
   sw_vers
   # Should be macOS 15.x (Tahoe) or newer
   ```

2. **Check Wi-Fi Card:**
   ```bash
   ioreg -l | grep -i broadcom
   system_profiler SPPCIDataType | grep -i broadcom
   ```

3. **Check Kext Loading:**
   ```bash
   kextstat | grep -i BCMC
   log show --predicate 'process == "kernel"' --info | grep BCMC
   ```

4. **Enable Debug Mode:**
   - Add `-bcmcdbg` to boot arguments
   - Check system logs for detailed information

### **Build Errors:**

1. **Missing Kext File:**
   - Download from [GitHub](https://github.com/0xFireWolf/AppleBCMWLANCompanion/releases)
   - Place in `payloads/Kexts/Wifi/` directory

2. **Import Errors:**
   - Ensure `wireless_tahoe.py` is in `oclp_r/efi_builder/networking/`
   - Check Python syntax and imports

3. **Version Mismatch:**
   - Update version in `constants.py`
   - Ensure kext filename matches version

## 📈 Performance Impact

### **Benefits:**
- ✅ No root volume modifications
- ✅ Works with SIP enabled
- ✅ Native Apple Wi-Fi driver integration
- ✅ Better power management
- ✅ Easier system updates

### **Considerations:**
- ⚠️ Beta software - test thoroughly
- ⚠️ Requires compatible Broadcom card
- ⚠️ macOS Tahoe or newer only

## 🔄 Update Process

### **Updating the Kext:**

1. Download new version from GitHub
2. Update version number in `constants.py`:
   ```python
   self.bcmwlancompanion_version: str = "1.0.1"  # New version
   ```
3. Replace kext file in `payloads/Kexts/Wifi/`
4. Rebuild OpenCore configuration

### **Updating OCLP-R:**

1. Pull latest changes from repository
2. Rebuild the application:
   ```bash
   python3 Build-Project.command
   ```
3. Wi-Fi support will be automatically included

## 📚 API Reference

### **wireless_tahoe.BuildWirelessNetworkingTahoe**

**Constructor:**
```python
__init__(model: str, global_constants: constants.Constants, config: dict)
```

**Methods:**
- `_build()`: Main build process
- `_on_model()`: Hardware detection and configuration
- `_enable_bcmwlancompanion()`: Enable kext with proper settings

**Properties:**
- `model`: Mac model identifier
- `config`: OpenCore configuration dictionary
- `constants`: Global constants object
- `computer`: Hardware detection object

## 🙏 Credits

### **AppleBCMWLANCompanion:**
- **Developer**: [0xFireWolf](https://github.com/0xFireWolf)
- **Repository**: [AppleBCMWLANCompanion](https://github.com/0xFireWolf/AppleBCMWLANCompanion)
- **License**: BSD-3-Clause
- **Support**: [Ko-fi](https://ko-fi.com/0xFireWolf)

### **Integration:**
- **OpenCore Legacy Patcher**: Sumit Duster
- **Version**: 3.0.1+
- **Date**: October 18, 2025

## ⚠️ Important Notes

1. **Beta Software**: AppleBCMWLANCompanion is in beta
2. **Compatibility**: Only BCM43602 and BCM4350 chips supported
3. **OS Requirement**: macOS Tahoe (15.x) or newer
4. **Testing**: Test thoroughly before daily use
5. **Backup**: Always backup working EFI before updates

## 📞 Support & Resources

- **OCLP-R Issues**: [GitHub Issues](https://github.com/sumitduster/OCLP-R/issues)
- **BCMC Issues**: [GitHub Issues](https://github.com/0xFireWolf/AppleBCMWLANCompanion/issues)
- **OCLP-R Discord**: [Join Discord](https://discord.gg/rqdPgH8xSN)
- **InsanelyMac Thread**: [Discussion](https://www.insanelymac.com)

---

**Last Updated**: October 18, 2025  
**OCLP-R Version**: 3.0.1+  
**AppleBCMWLANCompanion Version**: 1.0.0  
**Status**: Integrated & Beta Testing
