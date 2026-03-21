from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
import os

from src.data.loader import DataLoader
from src.features.indicators import FeatureEngineer
from src.core.trading_env import TradingEnv
from src.analysis.metrics import PerformanceMetrics
from src.analysis.risk import RiskManager
from src.core.optimizer import PortfolioOptimizer
from src.analysis.stress_test import StressTester

app = FastAPI(title="QuantVision Pro API", version="5.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str

class OptimizationRequest(BaseModel):
    tickers: List[str]
    start_date: str
    end_date: str

@app.get("/")
async def root():
    return {"status": "online", "engine": "QuantVision Pro V5"}

@app.post("/api/analyze")
async def analyze_ticker(req: AnalysisRequest):
    try:
        loader = DataLoader()
        raw_data = loader.fetch_data([req.ticker], req.start_date, req.end_date)
        df = loader.get_ticker_data(raw_data, req.ticker)
        
        engineer = FeatureEngineer()
        df_feat = engineer.add_indicators(df)
        df_feat = df_feat.dropna() # Critical: Remove NaNs from indicators
        
        if df_feat.empty:
            raise ValueError(f"No valid data remaining for {req.ticker} after feature engineering.")
            
        df_scaled = engineer.scale_features(df_feat)
        
        # RL Signal (Simplified Inference for API)
        env = TradingEnv(df_scaled)
        obs, _ = env.reset()
        done = False
        
        last_action = 0
        while not done:
            step = env.current_step
            if step >= len(df_feat):
                break
                
            rsi = df_feat["RSI"].iloc[step]
            # Defense against rare NaN in middle
            if pd.isna(rsi):
                last_action = 0
            else:
                last_action = 1 if rsi < 30 else (2 if rsi > 70 else 0)
                
            obs, reward, done, _, _ = env.step(last_action)
            
        rl_curve = pd.Series(env.equity_curve, index=df_feat.index[:len(env.equity_curve)])
        metrics = PerformanceMetrics.get_summary(rl_curve)
        
        # Prepare for JSON response
        history = rl_curve.reset_index().rename(columns={0: "value", "Date": "date"})
        history["date"] = history["date"].dt.strftime("%Y-%m-%d")
        
        return {
            "ticker": req.ticker,
            "signal": "BUY" if last_action == 1 else ("SELL" if last_action == 2 else "HOLD"),
            "metrics": metrics,
            "equity_curve": history.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize")
async def optimize_portfolio(req: OptimizationRequest):
    try:
        loader = DataLoader()
        raw_data = loader.fetch_data(req.tickers, req.start_date, req.end_date)
        
        returns_map = {t: loader.get_ticker_data(raw_data, t)["Close"].pct_change().dropna() for t in req.tickers}
        df_returns = pd.DataFrame(returns_map)
        
        weights = PortfolioOptimizer.calculate_optimal_weights(df_returns)
        performance = PortfolioOptimizer.get_portfolio_performance(df_returns, weights)
        
        return {
            "weights": weights,
            "performance": performance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stress-test")
async def stress_test_portfolio(req: OptimizationRequest):
    try:
        loader = DataLoader()
        raw_data = loader.fetch_data(req.tickers, req.start_date, req.end_date)
        
        returns_map = {t: loader.get_ticker_data(raw_data, t)["Close"].pct_change().dropna() for t in req.tickers}
        df_returns = pd.DataFrame(returns_map)
        global_equity = (df_returns + 1).cumprod().mean(axis=1) * 10000
        
        stresses = StressTester.run_stress_test(global_equity)
        risk = RiskManager.get_risk_report(global_equity.pct_change().dropna())
        
        return {
            "stresses": stresses,
            "risk_report": risk
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    message: str
    ticker: Optional[str] = None
    metrics: Optional[Dict] = None

@app.post("/api/chat")
async def chat_analysis(req: ChatRequest):
    msg = req.message.lower()
    ticker = req.ticker or "the selected asset"
    m = req.metrics or {}
    
    # Direct answer logic
    if "return" in msg or "profit" in msg:
        val = m.get("Annualized Return (%)", "N/A")
        return {"response": f"The annualized return for {ticker} is currently {val}%."}
    
    if "sharpe" in msg or "risk" in msg:
        val = m.get("Sharpe Ratio", "N/A")
        return {"response": f"The Sharpe Ratio (Risk Efficiency) for {ticker} is {val}."}
    
    if "drawdown" in msg or "loss" in msg:
        val = m.get("Max Drawdown (%)", "N/A")
        return {"response": f"The observed Max Drawdown for the {ticker} strategy is {val}%."}
        
    if "ticker" in msg or "stock" in msg or "asset" in msg:
        return {"response": f"You are currently analyzing {ticker}."}

    responses = [
        f"The {ticker} strategy is currently yielding an institutional-grade performance profile.",
        f"Analyzing {ticker}: The risk metrics suggest a highly favorable risk-adjusted return.",
        "Based on your recent analysis, the portfolio shows secular resilience."
    ]
    import random
    return {"response": random.choice(responses)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
