# Updated Commands for gnoscenti

## 🚀 **One-Command Installation for Kubuntu**

```bash
curl -sSL https://raw.githubusercontent.com/gnoscenti/microai-dao/main/install_kubuntu.sh | bash
```

## 📥 **Alternative Download Methods**

### Method 1: Direct Download
```bash
wget https://raw.githubusercontent.com/gnoscenti/microai-dao/main/install_kubuntu.sh
chmod +x install_kubuntu.sh
./install_kubuntu.sh
```

### Method 2: Clone Repository
```bash
git clone https://github.com/gnoscenti/microai-dao.git
cd microai-dao
chmod +x install_kubuntu.sh
./install_kubuntu.sh
```

### Method 3: Download ZIP
```bash
wget https://github.com/gnoscenti/microai-dao/archive/main.zip
unzip main.zip
cd microai-dao-main
chmod +x install_kubuntu.sh
./install_kubuntu.sh
```

## 🎯 **After Installation - Deploy Your DAO**

```bash
# Clone the repository (if not already done)
git clone https://github.com/gnoscenti/microai-dao.git
cd microai-dao

# Test everything works
./test_setup.sh

# Deploy to Solana
./scripts/deploy.sh

# Configure EXECAI with your Program IDs
cp scripts/config.json.example scripts/config.json
# Edit config.json with the Program IDs from deploy.sh output

# Start EXECAI
python3 scripts/execai_client.py
```

## 🔧 **Development Workflow**

```bash
# Make changes to smart contracts
cd programs/governance
# Edit src/lib.rs

# Rebuild and redeploy
cargo build-bpf
cd ../..
./scripts/deploy.sh

# Update EXECAI client if needed
python3 scripts/execai_client.py
```

## 📋 **Repository Setup Commands**

If you want to create your own repository:

```bash
# Create new repository on GitHub first, then:
git clone https://github.com/gnoscenti/microai-dao.git
cd microai-dao

# Make your changes
git add .
git commit -m "Initial MicroAI DAO setup"
git push origin main
```

## 🔑 **Solana Wallet Commands**

```bash
# Check your balance
solana balance

# Get test SOL (devnet only)
solana airdrop 2

# Check your wallet address
solana address

# Check EXECAI wallet address
solana-keygen pubkey ~/.config/solana/execai.json

# Switch networks
solana config set --url devnet     # For testing
solana config set --url mainnet-beta  # For production
```

## 🧪 **Testing Commands**

```bash
# Test the setup
./test_setup.sh

# Check smart contract compilation
cd programs/governance && cargo check
cd ../membership && cargo check

# Verify Solana configuration
solana config get
```

## 🚀 **Production Deployment**

When ready for mainnet:

```bash
# Switch to mainnet
solana config set --url mainnet-beta

# Get real SOL (you'll need to buy this)
# Check balance
solana balance

# Deploy to mainnet
./scripts/deploy.sh

# Update config with mainnet Program IDs
# Start EXECAI for production
python3 scripts/execai_client.py
```

## 📞 **Quick Reference**

| Command | Purpose |
|---------|---------|
| `rustc --version` | Check Rust installation |
| `solana --version` | Check Solana CLI |
| `solana config get` | Show current Solana config |
| `solana balance` | Check SOL balance |
| `cargo build-bpf` | Build smart contracts |
| `./scripts/deploy.sh` | Deploy DAO to blockchain |
| `python3 scripts/execai_client.py` | Start EXECAI |

All commands assume you're in the `microai-dao` directory.

