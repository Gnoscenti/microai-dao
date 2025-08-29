use anchor_lang::prelude::*;

declare_id!("6amHFyNoPK9MmbBKqthLMeoxTB4TV7CdVE5K4RXi1eDC");

#[program]
pub mod governance {
    use super::*;

    pub fn initialize(
        ctx: Context<Initialize>, 
        legal_name: String,
        registered_agent_address: String,
        principal_place_of_business: String,
    ) -> Result<()> {
        let dao = &mut ctx.accounts.dao;
        dao.authority = ctx.accounts.authority.key();
        dao.proposal_count = 0;
        dao.member_count = 0;
        dao.legal_name = legal_name;
        dao.registered_agent_address = registered_agent_address;
        dao.principal_place_of_business = principal_place_of_business;
        dao.formation_date = Clock::get()?.unix_timestamp;
        dao.jurisdiction = "Wyoming".to_string();
        dao.entity_type = "DAO LLC".to_string();
        Ok(())
    }

    pub fn create_proposal(
        ctx: Context<CreateProposal>,
        title: String,
        description: String,
        amount: u64,
    ) -> Result<()> {
        let dao = &mut ctx.accounts.dao;
        let proposal = &mut ctx.accounts.proposal;

        proposal.id = dao.proposal_count;
        proposal.title = title;
        proposal.description = description;
        proposal.amount = amount;
        proposal.proposer = ctx.accounts.proposer.key();
        proposal.votes_for = 0;
        proposal.votes_against = 0;
        proposal.status = ProposalStatus::Active;
        proposal.created_at = Clock::get()?.unix_timestamp;

        dao.proposal_count += 1;

        Ok(())
    }

    pub fn vote(ctx: Context<Vote>, support: bool) -> Result<()> {
        let proposal = &mut ctx.accounts.proposal;
        let vote_record = &mut ctx.accounts.vote_record;

        require!(proposal.status == ProposalStatus::Active, ErrorCode::ProposalNotActive);
        require!(!vote_record.has_voted, ErrorCode::AlreadyVoted);

        if support {
            proposal.votes_for += 1;
        } else {
            proposal.votes_against += 1;
        }

        vote_record.has_voted = true;
        vote_record.support = support;
        vote_record.voter = ctx.accounts.voter.key();

        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = authority, space = 8 + 32 + 8 + 8 + 256 + 512 + 512 + 8 + 64 + 64)]
    pub dao: Account<'info, Dao>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct CreateProposal<'info> {
    #[account(mut)]
    pub dao: Account<'info, Dao>,
    #[account(init, payer = proposer, space = 8 + 8 + 256 + 512 + 8 + 32 + 8 + 8 + 1 + 8)]
    pub proposal: Account<'info, Proposal>,
    #[account(mut)]
    pub proposer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Vote<'info> {
    #[account(mut)]
    pub proposal: Account<'info, Proposal>,
    #[account(init, payer = voter, space = 8 + 1 + 1 + 32)]
    pub vote_record: Account<'info, VoteRecord>,
    #[account(mut)]
    pub voter: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct Dao {
    pub authority: Pubkey,
    pub proposal_count: u64,
    pub member_count: u64,
    // Wyoming DAO LLC Compliance Fields
    pub legal_name: String,
    pub registered_agent_address: String,
    pub principal_place_of_business: String,
    pub formation_date: i64,
    pub jurisdiction: String,
    pub entity_type: String,
}

#[account]
pub struct Proposal {
    pub id: u64,
    pub title: String,
    pub description: String,
    pub amount: u64,
    pub proposer: Pubkey,
    pub votes_for: u64,
    pub votes_against: u64,
    pub status: ProposalStatus,
    pub created_at: i64,
}

#[account]
pub struct VoteRecord {
    pub has_voted: bool,
    pub support: bool,
    pub voter: Pubkey,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
pub enum ProposalStatus {
    Active,
    Executed,
    Rejected,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Proposal is not active")]
    ProposalNotActive,
    #[msg("Already voted on this proposal")]
    AlreadyVoted,
}
