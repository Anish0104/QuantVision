import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

class TradingEnv(gym.Env):
    """Professional Trading Environment for Reinforcement Learning."""
    metadata = {"render_modes": ["human"]}

    def __init__(
        self, 
        df: pd.DataFrame, 
        initial_balance: float = 10000.0,
        commission: float = 0.001,  # 0.1% transaction fee
        slippage: float = 0.0005,   # 0.05% slippage on entry/exit
    ):
        super(TradingEnv, self).__init__()
        
        self.df = df.reset_index(drop=True)
        self.initial_balance = initial_balance
        self.commission = commission
        self.slippage = slippage
        
        # Action space: 0 = Hold, 1 = Buy (100% Cash -> Asset), 2 = Sell (100% Asset -> Cash)
        # Note: In a real portfolio project, Continuous actions (allocation %) are better.
        # But let's stay with discrete for now to be compatible with SB3 PPO.
        self.action_space = spaces.Discrete(3)
        
        # Observation space: 
        # Indicators from df + [current_balance, current_shares, entry_price]
        self.n_features = len(df.columns)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.n_features + 3,), dtype=np.float32
        )

    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None):
        super().reset(seed=seed)
        
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares = 0
        self.entry_price = 0.0
        self.equity_curve = [self.initial_balance]
        
        return self._get_obs(), {}

    def _get_obs(self):
        obs = self.df.iloc[self.current_step].values
        # Add internal state to observation
        state = np.array([self.balance, self.shares, self.entry_price], dtype=np.float32)
        return np.concatenate([obs, state]).astype(np.float32)

    def step(self, action):
        current_price = self.df.iloc[self.current_step]["Close"]
        
        # Trading Logic (Discrete Actions)
        # 0 = Hold, 1 = Buy (Full Allocation), 2 = Sell (Exit Position)
        if action == 1: # Buy / Long
            if self.balance > 0:
                # Account for commission and slippage (Market Buy)
                adj_price = current_price * (1 + self.slippage)
                self.shares = (self.balance * (1 - self.commission)) / adj_price
                self.balance = 0
                self.entry_price = adj_price
                
        elif action == 2: # Sell / Close
            if self.shares > 0:
                # Account for commission and slippage (Market Sell)
                adj_price = current_price * (1 - self.slippage)
                self.balance = (self.shares * adj_price) * (1 - self.commission)
                self.shares = 0
                self.entry_price = 0.0
        
        # Net Worth Calculation
        current_net_worth = self.balance + (self.shares * current_price)
        prev_net_worth = self.equity_curve[-1]
        
        # Move to next step
        self.current_step += 1
        terminated = self.current_step >= len(self.df) - 1
        truncated = False
        
        # Reward: Percentage change in net worth
        # We add a small penalty for each step to encourage faster gains/avoid idle
        # Or even better: Step return - commission cost
        step_return = (current_net_worth / prev_net_worth) - 1
        reward = step_return
        
        # Advanced: Penalty for large drawdowns during the episode
        rolling_max = max(self.equity_curve)
        current_drawdown = (current_net_worth - rolling_max) / rolling_max
        if current_drawdown < -0.10: # Only penalize if drawdown > 10%
             reward += current_drawdown * 0.1 
        
        self.equity_curve.append(current_net_worth)
        
        return self._get_obs(), reward, terminated, truncated, {"net_worth": current_net_worth}

    def render(self):
        print(f"Step: {self.current_step}, Net Worth: {self.equity_curve[-1]:.2f}")
