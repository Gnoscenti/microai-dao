# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is the MicroAI DAO LLC implementation - a Wyoming DAO LLC with EXECAI as an AI stakeholder. The project combines Solana blockchain smart contracts, Python automation systems, and a React dashboard for governance and revenue generation.

## Core Architecture

### 1. Solana Smart Contracts (Rust)
- **Governance Program** (`lib.rs`): Handles DAO proposals, voting, and execution
- **Membership Program** (conceptual in `/programs/`): Manages DAO members including AI stakeholders
- Built with Solana's BPF (Berkeley Packet Filter) framework
- Uses Borsh serialization for data structures

### 2. Python Automation Systems
- **Revenue Generation** (`revenue_generation_system.py`): Automated revenue systems
- **Content Generation** (`youtube_content_generator.py`): YouTube content automation
- **Client Acquisition** (`client_acquisition_bot.py`): Automated client outreach
- **EXECAI Client** (`execai_client.py`): Interface for AI stakeholder interaction
- **EPI Integration** (`epi_integration_system.py`): Ethical Profitability Index system

### 3. React Dashboard (`microai-dashboard/`)
- **Frontend Framework**: React + TypeScript + Vite
- **Styling**: TailwindCSS
- **Charts**: Recharts library
- **Solana Integration**: @solana/web3.js
- **UI Components**: Custom components with Framer Motion animations

### 4. Configuration & Environment
- **Solana Configuration**: Uses devnet by default (`config.json.example`)
- **Environment Variables**: Dashboard uses Vite environment variables (`.env.example`)
- **Network**: Configurable between devnet, testnet, and mainnet

## Common Development Commands

### Solana Smart Contract Development
```bash
# Build Rust smart contracts
cargo build-bpf

# Deploy smart contracts
./deploy.sh

# Set up Solana environment
solana config set --url devnet
solana-keygen new --outfile ~/.config/solana/id.json
solana airdrop 2  # Get test SOL on devnet
```

### Dashboard Development
```bash
# Navigate to dashboard directory
cd microai-dashboard/

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Python Systems
```bash
# Install Python dependencies
pip3 install solana anchorpy openai requests pandas numpy beautifulsoup4 selenium webdriver-manager schedule flask stripe

# Run EXECAI client
python3 execai_client.py

# Run individual automation systems
python3 revenue_generation_system.py --auto
python3 youtube_content_generator.py --auto
python3 client_acquisition_bot.py --auto
```

### Complete Setup Automation
```bash
# Run the complete automated setup (installs everything)
./automated_execai_setup.sh

# Quick setup without Node.js (if Node.js already installed)
./execai_setup_no_nodejs.sh
```

## Key Configuration Files

### Solana Configuration
- `config.json.example` - Template for Solana program configuration
- Contains program IDs, network settings, and keypair paths
- Copy to `config.json` and update with actual program IDs after deployment

### Dashboard Configuration
- `microai-dashboard/.env.example` - Template for environment variables
- Copy to `microai-dashboard/.env.local` and configure:
  - `VITE_RPC_URL` - Solana RPC endpoint
  - `VITE_PROGRAM_ID` - Deployed governance program ID
  - `VITE_TREASURY_PUBKEY` - Treasury account public key

### Package Dependencies
- `Cargo.toml` - Rust dependencies for smart contracts
- `microai-dashboard/package.json` - Node.js dependencies for dashboard

## Important Development Notes

### Smart Contract Development
- The governance smart contract supports proposals, voting, and member management
- EXECAI is registered as an AI stakeholder with voting rights
- All transactions require proper signer verification
- Smart contracts log all actions for transparency

### Dashboard Integration
- Dashboard fetches data from `src/lib/data.ts` - currently uses mock data
- Replace mock data with real Solana RPC calls for production
- Uses TypeScript interfaces defined in `src/lib/types.ts`
- Configuration centralized in `src/lib/config.ts`

### Python System Architecture
- Systems are designed to run as background processes with `--auto` flag
- EXECAI client evaluates proposals using AI decision logic
- Revenue systems integrate with external APIs (OpenAI, Stripe, etc.)
- All systems log actions for monitoring and debugging

### Security Considerations
- Never commit keypair files (`.json` files are gitignored)
- Use environment variables for API keys and sensitive configuration
- Test on devnet before deploying to mainnet
- The current implementation includes basic security but production deployment requires additional hardening

### Network Configuration
- Default setup uses Solana devnet for testing
- Switch to mainnet for production: `solana config set --url mainnet-beta`
- Ensure sufficient SOL balance for transaction fees
- Program deployment requires significant SOL for rent exemption

## Testing
```bash
# Test Solana setup
./test_setup.sh

# Check program deployment status
solana program show [PROGRAM_ID]

# Check account balances
solana balance

# Test Python systems in debug mode
python3 revenue_generation_system.py --debug
```

## Deployment Process

1. **Setup Environment**: Run `./automated_execai_setup.sh`
2. **Build Contracts**: Use `cargo build-bpf` in program directories
3. **Deploy Contracts**: Run `./deploy.sh` script
4. **Configure Systems**: Update `config.json` with deployed program IDs
5. **Start Automation**: Launch Python systems with `--auto` flag
6. **Deploy Dashboard**: Build and deploy React dashboard to hosting platform

This repository implements a complete DAO ecosystem with blockchain governance, AI integration, and automated revenue generation systems.
