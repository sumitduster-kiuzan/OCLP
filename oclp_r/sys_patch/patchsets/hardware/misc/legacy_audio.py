"""
legacy_audio.py: Legacy Audio detection
"""

from ..base import BaseHardware, HardwareVariant

from ...base import PatchType

from .....constants import Constants
from .....support   import utilities

from .....datasets.os_data import os_data


class LegacyAudio(BaseHardware):

    def __init__(self, xnu_major, xnu_minor, os_build, global_constants: Constants) -> None:
        super().__init__(xnu_major, xnu_minor, os_build, global_constants)


    def name(self) -> str:
        """
        Display name for end users
        """
        return f"{self.hardware_variant()}: Legacy Audio"


    def present(self) -> bool:
        """
        Targeting Realtek Audio and machines without AppleALC
        Enhanced support for Tahoe includes additional models
        """
        # Always present for iMac7,1 and iMac8,1
        if self._computer.real_model in ["iMac7,1", "iMac8,1"]:
            return True
            
        # Extended model list for Tahoe support
        tahoe_models = ["MacBook5,1", "MacBook5,2", "MacBook6,1", "MacBook7,1",
                       "MacBookAir2,1", "MacBookAir3,1", "MacBookAir3,2", "MacBookAir4,1", "MacBookAir4,2",
                       "MacBookPro4,1", "MacBookPro5,1", "MacBookPro5,2", "MacBookPro5,3", "MacBookPro5,4", "MacBookPro5,5",
                       "MacBookPro6,1", "MacBookPro6,2", "MacBookPro7,1", "MacBookPro8,1", "MacBookPro8,2", "MacBookPro8,3",
                       "Macmini3,1", "Macmini4,1", "Macmini5,1", "Macmini5,2", "Macmini5,3",
                       "iMac9,1", "iMac10,1", "iMac11,1", "iMac11,2", "iMac11,3", "iMac12,1", "iMac12,2",
                       "MacPro3,1"]
        
        # Additional models for Tahoe HDA support
        if self._xnu_major >= os_data.tahoe.value:
            tahoe_models.extend([
                "MacBookAir5,1", "MacBookAir5,2",  # 2012 MacBook Air
                "MacBookPro9,1", "MacBookPro9,2", "MacBookPro10,1", "MacBookPro10,2",  # 2012-2013 MacBook Pro
                "Macmini6,1", "Macmini6,2",  # 2012 Mac mini
                "iMac13,1", "iMac13,2", "iMac13,3",  # 2012 iMac
            ])
        
        return (self._computer.real_model in tahoe_models and 
                utilities.check_kext_loaded("as.vit9696.AppleALC") is False)


    def native_os(self) -> bool:
        """
        - iMac7,1 and iMac8,1 last supported in macOS 10.11, El Capitan
        - All other models pre-2012 models last supported in macOS 10.13, High Sierra
        - HDA patches now support up to macOS 15 Tahoe
        """
        if self._computer.real_model in ["iMac7,1", "iMac8,1"]:
            return self._xnu_major < os_data.sierra.value
        # Allow HDA patches on all supported macOS versions including Tahoe
        return False


    def hardware_variant(self) -> HardwareVariant:
        """
        Type of hardware variant
        """
        return HardwareVariant.MISCELLANEOUS


    def _missing_gop_patches(self) -> dict:
        """
        Patches for graphics cards with missing GOP (ie. breaking AppleALC functionality)
        """
        # Use appropriate AppleHDA version based on macOS version
        if self._xnu_major >= os_data.tahoe.value:
            applehda_version = "15.0"  # Tahoe-compatible AppleHDA
        elif self._xnu_major >= os_data.sequoia.value:
            applehda_version = "14.0"  # Sequoia-compatible AppleHDA
        elif self._xnu_major >= os_data.sonoma.value:
            applehda_version = "13.0"  # Sonoma-compatible AppleHDA
        else:
            applehda_version = "10.13.6"  # Legacy version
            
        return {
            "Legacy Non-GOP": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleHDA.kext": applehda_version,
                    },
                },
            },
        }


    def _realtek_audio_patches(self) -> dict:
        """
        Patches for Realtek Audio
        """
        # Use appropriate kext versions based on macOS version
        if self._xnu_major >= os_data.tahoe.value:
            applehda_version = "15.0"      # Tahoe-compatible AppleHDA
            ioaudio_version = "15.0"       # Tahoe-compatible IOAudioFamily
        elif self._xnu_major >= os_data.sequoia.value:
            applehda_version = "14.0"      # Sequoia-compatible AppleHDA
            ioaudio_version = "14.0"       # Sequoia-compatible IOAudioFamily
        elif self._xnu_major >= os_data.sonoma.value:
            applehda_version = "13.0"      # Sonoma-compatible AppleHDA
            ioaudio_version = "13.0"       # Sonoma-compatible IOAudioFamily
        else:
            applehda_version = "10.11.6"   # Legacy versions
            ioaudio_version = "10.11.6"
            
        return {
            "Legacy Realtek": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleHDA.kext":      applehda_version,
                        "IOAudioFamily.kext": ioaudio_version,
                    },
                },
                PatchType.REMOVE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": [
                        "AppleVirtIO.kext",
                        "AppleVirtualGraphics.kext",
                        "AppleVirtualPlatform.kext",
                        "ApplePVPanic.kext",
                        "AppleVirtIOStorage.kext",
                        "AvpFairPlayDriver.kext",
                    ],
                },
            },
        }


    def _tahoe_hda_patches(self) -> dict:
        """
        Tahoe-specific HDA patches for enhanced audio support
        """
        return {
            "Tahoe HDA Support": {
                PatchType.OVERWRITE_SYSTEM_VOLUME: {
                    "/System/Library/Extensions": {
                        "AppleHDA.kext": "15.0",
                        "IOAudioFamily.kext": "15.0",
                    },
                },
                PatchType.MERGE_SYSTEM_VOLUME: {
                    "/System/Library/PrivateFrameworks": {
                        "CoreAudio.framework": "15.0",
                        "AudioToolbox.framework": "15.0",
                    },
                },
            },
        }

    def patches(self) -> dict:
        """
        Patches for legacy audio
        """
        if self.native_os() is True:
            return {}

        # Special handling for Tahoe
        if self._xnu_major >= os_data.tahoe.value:
            if self._computer.real_model in ["iMac7,1", "iMac8,1"]:
                return self._realtek_audio_patches()
            else:
                # Combine missing GOP patches with Tahoe-specific patches
                patches = self._missing_gop_patches()
                patches.update(self._tahoe_hda_patches())
                return patches

        # Legacy handling for older macOS versions
        if self._computer.real_model in ["iMac7,1", "iMac8,1"]:
            return self._realtek_audio_patches()
        return self._missing_gop_patches()