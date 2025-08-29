# MicroAI DAO LLC (Devnet)

A complete, production-grade Wyoming DAO LLC stack on Solana with:

- Governance & Membership smart contracts (Anchor)
- React governance dashboard with live on-chain data
- Live data sidecar (Node.js) for simplified account parsing
- EXECAI (AI stakeholder) client that votes on proposals on-chain
- Wyoming DAO LLC compliance fields persisted on-chain

This repo is structured to be easily duplicated for other companies with minimal changes.

## Repository Structure

- programs/
  - governance/ … Anchor program with Wyoming compliance fields (Dao + Proposal + VoteRecord)
  - membership/ … Anchor program with Member registry (includes KYC/compliance fields)
- microai-dashboard/ … React + Vite dashboard
- scripts/
  - seed_raw.js … Seeds a DAO + one Proposal on devnet via raw instructions
  - vote_raw.js … Casts a vote on a proposal (approve/reject)
- live-data-server.js … Serves clean JSON from on-chain accounts at http://localhost:8787
- execai_client.py … AI stakeholder client that evaluates and votes on proposals
- Anchor.toml … Anchor configuration with devnet program IDs
- config.json … Runtime configuration for EXECAI & RPC

## Quick Start (Devnet)

1) Prerequisites
- Node.js 20+, npm
- Rust toolchain, Solana CLI, Anchor
- Python 3.13+

2) Install dependencies (persistent, no virtualenv)

```
make install
```

3) Build smart contracts & dashboard (optional)
```
make build
```

4) Deploy programs to devnet (already deployed in this template)
- Governance: 6amHFyNoPK9MmbBKqthLMeoxTB4TV7CdVE5K4RXi1eDC
- Membership: FotEuL6PaHRDYuDmtqNrbbS52AwVX49MQSBjNwCWqRA4

If you need to redeploy:
```
anchor deploy --program-name governance
anchor deploy --program-name membership
```

5) Seed a DAO and a Proposal on devnet
```
npm run seed:dao
```

6) Start the live data API server (parses on-chain accounts)
```
npm run live-data
# Health check
curl -s http://localhost:8787/health
```

7) Start the dashboard (Vite dev server)
```
cd microai-dashboard && npm run dev
# Open the printed URL (e.g., http://localhost:5176)
```

8) Run EXECAI (AI stakeholder) to vote on-chain
```
# Update config.json if needed (keypair and RPC)
/usr/bin/python3 execai_client.py
```

9) Manually cast votes (optional)
```
# Approve
npm run vote -- D7D3EC2CKrquXnfJPRdGR2dvo3sfAZ6YqFmQiXkuUknr approve
# Reject
npm run vote -- <PROPOSAL_PUBKEY> reject
```

## Configuration

- Anchor.toml
  - [programs.devnet] has program IDs for governance & membership
  - [provider] uses ~/.config/solana/id.json

- config.json
  - governance_program_id, membership_program_id
  - keypair_path (EXECAI signer)
  - rpc_url (default: https://api.devnet.solana.com)

- microai-dashboard/src/lib/config.ts
  - Defaults to devnet, can switch to mainnet via env vars

## Wyoming DAO LLC Compliance

Compliance fields are stored directly on-chain in the Dao account:
- legal_name, registered_agent_address, principal_place_of_business
- formation_date, jurisdiction ("Wyoming"), entity_type ("DAO LLC")

The dashboard Wyoming tab includes an auto-fill JSON loader to streamline filings.

## Duplicating for Other Companies

1) Clone this repository
2) Change legal & registered agent details in:
   - scripts/seed_raw.js (initialize args)
   - wyoming-dao-config.json
3) Redeploy programs under your authority (optional) and update Anchor.toml & config.json
4) Run seed, live data server, dashboard, and EXECAI as above

## Mainnet Readiness Checklist

See docs/MAINNET_CHECKLIST.md for a step-by-step guide:
- Program deployment on mainnet-beta
- Update Anchor.toml [programs.mainnet]
- Lock IDL & publish (optional)
- Update dashboard env to mainnet
- Prepare Wyoming filing with mainnet program IDs & DAO pubkeys

## Security Notes

- Keys in ~/.config/solana/*.json — back them up securely.
- This repository avoids virtual environments for Python to maintain persistent environments.
- Use separate keys & wallets for mainnet.

## License

UNLICENSED – consult your legal counsel for compliance requirements.

