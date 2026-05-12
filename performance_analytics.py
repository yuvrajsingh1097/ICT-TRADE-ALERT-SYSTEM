"""
Advanced Performance Analytics Module
Trade statistics, equity curve analysis, comparative metrics
Works with backtester output for deeper analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TradeMetrics:
    """Individual trade metrics"""
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    position_size: float
    signal_type: str
    pnl: float
    pnl_percent: float
    
    def to_dict(self) -> Dict:
        return {
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat(),
            "entry_price": round(self.entry_price, 4),
            "exit_price": round(self.exit_price, 4),
            "size": self.position_size,
            "signal": self.signal_type,
            "pnl": round(self.pnl, 2),
            "pnl_pct": round(self.pnl_percent, 2)
        }


class EquityCurveAnalyzer:
    """Analyze equity curve and performance"""
    
    def __init__(self, initial_balance: float):
        self.initial_balance = initial_balance
        self.equity_history = [initial_balance]
        self.daily_returns = []
    
    def add_equity_point(self, equity: float):
        """Add equity point to history"""
        self.equity_history.append(equity)
        
        if len(self.equity_history) > 1:
            prev_equity = self.equity_history[-2]
            daily_return = (equity - prev_equity) / prev_equity
            self.daily_returns.append(daily_return)
    
    def calculate_statistics(self) -> Dict:
        """Calculate comprehensive equity curve statistics"""
        
        equity = np.array(self.equity_history)
        returns = np.array(self.daily_returns)
        
        # Basic metrics
        final_equity = equity[-1]
        total_return = (final_equity - self.initial_balance) / self.initial_balance
        
        # Drawdown analysis
        cumulative_max = np.maximum.accumulate(equity)
        drawdown = (equity - cumulative_max) / cumulative_max
        max_drawdown = np.min(drawdown)
        
        # Return statistics
        mean_return = np.mean(returns) if returns.size > 0 else 0
        std_return = np.std(returns) if returns.size > 0 else 0
        
        # Sharpe ratio (assuming 252 trading days)
        sharpe_ratio = (mean_return * 252) / std_return if std_return > 0 else 0
        
        # Sortino ratio (downside deviation only)
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) if downside_returns.size > 0 else 0
        sortino_ratio = (mean_return * 252) / downside_std if downside_std > 0 else 0
        
        # Calmar ratio
        total_days = len(equity) / 252  # Approximate years
        calmar = total_return / abs(max_drawdown) if max_drawdown != 0 and total_days > 0 else 0
        
        # Recovery factor
        total_wins = np.sum(returns[returns > 0])
        recovery_factor = total_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            "initial_capital": round(self.initial_balance, 2),
            "final_equity": round(final_equity, 2),
            "total_return_pct": round(total_return * 100, 2),
            "total_return_amount": round(final_equity - self.initial_balance, 2),
            "max_drawdown_pct": round(max_drawdown * 100, 2),
            "avg_daily_return_pct": round(mean_return * 100, 4),
            "daily_volatility_pct": round(std_return * 100, 4),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "sortino_ratio": round(sortino_ratio, 2),
            "calmar_ratio": round(calmar, 2),
            "recovery_factor": round(recovery_factor, 2),
            "profit_factor": round(total_wins / abs(np.sum(returns[returns < 0])), 2) if np.sum(returns[returns < 0]) != 0 else 0
        }


class TradeAnalyzer:
    """Analyze individual trades and trade sequences"""
    
    def __init__(self):
        self.trades: List[TradeMetrics] = []
    
    def add_trade(self, trade: TradeMetrics):
        """Add trade to analysis"""
        self.trades.append(trade)
    
    def calculate_win_rate(self) -> Tuple[float, int, int]:
        """Calculate win rate and winning/losing trades"""
        if not self.trades:
            return 0.0, 0, 0
        
        winners = sum(1 for t in self.trades if t.pnl > 0)
        losers = sum(1 for t in self.trades if t.pnl < 0)
        
        win_rate = winners / len(self.trades) if self.trades else 0
        return round(win_rate * 100, 2), winners, losers
    
    def calculate_average_trade(self) -> Dict:
        """Calculate average trade statistics"""
        if not self.trades:
            return {}
        
        pnls = [t.pnl for t in self.trades]
        pnl_pcts = [t.pnl_percent for t in self.trades]
        
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        
        return {
            "avg_pnl": round(np.mean(pnls), 2),
            "avg_pnl_pct": round(np.mean(pnl_pcts), 2),
            "avg_winner": round(np.mean([t.pnl for t in winning_trades]), 2) if winning_trades else 0,
            "avg_loser": round(np.mean([t.pnl for t in losing_trades]), 2) if losing_trades else 0,
            "largest_win": round(max(pnls), 2) if pnls else 0,
            "largest_loss": round(min(pnls), 2) if pnls else 0,
            "profit_factor": self._calculate_profit_factor()
        }
    
    def _calculate_profit_factor(self) -> float:
        """Profit factor = Gross Profit / Gross Loss"""
        if not self.trades:
            return 0.0
        
        gross_profit = sum(t.pnl for t in self.trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in self.trades if t.pnl < 0))
        
        if gross_loss == 0:
            return 0.0
        
        return round(gross_profit / gross_loss, 2)
    
    def analyze_trade_sequences(self) -> Dict:
        """Analyze consecutive wins/losses"""
        if not self.trades:
            return {}
        
        # Find winning and losing streaks
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in self.trades:
            if trade.pnl > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
        
        return {
            "longest_win_streak": max_wins,
            "longest_loss_streak": max_losses,
            "total_trades": len(self.trades)
        }
    
    def analyze_by_signal_type(self) -> Dict:
        """Performance breakdown by signal type"""
        signals = {}
        
        for trade in self.trades:
            signal = trade.signal_type
            if signal not in signals:
                signals[signal] = {
                    "count": 0,
                    "wins": 0,
                    "total_pnl": 0,
                    "trades": []
                }
            
            signals[signal]["count"] += 1
            if trade.pnl > 0:
                signals[signal]["wins"] += 1
            signals[signal]["total_pnl"] += trade.pnl
            signals[signal]["trades"].append(trade)
        
        # Calculate statistics per signal
        results = {}
        for signal, data in signals.items():
            win_rate = (data["wins"] / data["count"] * 100) if data["count"] > 0 else 0
            avg_pnl = data["total_pnl"] / data["count"] if data["count"] > 0 else 0
            
            results[signal] = {
                "count": data["count"],
                "wins": data["wins"],
                "win_rate_pct": round(win_rate, 2),
                "total_pnl": round(data["total_pnl"], 2),
                "avg_pnl": round(avg_pnl, 2)
            }
        
        return results


class PerformanceComparator:
    """Compare performance across different time periods or strategies"""
    
    @staticmethod
    def compare_periods(trades1: List[TradeMetrics], 
                       trades2: List[TradeMetrics]) -> Dict:
        """Compare performance between two periods"""
        
        analyzer1 = TradeAnalyzer()
        analyzer2 = TradeAnalyzer()
        
        for t in trades1:
            analyzer1.add_trade(t)
        for t in trades2:
            analyzer2.add_trade(t)
        
        wr1, w1, l1 = analyzer1.calculate_win_rate()
        wr2, w2, l2 = analyzer2.calculate_win_rate()
        
        avg1 = analyzer1.calculate_average_trade()
        avg2 = analyzer2.calculate_average_trade()
        
        return {
            "period1": {
                "trades": len(trades1),
                "win_rate": wr1,
                "avg_pnl": avg1.get("avg_pnl", 0),
                "profit_factor": avg1.get("profit_factor", 0)
            },
            "period2": {
                "trades": len(trades2),
                "win_rate": wr2,
                "avg_pnl": avg2.get("avg_pnl", 0),
                "profit_factor": avg2.get("profit_factor", 0)
            },
            "comparison": {
                "win_rate_diff": round(wr2 - wr1, 2),
                "avg_pnl_diff": round(avg2.get("avg_pnl", 0) - avg1.get("avg_pnl", 0), 2),
                "better_period": "Period 2" if wr2 > wr1 else "Period 1"
            }
        }


class PerformanceReport:
    """Generate comprehensive performance report"""
    
    def __init__(self, analyzer: TradeAnalyzer, equity_analyzer: EquityCurveAnalyzer):
        self.trade_analyzer = analyzer
        self.equity_analyzer = equity_analyzer
    
    def generate_report(self) -> str:
        """Generate complete performance report"""
        
        report = "\n" + "="*70 + "\n"
        report += "PERFORMANCE ANALYSIS REPORT\n"
        report += "="*70 + "\n\n"
        
        # Equity metrics
        equity_stats = self.equity_analyzer.calculate_statistics()
        report += "EQUITY & RETURNS:\n"
        report += "-" * 70 + "\n"
        report += f"Initial Capital:        ${equity_stats['initial_capital']:>12,.2f}\n"
        report += f"Final Equity:           ${equity_stats['final_equity']:>12,.2f}\n"
        report += f"Total Return:           {equity_stats['total_return_pct']:>12.2f}%\n"
        report += f"Total Return ($):       ${equity_stats['total_return_amount']:>12,.2f}\n"
        report += "\n"
        
        # Risk metrics
        report += "RISK METRICS:\n"
        report += "-" * 70 + "\n"
        report += f"Max Drawdown:           {equity_stats['max_drawdown_pct']:>12.2f}%\n"
        report += f"Daily Volatility:       {equity_stats['daily_volatility_pct']:>12.4f}%\n"
        report += f"Sharpe Ratio:           {equity_stats['sharpe_ratio']:>12.2f}\n"
        report += f"Sortino Ratio:          {equity_stats['sortino_ratio']:>12.2f}\n"
        report += f"Calmar Ratio:           {equity_stats['calmar_ratio']:>12.2f}\n"
        report += f"Recovery Factor:        {equity_stats['recovery_factor']:>12.2f}\n"
        report += "\n"
        
        # Trade statistics
        wr, wins, losses = self.trade_analyzer.calculate_win_rate()
        avg_trade = self.trade_analyzer.calculate_average_trade()
        sequences = self.trade_analyzer.analyze_trade_sequences()
        
        report += "TRADE STATISTICS:\n"
        report += "-" * 70 + "\n"
        report += f"Total Trades:           {sequences['total_trades']:>12}\n"
        report += f"Winning Trades:         {wins:>12}\n"
        report += f"Losing Trades:          {losses:>12}\n"
        report += f"Win Rate:               {wr:>12.2f}%\n"
        report += f"Avg Trade P&L:          ${avg_trade.get('avg_pnl', 0):>12,.2f}\n"
        report += f"Avg Trade %:            {avg_trade.get('avg_pnl_pct', 0):>12.2f}%\n"
        report += f"Avg Winner:             ${avg_trade.get('avg_winner', 0):>12,.2f}\n"
        report += f"Avg Loser:              ${avg_trade.get('avg_loser', 0):>12,.2f}\n"
        report += f"Largest Win:            ${avg_trade.get('largest_win', 0):>12,.2f}\n"
        report += f"Largest Loss:           ${avg_trade.get('largest_loss', 0):>12,.2f}\n"
        report += f"Profit Factor:          {avg_trade.get('profit_factor', 0):>12.2f}\n"
        report += "\n"
        
        # Streaks
        report += "STREAKS:\n"
        report += "-" * 70 + "\n"
        report += f"Longest Win Streak:     {sequences['longest_win_streak']:>12}\n"
        report += f"Longest Loss Streak:    {sequences['longest_loss_streak']:>12}\n"
        report += "\n"
        
        # By signal type
        by_signal = self.trade_analyzer.analyze_by_signal_type()
        if by_signal:
            report += "PERFORMANCE BY SIGNAL TYPE:\n"
            report += "-" * 70 + "\n"
            for signal, stats in by_signal.items():
                report += f"{signal:.<40} WR: {stats['win_rate_pct']:>6.2f}% | "
                report += f"Trades: {stats['count']:>4} | PnL: ${stats['total_pnl']:>10,.2f}\n"
        
        report += "\n" + "="*70 + "\n"
        return report
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """Export trades to DataFrame"""
        trades_data = [t.to_dict() for t in self.trade_analyzer.trades]
        return pd.DataFrame(trades_data)


# Example usage
if __name__ == "__main__":
    # Create sample trade
    equity_analyzer = EquityCurveAnalyzer(100000)
    trade_analyzer = TradeAnalyzer()
    
    # Add sample equity points
    for i in range(100):
        equity_analyzer.add_equity_point(100000 + i * 100)
    
    # Add sample trade
    trade = TradeMetrics(
        entry_time=datetime.now(),
        exit_time=datetime.now(),
        entry_price=1.0950,
        exit_price=1.0980,
        position_size=10000,
        signal_type="FVG",
        pnl=300,
        pnl_percent=0.3
    )
    trade_analyzer.add_trade(trade)
    
    # Generate report
    report = PerformanceReport(trade_analyzer, equity_analyzer)
    print(report.generate_report())
