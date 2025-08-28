# Quick Start Guide

## 🚀 Get Running in 10 Minutes

### 1. Install Prerequisites (on your local computer)

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
export PATH="~/.local/share/solana/install/active_release/bin:$PATH"

# Verify installations
rustc --version
solana --version
```

### 2. Clone and Setup

```bash
# Clone this repository
git clone https://github.com/gnoscenti/microai-dao.git
cd microai-dao

# Set up Solana for testing
solana config set --url devnet
solana-keygen new --outfile ~/.config/solana/id.json
solana-keygen new --outfile ~/.config/solana/execai.json

# Get test SOL
solana airdrop 2
```

### 3. Build and Deploy

```bash
# Build the smart contracts
cd programs/governance && cargo build-bpf
cd ../membership && cargo build-bpf
cd ../..

# Deploy everything
./scripts/deploy.sh
```

### 4. Configure EXECAI

```bash
# Copy example config
cp scripts/config.json.example scripts/config.json

# Edit config.json with the Program IDs from step 3
# Replace YOUR_GOVERNANCE_PROGRAM_ID_HERE and YOUR_MEMBERSHIP_PROGRAM_ID_HERE
```

### 5. Run EXECAI

```bash
# Start the EXECAI client
python3 scripts/execai_client.py
```

## 🎯 What You Just Did

1. **Built** smart contracts for DAO governance
2. **Deployed** them to Solana devnet
3. **Registered** EXECAI as a stakeholder
4. **Started** EXECAI client to monitor and vote on proposals

## 🔧 Troubleshooting

**"Command not found"**: Make sure you added Solana to your PATH
**"Insufficient funds"**: Run `solana airdrop 2` again
**"Program not found"**: Check your Program IDs in config.json

## 📋 Next Steps

1. **Test**: Create a proposal and watch EXECAI vote
2. **Wyoming**: File your DAO LLC with the Program IDs
3. **Production**: Deploy to mainnet when ready

## 🏗️ Architecture

```
Your Computer          Solana Blockchain
┌─────────────────┐    ┌─────────────────┐
│ EXECAI Client   │───▶│ Governance      │
│ (Python)        │    │ Contract        │
├─────────────────┤    ├─────────────────┤
│ Deploy Scripts  │───▶│ Membership      │
│ (Bash/Rust)     │    │ Contract        │
└─────────────────┘    └─────────────────┘
```

**EXECAI runs on your computer** and talks to **smart contracts on the blockchain**.

