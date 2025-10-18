#!/usr/bin/env python3
"""
Tahoe Optimization Script for iMac18,1
Optimizes OpenCore Legacy Patcher configuration for macOS Tahoe (15.x)
"""

import os
import sys
import plistlib
from pathlib import Path

class TahoeOptimizer:
    def __init__(self):
        self.config_path = Path("iMac18_1_Tahoe_Optimized.plist")
        self.optimizations_applied = []
        
    def optimize_for_tahoe(self):
        """Apply Tahoe-specific optimizations"""
        print("🚀 Starting Tahoe optimizations for iMac18,1...")
        
        # Load the configuration
        if not self.config_path.exists():
            print(f"❌ Configuration file not found: {self.config_path}")
            return False
            
        with open(self.config_path, 'rb') as f:
            config = plistlib.load(f)
        
        # Apply optimizations
        self._optimize_usb_power_management(config)
        self._optimize_graphics_settings(config)
        self._optimize_audio_settings(config)
        self._optimize_kernel_settings(config)
        self._optimize_nvram_settings(config)
        
        # Save optimized configuration
        with open(self.config_path, 'wb') as f:
            plistlib.dump(config, f)
        
        print("✅ Tahoe optimizations completed!")
        self._print_optimizations()
        return True
    
    def _optimize_usb_power_management(self, config):
        """Optimize USB power management for Tahoe"""
        print("🔌 Optimizing USB power management...")
        
        # Enable USB-Map-Tahoe.kext
        if 'Kernel' in config and 'Add' in config['Kernel']:
            for kext in config['Kernel']['Add']:
                if kext.get('BundlePath') == 'USB-Map-Tahoe.kext':
                    kext['Enabled'] = True
                    kext['MinKernel'] = '25.0.0'  # Tahoe kernel version
                    self.optimizations_applied.append("USB-Map-Tahoe.kext enabled for Tahoe")
                    break
        
        # Add USB power management settings
        if 'DeviceProperties' not in config:
            config['DeviceProperties'] = {}
        if 'Add' not in config['DeviceProperties']:
            config['DeviceProperties']['Add'] = {}
        
        # Add USB power optimization properties
        usb_props = {
            'kUSBSleepPortCurrentLimit': 1000,  # mA
            'kUSBSleepPowerSupply': 1500,       # mA
            'kUSBWakePortCurrentLimit': 1200,   # mA
            'kUSBWakePowerSupply': 1700,        # mA
        }
        
        # Apply to USB controller
        usb_controller = 'PciRoot(0x0)/Pci(0x14,0x0)'
        if usb_controller not in config['DeviceProperties']['Add']:
            config['DeviceProperties']['Add'][usb_controller] = {}
        
        config['DeviceProperties']['Add'][usb_controller].update(usb_props)
        self.optimizations_applied.append("USB power management optimized for Tahoe")
    
    def _optimize_graphics_settings(self, config):
        """Optimize graphics settings for Intel Iris Plus Graphics 640"""
        print("🎨 Optimizing graphics settings...")
        
        # Ensure proper graphics configuration
        if 'DeviceProperties' not in config:
            config['DeviceProperties'] = {}
        if 'Add' not in config['DeviceProperties']:
            config['DeviceProperties']['Add'] = {}
        
        # Intel Iris Plus Graphics 640 configuration
        igpu_path = 'PciRoot(0x0)/Pci(0x2,0x0)'
        if igpu_path not in config['DeviceProperties']['Add']:
            config['DeviceProperties']['Add'][igpu_path] = {}
        
        # Optimized framebuffer settings for Tahoe
        graphics_settings = {
            'AAPL,ig-platform-id': 'BwCbPg==',  # Kaby Lake iGPU
            'device-id': 'lqIAAA==',            # Intel Iris Plus Graphics 640
            'framebuffer-patch-enable': 'AQAAAA==',
            'framebuffer-stolenmem': 'AACQAA==',  # 64MB stolen memory
            'framebuffer-fbmem': 'AACQAA==',     # 64MB framebuffer
            'enable-hdmi20': 'AQAAAA==',         # Enable HDMI 2.0
            'enable-dpcd-max-link-rate': 'FgAAAA==',  # 4.32 Gbps
            'disable-external-gpu': 'AQAAAA==',  # Disable external GPU
        }
        
        config['DeviceProperties']['Add'][igpu_path].update(graphics_settings)
        self.optimizations_applied.append("Intel Iris Plus Graphics 640 optimized for Tahoe")
    
    def _optimize_audio_settings(self, config):
        """Optimize audio settings for Tahoe"""
        print("🎵 Optimizing audio settings...")
        
        # Add Tahoe-specific audio kexts
        if 'Kernel' not in config:
            config['Kernel'] = {}
        if 'Add' not in config['Kernel']:
            config['Kernel']['Add'] = []
        
        # Add AppleALC for audio
        applealc_kext = {
            'Arch': 'Any',
            'BundlePath': 'AppleALC.kext',
            'Comment': 'AppleALC 1.6.3 - Tahoe Audio Support',
            'Enabled': True,
            'ExecutablePath': 'Contents/MacOS/AppleALC',
            'MaxKernel': '',
            'MinKernel': '',
            'PlistPath': 'Contents/Info.plist'
        }
        
        # Check if AppleALC is already present
        applealc_exists = False
        for kext in config['Kernel']['Add']:
            if kext.get('BundlePath') == 'AppleALC.kext':
                kext['Enabled'] = True
                kext['Comment'] = 'AppleALC 1.6.3 - Tahoe Audio Support'
                applealc_exists = True
                break
        
        if not applealc_exists:
            config['Kernel']['Add'].append(applealc_kext)
        
        self.optimizations_applied.append("Audio settings optimized for Tahoe")
    
    def _optimize_kernel_settings(self, config):
        """Optimize kernel settings for Tahoe"""
        print("⚙️ Optimizing kernel settings...")
        
        if 'Kernel' not in config:
            config['Kernel'] = {}
        if 'Quirks' not in config['Kernel']:
            config['Kernel']['Quirks'] = {}
        
        # Tahoe-specific kernel quirks
        kernel_quirks = {
            'DisableLinkeditJettison': True,  # Required for Lilu plugins
            'PanicNoKextDump': True,          # Cleaner panic logs
            'ProvideCurrentCpuInfo': False,   # Not needed for iMac18,1
            'ThirdPartyDrives': False,        # Not needed for iMac18,1
            'XhciPortLimit': False,           # Not needed for iMac18,1
        }
        
        config['Kernel']['Quirks'].update(kernel_quirks)
        self.optimizations_applied.append("Kernel settings optimized for Tahoe")
    
    def _optimize_nvram_settings(self, config):
        """Optimize NVRAM settings for Tahoe"""
        print("💾 Optimizing NVRAM settings...")
        
        if 'NVRAM' not in config:
            config['NVRAM'] = {}
        if 'Add' not in config['NVRAM']:
            config['NVRAM']['Add'] = {}
        
        # Tahoe-optimized boot arguments
        boot_args = [
            '-lilubetaall',      # Enable Lilu beta features
            '-wegnoegpu',        # Disable external GPU
            'agdpmod=pikera',    # Fix GPU switching
            'shikigva=80',       # DRM support
            'unfairgva=1',       # DRM support
            '-wegtree',          # WhateverGreen tree
            'alcid=1',           # Audio layout ID
        ]
        
        # Apply to both NVRAM sections
        for nvram_key in ['4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102', '7C436110-AB2A-4BBB-A880-FE41995C9F82']:
            if nvram_key not in config['NVRAM']['Add']:
                config['NVRAM']['Add'][nvram_key] = {}
            
            config['NVRAM']['Add'][nvram_key]['boot-args'] = ' '.join(boot_args)
        
        self.optimizations_applied.append("NVRAM settings optimized for Tahoe")
    
    def _print_optimizations(self):
        """Print applied optimizations"""
        print("\n🎯 Applied Tahoe Optimizations:")
        print("=" * 50)
        for i, optimization in enumerate(self.optimizations_applied, 1):
            print(f"{i:2d}. {optimization}")
        print("=" * 50)
        print(f"\n📁 Optimized configuration saved to: {self.config_path}")
        print("\n💡 Next steps:")
        print("   1. Use this configuration with OpenCore Legacy Patcher")
        print("   2. Build and install OpenCore with the optimized settings")
        print("   3. Enjoy enhanced performance on macOS Tahoe!")

def main():
    """Main function"""
    print("🍰 Tahoe Optimization Script for iMac18,1")
    print("=" * 50)
    
    optimizer = TahoeOptimizer()
    
    if optimizer.optimize_for_tahoe():
        print("\n✅ Optimization completed successfully!")
        return 0
    else:
        print("\n❌ Optimization failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
