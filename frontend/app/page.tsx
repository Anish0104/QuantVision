"use client";

import React, { useState, useEffect } from "react";
import { 
  TrendingUp, 
  LayoutDashboard, 
  Wind, 
  PieChart, 
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  ShieldCheck,
  Search,
  LogOut,
  RefreshCw
} from "lucide-react";
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip,
  PieChart as RePieChart, // Renamed to avoid conflict with lucide-react PieChart
  Pie,
  Cell,
  BarChart,
  Bar
} from "recharts";
import { Menu, X } from "lucide-react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";

// --- COMPONENTS ---

const MetricCard = ({ label, value, subtext, trend }: any) => (
  <motion.div 
    initial={{ opacity: 0, y: 15 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-[#0a0a0a] border border-white/5 rounded-2xl p-6 transition-all duration-300 hover:border-[#6366f1]/40 relative overflow-hidden group"
  >
    <div className="absolute top-0 right-0 p-2 opacity-5 group-hover:opacity-10 transition-opacity">
      <Activity size={40} />
    </div>
    <p className="text-[9px] text-gray-600 font-black uppercase tracking-[0.25em] mb-4 flex items-center gap-2">
      <span className="w-1 h-1 bg-[#6366f1] rounded-full" />
      {label}
    </p>
    <h3 className="text-3xl font-black font-outfit text-white mb-2 tabular-nums tracking-tighter">{value}</h3>
    <div className="flex items-center gap-2">
      <div className={`flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-black ${trend > 0 ? "bg-[#6366f1]/10 text-[#6366f1]" : "bg-rose-500/10 text-rose-500"}`}>
        {trend > 0 ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />}
        {Math.abs(trend)}%
      </div>
      <span className="text-[9px] text-gray-700 font-bold uppercase tracking-widest">{subtext}</span>
    </div>
  </motion.div>
);

const SidebarItem = ({ icon: Icon, label, active, onClick }: any) => (
  <div 
    onClick={onClick}
    className={`flex items-center gap-3 px-8 py-4 cursor-pointer transition-all ${
      active 
        ? "text-white font-black" 
        : "text-gray-600 hover:text-gray-400"
    } group relative`}
  >
    {active && (
      <motion.div 
        layoutId="sidebar-active"
        className="absolute left-0 w-1 h-6 bg-[#6366f1] rounded-r-full shadow-[0_0_15px_rgba(99,102,241,0.5)]"
      />
    )}
    <Icon size={18} className={`${active ? "text-[#6366f1]" : "group-hover:text-gray-400"}`} />
    <span className="text-[10px] font-black uppercase tracking-[0.2em]">{label}</span>
  </div>
);

// --- MAIN PAGE ---

export default function Home() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const [activeTab, setActiveTab] = useState("Alpha Signals");
  const [ticker, setTicker] = useState("AAPL");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState("1M");
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [userName, setUserName] = useState("Global User");
  const [riskTolerance, setRiskTolerance] = useState("Moderate");
  const [profileOpen, setProfileOpen] = useState(false);
  const [entranceStep, setEntranceStep] = useState(0); // 0: Landing, 1: Dashboard
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [marketPrices, setMarketPrices] = useState([
    { label: "S&P 500", val: 5241.53, change: 1.2 },
    { label: "VIX INDEX", val: 13.42, change: -4.5 },
    { label: "BTC/USD", val: 67241, change: 2.1 },
    { label: "10Y YIELD", val: 4.21, change: 0.3 }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setMarketPrices(prev => prev.map(p => ({
        ...p,
        val: p.val + (Math.random() - 0.5) * (p.val * 0.001),
        change: p.change + (Math.random() - 0.5) * 0.1
      })));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const savedW = localStorage.getItem("finvision_watchlist");
    if (savedW) setWatchlist(JSON.parse(savedW));

    const u = localStorage.getItem("finvision_user");
    if (u) setUserName(u);
    const r = localStorage.getItem("finvision_risk");
    if (r) setRiskTolerance(r);
  }, []);

  const handleEnterTerminal = () => {
    setEntranceStep(1);
    triggerToast("Terminal Synchronized");
  };

  const saveProfile = (name: string, risk: string) => {
    setUserName(name);
    setRiskTolerance(risk);
    localStorage.setItem("finvision_user", name);
    localStorage.setItem("finvision_risk", risk);
    setProfileOpen(false);
  };

  const toggleWatchlist = (t: string) => {
    const newW = watchlist.includes(t) 
      ? watchlist.filter(x => x !== t) 
      : [...watchlist, t];
    setWatchlist(newW);
    localStorage.setItem("finvision_watchlist", JSON.stringify(newW));
  };

  const trendingAssets = [
    { symbol: "AAPL", label: "Apple", type: "Stock" },
    { symbol: "TSLA", label: "Tesla", type: "Stock" },
    { symbol: "BTC-USD", label: "Bitcoin", type: "Crypto" },
    { symbol: "NVDA", label: "Nvidia", type: "Stock" },
    { symbol: "GOOGL", label: "Google", type: "Stock" },
    { symbol: "MSFT", label: "Microsoft", type: "Stock" },
    { symbol: "META", label: "Meta", type: "Stock" },
    { symbol: "AMD", label: "AMD", type: "Stock" },
    { symbol: "NFLX", label: "Netflix", type: "Stock" },
    { symbol: "PYPL", label: "PayPal", type: "Stock" },
    { symbol: "SPY", label: "S&P 500", type: "Index" }
  ];

  const runAnalysis = async (customTicker?: string) => {
    const targetTicker = customTicker || ticker;
    if (customTicker) setTicker(targetTicker);
    
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/analyze`, {
        ticker: targetTicker,
        start_date: "2021-01-01",
        end_date: "2024-03-21"
      });
      // The backend returns { ticker, signal, metrics: { ... }, equity_curve: [ ... ] }
      // We need to ensure we map metrics correctly if they are used directly in the UI
      setData(res.data);
      triggerToast(`Analysis Synchronized: ${targetTicker}`);
      if (activeTab !== "Alpha Signals") {
        setActiveTab("Alpha Signals");
      }
      setIsMobileMenuOpen(false);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getFilteredData = () => {
    if (!data?.equity_curve) return [];
    if (timeRange === "1W") return data.equity_curve.slice(-7);
    if (timeRange === "1M") return data.equity_curve.slice(-30);
    if (timeRange === "1Y") return data.equity_curve.slice(-252);
    return data.equity_curve;
  };

  useEffect(() => {
    document.title = data ? `${ticker} | QuantVision` : "QuantVision | Institutional Strategy";
  }, [data, ticker]);
  const [showToast, setShowToast] = useState(false);
  const [toastMsg, setToastMsg] = useState("");

  const triggerToast = (msg: string) => {
    setToastMsg(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };


  const renderContent = () => {
    if (!data) {
      return (
        <div className="h-[60vh] flex items-center justify-center border-2 border-dashed border-white/10 rounded-[64px] bg-gradient-to-br from-white/[0.03] to-transparent">
          <motion.div 
            animate={{ y: [0, -15, 0] }}
            transition={{ repeat: Infinity, duration: 5 }}
            className="text-center"
          >
            <div className="w-28 h-28 rounded-[38px] bg-white/[0.03] flex items-center justify-center mx-auto mb-10 border border-white/10 shadow-2xl">
              <Search className="text-gray-700" size={48} />
            </div>
            <p className="text-gray-600 text-[11px] font-black uppercase tracking-[0.5em]">Analyst core ready for synchronization</p>
          </motion.div>
        </div>
      );
    }

    switch (activeTab) {
      case "Portfolio Hub":
        return (
          <div className="space-y-16">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-10">
               <MetricCard 
                 label="Strategy Yield" 
                 value={data.metrics?.["Total Return (%)"] !== undefined ? `${data.metrics["Total Return (%)"].toFixed(2)}%` : "N/A"} 
                 trend={data.metrics?.["Total Return (%)"] > 0 ? 2.4 : -1.2} 
                 subtext="Cumulative Return" 
               />
               <MetricCard 
                 label="Efficiency Index" 
                 value={data.metrics?.["Sharpe Ratio"] !== undefined ? data.metrics["Sharpe Ratio"].toFixed(2) : "N/A"} 
                 trend={data.metrics?.["Sharpe Ratio"] > 1 ? 4.1 : -0.5} 
                 subtext="Sharpe Ratio" 
               />
               <MetricCard 
                 label="Risk Exposure" 
                 value={data.metrics?.["Max Drawdown (%)"] !== undefined ? `${data.metrics["Max Drawdown (%)"].toFixed(1)}%` : "N/A"} 
                 trend={data.metrics?.["Max Drawdown (%)"] > -10 ? -4.1 : 2.0} 
                 subtext="Max Drawdown" 
               />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
               <motion.div className="lg:col-span-12 bg-[#111111]/40 backdrop-blur-xl border border-white/5 rounded-[40px] p-12">
                  <h4 className="font-black text-[11px] text-gray-500 uppercase tracking-[0.4em] mb-12 flex items-center gap-4">
                    <PieChart size={16} /> Asset Allocation Matrix
                  </h4>
                  <div className="flex flex-col lg:flex-row items-center justify-between gap-12">
                    <div className="w-full lg:w-1/2 h-[300px] md:h-[400px]">
                      <ResponsiveContainer>
                        <RePieChart>
                          <Pie 
                            data={[
                              { name: 'Equities', value: 65 },
                              { name: 'Bonds', value: 20 },
                              { name: 'Alpha', value: 15 }
                            ]}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            <Cell fill="#6366f1" />
                            <Cell fill="#1a1a1a" />
                            <Cell fill="#333" />
                          </Pie>
                        </RePieChart>
                      </ResponsiveContainer>
                      <div className="flex flex-wrap items-center justify-center gap-6 md:gap-12 pt-10">
                         {[
                           { label: "Equities", color: "#6366f1", val: "65%" },
                           { label: "Bonds", color: "#222", val: "20%" },
                           { label: "Alpha", color: "#444", val: "15%" }
                         ].map(item => (
                           <div key={item.label} className="text-center">
                              <div className="w-3 h-3 rounded-full mx-auto mb-3" style={{ background: item.color }} />
                              <p className="text-[10px] font-black uppercase text-gray-500 mb-1">{item.label}</p>
                              <p className="text-xl md:text-2xl font-black text-white">{item.val}</p>
                           </div>
                         ))}
                      </div>
                    </div>
                    <div className="w-full lg:w-1/2 space-y-8 lg:pl-12">
                       <p className="text-gray-400 text-sm md:text-base leading-relaxed">
                          Your portfolio is currently optimized for **Institutional Resilience**. 
                          The secular AI engine has clustered assets into a risk-parity framework.
                       </p>
                       <button className="w-full md:w-auto rounded-full px-8 py-4 bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-widest hover:bg-[#6366f1] hover:text-white transition-all">
                          Run Rebalance Logic
                       </button>
                    </div>
                  </div>
               </motion.div>
            </div>
          </div>
        );

      case "Stress Terminal":
        return (
          <div className="space-y-16">
            <div className="bg-[#1e1b4b]/10 border border-[#6366f1]/20 rounded-[40px] p-12">
               <h4 className="font-black text-[11px] text-[#6366f1] uppercase tracking-[0.4em] mb-12 flex items-center gap-4">
                 <Wind size={16} /> Crisis Simulation Engine
               </h4>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-20">
                  <div>
                    <p className="text-gray-400 text-lg mb-8">How would your strategy handle a **"Black Swan"** event? We've simulated historic crashes against your current neural weights.</p>
                    <div className="space-y-6">
                       {[
                         { name: "2008 Financial Crisis", impact: "-12.4%", status: "SURVIVED" },
                         { name: "2020 Pandemic Crash", impact: "-8.1%", status: "RECOVERED" },
                         { name: "2022 Fed Tightening", impact: "+2.4%", status: "THRIVED" }
                       ].map(event => (
                         <div key={event.name} className="flex justify-between items-center p-6 bg-white/5 rounded-3xl border border-white/5">
                            <div>
                               <p className="text-xs font-black text-white mb-1 uppercase tracking-wider">{event.name}</p>
                               <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">{event.status}</p>
                            </div>
                            <span className={`text-xl font-black ${event.impact.startsWith('+') ? 'text-[#6366f1]' : 'text-rose-500'}`}>{event.impact}</span>
                         </div>
                       ))}
                    </div>
                  </div>
                   <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed border-white/5 rounded-[40px] bg-white/[0.01]">
                      <div className="text-center">
                         <ShieldCheck className="mx-auto mb-6 text-[#6366f1]/30" size={64} />
                         <p className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-8">Crisis Shield: READY</p>
                         <button 
                           onClick={() => triggerToast("Simulation Node: RE-CALCULATING...")}
                           className="flex items-center gap-3 mx-auto px-6 py-3 bg-[#6366f1] text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-white hover:text-[#6366f1] transition-all"
                         >
                           <RefreshCw size={14} className="animate-spin-slow" />
                           Execute Stress Test
                         </button>
                      </div>
                   </div>
               </div>
            </div>
          </div>
        );

      case "Market Insights":
        return (
          <div className="space-y-16">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
               <div className="bg-[#111] p-12 rounded-[40px] border border-white/5">
                  <h4 className="font-black text-[11px] text-gray-500 uppercase tracking-[0.4em] mb-8">Sentiment Pulse</h4>
                  <div className="h-64 flex items-end gap-2 bg-white/5 rounded-3xl p-8 relative overflow-hidden">
                     <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-[#6366f1]/20 to-transparent" />
                     {[40, 60, 30, 80, 50, 90, 40, 70].map((h, i) => (
                       <motion.div 
                         key={i} 
                         initial={{ height: 0 }}
                         animate={{ height: `${h}%` }}
                         transition={{ delay: i * 0.1, duration: 1 }}
                         className="flex-1 bg-[#6366f1] rounded-t-lg opacity-40" 
                       />
                     ))}
                  </div>
                  <p className="mt-8 text-gray-400 text-sm">Fear & Greed Index: **74 (Extreme Greed)**. Analyst core suggests caution on entry points.</p>
               </div>
               <div className="bg-[#111] p-12 rounded-[40px] border border-white/5">
                  <h4 className="font-black text-[11px] text-gray-500 uppercase tracking-[0.4em] mb-8">Global Liquidity</h4>
                   <div className="space-y-8">
                      {[
                        { label: "M2 Money Supply", val: "STABLE" },
                        { label: "Repo Market Volume", val: "$1.2T" },
                        { label: "Capital Inflow", val: "+$420M" }
                      ].map(item => (
                        <div key={item.label} className="flex justify-between items-end border-b border-white/5 pb-4">
                           <span className="text-[10px] text-gray-500 font-black uppercase tracking-widest">{item.label}</span>
                           <span className="text-lg font-black text-white">{item.val}</span>
                        </div>
                      ))}
                   </div>
               </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="space-y-16">
            {/* Metric Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
              <MetricCard 
                label="Net Worth Impact" 
                value={`${(data?.metrics?.["Annualized Return (%)"] ?? 0).toFixed(1)}%`} 
                trend={14.8} 
                subtext="Targeting Growth" 
              />
              <MetricCard 
                label="Risk Score" 
                value={(data?.metrics?.["Sharpe Ratio"] ?? 0).toFixed(2)} 
                trend={3.1} 
                subtext="Institutional Grade" 
              />
              <MetricCard 
                label="Signal Health" 
                value={data.signal} 
                trend={100} 
                subtext="Analyst Confidence" 
              />
              <MetricCard 
                label="Liquid Reserve" 
                value="12,248.64" 
                trend={-0.5} 
                subtext="Available Capital" 
              />
            </div>

            {/* Chart & Detail */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
              <motion.div 
                 initial={{ opacity: 0, scale: 0.98 }}
                 animate={{ opacity: 1, scale: 1 }}
                 className="lg:col-span-8 bg-[#111111]/40 backdrop-blur-xl border border-white/5 rounded-[40px] p-10 group overflow-hidden"
              >
                <div className="flex justify-between items-center mb-16">
                  <h4 className="font-black text-[11px] text-gray-500 uppercase tracking-[0.4em] flex items-center gap-4">
                    <div className="w-3 h-3 rounded-full bg-[#6366f1] animate-pulse shadow-[0_0_10px_#6366f1]" />
                    Growth Projection Module
                  </h4>
                  <div className="flex gap-3">
                    {["1W", "1M", "1Y"].map((range) => (
                      <button 
                        key={range}
                        onClick={() => setTimeRange(range)}
                        className={`px-5 py-2 rounded-xl text-xs font-black transition-all ${
                          timeRange === range 
                            ? "bg-[#6366f1] text-white" 
                            : "bg-white/5 text-gray-400 hover:bg-white/10"
                        }`}
                      >
                        {range}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="h-[400px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={getFilteredData()}>
                      <defs>
                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.5}/>
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="15 15" vertical={false} stroke="#1a1a1a" />
                      <XAxis dataKey="date" hide />
                      <YAxis hide domain={['auto', 'auto']} />
                      <Tooltip 
                        contentStyle={{ background: '#080808', border: '1px solid #222', borderRadius: '24px', padding: '20px', boxShadow: '0 20px 40px rgba(0,0,0,0.8)' }}
                        labelStyle={{ color: '#6366f1', fontWeight: '900', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '2px' }}
                        itemStyle={{ color: '#fff', fontSize: '14px', fontWeight: '700' }}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="value" 
                        stroke="#6366f1" 
                        strokeWidth={5}
                        fillOpacity={1} 
                        fill="url(#colorValue)" 
                        animationDuration={3000}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </motion.div>

              <motion.div 
                 initial={{ opacity: 0, x: 30 }}
                 animate={{ opacity: 1, x: 0 }}
                 className="lg:col-span-4 bg-[#1e1b4b]/10 backdrop-blur-xl border border-[#6366f1]/20 rounded-[40px] p-10 flex flex-col justify-between"
              >
                <div>
                  <h4 className="font-black text-[11px] text-[#6366f1] uppercase tracking-[0.4em] mb-12 flex items-center gap-4">
                    <ShieldCheck size={20} />
                    Security Check
                  </h4>
                  <div className="space-y-10">
                    <div>
                      <p className="text-[11px] text-gray-600 font-black uppercase mb-4 tracking-widest">Portfolio Resilience</p>
                      <p className="text-6xl font-black font-outfit text-white">Elite</p>
                    </div>
                    <div className="pt-10 border-t border-white/5 space-y-6">
                      {[
                         { label: "Model Stability", val: "99.2%", color: "text-[#6366f1]" },
                         { label: "Market Sentiment", val: "BULLISH", color: "text-white" },
                         { label: "Analyst Buffer", val: "12ms", color: "text-gray-400" }
                      ].map((stat, i) => (
                        <div key={i} className="flex justify-between items-end">
                          <span className="text-[10px] text-gray-500 font-black uppercase tracking-widest">{stat.label}</span>
                          <span className={`text-lg font-black font-outfit ${stat.color}`}>{stat.val}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <button 
                  onClick={() => runAnalysis()}
                  className="w-full bg-white/5 hover:bg-[#6366f1]/10 text-[#6366f1] text-[11px] font-black uppercase tracking-[0.3em] py-5 rounded-2xl transition-all mt-12 border border-white/5 hover:border-[#6366f1]/30"
                >
                   Refresh Strategy Intelligence
                </button>
              </motion.div>
            </div>
          </div>
        );
    }
  };

  if (entranceStep === 0) {
    return (
      <div className="min-h-screen bg-[#020202] text-white flex items-center justify-center p-6 relative overflow-hidden font-inter selection:bg-[#6366f1] selection:text-white">
        {/* Elite Neural Background */}
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_0%,rgba(99,102,241,0.25),transparent)] pointer-events-none" />
        <div className="absolute top-0 left-0 w-full h-full opacity-[0.07] pointer-events-none" style={{ backgroundImage: `linear-gradient(#6366f1 1px, transparent 1px), linear-gradient(90deg, #6366f1 1px, transparent 1px)`, backgroundSize: '120px 120px' }} />
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.9, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          className="w-full max-w-4xl relative z-10 text-center"
        >
          <motion.div 
            animate={{ y: [0, -10, 0] }}
            transition={{ repeat: Infinity, duration: 8, ease: "easeInOut" }}
            className="w-20 h-20 rounded-[32px] bg-gradient-to-br from-[#6366f1] to-[#4f46e5] flex items-center justify-center mx-auto mb-12 shadow-[0_0_80px_rgba(99,102,241,0.4)]"
          >
            <Zap size={40} className="text-white" />
          </motion.div>
          
          <h1 className="text-[48px] md:text-[80px] font-black font-outfit tracking-tighter leading-none mb-4 text-white hover:italic transition-all cursor-default lg:text-[96px]">
            QuantVision
          </h1>
          <p className="text-[#6366f1]/80 font-black uppercase tracking-[0.5em] md:tracking-[1em] text-[8px] md:text-[10px] mb-12 md:ml-2">Institutional Quant Terminal</p>
          
          <div className="max-w-xl mx-auto space-y-8">
            <p className="text-gray-500 text-sm md:text-lg font-medium leading-relaxed italic">
              "Precision is the only edge in asymmetric markets."
            </p>
            
            <button 
              onClick={handleEnterTerminal}
              className="group relative px-8 py-4 md:px-12 md:py-5 bg-white text-[#020202] rounded-full font-black text-[9px] md:text-[10px] uppercase tracking-[0.4em] overflow-hidden transition-all hover:scale-105 active:scale-95 shadow-[0_20px_60px_rgba(99,102,241,0.2)]"
            >
              <span className="relative z-10">Access Node</span>
              <div className="absolute inset-0 bg-[#6366f1] opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="absolute inset-0 bg-white group-hover:bg-[#6366f1] transition-colors" />
              <span className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 text-white transition-opacity">Access Node</span>
            </button>
          </div>

          <div className="mt-20 md:mt-40 grid grid-cols-2 md:grid-cols-3 gap-8 md:gap-12 border-t border-white/5 pt-12 md:pt-20">
            {[
              { l: "SECURE NODE", v: "ACTIVE" },
              { l: "QUANT CORE", v: "V8.0" },
              { l: "MARKET CLOUD", v: "SYNCED" }
            ].map((i, idx) => (
              <div key={i.l} className={idx === 2 ? "col-span-2 md:col-span-1" : ""}>
                <p className="text-[8px] md:text-[9px] text-gray-500 font-black uppercase tracking-widest mb-2">{i.l}</p>
                <p className="text-base md:text-lg font-black text-white">{i.v}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-[#020202] text-white font-inter selection:bg-[#6366f1] selection:text-white overflow-hidden relative">
      
      {/* Mobile Header */}
      <div className="fixed top-0 left-0 w-full h-20 bg-black/80 backdrop-blur-md border-b border-white/5 z-[60] flex items-center justify-between px-6 lg:hidden">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-[#6366f1] flex items-center justify-center">
            <Zap size={18} className="text-white" />
          </div>
          <h1 className="text-xl font-black font-outfit tracking-tighter text-white">QuantVision</h1>
        </div>
        <button 
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center text-white"
        >
          {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Sidebar Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsMobileMenuOpen(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 w-72 bg-[#080808] border-r border-white/5 flex flex-col pt-12 z-[55] shadow-2xl transition-transform duration-500 ease-in-out lg:relative lg:translate-x-0 ${isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="px-8 mb-12">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-3 mb-2"
          >
            <div className="w-10 h-10 rounded-2xl bg-[#6366f1] flex items-center justify-center shadow-[0_0_30px_rgba(99,102,241,0.3)]">
              <Zap size={22} className="text-white" />
            </div>
            <h1 className="text-2xl font-black font-outfit tracking-tighter text-white">QuantVision</h1>
          </motion.div>
        </div>

        <nav className="flex-1">
          {[
            { id: "Alpha Signals", icon: Activity },
            { id: "Portfolio Hub", icon: PieChart },
            { id: "Stress Terminal", icon: Wind },
            { id: "Market Insights", icon: LayoutDashboard }
          ].map((item, idx) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <SidebarItem 
                icon={item.icon} 
                label={item.id} 
                active={activeTab === item.id} 
                onClick={() => {
                  setActiveTab(item.id);
                  setIsMobileMenuOpen(false);
                }}
              />
            </motion.div>
          ))}
          {watchlist.length > 0 && (
            <div className="px-10 mb-10 overflow-hidden">
              <p className="text-[10px] text-[#6366f1] mb-5 font-black uppercase tracking-[0.2em] border-b border-[#6366f1]/20 pb-2">My Proprietary Watchlist</p>
              <div className="flex flex-wrap gap-2">
                {watchlist.map((symbol) => (
                  <button 
                    key={symbol}
                    onClick={() => {
                      runAnalysis(symbol);
                      setIsMobileMenuOpen(false);
                    }}
                    className="px-4 py-2 rounded-xl bg-[#6366f1]/10 border border-[#6366f1]/30 text-[9px] font-black text-white hover:bg-[#6366f1]/20 transition-all font-outfit"
                  >
                    {symbol}
                  </button>
                ))}
              </div>
            </div>
          )}
        </nav>

        <div className="px-10 mb-10">
          <p className="text-[10px] text-gray-500 mb-5 font-black uppercase tracking-[0.2em] border-b border-white/5 pb-2">Trending Universe</p>
          <div className="flex flex-wrap gap-2">
            {trendingAssets.map((asset) => (
              <button 
                key={asset.symbol}
                onClick={() => {
                  runAnalysis(asset.symbol);
                  setIsMobileMenuOpen(false);
                }}
                className="px-4 py-2 rounded-xl bg-white/5 border border-white/5 text-[9px] font-black text-gray-400 hover:border-[#6366f1] hover:text-white hover:bg-[#6366f1]/10 transition-all font-outfit"
              >
                {asset.symbol}
              </button>
            ))}
          </div>
        </div>

        <div className="p-10 border-t border-white/5 bg-gradient-to-t from-[#1e1b4b]/20 to-transparent">
          <p className="text-[10px] text-gray-500 mb-6 font-black uppercase tracking-widest">Asset Analysis</p>
          <div className="space-y-4">
            <div className="relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-[#6366f1] transition-colors" size={16} />
              <input 
                type="text" 
                placeholder="Search global assets..." 
                className="w-full bg-white/5 border border-white/5 rounded-xl py-3 pl-12 pr-4 text-xs font-bold text-white focus:outline-none focus:border-[#6366f1] focus:ring-1 focus:ring-[#6366f1] transition-all"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                onKeyDown={(e) => e.key === 'Enter' && runAnalysis()}
              />
            </div>
            
            <div className="flex gap-2">
              <button 
                onClick={() => runAnalysis()}
                disabled={loading}
                className="flex-1 rounded-xl py-3 bg-[#6366f1] text-white text-[10px] font-black uppercase tracking-widest hover:bg-white hover:text-[#6366f1] hover:scale-[1.02] transition-all active:scale-95 disabled:opacity-50"
              >
                {loading ? "Analyzing..." : "Analyze"}
              </button>
              <button 
                onClick={() => toggleWatchlist(ticker)}
                className={`w-12 h-12 rounded-xl border flex items-center justify-center transition-all ${
                  watchlist.includes(ticker)
                    ? "bg-[#6366f1]/20 border-[#6366f1] text-[#6366f1]"
                    : "bg-white/5 border-white/5 text-gray-400 hover:border-gray-600"
                }`}
                title="Save to Watchlist"
              >
                <Zap size={16} />
              </button>
            </div>
          </div>
        </div>
        <div 
          onClick={() => setProfileOpen(true)}
          className="p-8 border-t border-white/5 flex items-center gap-4 bg-black/40 cursor-pointer hover:bg-white/5 transition-all group"
        >
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#6366f1] to-[#4f46e5] flex items-center justify-center font-black text-xs text-white group-hover:scale-110 transition-transform">
            {userName[0]}
          </div>
          <div>
            <p className="text-[10px] text-white font-black">{userName}</p>
            <p className="text-[9px] text-gray-400 font-bold group-hover:text-[#6366f1] transition-colors">{riskTolerance} Risk Profile</p>
          </div>
        </div>
      </aside>

      {/* Profile Modal */}
      <AnimatePresence>
        {profileOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setProfileOpen(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-xl"
            />
            <motion.div 
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="w-full max-w-md bg-[#0a0a0a] border border-white/10 rounded-[48px] p-12 relative z-10 shadow-[0_40px_100px_rgba(0,0,0,0.8)]"
            >
              <h3 className="text-3xl font-black font-outfit text-white mb-2">Edit Identity</h3>
              <p className="text-gray-500 text-xs font-bold uppercase tracking-widest mb-10">Institutional Account Settings</p>
              
              <div className="space-y-8">
                <div className="space-y-3">
                  <label className="text-[9px] text-gray-500 font-black uppercase tracking-widest ml-1">Full Identity Name</label>
                  <input 
                    type="text" 
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 px-6 text-sm font-bold text-white focus:border-[#6366f1] transition-all outline-none"
                  />
                </div>

                <div className="space-y-3">
                  <label className="text-[9px] text-gray-500 font-black uppercase tracking-widest ml-1">Risk Architecture</label>
                  <div className="grid grid-cols-3 gap-2">
                    {["Conservative", "Moderate", "Aggressive"].map((r) => (
                      <button 
                        key={r}
                        onClick={() => setRiskTolerance(r)}
                        className={`py-3 rounded-xl text-[9px] font-black uppercase tracking-tighter border transition-all ${
                          riskTolerance === r 
                            ? "bg-[#6366f1] text-white border-[#6366f1]" 
                            : "bg-white/5 text-gray-500 border-white/5 hover:border-white/10"
                        }`}
                      >
                        {r}
                      </button>
                    ))}
                  </div>
                </div>

                <button 
                  onClick={() => saveProfile(userName, riskTolerance)}
                  className="w-full bg-white text-[#6366f1] py-5 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-[#6366f1] hover:text-white transition-all mt-4"
                >
                  Confirm Evolution
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-[#020202] relative">
        {/* Visual Overlays */}
        <div className="absolute top-0 left-0 w-full h-[800px] bg-[radial-gradient(circle_at_50%_0%,rgba(99,102,241,0.08),transparent)] pointer-events-none" />
        <div className="absolute top-0 left-0 w-full h-full opacity-[0.03] pointer-events-none" style={{ backgroundImage: `linear-gradient(#6366f1 1px, transparent 1px), linear-gradient(90deg, #6366f1 1px, transparent 1px)`, backgroundSize: '60px 60px' }} />
        
        {/* Header Hero */}
        <header className="px-6 md:px-10 pt-32 md:pt-16 pb-12 relative border-b border-white/5">
          <div className="absolute top-0 right-0 w-full lg:w-[800px] h-[600px] bg-[#6366f1]/5 blur-[200px] -z-10 rounded-full animate-pulse" />
          
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="z-10 relative"
          >
            <div className="flex items-center gap-4 mb-6">
               <span className="h-[1px] w-8 md:w-12 bg-[#6366f1]/40" />
               <p className="text-[#6366f1] font-black tracking-[0.4em] text-[8px] md:text-[9px] uppercase">Institutional Node v8.1</p>
            </div>
            <h2 className="text-[32px] md:text-[52px] font-black font-outfit leading-[0.9] mb-6 tracking-tighter max-w-4xl">
               {data ? `Analysis: ${data.ticker}` : `Welcome, Institutional Agent`} <br /> <span className="text-gray-600 italic">Proprietary</span> {data ? "Optimization" : "Terminal Hub"}.
            </h2>
            <p className="text-gray-500 max-w-xl text-sm md:text-base leading-relaxed font-medium mb-10">
               Access high-fidelity optimization parameters for global equity markets. Precision-engineered for risk-adjusted performance.
            </p>

            {/* Quick Metrics Glance */}
            <div className="flex gap-6 md:gap-8 items-center border-l-2 border-white/5 pl-6 md:pl-12 flex-wrap">
              {marketPrices.map((m, i) => (
                <div key={i} className="group cursor-default">
                  <p className="text-[9px] text-gray-500 font-black uppercase tracking-widest mb-1 group-hover:text-[#6366f1] transition-colors">{m.label}</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-lg font-black text-white">{m.val.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>
                    <span className={`text-[10px] font-bold ${m.change > 0 ? "text-[#6366f1]" : "text-rose-500"}`}>
                      {m.change > 0 ? "+" : ""}{m.change.toFixed(2)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </header>

        {/* Dashboard Content */}
        <section className="px-6 md:px-12 pb-40" id="analysis-section">
           {renderContent()}
        </section>
      </main>

      {/* Persistence / Global UI */}
      <AnimatePresence>
        {showToast && (
          <motion.div 
            initial={{ opacity: 0, y: 50, x: "-50%" }}
            animate={{ opacity: 1, y: 0, x: "-50%" }}
            exit={{ opacity: 0, y: 20, x: "-50%" }}
            className="fixed bottom-12 left-1/2 -translate-x-1/2 z-[100] px-8 py-4 bg-[#6366f1] text-white font-black text-xs uppercase tracking-widest rounded-2xl shadow-[0_20px_50px_rgba(99,102,241,0.3)] border border-white/20 flex items-center gap-4"
          >
            <Zap size={16} />
            {toastMsg}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
