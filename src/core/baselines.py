import pandas as pd
import numpy as np

class StrategyBaselines:
    """Implement classic benchmark strategies."""
    
    @staticmethod
    def buy_and_hold(df: pd.DataFrame, initial_balance: float = 10000.0) -> pd.Series:
        """Passive strategy: Buy at the start and hold until the end."""
        first_price = df.iloc[0]["Close"]
        shares = initial_balance / first_price
        return df["Close"] * shares
        
    @staticmethod
    def sma_crossover(
        df: pd.DataFrame, 
        short_window: int = 20, 
        long_window: int = 50,
        initial_balance: float = 10000.0
    ) -> pd.Series:
        """Classic SMA crossover strategy (Golden Cross)."""
        signals = pd.DataFrame(index=df.index)
        signals["price"] = df["Close"]
        signals["short_mavg"] = df["Close"].rolling(window=short_window, min_periods=1, center=False).mean()
        signals["long_mavg"] = df["Close"].rolling(window=long_window, min_periods=1, center=False).mean()
        
        signals["signal"] = 0.0
        signals["signal"][short_window:] = np.where(
            signals["short_mavg"][short_window:] > signals["long_mavg"][short_window:], 1.0, 0.0
        )
        signals["positions"] = signals["signal"].diff()
        
        # Simulate returns
        balance = initial_balance
        shares = 0
        equity_curve = []
        
        for i in range(len(df)):
            price = df.iloc[i]["Close"]
            if signals["positions"].iloc[i] == 1.0: # Buy signal
                shares = balance / price
                balance = 0
            elif signals["positions"].iloc[i] == -1.0: # Sell signal
                balance = shares * price
                shares = 0
            
            equity_curve.append(balance + (shares * price))
            
        return pd.Series(equity_curve, index=df.index)
