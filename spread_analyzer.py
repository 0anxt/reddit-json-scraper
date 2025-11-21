"""
Spread Analyzer - Calculate and filter vertical spreads
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import config
from market_data import MarketDataFetcher


class SpreadAnalyzer:
    """Analyze and filter vertical spreads based on constraints"""
    
    def __init__(self, market_data: MarketDataFetcher):
        self.market_data = market_data
    
    def calculate_vertical_spreads(self, ticker: str, underlying_data: Dict, 
                                   options_chain: Dict, spread_type: str = 'bull_call') -> List[Dict]:
        """
        Calculate all possible vertical spreads for a given options chain
        
        Args:
            ticker: Ticker symbol
            underlying_data: Dict with price, atr, rsi, iv_rank
            options_chain: Dict with expiration, dte, calls, puts
            spread_type: 'bull_call', 'bull_put', 'bear_call', 'bear_put'
        
        Returns:
            List of spread dicts with all calculated metrics
        """
        spreads = []
        current_price = underlying_data['price']
        dte = options_chain['dte']
        
        # Select calls or puts based on spread type
        if spread_type in ['bull_call', 'bear_call']:
            options = options_chain['calls']
            option_type = 'call'
        else:
            options = options_chain['puts']
            option_type = 'put'
        
        # Filter for liquid options
        liquid_options = self.market_data.filter_liquid_options(options, current_price)
        
        if len(liquid_options) < 2:
            return []
        
        # Sort by strike
        liquid_options = liquid_options.sort_values('strike').reset_index(drop=True)
        
        # Generate all possible spreads
        for i in range(len(liquid_options)):
            for j in range(i + 1, len(liquid_options)):
                long_option = liquid_options.iloc[i]
                short_option = liquid_options.iloc[j]
                
                # For bull spreads: buy lower strike, sell higher strike
                # For bear spreads: sell lower strike, buy higher strike
                if spread_type in ['bull_call', 'bull_put']:
                    buy_strike = long_option['strike']
                    sell_strike = short_option['strike']
                    buy_price = long_option['ask']  # Pay ask when buying
                    sell_price = short_option['bid']  # Receive bid when selling
                else:  # bear spreads
                    buy_strike = short_option['strike']
                    sell_strike = long_option['strike']
                    buy_price = short_option['ask']
                    sell_price = long_option['bid']
                
                # Calculate spread metrics
                spread = self._calculate_spread_metrics(
                    ticker=ticker,
                    spread_type=spread_type,
                    buy_strike=buy_strike,
                    sell_strike=sell_strike,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    current_price=current_price,
                    dte=dte,
                    underlying_data=underlying_data,
                    option_type=option_type,
                )
                
                if spread:
                    spreads.append(spread)
        
        return spreads
    
    def _calculate_spread_metrics(self, ticker: str, spread_type: str, buy_strike: float,
                                  sell_strike: float, buy_price: float, sell_price: float,
                                  current_price: float, dte: int, underlying_data: Dict,
                                  option_type: str) -> Optional[Dict]:
        """
        Calculate all metrics for a vertical spread
        
        Returns:
            Dict with spread metrics or None if invalid
        """
        # Debit spreads: pay net premium
        # Credit spreads: receive net premium
        if spread_type in ['bull_call', 'bear_put']:
            # Debit spread
            net_debit = buy_price - sell_price
            if net_debit <= 0:
                return None
            
            entry_price = net_debit
            max_risk = net_debit * 100  # Per contract
            max_profit = (abs(sell_strike - buy_strike) - net_debit) * 100
            
        else:  # bull_put, bear_call (credit spreads)
            net_credit = sell_price - buy_price
            if net_credit <= 0:
                return None
            
            entry_price = net_credit
            max_risk = (abs(sell_strike - buy_strike) - net_credit) * 100
            max_profit = net_credit * 100
        
        # Skip if max risk exceeds constraints
        if max_risk > config.ACCOUNT_SIZES[500]['max_risk']:
            return None
        
        # Calculate ROI
        if max_risk <= 0:
            return None
        roi_pct = (max_profit / max_risk) * 100
        
        # Skip if ROI too low
        if roi_pct < config.MIN_ROI_PCT:
            return None
        
        # Estimate Greeks for both legs
        iv = underlying_data.get('iv_rank', 30) / 100  # Convert to decimal
        
        long_greeks = self.market_data.get_greeks_estimate(
            option_type, buy_strike, current_price, dte, iv
        )
        short_greeks = self.market_data.get_greeks_estimate(
            option_type, sell_strike, current_price, dte, iv
        )
        
        # Net Greeks (long - short for debit spreads, short - long for credit spreads)
        if spread_type in ['bull_call', 'bear_put']:
            net_delta = long_greeks['delta'] - short_greeks['delta']
            net_theta = long_greeks['theta'] - short_greeks['theta']
            net_vega = long_greeks['vega'] - short_greeks['vega']
        else:
            net_delta = short_greeks['delta'] - long_greeks['delta']
            net_theta = short_greeks['theta'] - long_greeks['theta']
            net_vega = short_greeks['vega'] - long_greeks['vega']
        
        # Calculate breakeven
        if spread_type == 'bull_call':
            breakeven = buy_strike + entry_price
        elif spread_type == 'bull_put':
            breakeven = sell_strike - entry_price
        elif spread_type == 'bear_call':
            breakeven = buy_strike + entry_price
        else:  # bear_put
            breakeven = sell_strike - entry_price
        
        # Calculate required move
        move_pct = abs((breakeven - current_price) / current_price) * 100
        
        # Skip if move requirement out of range
        if not (config.MIN_MOVE_PCT <= move_pct <= config.MAX_MOVE_PCT):
            return None
        
        return {
            'ticker': ticker,
            'spread_type': spread_type,
            'buy_strike': buy_strike,
            'sell_strike': sell_strike,
            'buy_price': round(buy_price, 2),
            'sell_price': round(sell_price, 2),
            'entry_price': round(entry_price, 2),
            'max_risk': round(max_risk, 2),
            'max_profit': round(max_profit, 2),
            'roi_pct': round(roi_pct, 1),
            'dte': dte,
            'net_delta': round(abs(net_delta), 2),
            'net_theta': round(net_theta, 3),
            'net_vega': round(net_vega, 3),
            'breakeven': round(breakeven, 2),
            'current_price': current_price,
            'move_pct': round(move_pct, 2),
            'long_delta': round(abs(long_greeks['delta']), 2),
            'short_delta': round(abs(short_greeks['delta']), 2),
        }
    
    def filter_spreads(self, spreads: List[Dict], underlying_data: Dict) -> List[Dict]:
        """
        Filter spreads by all constraints (Greeks, volatility, technicals)
        
        Args:
            spreads: List of spread dicts
            underlying_data: Dict with price, atr, rsi, iv_rank
        
        Returns:
            Filtered list of spreads
        """
        filtered = []
        
        for spread in spreads:
            # Greeks filters
            if not self._check_greeks_constraints(spread):
                continue
            
            # Volatility filters
            if not self._check_volatility_constraints(spread, underlying_data):
                continue
            
            # Technical filters
            if not self._check_technical_constraints(spread, underlying_data):
                continue
            
            filtered.append(spread)
        
        return filtered
    
    def _check_greeks_constraints(self, spread: Dict) -> bool:
        """Check if spread meets Greeks requirements"""
        # Long leg delta
        if not (config.LONG_LEG_DELTA_MIN <= spread['long_delta'] <= config.LONG_LEG_DELTA_MAX):
            return False
        
        # Short leg delta
        if not (config.SHORT_LEG_DELTA_MIN <= spread['short_delta'] <= config.SHORT_LEG_DELTA_MAX):
            return False
        
        # Net spread delta
        if not (config.NET_SPREAD_DELTA_MIN <= spread['net_delta'] <= config.NET_SPREAD_DELTA_MAX):
            return False
        
        return True
    
    def _check_volatility_constraints(self, spread: Dict, underlying_data: Dict) -> bool:
        """Check if spread meets volatility requirements"""
        iv_rank = underlying_data.get('iv_rank')
        
        # IV Rank check
        if iv_rank and iv_rank > config.MAX_IV_RANK:
            return False
        
        # Implied move vs ATR check
        atr = underlying_data.get('atr', 0)
        if atr > 0:
            atr_pct = (atr / underlying_data['price']) * 100
            implied_move = spread['move_pct']
            
            if implied_move > atr_pct * config.MAX_IMPLIED_MOVE_MULTIPLIER:
                return False
        
        return True
    
    def _check_technical_constraints(self, spread: Dict, underlying_data: Dict) -> bool:
        """Check if spread meets technical requirements"""
        rsi = underlying_data.get('rsi')
        
        # RSI range check
        if rsi and not (config.RSI_MIN <= rsi <= config.RSI_MAX):
            return False
        
        # Direction alignment check
        spread_type = spread['spread_type']
        
        # Bull spreads: prefer RSI < 60 (not overbought)
        if spread_type in ['bull_call', 'bull_put']:
            if rsi and rsi > 60:
                return False
        
        # Bear spreads: prefer RSI > 40 (not oversold)
        elif spread_type in ['bear_call', 'bear_put']:
            if rsi and rsi < 40:
                return False
        
        return True
    
    def rank_spreads(self, spreads: List[Dict], has_catalyst: bool = False) -> List[Dict]:
        """
        Rank spreads by priority (ROI, liquidity, catalyst alignment)
        
        Args:
            spreads: List of spread dicts
            has_catalyst: Whether ticker has upcoming catalyst
        
        Returns:
            Sorted list of spreads (best first)
        """
        # Calculate composite score for each spread
        for spread in spreads:
            score = 0
            
            # ROI score (0-40 points)
            roi = spread['roi_pct']
            score += min(roi / 2.5, 40)  # 100% ROI = 40 points
            
            # Delta score (0-20 points) - prefer higher delta
            delta = spread['net_delta']
            score += min(delta * 50, 20)  # 0.40 delta = 20 points
            
            # DTE score (0-20 points) - prefer shorter DTE
            dte = spread['dte']
            score += max(20 - (dte * 4), 0)  # 1 DTE = 16 points, 5 DTE = 0 points
            
            # Catalyst bonus (0-20 points)
            if has_catalyst:
                score += 20
            
            spread['score'] = round(score, 1)
        
        # Sort by score (descending)
        spreads.sort(key=lambda x: x['score'], reverse=True)
        
        return spreads
    
    def determine_spread_direction(self, underlying_data: Dict) -> str:
        """
        Determine optimal spread direction based on technicals
        
        Args:
            underlying_data: Dict with price, atr, rsi, iv_rank
        
        Returns:
            'bull' or 'bear'
        """
        rsi = underlying_data.get('rsi', 50)
        
        # Simple RSI-based direction
        if rsi < 50:
            return 'bull'  # Oversold, expect bounce
        else:
            return 'bear'  # Overbought, expect pullback
