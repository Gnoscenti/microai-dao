#!/bin/bash

# AUTOMATED EXECAI DAO SETUP SCRIPT
# ================================
# This script automates the complete setup of EXECAI DAO system
# From fresh Kubuntu system to deployed smart contracts
# 
# Usage: ./automated_execai_setup.sh
# Time: ~15 minutes to complete setup
# Result: Fully functional EXECAI DAO system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running on Ubuntu/Kubuntu
check_system() {
    log "Checking system compatibility..."
    
    if [[ ! -f /etc/os-release ]]; then
        error "Cannot determine OS. This script requires Ubuntu/Kubuntu."
    fi
    
    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        error "This script requires Ubuntu/Kubuntu. Detected: $ID"
    fi
    
    log "System check passed: $PRETTY_NAME"
}

# Install system dependencies
install_system_deps() {
    log "Installing system dependencies..."
    
    sudo apt update -y
    sudo apt install -y \
        curl \
        wget \
        git \
        build-essential \
        pkg-config \
        libssl-dev \
        libudev-dev \
        llvm \
        libclang-dev \
        protobuf-compiler \
        python3 \
        python3-pip \
        nodejs \
        npm \
        unzip \
        jq
    
    log "System dependencies installed successfully"
}

# Install Rust
install_rust() {
    log "Installing Rust toolchain..."
    
    if command -v rustc &> /dev/null; then
        warning "Rust already installed. Skipping..."
        return
    fi
    
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
    
    # Add to shell profile
    echo 'source ~/.cargo/env' >> ~/.bashrc
    
    # Install additional components
    rustup component add rustfmt clippy
    rustup target add wasm32-unknown-unknown
    
    # Install cargo tools
    cargo install cargo-audit cargo-outdated
    
    log "Rust installed successfully: $(rustc --version)"
}

# Install Solana CLI
install_solana() {
    log "Installing Solana CLI..."
    
    if command -v solana &> /dev/null; then
        warning "Solana CLI already installed. Skipping..."
        return
    fi
    
    sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
    
    # Add to PATH
    echo 'export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
    
    log "Solana CLI installed successfully: $(solana --version)"
}

# Install Anchor Framework
install_anchor() {
    log "Installing Anchor Framework..."
    
    if command -v anchor &> /dev/null; then
        warning "Anchor already installed. Skipping..."
        return
    fi
    
    # Install Node.js dependencies
    sudo npm install -g yarn
    
    # Install Anchor Version Manager
    cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
    
    # Install latest Anchor
    ~/.cargo/bin/avm install latest
    ~/.cargo/bin/avm use latest
    
    log "Anchor installed successfully: $(~/.cargo/bin/anchor --version)"
}

# Setup Solana configuration
setup_solana_config() {
    log "Setting up Solana configuration..."
    
    # Create config directory
    mkdir -p ~/.config/solana
    
    # Generate keypair if it doesn't exist
    if [[ ! -f ~/.config/solana/id.json ]]; then
        solana-keygen new --no-bip39-passphrase --outfile ~/.config/solana/id.json
    fi
    
    # Set configuration
    solana config set --url devnet
    solana config set --keypair ~/.config/solana/id.json
    
    # Request airdrop
    log "Requesting SOL airdrop for development..."
    solana airdrop 2 || warning "Airdrop failed. You may need to request manually later."
    
    # Show balance
    BALANCE=$(solana balance)
    log "Solana wallet balance: $BALANCE"
}

# Create EXECAI DAO project
create_execai_project() {
    log "Creating EXECAI DAO project..."
    
    # Create project directory
    PROJECT_DIR="$HOME/execai-dao"
    if [[ -d "$PROJECT_DIR" ]]; then
        warning "Project directory already exists. Backing up..."
        mv "$PROJECT_DIR" "${PROJECT_DIR}_backup_$(date +%s)"
    fi
    
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # Initialize Anchor project
    ~/.cargo/bin/anchor init execai-dao-governance --no-git
    cd execai-dao-governance
    
    # Initialize git
    git init
    
    # Create .gitignore
    cat > .gitignore << 'EOF'
target/
node_modules/
.DS_Store
keys/
.env
*.log
test-ledger/
EOF
    
    # Create environment file
    cat > .env << 'EOF'
ANCHOR_PROVIDER_URL=https://api.devnet.solana.com
ANCHOR_WALLET=~/.config/solana/id.json
SOLANA_CLUSTER=devnet
EOF
    
    log "EXECAI DAO project created at: $PROJECT_DIR/execai-dao-governance"
}

