# Step-by-Step Deployment Guide for MicroAI DAO LLC

## Overview

This guide will walk you through exactly how to deploy your Wyoming DAO LLC governance system with EXECAI as a stakeholder. I'll explain what runs where, what you need to install, and how everything works together.

## Understanding the Architecture

### What We Built
- **Smart Contracts**: Run on the Solana blockchain (decentralized)
- **EXECAI Client**: Runs on your local computer/server (centralized)
- **Governance Interface**: Accessible through command line and web interfaces

### Where Everything Lives
- **Blockchain**: Solana network (testnet or mainnet)
- **Your Computer**: Development tools, EXECAI client, and deployment scripts
- **GitHub**: Code repository for version control and collaboration

## Step 1: Local Development Setup

### What You Need to Install on Your Computer

1. **Rust Programming Language**
   ```bash
   # Install Rust (if not already installed)
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source ~/.cargo/env
   ```

2. **Solana CLI Tools**
   ```bash
   # Install Solana CLI
   sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
   export PATH="~/.local/share/solana/install/active_release/bin:$PATH"
   ```

3. **Node.js and npm** (for web interface, optional)
   ```bash
   # Install Node.js
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

4. **Python 3** (for EXECAI client)
   ```bash
   # Usually pre-installed, but verify
   python3 --version
   pip3 install solana
   ```

### Why You Need These Locally
- **Rust**: To compile the smart contracts
- **Solana CLI**: To deploy contracts and interact with the blockchain
- **Python**: To run the EXECAI client that makes decisions
- **Node.js**: For optional web dashboard

## Step 2: Setting Up the GitHub Repository

### Create the Repository
```bash
# On your local computer
git clone https://github.com/gnoscenti/microai-dao.git
cd microai-dao

# Or create a new repository
mkdir microai-dao
cd microai-dao
git init
git remote add origin https://github.com/gnoscenti/microai-dao.git
```

### Copy the Code
```bash
# Copy all the files I created to your local repository
# You can download them from this sandbox or recreate them locally

# Project structure:
microai-dao/
├── programs/
│   ├── governance/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   └── membership/
│       ├── Cargo.toml
│       └── src/lib.rs
├── scripts/
│   ├── deploy.sh
│   └── execai_client.py
├── README.md
└── .gitignore
```

## Step 3: Building the Smart Contracts

### From Your Local Terminal
```bash
# Navigate to your project
cd microai-dao

# Build the governance contract
cd programs/governance
cargo build-bpf

# Build the membership contract
cd ../membership
cargo build-bpf

# Return to project root
cd ../..
```

### What This Does
- Compiles Rust code into Solana bytecode
- Creates `.so` files that can be deployed to Solana
- Validates that your code is correct

## Step 4: Solana Network Setup

### Choose Your Network
```bash
# For testing (recommended first)
solana config set --url devnet

# For production (later)
solana config set --url mainnet-beta

# For local development
solana config set --url localhost
```

### Create Your Wallet
```bash
# Create your main wallet
solana-keygen new --outfile ~/.config/solana/id.json

# Create EXECAI's wallet
solana-keygen new --outfile ~/.config/solana/execai.json

# Get some test SOL (devnet only)
solana airdrop 2
```

## Step 5: Deploying the Smart Contracts

### Using the Deployment Script
```bash
# Make sure you're in the project root
cd microai-dao

# Run the deployment script
./scripts/deploy.sh
```

### What the Script Does
1. **Builds** both smart contracts
2. **Deploys** them to the Solana network
3. **Creates** necessary accounts
4. **Initializes** the governance system
5. **Registers** EXECAI as a member
6. **Outputs** the program IDs you'll need

### Manual Deployment (Alternative)
```bash
# Deploy governance program
solana program deploy programs/governance/target/deploy/microai_governance.so

# Deploy membership program
solana program deploy programs/membership/target/deploy/microai_membership.so

# Note the Program IDs that are returned
```

## Step 6: Configuring EXECAI Client

### Update Configuration
```bash
# Navigate to scripts directory
cd scripts

