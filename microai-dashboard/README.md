
# MicroAI Studios • Live Governance Dashboard

Future-forward dashboard with charts, blockchain visual, proposals, AI stream, and engagement metrics.

## Quickstart

```bash
npm install
npm run dev
# open http://localhost:5173
```

## Environment

Copy `.env.example` → `.env.local` and set:

- `VITE_RPC_URL` — Solana RPC endpoint (e.g., https://api.mainnet-beta.solana.com or your private RPC).
- `VITE_PROGRAM_ID` — Your governance program id (base58).
- `VITE_TREASURY_PUBKEY` — Treasury account public key (for balance/indexer lookups).
- `VITE_GOVERNANCE_API` — (Optional) Your off-chain governance/indexer service for proposals & votes.
- `VITE_INDEXER_URL` — (Optional) Your indexer for treasury USD, cohorts, TPS/peers, etc.
- `VITE_TIMELOCK_SECONDS` — Display-only timelock badge.

## Wiring Guide (Solana)

All data fetches are centralized in `src/lib/data.ts`. Replace mock returns with real calls:

1. **Chain Stats (`getChainStats`)**
   - Use `@solana/web3.js` (already installed) for block height and performance samples.
   - For peers/finality metrics, hit your validator metrics endpoint or indexer.

2. **Treasury USD (`getTreasuryUSD`)**
   - Query balances of `VITE_TREASURY_PUBKEY` via your indexer.
   - Convert to USD server-side; return a single `usd` number to the client.

3. **Proposals (`getProposals`)**
   - Expose a REST endpoint on your governance/indexer that returns:
     ```json
     [ { "id": "P-101", "title": "string", "progress": 68, "endsISO": "2025-08-28T19:00:00Z", "support": 72 } ]
     ```
   - `progress` = % of vote window elapsed; `support` = Yes% among counted votes.

4. **Engagement (`getEngagement`)**
   - Combine wallet sign-ins (web analytics) + on-chain `voter` set size.
   - Return `{ "votersActive": number, "engagementPct": number }`.

5. **Security Posture (`getSecurityPosture`)**
   - Return a composite index `{ transparency, security, participation }` (0–100).
   - Consider sourcing from audit status, on-chain transparency, participation rates, etc.

## Deploy

### Vercel
- Framework: **Vite**
- Build: `npm run build`
- Output dir: `dist`
- Optionally embed at `/dashboard` of your main site via iframe:
  ```html
  <iframe src="https://YOUR-DASH.vercel.app" style="width:100%;height:100vh;border:0;"></iframe>
  ```

### Netlify / Static
- Build → upload `dist/`.
- Set environment variables in your host.

## Where to plug contract variables in `App.tsx`

- **Program ID:** Comes from `CONFIG.PROGRAM_ID` (see the small label above the block animation).
- **Timelock:** `CONFIG.TIMELOCK_SECONDS` controls the header badge.
- **Treasury:** `getTreasuryUSD()` should read from your program/indexer and reflect live values.
- **Proposals & Votes:** `getProposals()` powers Active Proposals + Vote Split. Hook to your program accounts via indexer or RPC and map to `{ id, title, progress, endsISO, support }`.

Edit `src/lib/config.ts` to confirm your envs are read correctly.