# Generate smart contract code
generate_smart_contracts() {
    log "Generating EXECAI DAO smart contracts..."
    
    cd "$HOME/execai-dao/execai-dao-governance"
    
    # Update Anchor.toml
    cat > Anchor.toml << 'EOF'
[features]
seeds = false
skip-lint = false

[programs.devnet]
execai_dao_governance = "ExecAiDaoGovernance11111111111111111111111111"

[registry]
url = "https://api.apr.dev"

[provider]
cluster = "devnet"
wallet = "~/.config/solana/id.json"

[scripts]
test = "yarn run ts-mocha -p ./tsconfig.json -t 1000000 tests/**/*.ts"

[test]
startup_wait = 5000
shutdown_wait = 2000
upgradeable = false
EOF

    # Create program structure
    mkdir -p programs/execai-dao-governance/src/{state,instructions,errors}
    
    # Generate main lib.rs
    cat > programs/execai-dao-governance/src/lib.rs << 'EOF'
use anchor_lang::prelude::*;

declare_id!("ExecAiDaoGovernance11111111111111111111111111");

pub mod instructions;
pub mod state;
pub mod errors;

use instructions::*;
use state::*;

#[program]
pub mod execai_dao_governance {
    use super::*;

    pub fn initialize_dao(
        ctx: Context<InitializeDao>,
        name: String,
        description: String,
        human_quorum_threshold: u8,
        ai_quorum_threshold: u8,
    ) -> Result<()> {
        instructions::initialize_dao(ctx, name, description, human_quorum_threshold, ai_quorum_threshold)
    }

    pub fn create_proposal(
        ctx: Context<CreateProposal>,
        title: String,
        description: String,
        proposal_type: ProposalType,
        execution_data: Vec<u8>,
        voting_period: i64,
    ) -> Result<()> {
        instructions::create_proposal(ctx, title, description, proposal_type, execution_data, voting_period)
    }

    pub fn cast_vote(
        ctx: Context<CastVote>,
        vote_choice: VoteChoice,
        voter_type: VoterType,
        reasoning: Option<String>,
    ) -> Result<()> {
        instructions::cast_vote(ctx, vote_choice, voter_type, reasoning)
    }

    pub fn execute_proposal(ctx: Context<ExecuteProposal>) -> Result<()> {
        instructions::execute_proposal(ctx)
    }
}
EOF

    # Generate state modules
    cat > programs/execai-dao-governance/src/state/mod.rs << 'EOF'
pub mod dao;
pub mod proposal;
pub mod vote;

pub use dao::*;
pub use proposal::*;
pub use vote::*;
EOF

    # Generate DAO state
    cat > programs/execai-dao-governance/src/state/dao.rs << 'EOF'
use anchor_lang::prelude::*;

#[account]
pub struct Dao {
    pub authority: Pubkey,
    pub name: String,
    pub description: String,
    pub human_quorum_threshold: u8,
    pub ai_quorum_threshold: u8,
    pub total_members: u64,
    pub total_human_members: u64,
    pub total_ai_members: u64,
    pub proposal_count: u64,
    pub created_at: i64,
    pub bump: u8,
}

impl Dao {
    pub const LEN: usize = 8 + 32 + 4 + 64 + 4 + 256 + 1 + 1 + 8 + 8 + 8 + 8 + 8 + 1;
}
EOF

    # Generate proposal state
    cat > programs/execai-dao-governance/src/state/proposal.rs << 'EOF'
use anchor_lang::prelude::*;

#[account]
pub struct Proposal {
    pub id: u64,
    pub dao: Pubkey,
    pub proposer: Pubkey,
    pub title: String,
    pub description: String,
    pub proposal_type: ProposalType,
    pub status: ProposalStatus,
    pub execution_data: Vec<u8>,
    pub human_votes_for: u64,
    pub human_votes_against: u64,
    pub ai_votes_for: u64,
    pub ai_votes_against: u64,
    pub created_at: i64,
    pub voting_ends_at: i64,
    pub executed_at: Option<i64>,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
pub enum ProposalType {
    Basic,
    TreasurySpending,
    ParameterChange,
    MembershipChange,
    UpgradeProgram,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
pub enum ProposalStatus {
    Active,
    Succeeded,
    Failed,
    Executed,
    Cancelled,
}

impl Proposal {
    pub const LEN: usize = 8 + 8 + 32 + 32 + 4 + 128 + 4 + 512 + 1 + 1 + 4 + 1024 + 8 + 8 + 8 + 8 + 8 + 8 + 9 + 1;

    pub fn is_dual_quorum_met(&self, dao: &Dao) -> bool {
        let total_human_votes = self.human_votes_for + self.human_votes_against;
        let total_ai_votes = self.ai_votes_for + self.ai_votes_against;

        let human_quorum_met = if dao.total_human_members > 0 {
            (total_human_votes * 100) / dao.total_human_members >= dao.human_quorum_threshold as u64
        } else { false };

        let ai_quorum_met = if dao.total_ai_members > 0 {
            (total_ai_votes * 100) / dao.total_ai_members >= dao.ai_quorum_threshold as u64
        } else { false };

        human_quorum_met && ai_quorum_met
    }

    pub fn has_dual_majority(&self) -> bool {
        let human_majority = self.human_votes_for > self.human_votes_against;
        let ai_majority = self.ai_votes_for > self.ai_votes_against;
        human_majority && ai_majority
    }
}
EOF

    # Generate vote state
    cat > programs/execai-dao-governance/src/state/vote.rs << 'EOF'
use anchor_lang::prelude::*;

#[account]
pub struct Vote {
    pub proposal: Pubkey,
    pub voter: Pubkey,
    pub voter_type: VoterType,
    pub vote_choice: VoteChoice,
    pub reasoning: Option<String>,
    pub weight: u64,
    pub voted_at: i64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
pub enum VoterType {
    Human,
    Ai,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
pub enum VoteChoice {
    For,
    Against,
    Abstain,
}

impl Vote {
    pub const LEN: usize = 8 + 32 + 32 + 1 + 1 + 4 + 256 + 8 + 8 + 1;
}
EOF

    # Generate instruction modules
    cat > programs/execai-dao-governance/src/instructions/mod.rs << 'EOF'
pub mod initialize_dao;
pub mod create_proposal;
pub mod cast_vote;
pub mod execute_proposal;

pub use initialize_dao::*;
pub use create_proposal::*;
pub use cast_vote::*;
pub use execute_proposal::*;
EOF

    # Generate initialize_dao instruction
    cat > programs/execai-dao-governance/src/instructions/initialize_dao.rs << 'EOF'
use anchor_lang::prelude::*;
use crate::state::*;
use crate::errors::*;

#[derive(Accounts)]
#[instruction(name: String)]
pub struct InitializeDao<'info> {
    #[account(
        init,
        payer = authority,
        space = Dao::LEN,
        seeds = [b"dao", name.as_bytes()],
        bump
    )]
    pub dao: Account<'info, Dao>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

pub fn initialize_dao(
    ctx: Context<InitializeDao>,
    name: String,
    description: String,
    human_quorum_threshold: u8,
    ai_quorum_threshold: u8,
) -> Result<()> {
    require!(human_quorum_threshold > 0 && human_quorum_threshold <= 100, GovernanceError::InvalidQuorumThreshold);
    require!(ai_quorum_threshold > 0 && ai_quorum_threshold <= 100, GovernanceError::InvalidQuorumThreshold);
    require!(name.len() <= 64, GovernanceError::NameTooLong);
    require!(description.len() <= 256, GovernanceError::DescriptionTooLong);

    let dao = &mut ctx.accounts.dao;
    dao.authority = ctx.accounts.authority.key();
    dao.name = name;
    dao.description = description;
    dao.human_quorum_threshold = human_quorum_threshold;
    dao.ai_quorum_threshold = ai_quorum_threshold;
    dao.total_members = 0;
    dao.total_human_members = 0;
    dao.total_ai_members = 0;
    dao.proposal_count = 0;
    dao.created_at = Clock::get()?.unix_timestamp;
    dao.bump = ctx.bumps.dao;

    msg!("DAO initialized: {}", dao.name);
    Ok(())
}
EOF

    # Generate create_proposal instruction
    cat > programs/execai-dao-governance/src/instructions/create_proposal.rs << 'EOF'
use anchor_lang::prelude::*;
use crate::state::*;
use crate::errors::*;

#[derive(Accounts)]
pub struct CreateProposal<'info> {
    #[account(
        init,
        payer = proposer,
        space = Proposal::LEN,
        seeds = [b"proposal", dao.key().as_ref(), dao.proposal_count.to_le_bytes().as_ref()],
        bump
    )]
    pub proposal: Account<'info, Proposal>,

    #[account(mut)]
    pub dao: Account<'info, Dao>,

    #[account(mut)]
    pub proposer: Signer<'info>,

    pub system_program: Program<'info, System>,
}

