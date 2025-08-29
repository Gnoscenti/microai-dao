
export type Proposal = {
  id: string;
  title: string;
  progress: number;   // % of vote window elapsed
  endsISO: string;    // ISO timestamp for display
  support: number;    // % yes vs total
};

export type Metrics = {
  treasuryUSD: number;
  votersActive: number;
  engagementPct: number;
  security: { transparency: number; security: number; participation: number; };
  tps?: number;
  blockHeight?: number;
  finalityMs?: number;
  peers?: number;
};
