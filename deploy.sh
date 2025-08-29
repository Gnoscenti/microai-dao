#!/bin/bash
set +H
echo "🚀 Deploying EXECAI DAO Smart Contracts"
echo "======================================"

# Check SOL balance
BALANCE=$(solana balance | grep -o '[0-9.]*' | head -1)
echo "Current SOL balance: $BALANCE SOL"

if (( $(echo "$BALANCE < 0.5" | bc -l) )); then
    echo "Getting SOL tokens for deployment..."
    solana airdrop 2
fi

# Build contracts
echo "Building smart contracts..."
if command -v anchor &> /dev/null; then
    echo "Building with Anchor..."
    anchor build
else
    echo "Building with cargo..."
    cd programs/governance && cargo build-bpf --manifest-path Cargo.toml --bpf-out-dir ../../target/deploy
    cd ../membership && cargo build-bpf --manifest-path Cargo.toml --bpf-out-dir ../../target/deploy
    cd ../..
fi

# Deploy contracts
echo "Deploying contracts..."
if command -v anchor &> /dev/null; then
    echo "Deploying with Anchor..."
    anchor deploy
else
    echo "Deploying manually..."
    if [ -f "target/deploy/governance.so" ]; then
        echo "Deploying governance contract..."
        GOVERNANCE_ID=$(solana program deploy target/deploy/governance.so | grep "Program Id:" | awk '{print $3}')
        echo "Governance Program ID: $GOVERNANCE_ID"
    fi
    if [ -f "target/deploy/membership.so" ]; then
        echo "Deploying membership contract..."
        MEMBERSHIP_ID=$(solana program deploy target/deploy/membership.so | grep "Program Id:" | awk '{print $3}')
        echo "Membership Program ID: $MEMBERSHIP_ID"
    fi
fi

echo ""
echo "✅ Deployment complete!"
echo "======================================"
echo "Update your dashboard .env.local with the Program IDs shown above"
echo "Then run: python3 execai_client.py --test"
set -H
