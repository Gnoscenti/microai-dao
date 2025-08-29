#!/bin/bash

echo "🚀 EXECAI DAO SETUP (No Node.js)"
echo "================================"

# Update system
sudo apt update

# Install essential build tools
sudo apt install -y build-essential curl git python3 python3-pip pkg-config libssl-dev

# Install Rust
echo "✅ Installing Rust..."
if ! command -v rustc &> /dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
fi

# Install Solana CLI
echo "✅ Installing Solana CLI..."
if ! command -v solana &> /dev/null; then
    sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
    echo 'export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
fi

# Install Python dependencies
echo "✅ Installing Python dependencies..."
pip3 install --user --upgrade pip
pip3 install --user solana anchorpy openai requests pandas numpy beautifulsoup4 selenium webdriver-manager schedule flask stripe

# Create Solana keypair
echo "✅ Creating Solana keypair..."
solana-keygen new --no-bip39-passphrase --silent --outfile ~/.config/solana/id.json || true

# Set Solana config
solana config set --url https://api.devnet.solana.com
solana config set --keypair ~/.config/solana/id.json

# Verify installations
echo "✅ Verifying installations..."
source ~/.cargo/env
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

echo "Rust version: $(rustc --version)"
echo "Solana version: $(solana --version)"
echo "Python version: $(python3 --version)"

echo ""
echo "🎉 EXECAI DAO SETUP COMPLETE (No Node.js)!"
echo "=========================================="
echo ""
echo "✅ Rust: Ready for smart contract development"
echo "✅ Solana: Ready for blockchain deployment"  
echo "✅ Python: Ready for automation systems"
echo ""
echo "🚀 Next steps:"
echo "1. Get SOL tokens: solana airdrop 2"
echo "2. Deploy contracts: ./deploy.sh"
echo "3. Start revenue systems: python3 revenue_generation_system.py"

