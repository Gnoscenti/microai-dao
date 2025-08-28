//! MicroAI DAO LLC Membership Program
//! 
//! This program implements the membership management for a Wyoming DAO LLC
//! with EXECAI as a stakeholder.

use borsh::{BorshDeserialize, BorshSerialize};
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
};

/// Program entrypoint
entrypoint!(process_instruction);

/// Program instructions
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub enum MembershipInstruction {
    /// Initialize the membership program
    /// 
    /// Accounts expected:
    /// 0. `[writable]` Membership state account
    /// 1. `[]` Rent sysvar
    Initialize,

    /// Register a new member
    /// 
    /// Accounts expected:
    /// 0. `[]` Membership state account
    /// 1. `[writable]` Member account
    /// 2. `[signer]` Authority account
    RegisterMember {
        /// Name of the member
        name: String,
        /// Whether the member is an AI entity
        is_ai: bool,
        /// Voting power of the member
        voting_power: u64,
    },

    /// Update member voting power
    /// 
    /// Accounts expected:
    /// 0. `[]` Membership state account
    /// 1. `[writable]` Member account
    /// 2. `[signer]` Authority account
    UpdateVotingPower {
        /// New voting power
        voting_power: u64,
    },
}

/// Membership state
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Membership {
    /// Number of members registered
    pub member_count: u64,
    /// Authority that can register members
    pub authority: Pubkey,
}

/// Member state
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct Member {
    /// Unique member ID
    pub id: u64,
    /// Name of the member
    pub name: String,
    /// Whether the member is an AI entity
    pub is_ai: bool,
    /// Voting power of the member
    pub voting_power: u64,
    /// Public key of the member
    pub pubkey: Pubkey,
}

/// Program errors
#[derive(Debug, thiserror::Error)]
pub enum MembershipError {
    #[error("Invalid instruction")]
    InvalidInstruction,
    
    #[error("Member already exists")]
    MemberAlreadyExists,
    
    #[error("Member not found")]
    MemberNotFound,
    
    #[error("Not authorized")]
    NotAuthorized,
}

impl From<MembershipError> for ProgramError {
    fn from(e: MembershipError) -> Self {
        ProgramError::Custom(e as u32)
    }
}

/// Process program instruction
pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let instruction = MembershipInstruction::try_from_slice(instruction_data)?;
    
    match instruction {
        MembershipInstruction::Initialize => {
            process_initialize(program_id, accounts)
        }
        MembershipInstruction::RegisterMember { name, is_ai, voting_power } => {
            process_register_member(program_id, accounts, name, is_ai, voting_power)
        }
        MembershipInstruction::UpdateVotingPower { voting_power } => {
            process_update_voting_power(program_id, accounts, voting_power)
        }
    }
}

/// Process Initialize instruction
fn process_initialize(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let membership_account = next_account_info(account_info_iter)?;
    let authority_account = next_account_info(account_info_iter)?;
    
    // Ensure authority signed the transaction
    if !authority_account.is_signer {
        return Err(MembershipError::NotAuthorized.into());
    }
    
    let membership = Membership {
        member_count: 0,
        authority: *authority_account.key,
    };
    
    membership.serialize(&mut *membership_account.data.borrow_mut())?;
    
    msg!("Membership initialized with authority: {}", authority_account.key);
    Ok(())
}

/// Process RegisterMember instruction
fn process_register_member(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    name: String,
    is_ai: bool,
    voting_power: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let membership_account = next_account_info(account_info_iter)?;
    let member_account = next_account_info(account_info_iter)?;
    let authority_account = next_account_info(account_info_iter)?;
    
    // Load membership state
    let mut membership = Membership::try_from_slice(&membership_account.data.borrow())?;
    
    // Ensure authority signed the transaction
    if !authority_account.is_signer || *authority_account.key != membership.authority {
        return Err(MembershipError::NotAuthorized.into());
    }
    
    // Create member
    let member = Member {
        id: membership.member_count,
        name,
        is_ai,
        voting_power,
        pubkey: *member_account.key,
    };
    
    // Increment member count
    membership.member_count += 1;
    
    // Save states
    member.serialize(&mut *member_account.data.borrow_mut())?;
    membership.serialize(&mut *membership_account.data.borrow_mut())?;
    
    msg!("Member registered with ID: {}", member.id);
    if is_ai {
        msg!("Member is an AI entity with voting power: {}", voting_power);
    } else {
        msg!("Member is a human entity with voting power: {}", voting_power);
    }
    
    Ok(())
}

/// Process UpdateVotingPower instruction
fn process_update_voting_power(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    voting_power: u64,
) -> ProgramResult {
    let account_info_iter = &mut accounts.iter();
    let membership_account = next_account_info(account_info_iter)?;
    let member_account = next_account_info(account_info_iter)?;
    let authority_account = next_account_info(account_info_iter)?;
    
    // Load membership state
    let membership = Membership::try_from_slice(&membership_account.data.borrow())?;
    
    // Ensure authority signed the transaction
    if !authority_account.is_signer || *authority_account.key != membership.authority {
        return Err(MembershipError::NotAuthorized.into());
    }
    
    // Load and update member
    let mut member = Member::try_from_slice(&member_account.data.borrow())?;
    member.voting_power = voting_power;
    
    // Save member state
    member.serialize(&mut *member_account.data.borrow_mut())?;
    
    msg!("Voting power updated for member ID {}: {}", member.id, voting_power);
    Ok(())
}

