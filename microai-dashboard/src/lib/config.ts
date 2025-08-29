/// <reference types="vite/client" />

export const CONFIG = {
  RPC_URL: import.meta.env.VITE_RPC_URL || 'https://api.devnet.solana.com',
  GOVERNANCE_PROGRAM_ID: import.meta.env.VITE_GOVERNANCE_PROGRAM_ID || '6amHFyNoPK9MmbBKqthLMeoxTB4TV7CdVE5K4RXi1eDC',
  MEMBERSHIP_PROGRAM_ID: import.meta.env.VITE_MEMBERSHIP_PROGRAM_ID || 'FotEuL6PaHRDYuDmtqNrbbS52AwVX49MQSBjNwCWqRA4',
  TREASURY_PUBKEY: import.meta.env.VITE_TREASURY_PUBKEY || '5tZtDijyKeKCqKeLGD3eqtddCBmwLHDocgtsXmzssKeR',
  GOV_API: import.meta.env.VITE_GOVERNANCE_API || '',
  INDEXER_URL: import.meta.env.VITE_INDEXER_URL || '',
  TIMELOCK_SECONDS: Number(import.meta.env.VITE_TIMELOCK_SECONDS || 24*60*60),
};