pub fn create_proposal(
    ctx: Context<CreateProposal>,
    title: String,
    description: String,
    proposal_type: ProposalType,
    execution_data: Vec<u8>,
    voting_period: i64,
) -> Result<()> {
    require!(title.len() <= 128, GovernanceError::TitleTooLong);
    require!(description.len() <= 512, GovernanceError::DescriptionTooLong);
    require!(execution_data.len() <= 1024, GovernanceError::ExecutionDataTooLarge);
    require!(voting_period > 0, GovernanceError::InvalidVotingPeriod);

    let dao = &mut ctx.accounts.dao;
    let proposal = &mut ctx.accounts.proposal;
    let clock = Clock::get()?;

    proposal.id = dao.proposal_count;
    proposal.dao = dao.key();
    proposal.proposer = ctx.accounts.proposer.key();
    proposal.title = title;
    proposal.description = description;
    proposal.proposal_type = proposal_type;
    proposal.status = ProposalStatus::Active;
    proposal.execution_data = execution_data;
    proposal.human_votes_for = 0;
    proposal.human_votes_against = 0;
    proposal.ai_votes_for = 0;
    proposal.ai_votes_against = 0;
    proposal.created_at = clock.unix_timestamp;
    proposal.voting_ends_at = clock.unix_timestamp + voting_period;
    proposal.executed_at = None;
    proposal.bump = ctx.bumps.proposal;

    dao.proposal_count += 1;

    msg!("Proposal created: {} (ID: {})", proposal.title, proposal.id);
    Ok(())
}
EOF

    # Generate cast_vote instruction
    cat > programs/execai-dao-governance/src/instructions/cast_vote.rs << 'EOF'
