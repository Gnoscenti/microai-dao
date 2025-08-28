#!/bin/bash

# MicroAI DAO LLC - Kubuntu/Ubuntu Installation Script
# Optimized for Kubuntu and Ubuntu systems

set -e

echo "🐧 Installing MicroAI DAO Development Tools on Kubuntu..."
echo "======================================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Update package list
echo "📦 Updating package list..."
sudo apt-get update
echo ""

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
if command_exists node && command_exists npm; then
    echo "   ✅ Node.js already installed: $(node --version)"
    echo "   ✅ npm already installed: $(npm --version)"
else
    echo "   📦 Installing Node.js and npm..."
    
    # Install Node.js 18.x LTS
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    echo "   ✅ Node.js installed: $(node --version)"
    echo "   ✅ npm installed: $(npm --version)"
fi
echo ""

# 4. Install Python 3 and pip
echo "4️⃣  Installing Python 3 and pip..."
if command_exists python3; then
    echo "   ✅ Python 3 already installed: $(python3 --version)"
else
    echo "   📦 Installing Python 3..."
    sudo apt-get install -y python3 python3-pip python3-venv
    echo "   ✅ Python 3 installed: $(python3 --version)"
fi

# Install pip if not present
if command_exists pip3; then
    echo "   ✅ pip3 already installed: $(pip3 --version)"
else
    echo "   📦 Installing pip3..."
    sudo apt-get install -y python3-pip
    echo "   ✅ pip3 installed: $(pip3 --version)"
fi
echo ""

# 5. Install additional development tools
echo "5️⃣  Installing additional development tools..."
echo "   📦 Installing build essentials..."
sudo apt-get install -y build-essential curl wget git

# Install Python packages for EXECAI client
echo "   📦 Installing Python packages for EXECAI..."
pip3 install --user solana base58 requests borsh-construct

echo "   ✅ Development tools installed"
echo ""

# 6. Set up environment variables
echo "6️⃣  Setting up environment variables..."

# Determine shell profile
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
    echo '' >> "$SHELL_PROFILE"
    echo '# Rust environment' >> "$SHELL_PROFILE"
    echo 'source ~/.cargo/env' >> "$SHELL_PROFILE"
    echo "   ✅ Added Rust to PATH"
fi

# Add Solana to PATH
if ! grep -q "solana/install" "$SHELL_PROFILE" 2>/dev/null; then
    echo '' >> "$SHELL_PROFILE"
    echo '# Solana CLI' >> "$SHELL_PROFILE"
    echo 'export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"' >> "$SHELL_PROFILE"
    echo "   ✅ Added Solana to PATH"
fi

# Add Python user bin to PATH
if ! grep -q "/.local/bin" "$SHELL_PROFILE" 2>/dev/null; then
    echo '' >> "$SHELL_PROFILE"
    echo '# Python user packages' >> "$SHELL_PROFILE"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_PROFILE"
    echo "   ✅ Added Python user bin to PATH"
fi

echo ""

# 7. Configure Solana for development
echo "7️⃣  Configuring Solana for development..."

# Source the environment to make solana available
source ~/.cargo/env 2>/dev/null || true
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

if command_exists solana; then
    echo "   📝 Setting up Solana configuration..."
    
    # Set to devnet for testing
    solana config set --url devnet
    echo "   ✅ Solana configured for devnet"
    
    # Create keypair directory if it doesn't exist
    mkdir -p ~/.config/solana
    
    # Create default keypair if it doesn't exist
    if [ ! -f ~/.config/solana/id.json ]; then
        echo "   🔑 Creating default keypair..."
        solana-keygen new --no-passphrase --outfile ~/.config/solana/id.json
        echo "   ✅ Default keypair created"
    fi
    
    # Create EXECAI keypair if it doesn't exist
    if [ ! -f ~/.config/solana/execai.json ]; then
        echo "   🤖 Creating EXECAI keypair..."
        solana-keygen new --no-passphrase --outfile ~/.config/solana/execai.json
        echo "   ✅ EXECAI keypair created"
    fi
    
    echo "   💰 Getting test SOL for development..."
    solana airdrop 2 || echo "   ⚠️  Airdrop failed - you can try again later"
    
else
    echo "   ⚠️  Solana CLI not found in PATH - restart terminal and try again"
fi
echo ""

# 8. Verify installations
echo "8️⃣  Verifying installations..."

# Source the updated profile
source "$SHELL_PROFILE" 2>/dev/null || true

echo "   🔍 Checking all tools..."

if command_exists rustc; then
    echo "   ✅ Rust: $(rustc --version)"
else
    echo "   ❌ Rust: Not found - restart terminal and check"
fi

if command_exists cargo; then
    echo "   ✅ Cargo: $(cargo --version)"
else
    echo "   ❌ Cargo: Not found - restart terminal and check"
fi

if command_exists solana; then
    echo "   ✅ Solana: $(solana --version)"
    echo "   ✅ Solana Config: $(solana config get)"
else
    echo "   ❌ Solana: Not found - restart terminal and check"
fi

if command_exists node; then
    echo "   ✅ Node.js: $(node --version)"
else
    echo "   ❌ Node.js: Not found"
fi

if command_exists npm; then
    echo "   ✅ npm: $(npm --version)"
else
    echo "   ❌ npm: Not found"
fi

if command_exists python3; then
    echo "   ✅ Python 3: $(python3 --version)"
else
    echo "   ❌ Python 3: Not found"
fi

if command_exists pip3; then
    echo "   ✅ pip3: $(pip3 --version)"
else
    echo "   ❌ pip3: Not found"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📋 IMPORTANT - Next steps:"
echo "1. 🔄 RESTART YOUR TERMINAL or run: source $SHELL_PROFILE"
echo "2. 📁 Clone/download the MicroAI DAO repository"
echo "3. 🧪 Run: ./test_setup.sh to verify everything works"
echo "4. 🚀 Run: ./scripts/deploy.sh to deploy your DAO"
echo ""
echo "💡 Your Solana wallet addresses:"
if [ -f ~/.config/solana/id.json ]; then
    echo "   Main wallet: $(solana-keygen pubkey ~/.config/solana/id.json 2>/dev/null || echo 'Error reading keypair')"
fi
if [ -f ~/.config/solana/execai.json ]; then
    echo "   EXECAI wallet: $(solana-keygen pubkey ~/.config/solana/execai.json 2>/dev/null || echo 'Error reading keypair')"
fi
echo ""
echo "🔗 Useful commands:"
echo "   solana balance                    # Check your SOL balance"
echo "   solana airdrop 2                 # Get test SOL (devnet only)"
echo "   solana config get                # Show current configuration"
echo "   cargo --version                  # Check Rust/Cargo version"
echo ""
echo "🆘 If something didn't work:"
echo "   - Restart your terminal first"
echo "   - Check the error messages above"
echo "   - Run individual install commands manually if needed"

