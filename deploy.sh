#!/bin/bash

# MicroAI DAO LLC Deployment Script
# This script builds and deploys the MicroAI DAO LLC smart contracts to Solana

set -e

# Check if Solana CLI is installed
if ! command -v solana &> /dev/null; then
    echo "Solana CLI not found. Please install it first."
    exit 1
fi

# Check if we're connected to a Solana cluster
CLUSTER_URL=$(solana config get | grep "RPC URL" | awk '{print $3}')
if [ -z "$CLUSTER_URL" ]; then
    echo "No Solana cluster configured. Setting up localnet..."
    solana config set --url localhost
fi

# Create keypairs if they don't exist
if [ ! -f ~/.config/solana/id.json ]; then
    echo "Creating default keypair..."
    solana-keygen new --no-passphrase
fi

if [ ! -f ~/.config/solana/execai.json ]; then
    echo "Creating EXECAI keypair..."
    solana-keygen new --no-passphrase -o ~/.config/solana/execai.json
fi

# Build the programs
echo "Building governance program..."
cd "$(dirname "$0")/../programs/governance"
cargo build-bpf

echo "Building membership program..."
cd "$(dirname "$0")/../programs/membership"
cargo build-bpf

# Deploy the programs
echo "Deploying governance program..."
cd "$(dirname "$0")/../programs/governance"
GOVERNANCE_PROGRAM_ID=$(solana program deploy --program-id ~/.config/solana/governance-program-id.json ./target/deploy/microai_governance.so | grep "Program Id" | awk '{print $3}')

echo "Deploying membership program..."
cd "$(dirname "$0")/../programs/membership"
MEMBERSHIP_PROGRAM_ID=$(solana program deploy --program-id ~/.config/solana/membership-program-id.json ./target/deploy/microai_membership.so | grep "Program Id" | awk '{print $3}')

echo "Programs deployed successfully!"
echo "Governance Program ID: $GOVERNANCE_PROGRAM_ID"
echo "Membership Program ID: $MEMBERSHIP_PROGRAM_ID"

# Create accounts for the programs
echo "Creating governance state account..."
GOVERNANCE_ACCOUNT=$(solana-keygen new --no-passphrase -o ~/.config/solana/governance-account.json | grep "pubkey" | awk '{print $3}')
solana create-account $GOVERNANCE_ACCOUNT 1 1024 $GOVERNANCE_PROGRAM_ID

echo "Creating membership state account..."
MEMBERSHIP_ACCOUNT=$(solana-keygen new --no-passphrase -o ~/.config/solana/membership-account.json | grep "pubkey" | awk '{print $3}')
solana create-account $MEMBERSHIP_ACCOUNT 1 1024 $MEMBERSHIP_PROGRAM_ID

echo "Creating EXECAI member account..."
EXECAI_ACCOUNT=$(solana-keygen new --no-passphrase -o ~/.config/solana/execai-account.json | grep "pubkey" | awk '{print $3}')
solana create-account $EXECAI_ACCOUNT 1 1024 $MEMBERSHIP_PROGRAM_ID

echo "Accounts created successfully!"
echo "Governance Account: $GOVERNANCE_ACCOUNT"
echo "Membership Account: $MEMBERSHIP_ACCOUNT"
echo "EXECAI Account: $EXECAI_ACCOUNT"

# Initialize the programs
echo "Initializing governance program..."
# TODO: Add command to initialize governance program

echo "Initializing membership program..."
# TODO: Add command to initialize membership program

echo "Registering EXECAI as a member..."
# TODO: Add command to register EXECAI as a member

echo "MicroAI DAO LLC deployed successfully!"

