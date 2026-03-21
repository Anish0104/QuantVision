import os
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from src.data.loader import DataLoader
from src.features.indicators import FeatureEngineer
from src.core.trading_env import TradingEnv

def train_agent(ticker: str = "AAPL", total_steps: int = 50000):
    """Train a professional PPO agent for a specific ticker."""
    print(f"🚀 Starting training for {ticker}...")
    
    # 1. Load and prepare data
    loader = DataLoader()
    raw_data = loader.fetch_data([ticker], "2015-01-01", "2023-01-01")
    df = loader.get_ticker_data(raw_data, ticker)
    
    engineer = FeatureEngineer()
    df_features = engineer.add_indicators(df)
    df_scaled = engineer.scale_features(df_features)
    
    # 2. Setup Environment
    env = TradingEnv(df_scaled)
    eval_env = TradingEnv(df_scaled) # For simplicity, using same data for eval smoke test
    
    # 3. Setup Model
    model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1, 
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        device="cpu" # Use "auto" if GPU available
    )
    
    # 4. Evaluation Callback
    if not os.path.exists("models"):
        os.makedirs("models")
        
    eval_callback = EvalCallback(
        eval_env, 
        best_model_save_path="./models/",
        log_path="./logs/", 
        eval_freq=5000,
        deterministic=True, 
        render=False
    )
    
    # 5. Train
    model.learn(total_timesteps=total_steps, callback=eval_callback)
    
    # 6. Save Final Model
    model.save(f"models/ppo_{ticker}")
    print(f"✅ Training complete. Model saved to models/ppo_{ticker}.zip")

if __name__ == "__main__":
    # Smoke train on a small number of steps for verification
    train_agent(ticker="AAPL", total_steps=10000)