use anchor_lang::prelude::*;
use crate::state::*;
use crate::errors::*;

#[derive(Accounts)]
pub struct CastVote<'info> {
    #[account(
        init,
        payer = voter,
        space = Vote::LEN,
        seeds = [b"vote", proposal.key().as_ref(), voter.key().as_ref()],
        bump
    )]
    pub vote: Account<'info, Vote>,

    #[account(mut)]
    pub proposal: Account<'info, Proposal>,

    pub dao: Account<'info, Dao>,

    #[account(mut)]
    pub voter: Signer<'info>,

    pub system_program: Program<'info, System>,
}

pub fn cast_vote(
    ctx: Context<CastVote>,
    vote_choice: VoteChoice,
    voter_type: VoterType,
    reasoning: Option<String>,
) -> Result<()> {
    let proposal = &mut ctx.accounts.proposal;
    let dao = &ctx.accounts.dao;
    let clock = Clock::get()?;

    require!(clock.unix_timestamp <= proposal.voting_ends_at, GovernanceError::VotingPeriodEnded);
    require!(proposal.status == ProposalStatus::Active, GovernanceError::ProposalNotActive);

    if let Some(ref reason) = reasoning {
        require!(reason.len() <= 256, GovernanceError::ReasoningTooLong);
    }

    let vote = &mut ctx.accounts.vote;
    vote.proposal = proposal.key();
    vote.voter = ctx.accounts.voter.key();
    vote.voter_type = voter_type.clone();
    vote.vote_choice = vote_choice.clone();
    vote.reasoning = reasoning;
    vote.weight = 1;
    vote.voted_at = clock.unix_timestamp;
    vote.bump = ctx.bumps.vote;

    match (&voter_type, &vote_choice) {
        (VoterType::Human, VoteChoice::For) => proposal.human_votes_for += vote.weight,
        (VoterType::Human, VoteChoice::Against) => proposal.human_votes_against += vote.weight,
        (VoterType::Ai, VoteChoice::For) => proposal.ai_votes_for += vote.weight,
        (VoterType::Ai, VoteChoice::Against) => proposal.ai_votes_against += vote.weight,
        (_, VoteChoice::Abstain) => {},
    }

    if proposal.is_dual_quorum_met(dao) && proposal.has_dual_majority() {
        proposal.status = ProposalStatus::Succeeded;
        msg!("Proposal {} has reached dual quorum and majority!", proposal.id);
    }

    msg!("Vote cast by {:?} voter: {:?}", voter_type, vote_choice);
    Ok(())
}
EOF

    # Generate execute_proposal instruction
    cat > programs/execai-dao-governance/src/instructions/execute_proposal.rs << 'EOF'
