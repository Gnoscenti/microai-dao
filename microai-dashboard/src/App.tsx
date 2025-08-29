
import React, { useEffect, useMemo, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { motion } from "framer-motion";
import {
  AreaChart, Area, LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip as RTooltip, ResponsiveContainer,
  RadialBarChart, RadialBar, Legend
} from "recharts";
import { Activity, Zap, Lock, Shield, Coins, Vote, Users, Bot, Clock, Link as LinkIcon, TrendingUp, Sparkles, ChartBar, Eye, GitBranch } from "lucide-react";
import { CONFIG } from "@/lib/config";
import { getChainStats, getTreasuryUSD, getProposals, getEngagement, getSecurityPosture } from "@/lib/data";
import type { Proposal } from "@/lib/types";

const range = (n:number) => Array.from({ length: n }, (_, i) => i);
const makeSeries = (points = 24, start = 100, jitter = 8) => {
  let v = start;
  return range(points).map((i) => {
    v += (Math.random() - 0.5) * jitter;
    return { t: i, v: +v.toFixed(2) };
  });
};
const palette = ["#7C3AED", "#06B6D4", "#16A34A", "#F59E0B", "#EF4444", "#3B82F6"];

const makeHeatmap = () => {
  const days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  const hours = range(24);
  return { days, hours, cells: days.map(() => hours.map(() => Math.floor(Math.random() * 8))) };
};

const aiBlurbs = [
  "Analyzing treasury runway vs. monthly burn…",
  "Flagged duplicate wallets in voting cohort, initiating dedupe…",
  "Backtesting governance quorum thresholds against prior 90 days…",
  "Computing grant ROI projections from GitHub velocity…",
  "Reweighting EPI index after stakeholder feedback…",
  "Auditing multisig timelock latencies before proposal execution…",
];

export default function App(){
  const [now, setNow] = useState(new Date());
  const [tps, setTps] = useState<number>(0);
  const [chainStats, setChainStats] = useState<{blockHeight?:number; finalityMs?:number; peers?:number}>({});
  const [treasuryUSD, setTreasuryUSD] = useState<number>(0);
  const [votersActive, setVotersActive] = useState<number>(0);
  const [engagementPct, setEngagementPct] = useState<number>(0);
  const [security, setSecurity] = useState<{transparency:number; security:number; participation:number}>({ transparency: 0, security: 0, participation: 0 });
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [aiLog, setAiLog] = useState<string[]>([aiBlurbs[0]]);
  const [heatmap] = useState(makeHeatmap());

  const seriesTreasury = useMemo(() => makeSeries(36, 4.8, 0.2).map((d) => ({ t: d.t, v: +(d.v).toFixed(2) })), []);
  const seriesUsers = useMemo(() => makeSeries(30, 1200, 55), []);
  const seriesEngagement = useMemo(() => makeSeries(30, 45, 4), []);

  useEffect(() => { const id = setInterval(() => setNow(new Date()), 1000); return () => clearInterval(id); }, []);
  useEffect(() => {
    const id = setInterval(() => {
      setTps((prev) => Math.max(1000, Math.floor(1200 + (Math.random() - 0.5) * 300)));
      setAiLog((l) => [aiBlurbs[Math.floor(Math.random() * aiBlurbs.length)], ...l].slice(0, 7));
    }, 3000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    // Initial load from data layer (replaces mocks as you wire real endpoints)
    (async () => {
      const [cs, usd, props, eng, sec] = await Promise.all([
        getChainStats(),
        getTreasuryUSD(),
        getProposals(),
        getEngagement(),
        getSecurityPosture(),
      ]);
      setChainStats({ blockHeight: cs.blockHeight, finalityMs: cs.finalityMs, peers: cs.peers });
      setTreasuryUSD(usd);
      setProposals(props);
      setVotersActive(eng.votersActive);
      setEngagementPct(eng.engagementPct);
      setSecurity(sec);
    })();
  }, []);

  const pieData = [
    { name: "Yes", value: Math.max(40, Math.min(90, Math.round((proposals[0]?.support ?? 70)))) },
    { name: "No", value: 100 - Math.max(40, Math.min(90, Math.round((proposals[0]?.support ?? 70)))) - 11 },
    { name: "Abstain", value: 11 },
  ];

  const radialData = [
    { name: "Transparency", value: security.transparency, fill: palette[0] },
    { name: "Security", value: security.security, fill: palette[1] },
    { name: "Participation", value: security.participation, fill: palette[2] },
  ];

  const funnel = [
    { step: "Visitors", v: 100 },
    { step: "Signed In", v: 62 },
    { step: "Wallets Linked", v: 54 },
    { step: "First Vote", v: 41 },
    { step: "Repeat Voters", v: 33 },
  ];

  const Blocks = () => (
    <div className="relative w-full overflow-hidden">
      <div className="absolute right-0 top-0 text-xs text-zinc-400">program: {CONFIG.GOVERNANCE_PROGRAM_ID.slice(0,6)}… chain</div>
      <div className="flex gap-3 py-2 animate-[scrollLeft_18s_linear_infinite]" style={{ width: "max-content" }}>
        {range(20).map((i) => (
          <motion.div
            key={i}
            className="min-w-[140px] rounded-2xl border bg-gradient-to-br from-zinc-900 to-zinc-800 p-3 shadow-md"
            animate={{ y: [0, -3, 0] }}
            transition={{ duration: 3 + (i % 3), repeat: Infinity }}
          >
            <div className="text-xs text-zinc-400">Block</div>
            <div className="font-mono text-sm">#{(chainStats.blockHeight ?? 1234567) + i}</div>
            <div className="my-2 h-px bg-white/10" />
            <div className="text-xs break-all font-mono text-zinc-400">
              {Math.random().toString(16).slice(2, 10)}…{Math.random().toString(16).slice(2, 10)}
            </div>
          </motion.div>
        ))}
      </div>
      <style>{`
        @keyframes scrollLeft { 0%{ transform: translateX(0);} 100%{ transform: translateX(-50%);} }
      `}</style>
    </div>
  );

  const ClockTile = () => (
    <div className="flex items-center gap-3">
      <Clock className="h-4 w-4" />
      <div className="font-mono">
        <div>{now.toLocaleString()}</div>
        <div className="text-xs text-zinc-400">UTC: {new Date(now.getTime() + now.getTimezoneOffset()*60000).toISOString().replace("T"," ").slice(0,19)}</div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-black via-zinc-950 to-black text-zinc-100">
      <header className="sticky top-0 z-50 backdrop-blur supports-[backdrop-filter]:bg-black/40 border-b border-white/5">
        <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="h-5 w-5 text-fuchsia-400" />
            <h1 className="text-lg font-semibold tracking-tight">MicroAI Studios • Live Governance</h1>
            <Badge className="ml-2 bg-zinc-800 text-zinc-200">Alpha Mock</Badge>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden md:block"><ClockTile /></div>
            <Badge className="gap-1 bg-emerald-600"><Zap className="h-3 w-3"/> {tps || 1200} TPS</Badge>
            <Badge className="gap-1 border border-cyan-500/40 text-cyan-300"><Shield className="h-3 w-3"/> Timelock: {Math.round(CONFIG.TIMELOCK_SECONDS/3600)}h</Badge>
            <Button><Vote className="h-4 w-4 mr-1"/> Enter Vote</Button>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-4 py-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card><CardContent>
          <div className="flex items-center justify-between"><div className="text-xs text-zinc-400">Treasury</div><Coins className="h-4 w-4"/></div>
          <div className="text-2xl font-bold mt-1">${(treasuryUSD/1e6).toFixed(2)}M</div>
          <div className="text-xs text-emerald-400">+3.1% 30d</div>
          <div className="h-16 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={seriesTreasury}>
                <defs>
                  <linearGradient id="g1" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#16A34A" stopOpacity={0.6}/>
                    <stop offset="95%" stopColor="#16A34A" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <Area dataKey="v" type="monotone" stroke="#16A34A" fill="url(#g1)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent></Card>

        <Card><CardContent>
          <div className="flex items-center justify-between"><div className="text-xs text-zinc-400">Active Voters</div><Users className="h-4 w-4"/></div>
          <div className="text-2xl font-bold mt-1">{votersActive.toLocaleString()}</div>
          <div className="text-xs text-blue-400">+128 today</div>
          <div className="h-16 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={makeSeries(30, 1200, 55)}>
                <Line dataKey="v" type="monotone" stroke="#3B82F6" strokeWidth={2} dot={false}/>
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent></Card>

        <Card><CardContent>
          <div className="flex items-center justify-between"><div className="text-xs text-zinc-400">Engagement</div><Activity className="h-4 w-4"/></div>
          <div className="text-2xl font-bold mt-1">{engagementPct.toFixed(1)}%</div>
          <div className="text-xs text-fuchsia-400">7d high</div>
          <div className="h-16 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={makeSeries(30, 45, 4)}>
                <Bar dataKey="v" fill="#7C3AED" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent></Card>

        <Card><CardContent>
          <div className="flex items-center justify-between"><div className="text-xs text-zinc-400">Security Posture</div><Lock className="h-4 w-4"/></div>
          <div className="text-2xl font-bold mt-1">High</div>
          <div className="mt-2 h-16">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart innerRadius="40%" outerRadius="100%" data={[
                { name: "Transparency", value: security.transparency, fill: palette[0] },
                { name: "Security", value: security.security, fill: palette[1] },
                { name: "Participation", value: security.participation, fill: palette[2] },
              ]}>
                <RadialBar dataKey="value" />
                <Legend />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
        </CardContent></Card>
      </section>

      <section className="mx-auto max-w-7xl px-4 pb-16 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="col-span-1 lg:col-span-2 space-y-6">
          <Card><CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm"><Vote className="h-4 w-4"/><span>Active Proposals</span></div>
              <Button>Submit Proposal</Button>
            </div>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              {proposals.map((p) => (
                <div key={p.id} className="rounded-2xl border border-white/10 bg-zinc-900/60 p-4">
                  <div className="text-xs text-zinc-400">{p.id}</div>
                  <div className="font-medium mt-1 line-clamp-2">{p.title}</div>
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span>Progress</span>
                      <span>{p.progress}%</span>
                    </div>
                    <Progress value={p.progress} />
                    <div className="flex items-center justify-between text-xs mt-2">
                      <span>Ends {new Date(p.endsISO).toLocaleTimeString()}</span>
                      <span className="text-emerald-400">Support {p.support}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent></Card>

          <Card><CardContent>
            <div className="flex items-center gap-2 text-sm mb-4"><ChartBar className="h-4 w-4"/> Live Vote Split</div>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={[...[{ name: "Yes", value: pieData[0].value }, { name:"No", value: pieData[1].value }, {name:"Abstain", value: pieData[2].value }]]} dataKey="value" nameKey="name" innerRadius={70} outerRadius={110} paddingAngle={2}>
                    {pieData.map((_, i) => (<Cell key={i} fill={palette[i]} />))}
                  </Pie>
                  <RTooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 grid grid-cols-3 text-xs text-center">
              {pieData.map((p, i) => (
                <div key={i} className="flex items-center gap-2 justify-center"><span className="h-2 w-2 rounded-full" style={{ background: palette[i] }} /> {p.name} {p.value}%</div>
              ))}
            </div>
          </CardContent></Card>

          <Card><CardContent>
            <div className="flex items-center gap-2 text-sm mb-3"><TrendingUp className="h-4 w-4"/> Community Growth</div>
            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={makeSeries(30, 1200, 55)}>
                  <defs>
                    <linearGradient id="g2" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.6}/>
                      <stop offset="95%" stopColor="#06B6D4" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="t" stroke="#6b7280"/>
                  <YAxis stroke="#6b7280"/>
                  <Area dataKey="v" type="monotone" stroke="#06B6D4" fill="url(#g2)" strokeWidth={2} />
                  <RTooltip/>
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent></Card>
        </div>

        <div className="space-y-6">
          <Card><CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm"><LinkIcon className="h-4 w-4"/> Blockchain</div>
              <Badge>Slots live</Badge>
            </div>
            <div className="mt-3"><Blocks /></div>
            <div className="mt-3 grid grid-cols-3 text-xs">
              <div>Height<br/><span className="font-mono text-emerald-400">{chainStats.blockHeight ?? 1234567}</span></div>
              <div>Finality<br/><span className="font-mono text-blue-400">~{chainStats.finalityMs ?? 400}ms</span></div>
              <div>Peers<br/><span className="font-mono text-fuchsia-400">{chainStats.peers ?? 842}</span></div>
            </div>
          </CardContent></Card>

          <Card><CardContent>
            <div className="flex items-center gap-2 text-sm mb-2"><Bot className="h-4 w-4"/> AI Governance Stream</div>
            <div className="space-y-2 max-h-48 overflow-auto pr-1">
              {aiLog.map((line, i) => (
                <div key={i} className="text-xs bg-zinc-900/60 border border-white/10 rounded-lg p-2 font-mono">{line}</div>
              ))}
            </div>
          </CardContent></Card>

          <Card><CardContent>
            <div className="flex items-center gap-2 text-sm mb-3"><Users className="h-4 w-4"/> Engagement Funnel</div>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={[
                  { step: "Visitors", v: 100 },
                  { step: "Signed In", v: 62 },
                  { step: "Wallets Linked", v: 54 },
                  { step: "First Vote", v: 41 },
                  { step: "Repeat Voters", v: 33 },
                ]}>
                  <XAxis dataKey="step" stroke="#6b7280" interval={0} angle={-15} textAnchor="end" height={50}/>
                  <YAxis stroke="#6b7280"/>
                  <Bar dataKey="v" radius={[6,6,0,0]}>
                    {[0,1,2,3,4].map((i) => (<Cell key={i} fill={palette[i % palette.length]} />))}
                  </Bar>
                  <RTooltip />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent></Card>

          <Card><CardContent>
            <div className="flex items-center gap-2 text-sm mb-2"><Eye className="h-4 w-4"/> Activity Heatmap</div>
            <div className="grid grid-cols-8 gap-1">
              <div className="text-[10px] text-right pr-1 col-span-1 space-y-1">
                {["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].map((d) => (<div key={d}>{d}</div>))}
              </div>
              <div className="col-span-7">
                {["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].map((_, r) => (
                  <div key={r} className="grid grid-cols-24 gap-1 mb-1">
                    {Array.from({length:24}).map((_, c) => {
                      const v = Math.floor(Math.random()*8);
                      const alpha = 0.15 + v * 0.1;
                      return <div key={c} className="h-3 rounded" style={{ background: `rgba(124,58,237,${alpha})`}} />;
                    })}
                  </div>
                ))}
              </div>
            </div>
          </CardContent></Card>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 pb-24">
        <Card className="bg-gradient-to-r from-fuchsia-900/40 via-cyan-900/30 to-emerald-900/30">
          <CardContent className="p-6 md:p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div>
                <div className="text-sm uppercase tracking-widest text-zinc-300">Founding Citizen Drive</div>
                <h2 className="mt-2 text-2xl md:text-3xl font-semibold">Become a co-author of the AI–Human Republic</h2>
                <p className="mt-2 text-zinc-300">Earn an on-chain badge for your first 3 votes, unlock proposal authoring, and get early access to governance workshops.</p>
                <div className="mt-4 flex gap-3">
                  <Button><Vote className="h-4 w-4 mr-1"/> Cast Your First Vote</Button>
                  <Button variant="secondary"><GitBranch className="h-4 w-4 mr-1"/> Contribute on Git</Button>
                </div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
                <div className="text-sm mb-2">Launch Milestones</div>
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center justify-between text-xs"><span>Genesis Vote Participation</span><span>78%</span></div>
                    <Progress value={78} />
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs"><span>Docs & Tutorials Completed</span><span>64%</span></div>
                    <Progress value={64} />
                  </div>
                  <div>
                    <div className="flex items-center justify-between text-xs"><span>Audit Readiness</span><span>55%</span></div>
                    <Progress value={55} />
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      <footer className="border-t border-white/5 py-8 text-center text-xs text-zinc-400">© {new Date().getFullYear()} MicroAI Studios — Dashboard.</footer>
    </div>
  );
}
