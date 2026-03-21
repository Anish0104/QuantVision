import pandas as pd
import numpy as np
from typing import Dict, List

class StressTester:
    """Historical regime and black-swan event simulation."""
    
    REGIMES = {
        "2008 Financial Crisis": ("2008-01-01", "2009-03-31"),
        "2011 Flash Crash": ("2011-05-01", "2011-10-31"),
        "2015 China Slowdown": ("2015-06-01", "2016-02-29"),
        "2020 COVID Crash": ("2020-02-20", "2020-04-30"),
        "2022 Inflation/Rate Hikes": ("2022-01-01", "2022-12-31")
    }
    
    @staticmethod
    def run_stress_test(full_history: pd.Series) -> Dict[str, float]:
        """Simulate how a strategy WOULD have performed during historic crashes."""
        results = {}
        for event, (start, end) in StressTester.REGIMES.items():
            try:
                # Find corresponding dates in history
                regime_data = full_history.loc[start:end]
                if len(regime_data) > 5:
                    ret = (regime_data.iloc[-1] / regime_data.iloc[0]) - 1
                    results[event] = ret * 100
                else:
                    results[event] = None # Data not available
            except:
                results[event] = None
        return results

    @staticmethod
    def get_max_daily_loss(returns: pd.Series) -> float:
        """Find the single worst day in the series."""
        return returns.min() * 100
