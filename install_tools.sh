#!/bin/bash

# MicroAI DAO LLC - Development Tools Installation Script
# This script installs all required tools for developing and deploying the DAO

set -e

echo "🚀 Installing MicroAI DAO Development Tools..."
echo "================================================"

# Detect operating system
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

echo "Detected OS: $OS"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Install Rust Programming Language
echo "1️⃣  Installing Rust Programming Language..."
if command_exists rustc; then
    echo "   ✅ Rust already installed: $(rustc --version)"
else
    echo "   📦 Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
    echo "   ✅ Rust installed: $(rustc --version)"
fi
echo ""

# 2. Install Solana CLI Tools
echo "2️⃣  Installing Solana CLI Tools..."
if command_exists solana; then
    echo "   ✅ Solana CLI already installed: $(solana --version)"
else
    echo "   📦 Installing Solana CLI..."
    sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
    export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
    echo "   ✅ Solana CLI installed: $(solana --version)"
fi
echo ""

# 3. Install Node.js and npm
echo "3️⃣  Installing Node.js and npm..."
if command_exists node; then
    echo "   ✅ Node.js already installed: $(node --version)"
    echo "   ✅ npm already installed: $(npm --version)"
else
    echo "   📦 Installing Node.js and npm..."
    
    if [[ "$OS" == "linux" ]]; then
        # Ubuntu/Debian
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif [[ "$OS" == "macos" ]]; then
        # macOS - using Homebrew
        if command_exists brew; then
            brew install node
        else
            echo "   ⚠️  Please install Homebrew first, then run: brew install node"
            echo "   Or download Node.js from: https://nodejs.org/"
        fi
    elif [[ "$OS" == "windows" ]]; then
        echo "   ⚠️  Please download Node.js from: https://nodejs.org/"
        echo "   Or use chocolatey: choco install nodejs"
    fi
    
    if command_exists node; then
        echo "   ✅ Node.js installed: $(node --version)"
        echo "   ✅ npm installed: $(npm --version)"
    fi
fi
echo ""

# 4. Install/Verify Python 3
echo "4️⃣  Checking Python 3..."
if command_exists python3; then
    echo "   ✅ Python 3 already installed: $(python3 --version)"
else
    echo "   📦 Installing Python 3..."
    
    if [[ "$OS" == "linux" ]]; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    elif [[ "$OS" == "macos" ]]; then
        # macOS - using Homebrew
        if command_exists brew; then
            brew install python3
        else
            echo "   ⚠️  Please install Homebrew first, then run: brew install python3"
            echo "   Or download Python from: https://www.python.org/"
        fi
    elif [[ "$OS" == "windows" ]]; then
        echo "   ⚠️  Please download Python from: https://www.python.org/"
        echo "   Or use chocolatey: choco install python3"
    fi
    
    if command_exists python3; then
        echo "   ✅ Python 3 installed: $(python3 --version)"
    fi
fi

# Install Python packages for EXECAI client
if command_exists pip3; then
    echo "   📦 Installing Python packages..."
    pip3 install solana base58 requests
    echo "   ✅ Python packages installed"
else
    echo "   ⚠️  pip3 not found. Please install pip3 manually."
fi
echo ""

# 5. Set up environment variables
echo "5️⃣  Setting up environment variables..."

# Create or update shell profile
SHELL_PROFILE=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_PROFILE="$HOME/.bashrc"
else
    SHELL_PROFILE="$HOME/.profile"
fi

echo "   📝 Updating $SHELL_PROFILE..."

# Add Rust to PATH
if ! grep -q "cargo/env" "$SHELL_PROFILE" 2>/dev/null; then
    echo 'source ~/.cargo/env' >> "$SHELL_PROFILE"
    echo "   ✅ Added Rust to PATH"
fi

# Add Solana to PATH
if ! grep -q "solana/install" "$SHELL_PROFILE" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"' >> "$SHELL_PROFILE"
    echo "   ✅ Added Solana to PATH"
fi

echo ""

# 6. Verify installations
echo "6️⃣  Verifying installations..."

# Source the updated profile
source "$SHELL_PROFILE" 2>/dev/null || true

echo "   🔍 Checking all tools..."

if command_exists rustc; then
    echo "   ✅ Rust: $(rustc --version)"
else
    echo "   ❌ Rust: Not found"
fi

if command_exists solana; then
    echo "   ✅ Solana: $(solana --version)"
else
    echo "   ❌ Solana: Not found"
fi

if command_exists node; then
    echo "   ✅ Node.js: $(node --version)"
else
    echo "   ⚠️  Node.js: Not found (optional)"
fi

if command_exists npm; then
    echo "   ✅ npm: $(npm --version)"
else
    echo "   ⚠️  npm: Not found (optional)"
fi

if command_exists python3; then
    echo "   ✅ Python 3: $(python3 --version)"
else
    echo "   ❌ Python 3: Not found"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Restart your terminal or run: source $SHELL_PROFILE"
echo "2. Clone the MicroAI DAO repository"
echo "3. Run: ./test_setup.sh to verify everything works"
echo "4. Run: ./scripts/deploy.sh to deploy your DAO"
echo ""
echo "💡 If any tool failed to install, please install it manually:"
echo "   - Rust: https://rustup.rs/"
echo "   - Solana: https://docs.solana.com/cli/install-solana-cli-tools"
echo "   - Node.js: https://nodejs.org/"
echo "   - Python: https://www.python.org/"

