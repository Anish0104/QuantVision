import numpy as np
import pandas as pd

from typing import Dict

class RiskManager:
    """Institutional-grade risk analytics engine."""
    
    @staticmethod
    def calculate_beta(strategy_returns: pd.Series, market_returns: pd.Series) -> float:
        """Calculate Beta against a market benchmark."""
        # Align returns
        combined = pd.concat([strategy_returns, market_returns], axis=1).dropna()
        if len(combined) < 2: return 0.0
        
        covariance = np.cov(combined.iloc[:, 0], combined.iloc[:, 1])[0, 1]
        market_variance = np.var(combined.iloc[:, 1])
        
        return covariance / market_variance if market_variance != 0 else 0.0
        
    @staticmethod
    def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk (VaR) using the parametric method."""
        if len(returns) < 2: return 0.0
        mu = np.mean(returns)
        sigma = np.std(returns)
        
        # Use hardcoded z-score for 95% confidence interval instead of scipy.stats.norm
        # norm.ppf(0.05) is approx -1.64485
        z_score = -1.64485
        return mu + z_score * sigma
        
    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)."""
        if len(returns) < 2: return 0.0
        var = RiskManager.calculate_var(returns, confidence_level)
        tail_losses = returns[returns <= var]
        return np.mean(tail_losses) if len(tail_losses) > 0 else var

    @classmethod
    def get_risk_report(cls, strategy_returns: pd.Series, market_returns: pd.Series = None) -> Dict[str, float]:
        """Generate a comprehensive risk report."""
        report = {
            "Value at Risk (95%)": cls.calculate_var(strategy_returns, 0.95) * 100,
            "CVaR (Expected Shortfall)": cls.calculate_cvar(strategy_returns, 0.95) * 100,
        }
        
        if market_returns is not None:
            report["Beta"] = cls.calculate_beta(strategy_returns, market_returns)
            
        return report
