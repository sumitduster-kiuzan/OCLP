#!/bin/bash

echo "🔧 Installing OCLP-R Privileged Helper Tool"
echo "============================================="

# Check if we're running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root directly."
   echo "   Please run it normally and enter your password when prompted."
   exit 1
fi

# Check if the helper tool exists
if [[ ! -f "./ci_tooling/privileged_helper_tool/com.sumitduster.oclp-r.privileged-helper" ]]; then
    echo "❌ Privileged helper tool not found. Building it first..."
    cd ci_tooling/privileged_helper_tool
    make debug
    cd ../..
fi

echo "📁 Creating directory structure..."
sudo mkdir -p /Library/PrivilegedHelperTools

echo "📋 Copying privileged helper tool..."
sudo cp ./ci_tooling/privileged_helper_tool/com.sumitduster.oclp-r.privileged-helper /Library/PrivilegedHelperTools/

echo "🔐 Setting SUID bit..."
sudo chmod +s /Library/PrivilegedHelperTools/com.sumitduster.oclp-r.privileged-helper

echo "✅ Verifying installation..."
if [[ -f "/Library/PrivilegedHelperTools/com.sumitduster.oclp-r.privileged-helper" ]]; then
    echo "✅ Privileged helper tool installed successfully!"
    echo "   Location: /Library/PrivilegedHelperTools/com.sumitduster.oclp-r.privileged-helper"
    echo ""
    echo "🚀 You can now try installing OpenCore again in OCLP-R GUI!"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