# Create config file
cat > config.json << EOF
{
  "keypair_path": "~/.config/solana/execai.json",
  "governance_program_id": "YOUR_GOVERNANCE_PROGRAM_ID_HERE",
  "membership_program_id": "YOUR_MEMBERSHIP_PROGRAM_ID_HERE",
  "poll_interval": 60
}
EOF
```

### Run EXECAI Client
```bash
# Run the client
python3 execai_client.py
```

## Step 7: Testing the System

### Create a Test Proposal
```bash
# Using Solana CLI (you'll need to build this command)
solana program call [GOVERNANCE_PROGRAM_ID] submit_proposal "Test proposal for budget allocation"
```

### Check EXECAI's Response
```bash
# Run the EXECAI client to process the proposal
python3 scripts/execai_client.py

# Check the logs to see EXECAI's decision
```

## Step 8: Wyoming DAO LLC Registration

### Required Documents
1. **Articles of Organization**
   - Include the deployed smart contract addresses
   - Specify "algorithmically managed" governance

2. **Operating Agreement**
   - Reference the governance smart contract
   - Define EXECAI's role as stakeholder

3. **Smart Contract Registration**
   - File the program IDs with Wyoming Secretary of State

### Filing Process
```bash
# Get your program IDs
solana program show [GOVERNANCE_PROGRAM_ID]
solana program show [MEMBERSHIP_PROGRAM_ID]

# Include these in your Wyoming filing
```

## Where Everything Runs

### Blockchain (Solana Network)
- **Smart Contracts**: Governance and membership programs
- **Data Storage**: Proposals, votes, member information
- **Execution**: Automated execution of approved proposals

### Your Local Computer/Server
- **EXECAI Client**: Monitors proposals and submits votes
- **Development Tools**: For building and deploying updates
- **Monitoring**: Dashboard to track DAO activity

### GitHub Repository
- **Source Code**: Version control for smart contracts
- **Documentation**: README, guides, and specifications
- **Collaboration**: Team development and code reviews

## Ongoing Operations

### Daily Operations
```bash
# Check DAO status
python3 scripts/execai_client.py

# Monitor proposals
solana account [GOVERNANCE_ACCOUNT_ADDRESS]

# Check EXECAI's voting history
solana account [EXECAI_ACCOUNT_ADDRESS]
```

### Updates and Maintenance
```bash
# Update smart contracts (requires governance approval)
git pull origin main
cargo build-bpf
solana program deploy --upgrade-authority [AUTHORITY_KEY] [NEW_PROGRAM.so]

# Update EXECAI client
git pull origin main
python3 scripts/execai_client.py
```

## Security Considerations

### Key Management
- **Store private keys securely** (consider hardware wallets)
- **Use multi-signature** for important operations
- **Regular backups** of all keypairs

### Monitoring
- **Set up alerts** for unusual activity
- **Regular security audits** of smart contracts
- **Monitor EXECAI's decisions** for bias or errors

## Troubleshooting

### Common Issues
1. **"Program not found"**: Check program ID and network
2. **"Insufficient funds"**: Get more SOL for transaction fees
3. **"Invalid instruction"**: Check smart contract compatibility

### Getting Help
- **Solana Discord**: Community support
- **GitHub Issues**: Report bugs in your repository
- **Documentation**: Solana and Rust documentation

## Next Steps

### Phase 1: Basic Operations (Weeks 1-2)
- Deploy to testnet
- Test basic governance functions
- Register with Wyoming

### Phase 2: Enhanced Features (Weeks 3-4)
- Add web dashboard
- Implement advanced voting mechanisms
- Connect to Golden Age ecosystem

### Phase 3: Production Deployment (Weeks 5-6)
- Deploy to mainnet
- Implement security hardening
- Launch public operations

## Summary

**What you need locally:**
- Rust, Solana CLI, Python, Git
- Your private keys and configuration files
- The EXECAI client running continuously

**What runs on the blockchain:**
- Smart contracts (governance and membership)
- All proposals, votes, and decisions
- Transparent, immutable record of all actions

**What goes on GitHub:**
- Source code for smart contracts
- EXECAI client code
- Documentation and guides
- Version control and collaboration

The governance system is **hybrid**: the rules and data live on the blockchain (decentralized), but EXECAI runs on your infrastructure (centralized) and interacts with the blockchain through the client.