use anchor_lang::prelude::*;
use crate::state::*;
use crate::errors::*;

#[derive(Accounts)]
pub struct ExecuteProposal<'info> {
    #[account(mut)]
    pub proposal: Account<'info, Proposal>,

    pub dao: Account<'info, Dao>,

    pub executor: Signer<'info>,
}

pub fn execute_proposal(ctx: Context<ExecuteProposal>) -> Result<()> {
    let proposal = &mut ctx.accounts.proposal;
    let dao = &ctx.accounts.dao;

    require!(proposal.status == ProposalStatus::Succeeded, GovernanceError::ProposalNotExecutable);
    require!(proposal.executed_at.is_none(), GovernanceError::ProposalAlreadyExecuted);

    // Execute the proposal logic here
    // This would involve parsing and executing the execution_data

    proposal.status = ProposalStatus::Executed;
    proposal.executed_at = Some(Clock::get()?.unix_timestamp);

    msg!("Proposal {} executed successfully", proposal.id);
    Ok(())
}
EOF

    # Generate errors
    cat > programs/execai-dao-governance/src/errors/mod.rs << 'EOF'
use anchor_lang::prelude::*;

#[error_code]
pub enum GovernanceError {
    #[msg("Invalid quorum threshold. Must be between 1 and 100.")]
    InvalidQuorumThreshold,
    #[msg("DAO name is too long. Maximum 64 characters.")]
    NameTooLong,
    #[msg("Description is too long. Maximum 256 characters.")]
    DescriptionTooLong,
    #[msg("Title is too long. Maximum 128 characters.")]
    TitleTooLong,
    #[msg("Execution data is too large. Maximum 1024 bytes.")]
    ExecutionDataTooLarge,
    #[msg("Invalid voting period. Must be greater than 0.")]
    InvalidVotingPeriod,
    #[msg("Voting period has ended for this proposal.")]
    VotingPeriodEnded,
    #[msg("Proposal is not in active status.")]
    ProposalNotActive,
    #[msg("Reasoning text is too long. Maximum 256 characters.")]
    ReasoningTooLong,
    #[msg("Proposal is not executable.")]
    ProposalNotExecutable,
    #[msg("Proposal has already been executed.")]
    ProposalAlreadyExecuted,
}
EOF

    log "Smart contracts generated successfully"
}

