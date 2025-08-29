# Wyoming DAO LLC Compliance Notes

This project stores core compliance data on-chain in the `Dao` account:
- legal_name
- registered_agent_address
- principal_place_of_business
- formation_date
- jurisdiction (e.g., "Wyoming")
- entity_type (e.g., "DAO LLC")

The dashboard provides an auto-fill form and JSON configuration loader to simplify registration workflows.

For filing, include:
- Program IDs (governance & membership) on the selected network (mainnet preferred)
- DAO account public key
- Registered agent details and principal address

For mainnet, ensure you maintain:
- Upgrade authority custody and procedures
- Audit logs for EXECAI votes
- Treasury governance (timelock, multisig) if applicable

