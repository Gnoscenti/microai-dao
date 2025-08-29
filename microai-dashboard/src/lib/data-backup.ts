
import { Connection, PublicKey } from '@solana/web3.js';
import { CONFIG } from './config';
import { mockProposals, mockMetrics } from './mock';
import type { Proposal, Metrics } from './types';

/**
 * Data layer: replace mock calls with real chain/indexer queries.
 * Keep functions stable so App.tsx doesn't need changes later.
 */

const conn = new Connection(CONFIG.RPC_URL, 'confirmed');

export async function getChainStats(): Promise<Partial<Metrics>> {
  try {
    const epochInfo = await conn.getEpochInfo();
    const bh = await conn.getBlockHeight('finalized');
    // TPS is non-trivial; placeholder: recent performance sample
    const perf = await conn.getRecentPerformanceSamples(1);
    const tps = perf?.[0] ? Math.round(perf[0].numTransactions / perf[0].samplePeriodSecs) : undefined;
    return {
      tps,
      blockHeight: bh,
      finalityMs: 400, // replace with your chain metrics source if available
      peers: undefined, // not available via web3.js; fill via your node metrics
    };
  } catch (e) {
    console.warn('getChainStats fallback → mock', e);
    return { tps: mockMetrics.tps, blockHeight: mockMetrics.blockHeight, finalityMs: mockMetrics.finalityMs, peers: mockMetrics.peers };
  }
}

export async function getTreasuryUSD(): Promise<number> {
  try {
    // Example: query your indexer or program-derived address balances and convert to USD off-chain
    // const res = await fetch(`${CONFIG.INDEXER_URL}/treasury-usd`).then(r=>r.json());
    // return res.usd;
    return mockMetrics.treasuryUSD;
  } catch {
    return mockMetrics.treasuryUSD;
  }
}

export async function getProposals(): Promise<Proposal[]> {
  try {
    // Example governance API (off-chain indexer to avoid heavy client parsing):
    // const res = await fetch(`${CONFIG.GOV_API}/proposals`).then(r=>r.json());
    // return res as Proposal[];
    return mockProposals;
  } catch {
    return mockProposals;
  }
}

export async function getEngagement(): Promise<{ votersActive:number; engagementPct:number; }> {
  try {
    // Example: combine wallet sign-ins + on-chain voter set
    // const res = await fetch(`${CONFIG.INDEXER_URL}/engagement`).then(r=>r.json());
    // return res;
    return { votersActive: mockMetrics.votersActive, engagementPct: mockMetrics.engagementPct };
  } catch {
    return { votersActive: mockMetrics.votersActive, engagementPct: mockMetrics.engagementPct };
  }
}

export async function getSecurityPosture(): Promise<{ transparency:number; security:number; participation:number; }>{ 
  // Could be a composite EPI-like index; start with mock
  return mockMetrics.security;
}
