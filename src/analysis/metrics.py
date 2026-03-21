import numpy as np
import pandas as pd
from typing import Dict

class PerformanceMetrics:
    """Institutional-grade backtest metric calculator."""
    
    @staticmethod
    def calculate_sharpe(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate annualized Sharpe Ratio."""
        if len(returns) < 2: return 0.0
        excess_returns = returns - (risk_free_rate / 252)
        return (np.mean(excess_returns) / np.std(excess_returns)) * np.sqrt(252)
        
    @staticmethod
    def calculate_sortino(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate annualized Sortino Ratio (downside risk)."""
        if len(returns) < 2: return 0.0
        excess_returns = returns - (risk_free_rate / 252)
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) == 0: return np.inf
        return (np.mean(excess_returns) / np.std(downside_returns)) * np.sqrt(252)
        
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """Calculate Maximum Drawdown percentage."""
        if len(equity_curve) < 2: return 0.0
        rolling_max = equity_curve.cummax()
        drawdown = (equity_curve - rolling_max) / rolling_max
        return drawdown.min()
        
    @classmethod
    def get_summary(cls, equity_curve: pd.Series) -> Dict[str, float]:
        """Summarize strategy performance with annualized metrics."""
        if len(equity_curve) < 2:
            return {
                "Total Return (%)": 0.0,
                "Annualized Return (%)": 0.0,
                "Sharpe Ratio": 0.0,
                "Sortino Ratio": 0.0,
                "Max Drawdown (%)": 0.0,
                "Daily Volatility (%)": 0.0,
            }
            
        returns = equity_curve.pct_change().dropna()
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        
        # Annualization factor (assuming daily data)
        days = len(equity_curve)
        annualized_return = ((1 + total_return) ** (252 / days) - 1) if days > 0 else total_return
        
        return {
            "Total Return (%)": total_return * 100,
            "Annualized Return (%)": annualized_return * 100,
            "Sharpe Ratio": cls.calculate_sharpe(returns),
            "Sortino Ratio": cls.calculate_sortino(returns),
            "Max Drawdown (%)": cls.calculate_max_drawdown(equity_curve) * 100,
            "Daily Volatility (%)": returns.std() * 100,
        }