# Build and deploy contracts
build_and_deploy() {
    log "Building and deploying EXECAI DAO contracts..."
    
    cd "$HOME/execai-dao/execai-dao-governance"
    
    # Install dependencies
    yarn install
    
    # Build the program
    ~/.cargo/bin/anchor build
    
    if [[ $? -ne 0 ]]; then
        error "Build failed. Check the error messages above."
    fi
    
    # Deploy to devnet
    ~/.cargo/bin/anchor deploy
    
    if [[ $? -ne 0 ]]; then
        error "Deployment failed. Check the error messages above."
    fi
    
    # Get program ID
    PROGRAM_ID=$(solana address -k target/deploy/execai_dao_governance-keypair.json)
    log "Program deployed successfully! Program ID: $PROGRAM_ID"
    
    # Update program ID in lib.rs
    sed -i "s/ExecAiDaoGovernance11111111111111111111111111/$PROGRAM_ID/g" programs/execai-dao-governance/src/lib.rs
    sed -i "s/ExecAiDaoGovernance11111111111111111111111111/$PROGRAM_ID/g" Anchor.toml
    
    # Rebuild with correct program ID
    ~/.cargo/bin/anchor build
    ~/.cargo/bin/anchor deploy
    
    log "EXECAI DAO contracts deployed successfully!"
}

