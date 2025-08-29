
import { Proposal, Metrics } from './types';

// Mock fallbacks while wiring real data sources
export const mockProposals: Proposal[] = [
  { id: 'P-101', title: 'Fund Open-Source Wallet Integration', progress: 68, endsISO: new Date(Date.now()+4*3600e3).toISOString(), support: 72 },
  { id: 'P-102', title: 'Community Bounty: Docs & Tutorials', progress: 39, endsISO: new Date(Date.now()+12*3600e3).toISOString(), support: 61 },
  { id: 'P-103', title: 'AI Ethics Allocation (1%)', progress: 85, endsISO: new Date(Date.now()+1*3600e3).toISOString(), support: 88 },
];

export const mockMetrics: Metrics = {
  treasuryUSD: 4.82e6,
  votersActive: 1342,
  engagementPct: 46.7,
  security: { transparency: 92, security: 88, participation: 74 },
  tps: 1200,
  blockHeight: 1234567,
  finalityMs: 400,
  peers: 842,
};
