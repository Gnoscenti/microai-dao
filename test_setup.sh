#!/bin/bash

echo "🧪 Testing MicroAI DAO Setup..."

# Test 1: Check if Rust is available
echo "1. Checking Rust..."
if command -v rustc &> /dev/null; then
    echo "   ✅ Rust installed: $(rustc --version)"
else
    echo "   ❌ Rust not found"
    exit 1
fi

# Test 2: Check if Solana CLI is available
echo "2. Checking Solana CLI..."
if command -v solana &> /dev/null; then
    echo "   ✅ Solana CLI installed: $(solana --version)"
else
    echo "   ❌ Solana CLI not found"
    exit 1
fi

# Test 3: Check if smart contracts can be built
echo "3. Testing smart contract compilation..."
cd programs/governance
if cargo check --quiet; then
    echo "   ✅ Governance contract compiles"
else
    echo "   ❌ Governance contract has errors"
    exit 1
fi

cd ../membership
if cargo check --quiet; then
    echo "   ✅ Membership contract compiles"
else
    echo "   ❌ Membership contract has errors"
    exit 1
fi

cd ../..

# Test 4: Check if Python is available
echo "4. Checking Python..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python installed: $(python3 --version)"
else
    echo "   ❌ Python not found"
    exit 1
fi

echo ""
echo "🎉 All tests passed! You're ready to deploy."
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/deploy.sh"
echo "2. Update: scripts/config.json with your Program IDs"
echo "3. Run: python3 scripts/execai_client.py"
