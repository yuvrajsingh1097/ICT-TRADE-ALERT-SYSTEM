"""
Multi-Timeframe Analysis Module
Detects confluence signals across multiple timeframes
Enhances signal quality without altering core logic
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class MultiTimeframeAnalyzer:
    """Analyze market structure across multiple timeframes"""
    
    def __init__(self):
        self.timeframes = ["1H", "4H", "Daily"]
        self.confluence_levels = {}
        self.mtf_signals = []
    
    def detect_market_structure(self, df: pd.DataFrame, 
                               lookback: int = 20) -> Dict[str, str]:
        """
        Identify HH/HL/LH/LL across timeframe
        Returns: market_structure dictionary
        """
        if len(df) < lookback:
            return {"status": "insufficient_data"}
        
        df_recent = df.tail(lookback).reset_index(drop=True)
        
        # Get recent highs/lows
        recent_high = df_recent['high'].max()
        recent_low = df_recent['low'].min()
        
        # Get previous highs/lows (before recent period)
        prev_high = df.iloc[:-lookback]['high'].tail(lookback).max() if len(df) > lookback else recent_high
        prev_low = df.iloc[:-lookback]['low'].tail(lookback).min() if len(df) > lookback else recent_low
        
        # Classify structure
        if recent_high > prev_high and recent_low > prev_low:
            structure = "HH/HL (Uptrend)"
            direction = 1
        elif recent_high < prev_high and recent_low < prev_low:
            structure = "LH/LL (Downtrend)"
            direction = -1
        elif recent_high > prev_high and recent_low < prev_low:
            structure = "Ranging (Consolidation)"
            direction = 0
        else:
            structure = "Mixed"
            direction = 0
        
        return {
            "structure": structure,
            "direction": direction,
            "recent_high": recent_high,
            "recent_low": recent_low,
            "prev_high": prev_high,
            "prev_low": prev_low
        }
    
    def find_confluence_levels(self, dfs: Dict[str, pd.DataFrame]) -> Dict:
        """
        Find price levels that align across multiple timeframes
        dfs: {"1H": df1, "4H": df4, "Daily": df_daily}
        Returns: levels where 2+ timeframes agree
        """
        confluence_highs = {}
        confluence_lows = {}
        
        for tf, df in dfs.items():
            struct = self.detect_market_structure(df)
            
            if struct["direction"] != 0:  # Skip ranging
                high = struct["recent_high"]
                low = struct["recent_low"]
                
                # Round to nearest 0.05 (creates confluence zones)
                high_rounded = round(high / 0.05) * 0.05
                low_rounded = round(low / 0.05) * 0.05
                
                confluence_highs[high_rounded] = confluence_highs.get(high_rounded, 0) + 1
                confluence_lows[low_rounded] = confluence_lows.get(low_rounded, 0) + 1
        
        # Filter confluences with 2+ timeframes
        strong_highs = {k: v for k, v in confluence_highs.items() if v >= 2}
        strong_lows = {k: v for k, v in confluence_lows.items() if v >= 2}
        
        return {
            "confluence_highs": strong_highs,
            "confluence_lows": strong_lows,
            "total_confluences": len(strong_highs) + len(strong_lows)
        }
    
    def detect_mtf_divergence(self, dfs: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        SMT Divergence: Asset structures don't align
        Bearish: Higher TF up, Lower TF down
        Bullish: Higher TF down, Lower TF up
        """
        divergences = []
        
        tf_list = list(dfs.keys())
        
        for i in range(len(tf_list) - 1):
            higher_tf = tf_list[i]
            lower_tf = tf_list[i + 1]
            
            higher_struct = self.detect_market_structure(dfs[higher_tf])
            lower_struct = self.detect_market_structure(dfs[lower_tf])
            
            higher_dir = higher_struct["direction"]
            lower_dir = lower_struct["direction"]
            
            # Divergence detection
            if higher_dir != 0 and lower_dir != 0 and higher_dir != lower_dir:
                if higher_dir == 1 and lower_dir == -1:
                    div_type = "Bearish (HTF up, LTF down)"
                    confidence = 0.8
                elif higher_dir == -1 and lower_dir == 1:
                    div_type = "Bullish (HTF down, LTF up)"
                    confidence = 0.8
                else:
                    div_type = "Mixed"
                    confidence = 0.5
                
                divergences.append({
                    "type": div_type,
                    "higher_tf": higher_tf,
                    "lower_tf": lower_tf,
                    "confidence": confidence,
                    "higher_structure": higher_struct["structure"],
                    "lower_structure": lower_struct["structure"]
                })
        
        return divergences
    
    def get_mtf_bias(self, dfs: Dict[str, pd.DataFrame]) -> str:
        """Get overall market bias from higher timeframes"""
        
        if "Daily" in dfs:
            daily_struct = self.detect_market_structure(dfs["Daily"])
            direction = daily_struct["direction"]
            
            if direction == 1:
                return "BULLISH"
            elif direction == -1:
                return "BEARISH"
            else:
                return "NEUTRAL"
        
        return "UNKNOWN"
    
    def calculate_confluence_score(self, price: float, 
                                   dfs: Dict[str, pd.DataFrame]) -> float:
        """
        Score price level based on confluence strength
        Higher score = stronger level
        Returns: 0-100 score
        """
        confluence = self.find_confluence_levels(dfs)
        
        all_levels = list(confluence["confluence_highs"].keys()) + \
                     list(confluence["confluence_lows"].keys())
        
        if not all_levels:
            return 0.0
        
        # Find closest level
        distances = [abs(price - level) for level in all_levels]
        min_distance = min(distances)
        closest_level = all_levels[distances.index(min_distance)]
        
        # Score based on proximity (within 0.1 of level = max score)
        if min_distance < 0.1:
            base_score = 100.0
        else:
            base_score = max(0, 100 - (min_distance / 0.1) * 50)
        
        # Boost score by timeframe agreement
        if closest_level in confluence["confluence_highs"]:
            boost = confluence["confluence_highs"][closest_level] * 15
        elif closest_level in confluence["confluence_lows"]:
            boost = confluence["confluence_lows"][closest_level] * 15
        else:
            boost = 0
        
        final_score = min(100, base_score + boost)
        return round(final_score, 2)
    
    def generate_mtf_report(self, dfs: Dict[str, pd.DataFrame]) -> str:
        """Generate comprehensive MTF analysis report"""
        
        report = "\n" + "="*60 + "\n"
        report += "MULTI-TIMEFRAME ANALYSIS REPORT\n"
        report += "="*60 + "\n\n"
        
        # Bias
        bias = self.get_mtf_bias(dfs)
        report += f"Overall Bias: {bias}\n\n"
        
        # Structure per timeframe
        report += "MARKET STRUCTURE PER TIMEFRAME:\n"
        report += "-" * 60 + "\n"
        for tf, df in dfs.items():
            struct = self.detect_market_structure(df)
            report += f"{tf:>8}: {struct['structure']}\n"
        
        report += "\n"
        
        # Confluence levels
        confluence = self.find_confluence_levels(dfs)
        report += f"CONFLUENCE LEVELS ({confluence['total_confluences']} total):\n"
        report += "-" * 60 + "\n"
        if confluence["confluence_highs"]:
            report += "Resistance Zones:\n"
            for level, count in sorted(confluence["confluence_highs"].items(), reverse=True):
                report += f"  {level:.4f} ({count} TF agreement)\n"
        if confluence["confluence_lows"]:
            report += "Support Zones:\n"
            for level, count in sorted(confluence["confluence_lows"].items(), reverse=True):
                report += f"  {level:.4f} ({count} TF agreement)\n"
        
        report += "\n"
        
        # Divergences
        divs = self.detect_mtf_divergence(dfs)
        if divs:
            report += f"SMT DIVERGENCES ({len(divs)} detected):\n"
            report += "-" * 60 + "\n"
            for div in divs:
                report += f"{div['type']}: {div['higher_tf']} vs {div['lower_tf']}\n"
                report += f"  Confidence: {div['confidence']*100:.0f}%\n"
        else:
            report += "No MTF divergences detected\n"
        
        report += "\n" + "="*60 + "\n"
        return report


# Example usage
if __name__ == "__main__":
    # Simulated DFs (replace with real data)
    df_1h = pd.DataFrame({
        'high': np.random.uniform(100, 110, 100),
        'low': np.random.uniform(90, 100, 100)
    })
    
    df_4h = pd.DataFrame({
        'high': np.random.uniform(100, 110, 25),
        'low': np.random.uniform(90, 100, 25)
    })
    
    df_daily = pd.DataFrame({
        'high': np.random.uniform(100, 110, 5),
        'low': np.random.uniform(90, 100, 5)
    })
    
    analyzer = MultiTimeframeAnalyzer()
    dfs = {"1H": df_1h, "4H": df_4h, "Daily": df_daily}
    
    print(analyzer.generate_mtf_report(dfs))
