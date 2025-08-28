# Kubuntu Setup Guide for MicroAI DAO LLC

## 🐧 One-Command Installation

For Kubuntu/Ubuntu systems, run this single command to install everything:

```bash
curl -sSL https://raw.githubusercontent.com/gnoscenti/microai-dao/main/install_kubuntu.sh | bash
```

Or download and run locally:

```bash
wget https://raw.githubusercontent.com/gnoscenti/microai-dao/main/install_kubuntu.sh
chmod +x install_kubuntu.sh
./install_kubuntu.sh
```

## 📋 What Gets Installed

### 1. **Rust Programming Language**
- Latest stable Rust compiler
- Cargo package manager
- Automatically added to PATH

### 2. **Solana CLI Tools**
- Solana CLI for blockchain interaction
- Configured for devnet (testing)
- Keypairs created automatically

### 3. **Node.js and npm**
- Node.js 18.x LTS
- npm package manager
- For optional web interfaces

### 4. **Python 3 and pip**
- Python 3 (latest available)
- pip3 package manager
- Required Python packages for EXECAI

### 5. **Development Tools**
- build-essential (gcc, make, etc.)
- curl, wget, git
- All dependencies for compiling

## 🔧 Manual Installation (if script fails)

### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source ~/.cargo/env
```

### Step 3: Install Solana CLI
```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
```

### Step 4: Install Node.js
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Step 5: Install Python and Tools
```bash
sudo apt-get install -y python3 python3-pip python3-venv build-essential
pip3 install --user solana base58 requests borsh-construct
```

### Step 6: Update Shell Profile
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
# Rust environment
source ~/.cargo/env

# Solana CLI
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# Python user packages
export PATH="$HOME/.local/bin:$PATH"
```

## ✅ Verification

After installation, restart your terminal and run:

```bash
# Check all tools
rustc --version
cargo --version
solana --version
node --version
npm --version
python3 --version
pip3 --version

# Check Solana configuration
solana config get
solana balance
```

## 🚀 Quick Start After Installation

1. **Clone the repository:**
```bash
git clone https://github.com/gnoscenti/microai-dao.git
cd microai-dao
```

2. **Test the setup:**
```bash
./test_setup.sh
```

3. **Deploy your DAO:**
```bash
./scripts/deploy.sh
```

4. **Start EXECAI:**
```bash
python3 scripts/execai_client.py
```

## 🔑 Solana Wallet Setup

The script automatically creates:
- **Main wallet**: `~/.config/solana/id.json`
- **EXECAI wallet**: `~/.config/solana/execai.json`

### Get Test SOL
```bash
solana airdrop 2
```

### Check Balance
```bash
solana balance
```

### Switch Networks
```bash
# For testing (default)
solana config set --url devnet

# For production (later)
solana config set --url mainnet-beta
```

## 🛠️ Troubleshooting

### "Command not found" errors
```bash
# Restart terminal or reload shell
source ~/.bashrc
# or
source ~/.zshrc
```

### Solana airdrop fails
```bash
# Try different devnet endpoints
solana config set --url https://api.devnet.solana.com
solana airdrop 1
```

### Rust compilation errors
```bash
# Update Rust
rustup update
```

### Python package errors
```bash
# Install in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install solana base58 requests borsh-construct
```

## 📁 File Locations

After installation, important files are located at:

```
~/.cargo/                    # Rust installation
~/.local/share/solana/       # Solana CLI
~/.config/solana/            # Solana keypairs and config
~/.local/bin/                # Python user packages
```

## 🔒 Security Notes

- **Never share your private keys** (*.json files)
- **Backup your keypairs** before deploying to mainnet
- **Use hardware wallets** for production deployments
- **Keep your system updated** for security patches

## 📞 Getting Help

If you encounter issues:

1. **Check the error messages** - they usually tell you what's wrong
2. **Restart your terminal** - environment variables need to be reloaded
3. **Run commands individually** - to isolate the problem
4. **Check versions** - make sure everything installed correctly

### Common Commands for Debugging
```bash
# Check what's in your PATH
echo $PATH

# Check if tools are found
which rustc
which solana
which python3

# Check Solana configuration
solana config get

# Check available SOL
solana balance
```

