const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { Connection, PublicKey } = require('@solana/web3.js');

const PORT = process.env.PORT || 8787;
const RPC_URL = process.env.RPC_URL || 'https://api.devnet.solana.com';
const GOVERNANCE_PROGRAM_ID = process.env.GOVERNANCE_PROGRAM_ID || '6amHFyNoPK9MmbBKqthLMeoxTB4TV7CdVE5K4RXi1eDC';

function readU64LE(buf, offset){ return Number(buf.readBigUInt64LE(offset)); }
function readI64LE(buf, offset){ return Number(buf.readBigInt64LE(offset)); }
function readStr(buf, offsetObj){ const len = buf.readUInt32LE(offsetObj.offset); offsetObj.offset += 4; const s = buf.slice(offsetObj.offset, offsetObj.offset + len).toString('utf8'); offsetObj.offset += len; return s; }

async function fetchProgramAccounts(){
  const connection = new Connection(RPC_URL, 'confirmed');
  const programId = new PublicKey(GOVERNANCE_PROGRAM_ID);
  const accounts = await connection.getProgramAccounts(programId);
  return accounts;
}

async function main() {
  const app = express();
  app.use(cors());

  app.get('/health', (req, res) => res.json({ ok: true }));

  app.get('/api/dao', async (req, res) => {
    try {
      const accounts = await fetchProgramAccounts();
      // Find a DAO account by attempting to parse layout
      for (const { pubkey, account } of accounts){
        const data = account.data;
        if (!Buffer.isBuffer(data)) continue;
        try {
          let o = { offset: 8 };
          const authority = new PublicKey(data.slice(o.offset, o.offset + 32)); o.offset += 32;
          const proposalCount = readU64LE(data, o.offset); o.offset += 8;
          const memberCount = readU64LE(data, o.offset); o.offset += 8;
          const legalName = readStr(data, o);
          const registeredAgentAddress = readStr(data, o);
          const principalPlaceOfBusiness = readStr(data, o);
          const formationDate = readI64LE(data, o.offset); o.offset += 8;
          const jurisdiction = readStr(data, o);
          const entityType = readStr(data, o);
          // Basic sanity check
          if (legalName && legalName.length > 0 && legalName.length < 200 && registeredAgentAddress.length > 0 && entityType.includes('DAO')){
            return res.json({
              pubkey: pubkey.toBase58(),
              authority: authority.toBase58(),
              proposalCount,
              memberCount,
              legalName,
              registeredAgentAddress,
              principalPlaceOfBusiness,
              formationDate,
              jurisdiction,
              entityType,
            });
          }
        } catch(_e){ /* skip non-DAO accounts */ }
      }
      return res.status(404).json({ error: 'No DAO account found' });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  app.get('/api/proposals', async (req, res) => {
    try {
      const accounts = await fetchProgramAccounts();
      const results = [];
      for (const { pubkey, account } of accounts){
        const data = account.data;
        if (!Buffer.isBuffer(data)) continue;
        try {
          let o = { offset: 8 };
          // Proposal starts with id u64, not a pubkey
          const id = readU64LE(data, o.offset); o.offset += 8;
          // Title
          const title = readStr(data, o);
          const description = readStr(data, o);
          const amount = readU64LE(data, o.offset); o.offset += 8;
          const proposer = new PublicKey(data.slice(o.offset, o.offset + 32)); o.offset += 32;
          const votesFor = readU64LE(data, o.offset); o.offset += 8;
          const votesAgainst = readU64LE(data, o.offset); o.offset += 8;
          const statusIdx = data.readUInt8(o.offset); o.offset += 1;
          const createdAt = readI64LE(data, o.offset); o.offset += 8;
          // Heuristic: titles are ascii-ish and not too long
          if (title && title.length < 256 && description.length < 1024){
            results.push({
              pubkey: pubkey.toBase58(), id, title, description, amount, proposer: proposer.toBase58(), votesFor, votesAgainst, status: statusIdx, createdAt
            });
          }
        } catch(_e){ /* not a proposal; skip */ }
      }
      res.json(results);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  app.listen(PORT, () => console.log(`Live data server listening on http://localhost:${PORT}`));
}

main().catch((e) => {
  console.error('Server failed to start', e);
  process.exit(1);
});