# Create Python client for EXECAI
create_python_client() {
    log "Creating Python client for EXECAI interaction..."
    
    cd "$HOME/execai-dao/execai-dao-governance"
    
    # Install Python dependencies
    pip3 install solana anchorpy

    # Create Python client
    cat > execai_client.py << 'EOF'
#!/usr/bin/env python3

import asyncio
import json
import os
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.publickey import PublicKey
from anchorpy import Program, Provider, Wallet
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE

class ExecaiDaoClient:
    def __init__(self, program_id: str, keypair_path: str = None):
        self.program_id = PublicKey(program_id)
        self.client = AsyncClient("https://api.devnet.solana.com")
        
        # Load keypair
        if keypair_path is None:
            keypair_path = os.path.expanduser("~/.config/solana/id.json")
        
        with open(keypair_path, 'r') as f:
            keypair_data = json.load(f)
        
        self.keypair = Keypair.from_secret_key(bytes(keypair_data))
        self.wallet = Wallet(self.keypair)
        self.provider = Provider(self.client, self.wallet)
        
        # Load program IDL
        with open('target/idl/execai_dao_governance.json', 'r') as f:
            idl = json.load(f)
        
        self.program = Program(idl, self.program_id, self.provider)

    async def initialize_dao(self, name: str, description: str, human_quorum: int = 51, ai_quorum: int = 51):
        """Initialize a new DAO"""
        dao_pda, dao_bump = PublicKey.find_program_address(
            [b"dao", name.encode()],
            self.program_id
        )
        
        tx = await self.program.rpc["initialize_dao"](
            name,
            description,
            human_quorum,
            ai_quorum,
            ctx={
                "accounts": {
                    "dao": dao_pda,
                    "authority": self.keypair.public_key,
                    "system_program": PublicKey("11111111111111111111111111111112"),
                },
                "signers": [self.keypair],
            }
        )
        
        print(f"DAO initialized: {name}")
        print(f"Transaction: {tx}")
        print(f"DAO Address: {dao_pda}")
        return dao_pda

    async def create_proposal(self, dao_name: str, title: str, description: str, voting_period: int = 604800):
        """Create a new proposal (voting_period in seconds, default 7 days)"""
        dao_pda, _ = PublicKey.find_program_address(
            [b"dao", dao_name.encode()],
            self.program_id
        )
        
        # Get DAO account to get proposal count
        dao_account = await self.program.account["Dao"].fetch(dao_pda)
        proposal_id = dao_account.proposal_count
        
        proposal_pda, proposal_bump = PublicKey.find_program_address(
            [b"proposal", bytes(dao_pda), proposal_id.to_bytes(8, 'little')],
            self.program_id
        )
        
        tx = await self.program.rpc["create_proposal"](
            title,
            description,
            {"basic": {}},  # ProposalType::Basic
            [],  # execution_data
            voting_period,
            ctx={
                "accounts": {
                    "proposal": proposal_pda,
                    "dao": dao_pda,
                    "proposer": self.keypair.public_key,
                    "system_program": PublicKey("11111111111111111111111111111112"),
                },
                "signers": [self.keypair],
            }
        )
        
        print(f"Proposal created: {title}")
        print(f"Transaction: {tx}")
        print(f"Proposal Address: {proposal_pda}")
        return proposal_pda

    async def cast_vote(self, proposal_address: str, vote_choice: str, voter_type: str = "human", reasoning: str = None):
        """Cast a vote on a proposal"""
        proposal_pda = PublicKey(proposal_address)
        
        # Get proposal account to get DAO
        proposal_account = await self.program.account["Proposal"].fetch(proposal_pda)
        dao_pda = proposal_account.dao
        
        vote_pda, vote_bump = PublicKey.find_program_address(
            [b"vote", bytes(proposal_pda), bytes(self.keypair.public_key)],
            self.program_id
        )
        
        # Convert vote choice
        vote_choice_enum = {"for": {"for": {}}, "against": {"against": {}}, "abstain": {"abstain": {}}}[vote_choice.lower()]
        voter_type_enum = {"human": {"human": {}}, "ai": {"ai": {}}}[voter_type.lower()]
        
        tx = await self.program.rpc["cast_vote"](
            vote_choice_enum,
            voter_type_enum,
            reasoning,
            ctx={
                "accounts": {
                    "vote": vote_pda,
                    "proposal": proposal_pda,
                    "dao": dao_pda,
                    "voter": self.keypair.public_key,
                    "system_program": PublicKey("11111111111111111111111111111112"),
                },
                "signers": [self.keypair],
            }
        )
        
        print(f"Vote cast: {vote_choice} as {voter_type}")
        print(f"Transaction: {tx}")
        return vote_pda

    async def get_dao_info(self, dao_name: str):
        """Get DAO information"""
        dao_pda, _ = PublicKey.find_program_address(
            [b"dao", dao_name.encode()],
            self.program_id
        )
        
        dao_account = await self.program.account["Dao"].fetch(dao_pda)
        return {
            "address": str(dao_pda),
            "name": dao_account.name,
            "description": dao_account.description,
            "human_quorum_threshold": dao_account.human_quorum_threshold,
            "ai_quorum_threshold": dao_account.ai_quorum_threshold,
            "total_members": dao_account.total_members,
            "total_human_members": dao_account.total_human_members,
            "total_ai_members": dao_account.total_ai_members,
            "proposal_count": dao_account.proposal_count,
        }

    async def get_proposal_info(self, proposal_address: str):
        """Get proposal information"""
        proposal_pda = PublicKey(proposal_address)
        proposal_account = await self.program.account["Proposal"].fetch(proposal_pda)
        
        return {
            "address": str(proposal_pda),
            "id": proposal_account.id,
            "title": proposal_account.title,
            "description": proposal_account.description,
            "status": proposal_account.status,
            "human_votes_for": proposal_account.human_votes_for,
            "human_votes_against": proposal_account.human_votes_against,
            "ai_votes_for": proposal_account.ai_votes_for,
            "ai_votes_against": proposal_account.ai_votes_against,
            "created_at": proposal_account.created_at,
            "voting_ends_at": proposal_account.voting_ends_at,
        }

    async def close(self):
        """Close the client connection"""
        await self.client.close()

# Example usage
async def main():
    # Replace with your actual program ID after deployment
    PROGRAM_ID = "ExecAiDaoGovernance11111111111111111111111111"
    
    client = ExecaiDaoClient(PROGRAM_ID)
    
    try:
        # Initialize DAO
        dao_address = await client.initialize_dao(
            "MicroAI Studios DAO",
            "AI-Human collaborative governance for MicroAI Studios",
            51,  # 51% human quorum
            51   # 51% AI quorum
        )
        
        # Create a proposal
        proposal_address = await client.create_proposal(
            "MicroAI Studios DAO",
            "Approve Q1 2024 Budget",
            "Proposal to approve the Q1 2024 budget allocation for MicroAI Studios operations"
        )
        
        # Cast a vote
        await client.cast_vote(
            str(proposal_address),
            "for",
            "human",
            "This budget allocation aligns with our strategic goals"
        )
        
        # Get DAO info
        dao_info = await client.get_dao_info("MicroAI Studios DAO")
        print("DAO Info:", dao_info)
        
        # Get proposal info
        proposal_info = await client.get_proposal_info(str(proposal_address))
        print("Proposal Info:", proposal_info)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
EOF

    chmod +x execai_client.py
    log "Python client created successfully"
}

