# 📶 Broadcom Wi-Fi Support for macOS Tahoe

## Overview
This guide explains how to enable legacy Broadcom Wi-Fi cards on macOS Sonoma, Sequoia, and Tahoe using **AppleBCMWLANCompanion** - a revolutionary solution that works **WITHOUT root patches**!

## 🎉 What's New?
Thanks to [0xFireWolf's AppleBCMWLANCompanion](https://github.com/0xFireWolf/AppleBCMWLANCompanion), you can now use legacy Broadcom Wi-Fi cards on macOS Tahoe without requiring root patches!

## ✅ Supported Wi-Fi Cards

| Chip Name | Device ID | Card Models |
|-----------|-----------|-------------|
| **BCM43602** | 0x14E4, 0x43BA | BCM943602BAED, BCM943602CDP, BCM943602CS, DW1830 |
| **BCM4350** | 0x14E4, 0x43A3 | BCM94350ZAE, DW1820A |

## 🔧 Installation Steps

### Step 1: Download AppleBCMWLANCompanion
1. Visit the [AppleBCMWLANCompanion GitHub repository](https://github.com/0xFireWolf/AppleBCMWLANCompanion)
2. Download the latest release (v1.0.0 or newer)
3. Extract the kext file

### Step 2: Install the Kext
1. Copy `AppleBCMWLANCompanion.kext` to your OpenCore EFI folder:
   ```
   EFI/OC/Kexts/AppleBCMWLANCompanion.kext
   ```

### Step 3: Update Your Config.plist
The kext has already been added to your `iMac18_1_Tahoe_Optimized.plist` configuration:

```xml
<dict>
    <key>BundlePath</key>
    <string>AppleBCMWLANCompanion.kext</string>
    <key>Comment</key>
    <string>AppleBCMWLANCompanion 1.0.0 - Broadcom Wi-Fi Support for Tahoe</string>
    <key>Enabled</key>
    <true/>
    <key>MinKernel</key>
    <string>23.0.0</string>
</dict>
```

### Step 4: Boot Arguments
The following boot arguments have been added to your configuration:
- **`-bcmcdbg`**: Enable debug logging (optional, can be removed for production)
- **`-bcmcbeta`**: Enable beta features

## 📊 Supported Systems

| macOS Version | Build Number | Status |
|---------------|--------------|--------|
| **macOS Tahoe** | 26.0 (25A354) | ✅ Supported |
| **macOS Sequoia** | 15.7 (24G222) | ✅ Supported |
| **macOS Sonoma** | 14.8 (23J21) | ⚠️ Not Verified Yet |

## 🎯 Key Features

### ✨ No Root Patches Required!
Unlike the old WiFi patches that required root volume modifications, AppleBCMWLANCompanion works as a simple kext:
- **No SIP modifications needed**
- **No root volume patching**
- **Clean and reversible installation**
- **Easier updates and maintenance**

### 🚀 Better Performance
- Native integration with Apple's new Wi-Fi driver
- Optimized for macOS Tahoe
- Better power management
- Improved stability

### 🔒 Enhanced Security
- Works with System Integrity Protection (SIP)
- No system file modifications
- Safer and more secure

## ⚠️ Current Status
**Important:** As of the latest update (Sep 20, 2025):
- **Status**: Beta Testing
- **Recommendation**: Not recommended for daily use yet
- **Known Issues**: Check the [GitHub repository](https://github.com/0xFireWolf/AppleBCMWLANCompanion) for limitations

## 🔍 Device Properties (Optional)

For advanced users, you can add specific device properties for your Broadcom card. Check the [manual](https://github.com/0xFireWolf/AppleBCMWLANCompanion/tree/main/Documentation) for details.

Common device properties location:
```
PciRoot(0x0)/Pci(0x1C,0x1)/Pci(0x0,0x0)
```

## 🐛 Troubleshooting

### Wi-Fi Not Working?
1. **Verify your card is supported**: Check the supported chips table above
2. **Check kext loading**: Look for AppleBCMWLANCompanion in system logs
3. **Enable debug mode**: Use `-bcmcdbg` boot argument
4. **Check device ID**: Verify your card's device ID matches supported chips

### How to Check Your Card
Run in Terminal:
```bash
ioreg -l | grep -i broadcom
system_profiler SPPCIDataType | grep -i broadcom
```

### Debug Logs
View logs with:
```bash
log show --predicate 'process == "kernel"' --info --debug | grep BCMC
```

## 📚 Additional Resources

- **GitHub Repository**: [AppleBCMWLANCompanion](https://github.com/0xFireWolf/AppleBCMWLANCompanion)
- **Discussion Thread**: Available on [InsanelyMac](https://www.insanelymac.com)
- **Manual**: Check the Documentation folder in the repository
- **Support**: Ko-fi donations at [ko-fi.com/0xFireWolf](https://ko-fi.com/0xFireWolf)

## 🎯 Integration with OCLP-R

Your optimized Tahoe configuration (`iMac18_1_Tahoe_Optimized.plist`) now includes:

1. ✅ **AppleBCMWLANCompanion.kext** - Broadcom Wi-Fi support
2. ✅ **USB-Map-Tahoe.kext** - Optimized USB power management
3. ✅ **AppleALC.kext** - Enhanced audio support
4. ✅ **WhateverGreen.kext** - Graphics optimization
5. ✅ **Lilu.kext** - Required framework

## 🔄 Complete Boot Arguments

Your configuration includes these boot arguments:
```
-lilubetaall        # Lilu beta features
-wegnoegpu          # Disable external GPU
agdpmod=pikera      # GPU switching fix
shikigva=80         # DRM support
unfairgva=1         # DRM support
-wegtree            # WhateverGreen tree
alcid=1             # Audio layout ID
-bcmcdbg            # BCMC debug logging (optional)
-bcmcbeta           # BCMC beta features
```

## ⚠️ Important Notes

1. **Beta Software**: AppleBCMWLANCompanion is currently in beta
2. **Backup First**: Always backup your working EFI before making changes
3. **Check Compatibility**: Verify your Wi-Fi card is on the supported list
4. **Stay Updated**: Check the GitHub repository for updates
5. **Debug Mode**: Remove `-bcmcdbg` for production use

## 🚀 Performance Benefits

Compared to the old WiFi patches:
- ✅ No root volume modifications
- ✅ Faster boot times
- ✅ Better update compatibility
- ✅ Easier to maintain
- ✅ Works with SIP enabled
- ✅ More stable Wi-Fi connection

## 💡 Tips

1. **First Boot**: Wi-Fi may take a few seconds to initialize
2. **Auto-Join**: May need to forget and rejoin networks initially
3. **Updates**: Check for kext updates regularly
4. **Logs**: Keep debug logs enabled until you verify everything works
5. **Fallback**: Keep a backup EFI with your old working configuration

## 🙏 Credits

- **Developer**: [0xFireWolf](https://github.com/0xFireWolf)
- **License**: BSD-3-Clause
- **Copyright**: © 2023-2025 FireWolf @ FireWolf Pl.
- **Support**: Consider supporting the developer on [Ko-fi](https://ko-fi.com/0xFireWolf)

---

**Last Updated**: October 18, 2025  
**AppleBCMWLANCompanion Version**: 1.0.0  
**Status**: Beta Testing  

📶 **Enjoy your working Wi-Fi on macOS Tahoe!** 📶
