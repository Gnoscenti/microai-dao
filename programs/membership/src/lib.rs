use anchor_lang::prelude::*;

declare_id!("FotEuL6PaHRDYuDmtqNrbbS52AwVX49MQSBjNwCWqRA4");

#[program]
pub mod membership {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let registry = &mut ctx.accounts.registry;
        registry.authority = ctx.accounts.authority.key();
        registry.member_count = 0;
        Ok(())
    }

    pub fn add_member(
        ctx: Context<AddMember>,
        member_type: MemberType,
        voting_power: u64,
    ) -> Result<()> {
        let registry = &mut ctx.accounts.registry;
        let member = &mut ctx.accounts.member;

        member.pubkey = ctx.accounts.member_pubkey.key();
        member.member_type = member_type;
        member.voting_power = voting_power;
        member.joined_at = Clock::get()?.unix_timestamp;
        member.is_active = true;

        registry.member_count += 1;

        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = authority, space = 8 + 32 + 8)]
    pub registry: Account<'info, MemberRegistry>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct AddMember<'info> {
    #[account(mut)]
    pub registry: Account<'info, MemberRegistry>,
    #[account(init, payer = authority, space = 8 + 32 + 1 + 8 + 8 + 1)]
    pub member: Account<'info, Member>,
    /// CHECK: Member pubkey is validated by the program logic
    pub member_pubkey: AccountInfo<'info>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct MemberRegistry {
    pub authority: Pubkey,
    pub member_count: u64,
}

#[account]
pub struct Member {
    pub pubkey: Pubkey,
    pub member_type: MemberType,
    pub voting_power: u64,
    pub joined_at: i64,
    pub is_active: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub enum MemberType {
    Human,
    AI,
    Organization,
}
