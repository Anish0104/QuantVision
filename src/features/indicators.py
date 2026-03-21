import pandas as pd
import numpy as np

class FeatureEngineer:
    """Robust technical indicator engine using native pandas/numpy."""
    
    def __init__(self):
        pass
        
    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Indicators manually to avoid external requirements."""
        df = df.copy()
        
        # 1. RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 2. MACD (Moving Average Convergence Divergence)
        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # 3. Bollinger Bands
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        std_20 = df['Close'].rolling(window=20).std()
        df['BBU_20_2.0'] = df['SMA_20'] + (std_20 * 2)
        df['BBL_20_2.0'] = df['SMA_20'] - (std_20 * 2)
        
        # 4. Moving Averages
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        # 5. OBV (On-Balance Volume)
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        
        # 6. ATR (Average True Range) - Volatility measure
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR_14'] = true_range.rolling(14).mean()
        
        df.dropna(inplace=True)
        return df

    def scale_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize features to [0, 1] or Z-score for RL stability."""
        # Simple Min-Max scaling for this demonstration
        # In production, use StandardScaler from sklearn
        df_scaled = df.copy()
        for col in df_scaled.columns:
            if col not in ["Open", "High", "Low", "Close", "Volume"]:
                col_min = df_scaled[col].min()
                col_max = df_scaled[col].max()
                if col_max > col_min:
                    df_scaled[col] = (df_scaled[col] - col_min) / (col_max - col_min)
        return df_scaled
