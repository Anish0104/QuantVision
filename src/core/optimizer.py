import numpy as np
import pandas as pd
from typing import List, Dict

class PortfolioOptimizer:
    """Modern Portfolio Theory (MPT) engine for asset allocation."""
    
    @staticmethod
    def calculate_optimal_weights(returns_df: pd.DataFrame) -> Dict[str, float]:
        """Find weights that maximize the Sharpe Ratio (Tangency Portfolio)."""
        if returns_df.empty: return {}
        
        num_assets = len(returns_df.columns)
        mean_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        # Monte Carlo Simulation for simplicity (in a real startup, use scipy.optimize)
        num_portfolios = 5000
        results = np.zeros((3, num_portfolios))
        weights_record = []
        
        for i in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            weights_record.append(weights)
            
            p_ret = np.sum(mean_returns * weights)
            p_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            results[0, i] = p_ret
            results[1, i] = p_std
            results[2, i] = p_ret / p_std # Sharpe Ratio (assumed risk-free = 0)
            
        max_sharpe_idx = np.argmax(results[2])
        best_weights = weights_record[max_sharpe_idx]
        
        return dict(zip(returns_df.columns, best_weights))

    @staticmethod
    def get_portfolio_performance(returns_df: pd.DataFrame, weights: Dict[str, float]) -> Dict[str, float]:
        """Calculate annualized performance of a weighted portfolio."""
        w = np.array([weights[col] for col in returns_df.columns])
        p_returns = returns_df.dot(w)
        
        total_return = (1 + p_returns).prod() - 1
        ann_return = p_returns.mean() * 252
        ann_vol = p_returns.std() * np.sqrt(252)
        
        return {
            "Total Portfolio Return (%)": total_return * 100,
            "Annualized Return (%)": ann_return * 100,
            "Annualized Volatility (%)": ann_vol * 100,
            "Portfolio Sharpe": ann_return / ann_vol if ann_vol != 0 else 0
        }
