# Development Setup (Devnet)

## Install toolchains
- Rust, Solana CLI, Anchor: see automated_execai_setup.sh for reference
- Node.js 20+, npm
- Python 3.13+

## Project install (persistent, no venv)
```
make install
```

## (Re)build everything
```
make build
```

## Deploy to devnet
```
anchor deploy --program-name governance
anchor deploy --program-name membership
```

## Seed on-chain data
```
npm run seed:dao
```

## Start live data server
```
npm run live-data
```

## Start dashboard
```
cd microai-dashboard && npm run dev
```

## Run EXECAI votes
```
/usr/bin/python3 execai_client.py
```

## Manual vote
```
npm run vote -- <PROPOSAL_PUBKEY> approve
```

