# Mainnet Deployment Checklist

Use this list when promoting from devnet to mainnet-beta.

- [ ] Anchor.toml:
  - Add [programs.mainnet] with deployed mainnet program IDs
  - Keep [provider] wallet to your production authority keypair
- [ ] Deploy programs to mainnet-beta:
  - anchor deploy --provider.cluster mainnet --program-name governance
  - anchor deploy --provider.cluster mainnet --program-name membership
- [ ] Freeze IDL (optional) and publish via registry (optional)
- [ ] Update dashboard env to mainnet:
  - microai-dashboard/.env.local: VITE_RPC_URL, VITE_GOVERNANCE_PROGRAM_ID, VITE_MEMBERSHIP_PROGRAM_ID
- [ ] Start live-data-server against mainnet RPC
- [ ] Update config.json for EXECAI API and RPC to mainnet
- [ ] Wyoming filing paperwork:
  - Include mainnet program IDs and DAO pubkeys
  - Attach registered agent and principal business addresses
  - Verify EXECAI stakeholder disclosures are current
- [ ] Incident response and ops:
  - Key backups
  - Monitoring for proposals and votes
  - Treasury controls (multisig, timelock)