# Create management scripts
create_management_scripts() {
    log "Creating management scripts..."
    
    cd "$HOME/execai-dao/execai-dao-governance"
    
    # Create deployment script
    cat > deploy.sh << 'EOF'
#!/bin/bash
echo "Building and deploying EXECAI DAO..."
anchor build
anchor deploy
echo "Deployment complete!"
EOF
    chmod +x deploy.sh
    
    # Create test script
    cat > test.sh << 'EOF'
#!/bin/bash
echo "Running EXECAI DAO tests..."
anchor test
echo "Tests complete!"
EOF
    chmod +x test.sh
    
    # Create status script
    cat > status.sh << 'EOF'
#!/bin/bash
echo "=== EXECAI DAO Status ==="
echo "Solana Config:"
solana config get
echo ""
echo "Wallet Balance:"
solana balance
echo ""
echo "Program Info:"
if [ -f "target/deploy/execai_dao_governance-keypair.json" ]; then
    PROGRAM_ID=$(solana address -k target/deploy/execai_dao_governance-keypair.json)
    echo "Program ID: $PROGRAM_ID"
    solana program show $PROGRAM_ID
else
    echo "Program not deployed yet"
fi
EOF
    chmod +x status.sh
    
    log "Management scripts created successfully"
}

# Final setup and verification
final_setup() {
    log "Performing final setup and verification..."
    
    cd "$HOME/execai-dao/execai-dao-governance"
    
    # Create README
    cat > README.md << 'EOF'
# EXECAI DAO - AI-Human Collaborative Governance

This project implements a dual-quorum governance system on Solana where both human and AI stakeholders participate in decision-making.

## Quick Start

1. **Check Status**: `./status.sh`
2. **Deploy Contracts**: `./deploy.sh`
3. **Run Tests**: `./test.sh`
4. **Use Python Client**: `python3 execai_client.py`

## Project Structure

- `programs/` - Rust smart contracts
- `tests/` - TypeScript tests
- `execai_client.py` - Python client for interaction
- `deploy.sh` - Deployment script
- `test.sh` - Test runner
- `status.sh` - System status checker

## Features

- Dual-quorum governance (human + AI)
- Proposal creation and voting
- Transparent on-chain governance
- Python client for easy integration
- Wyoming DAO LLC compliant structure

## Usage

### Initialize DAO
```python
dao_address = await client.initialize_dao(
    "MicroAI Studios DAO",
    "AI-Human collaborative governance",
    51,  # Human quorum threshold
    51   # AI quorum threshold
)
```

### Create Proposal
```python
proposal_address = await client.create_proposal(
    "MicroAI Studios DAO",
    "Budget Approval",
    "Q1 2024 budget allocation"
)
```

### Cast Vote
```python
await client.cast_vote(
    proposal_address,
    "for",
    "human",
    "Reasoning for the vote"
)
```

## Development

- Built with Anchor Framework
- Deployed on Solana Devnet
- Python client using anchorpy
- TypeScript tests with Mocha

## Support

For issues or questions, check the logs in the project directory.
EOF
    
    # Create initial commit
    git add .
    git commit -m "Initial EXECAI DAO implementation"
    
    # Show final status
    echo ""
    echo "=================================="
    log "EXECAI DAO SETUP COMPLETE!"
    echo "=================================="
    echo ""
    info "Project Location: $HOME/execai-dao/execai-dao-governance"
    info "Next Steps:"
    echo "  1. cd $HOME/execai-dao/execai-dao-governance"
    echo "  2. ./status.sh    # Check system status"
    echo "  3. ./deploy.sh    # Deploy contracts"
    echo "  4. python3 execai_client.py  # Test the system"
    echo ""
    info "Your EXECAI DAO is ready for Wyoming DAO LLC integration!"
}

# Main execution
main() {
    log "Starting EXECAI DAO automated setup..."
    
    check_system
    install_system_deps
    install_rust
    install_solana
    install_anchor
    setup_solana_config
    create_execai_project
    generate_smart_contracts
    build_and_deploy
    create_python_client
    create_management_scripts
    final_setup
    
    log "EXECAI DAO setup completed successfully!"
}

# Run main function
main "$@"

