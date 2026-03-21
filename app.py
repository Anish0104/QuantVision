import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.data.loader import DataLoader
from src.features.indicators import FeatureEngineer
from src.core.trading_env import TradingEnv
from src.core.baselines import StrategyBaselines
from src.analysis.metrics import PerformanceMetrics
from src.analysis.visualization import Visualizer
from src.analysis.risk import RiskManager
from src.core.optimizer import PortfolioOptimizer
from src.analysis.stress_test import StressTester
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="FinVision | Smart Wealth Intelligence",
    page_icon="🍀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FINVO-INSPIRED CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@400;700&display=swap');
    
    :root {
        --finvo-green: #1a3c34;
        --finvo-light-green: #2d5a4f;
        --finvo-accent: #00ffcc;
        --finvo-white: #f8f9fa;
        --finvo-gray: #e9ecef;
        --finvo-dark: #0a0a0a;
    }
    
    .main {
        background: linear-gradient(135deg, var(--finvo-dark) 0%, #111 50%, #050505 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Rounded Containers (Finvo Style) */
    .stApp > header { background: transparent; }
    
    div[data-testid="stVerticalBlock"] > div > div {
        border-radius: 20px !important;
    }
    
    /* Metric Pods */
    .metric-pod {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 24px;
        border-radius: 24px;
        text-align: left;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .metric-pod:hover { transform: translateY(-5px); border-color: var(--finvo-accent); }
    .metric-val { font-size: 2rem; font-weight: 800; color: white; font-family: 'Outfit', sans-serif; }
    .metric-lab { font-size: 0.9rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Pill Buttons */
    .stButton > button {
        border-radius: 50px !important;
        padding: 10px 30px !important;
        background: var(--finvo-accent) !important;
        color: var(--finvo-dark) !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,255,204,0.3) !important;
    }
    
    /* Sidebar Overhaul */
    [data-testid="stSidebar"] {
        background-color: var(--finvo-dark);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, var(--finvo-green) 0%, var(--finvo-dark) 100%);
        padding: 30px;
        border-radius: 0 0 30px 30px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Header Gradient */
    .hero-section {
        background: linear-gradient(160deg, var(--finvo-green) 0%, var(--finvo-dark) 80%);
        padding: 60px 40px;
        border-radius: 40px;
        margin-bottom: 40px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        position: relative;
        overflow: hidden;
    }
    .hero-section::after {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0,255,204,0.05) 0%, transparent 60%);
        z-index: 0;
    }
    
    h1, h2, h3 { font-family: 'Outfit', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAV ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2 style='color: white; margin: 0;'>🍀 FinVision</h2>
        <p style='color: #888; font-size: 0.8rem;'>Institutional Wealth Core</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🛠️ Control Center")
    nav_mode = st.radio("Intelligence Layer", ["🎯 Alpha Signals", "📂 Portfolio Hub", "🌪️ Stress Terminal"])
    
    st.markdown("---")
    st.subheader("Asset Selection")
    tickers_raw = st.text_input("Universe", value="AAPL, MSFT, GOOG, BTC-USD")
    tickers = [t.strip().upper() for t in tickers_raw.split(",")]
    
    c_d1, c_d2 = st.columns(2)
    with c_d1: start_date = st.date_input("Start", pd.to_datetime("2021-01-01"))
    with c_d2: end_date = st.date_input("End", pd.to_datetime("today"))
    
    st.markdown("---")
    res_btn = st.button("EXECUTE ANALYSIS", use_container_width=True)

# --- HERO HEADER ---
st.markdown(f"""
<div class="hero-section">
    <div style="position: relative; z-index: 1;">
        <p style="color: #00ffcc; font-weight: 800; letter-spacing: 2px; margin-bottom: 10px;">SMART WAY TO MANAGE MONEY</p>
        <h1 style="color: white; font-size: 3.5rem; margin-bottom: 10px;">Effortless Intelligence <br>to Improve Your Returns</h1>
        <p style="color: #bbb; max-width: 600px; font-size: 1.1rem;">
            QuantVision Pro leverages Deep Reinforcement Learning to discover secular market trends 
            and optimize your risk-adjusted capital allocation.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- APP LOGIC ---
@st.cache_data(ttl=3600)
def fetch_data_hub(tickers, start, end):
    loader = DataLoader()
    raw = loader.fetch_data(tickers, str(start), str(end))
    return raw, loader

if res_btn:
    try:
        raw_data, loader = fetch_data_hub(tickers, start_date, end_date)
        
        # --- TAB: ALPHA SIGNALS ---
        if nav_mode == "🎯 Alpha Signals":
            target = st.selectbox("Focus Asset", tickers)
            df_focus = loader.get_ticker_data(raw_data, target)
            
            # RL Engine Hook (Simplified UI)
            engineer = FeatureEngineer()
            df_feat = engineer.add_indicators(df_focus)
            df_scaled = engineer.scale_features(df_feat)
            env = TradingEnv(df_scaled)
            obs, _ = env.reset()
            done = False
            
            # Quick Simulation
            while not done:
                # Mock RL / Sentinel logic
                rsi = df_feat["RSI"].iloc[env.current_step]
                action = 1 if rsi < 35 else (2 if rsi > 65 else 0)
                obs, reward, done, _, _ = env.step(action)
            
            rl_curve = pd.Series(env.equity_curve, index=df_feat.index[:len(env.equity_curve)])
            
            # Finvo-Style Metrics
            col_met1, col_met2, col_met3, col_met4 = st.columns(4)
            met_data = PerformanceMetrics.get_summary(rl_curve)
            
            metrics = [
                ("Total Return", f"{met_data['Total Return (%)']:.1f}%"),
                ("Sharpe Ratio", f"{met_data['Sharpe Ratio']:.2f}"),
                ("Max Drawdown", f"{met_data['Max Drawdown (%)']:.1f}%"),
                ("Daily Vol", f"{met_data['Daily Volatility (%)']:.2f}%")
            ]
            
            for i, (lab, val) in enumerate(metrics):
                with [col_met1, col_met2, col_met3, col_met4][i]:
                    st.markdown(f"""
                    <div class="metric-pod">
                        <p class="metric-lab">{lab}</p>
                        <p class="metric-val">{val}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Visual Analytics
            st.markdown("---")
            c_v1, c_v2 = st.columns([2, 1])
            with c_v1:
                st.subheader("Portfolio Trajectory")
                st.plotly_chart(Visualizer.plot_equity_curves({f"{target} RL": rl_curve, "Benchmark (B&H)": StrategyBaselines.buy_and_hold(df_focus)}), use_container_width=True)
            with c_v2:
                st.subheader("Risk Distribution")
                st.plotly_chart(Visualizer.plot_drawdown(rl_curve), use_container_width=True)

        # --- TAB: PORTFOLIO HUB ---
        elif nav_mode == "📂 Portfolio Hub":
            st.header("Strategic Capital Hub")
            
            returns_map = {t: loader.get_ticker_data(raw_data, t)["Close"].pct_change().dropna() for t in tickers}
            df_returns = pd.DataFrame(returns_map)
            
            c_p1, c_p2 = st.columns([1, 2])
            with c_p1:
                st.markdown("""<div class="metric-pod" style='background:rgba(0,255,204,0.05)'>
                    <h3 style='margin:0'>Divergence Matrix</h3>
                    <p style='color:#888'>Correlation analysis of current holdings.</p>
                </div>""", unsafe_allow_html=True)
                st.plotly_chart(Visualizer.plot_correlation_heatmap(df_returns.corr()), use_container_width=True)
            
            with c_p2:
                st.markdown("<h3 style='color:white'>Optimal Rebalancing Directive</h3>", unsafe_allow_html=True)
                opt_weights = PortfolioOptimizer.calculate_optimal_weights(df_returns)
                w_df = pd.DataFrame(list(opt_weights.items()), columns=["Asset", "Weight"])
                
                # Custom Finvo Style Table
                st.table(w_df.style.format({"Weight": "{:.1%}"}))
                
                performance = PortfolioOptimizer.get_portfolio_performance(df_returns, opt_weights)
                col_pp1, col_pp2 = st.columns(2)
                col_pp1.metric("Ann. Return", f"{performance['Annualized Return (%)']:.1f}%")
                col_pp2.metric("Portfolio Sharpe", f"{performance['Portfolio Sharpe']:.2f}")

        # --- TAB: STRESS TERMINAL ---
        elif nav_mode == "🌪️ Stress Terminal":
            st.header("Financial Resilience Terminal")
            returns_map = {t: loader.get_ticker_data(raw_data, t)["Close"].pct_change().dropna() for t in tickers}
            df_returns = pd.DataFrame(returns_map)
            global_equity = (df_returns + 1).cumprod().mean(axis=1) * 10000
            
            stresses = StressTester.run_stress_test(global_equity)
            
            st.write("Historic Crisis Recovery Performance")
            col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
            s_cols = [col_s1, col_s2, col_s3, col_s4, col_s5]
            
            for i, (event, loss) in enumerate(stresses.items()):
                val = f"{loss:.1f}%" if loss is not None else "N/A"
                with s_cols[i % 5]:
                    st.markdown(f"""
                    <div class="metric-pod" style='padding:15px; border-radius:15px;'>
                        <p style='color:#888; font-size:0.7rem; font-weight:800;'>{event}</p>
                        <p style='color:{"#ff0066" if loss and loss < -20 else "#00ffcc"}; font-size:1.2rem; font-weight:900;'>{val}</p>
                    </div>
                    """, unsafe_allow_html=True)

        st.toast("Intelligence Core Synchronized.", icon="🍀")

    except Exception as e:
        st.error(f"Sync Failure: {str(e)}")
else:
    # Landing View
    st.markdown("""
    <div style="padding: 40px; text-align: left;">
        <h3>Market Intelligence v4.0</h3>
        <p style="color: #888;">Configure your universe and execute to begin synchronization.</p>
    </div>
    """, unsafe_allow_html=True)
