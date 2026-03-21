import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class Visualizer:
    """Professional interactive charts for trading strategy analysis."""
    
    @staticmethod
    def plot_equity_curves(curves_dict: dict, title: str = "Strategy Comparison"):
        """Plot multiple equity curves on the same interactive chart."""
        fig = go.Figure()
        
        for name, curve in curves_dict.items():
            fig.add_trace(go.Scatter(
                x=curve.index, 
                y=curve.values, 
                mode='lines', 
                name=name,
                hovertemplate='%{y:.2f}'
            ))
            
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            template="plotly_dark",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        return fig
        
    @staticmethod
    def plot_drawdown(equity_curve: pd.Series):
        """Plot the drawdown ('underwater') chart."""
        rolling_max = equity_curve.cummax()
        drawdown = (equity_curve - rolling_max) / rolling_max * 100
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=drawdown.index, 
            y=drawdown.values, 
            fill='tozeroy', 
            line=dict(color='red'),
            name="Drawdown (%)"
        ))
        
        fig.update_layout(
            title="Max Drawdown (Underwater Chart)",
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            template="plotly_dark"
        )
        return fig
    @staticmethod
    def plot_correlation_heatmap(corr_df: pd.DataFrame):
        """Plot a beautiful correlation heatmap for portfolio assets."""
        fig = px.imshow(
            corr_df, 
            text_auto=".2f", 
            aspect="auto", 
            color_continuous_scale='RdBu_r', 
            zmin=-1, zmax=1
        )
        fig.update_layout(
            title="Portfolio Correlation Matrix",
            template="plotly_dark",
            xaxis_title="Assets",
            yaxis_title="Assets"
        )
        return fig
