"""
Market Data Module - Fetch real-time market data and technical indicators
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import config


class MarketDataFetcher:
    """Fetch real-time market data, options chains, and calculate technical indicators"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timestamp = {}
        self.cache_duration = 60  # Cache for 60 seconds
    
    def get_underlying_data(self, ticker: str) -> Optional[Dict]:
        """
        Get underlying stock/ETF data including price, IV, ATR, RSI
        
        Returns:
            Dict with keys: price, iv_rank, atr, rsi, volume, or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get current price and info
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if not current_price:
                # Fallback: get from history
                hist = stock.history(period='1d')
                if hist.empty:
                    return None
                current_price = hist['Close'].iloc[-1]
            
            # Get historical data for technical indicators
            hist = stock.history(period='60d')
            if hist.empty or len(hist) < config.ATR_PERIOD:
                return None
            
            # Calculate ATR (Average True Range)
            atr = self._calculate_atr(hist, config.ATR_PERIOD)
            
            # Calculate RSI
            rsi = self._calculate_rsi(hist['Close'], config.RSI_PERIOD)
            
            # Get implied volatility (from options chain)
            iv_rank = self._calculate_iv_rank(stock)
            
            return {
                'ticker': ticker,
                'price': round(current_price, 2),
                'iv_rank': round(iv_rank, 1) if iv_rank else None,
                'atr': round(atr, 2),
                'rsi': round(rsi, 1),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
            }
        
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    def get_options_chain(self, ticker: str, dte_min: int = 1, dte_max: int = 5) -> List[Dict]:
        """
        Get options chain for specified DTE range
        
        Returns:
            List of dicts with expiration dates and options data
        """
        try:
            stock = yf.Ticker(ticker)
            expirations = stock.options
            
            if not expirations:
                return []
            
            # Filter expirations by DTE
            today = datetime.now().date()
            valid_chains = []
            
            for exp_str in expirations:
                exp_date = datetime.strptime(exp_str, '%Y-%m-%d').date()
                dte = (exp_date - today).days
                
                if dte_min <= dte <= dte_max:
                    # Get calls and puts
                    calls = stock.option_chain(exp_str).calls
                    puts = stock.option_chain(exp_str).puts
                    
                    valid_chains.append({
                        'expiration': exp_str,
                        'dte': dte,
                        'calls': calls,
                        'puts': puts,
                    })
            
            return valid_chains
        
        except Exception as e:
            print(f"Error fetching options chain for {ticker}: {e}")
            return []
    
    def _calculate_atr(self, hist: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        high = hist['High']
        low = hist['Low']
        close = hist['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        return atr
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def _calculate_iv_rank(self, stock) -> Optional[float]:
        """
        Calculate IV Rank (current IV percentile over 52 weeks)
        Note: This is a simplified version using historical volatility as proxy
        """
        try:
            # Get 1 year of historical data
            hist = stock.history(period='1y')
            if hist.empty or len(hist) < 252:
                return None
            
            # Calculate historical volatility (annualized)
            returns = np.log(hist['Close'] / hist['Close'].shift(1))
            current_hv = returns.iloc[-21:].std() * np.sqrt(252) * 100  # 21-day HV
            
            # Calculate rolling 21-day HV for the year
            rolling_hv = returns.rolling(window=21).std() * np.sqrt(252) * 100
            rolling_hv = rolling_hv.dropna()
            
            if len(rolling_hv) == 0:
                return None
            
            # IV Rank = where current HV ranks in the distribution
            iv_rank = (rolling_hv < current_hv).sum() / len(rolling_hv) * 100
            
            return iv_rank
        
        except Exception as e:
            return None
    
    def calculate_implied_move(self, options_chain: Dict, current_price: float) -> float:
        """
        Calculate implied move from ATM straddle price
        
        Args:
            options_chain: Dict with 'calls' and 'puts' DataFrames
            current_price: Current underlying price
        
        Returns:
            Implied move as percentage
        """
        try:
            calls = options_chain['calls']
            puts = options_chain['puts']
            
            # Find ATM strike (closest to current price)
            calls['strike_diff'] = abs(calls['strike'] - current_price)
            atm_call = calls.loc[calls['strike_diff'].idxmin()]
            
            puts['strike_diff'] = abs(puts['strike'] - current_price)
            atm_put = puts.loc[puts['strike_diff'].idxmin()]
            
            # Straddle price (call + put at same strike)
            if atm_call['strike'] == atm_put['strike']:
                straddle_price = atm_call['lastPrice'] + atm_put['lastPrice']
            else:
                # Use average if strikes don't match exactly
                straddle_price = (atm_call['lastPrice'] + atm_put['lastPrice'])
            
            # Implied move = straddle price / stock price
            implied_move_pct = (straddle_price / current_price) * 100
            
            return implied_move_pct
        
        except Exception as e:
            return 0.0
    
    def filter_liquid_options(self, options_df: pd.DataFrame, current_price: float) -> pd.DataFrame:
        """
        Filter options by liquidity requirements
        
        Args:
            options_df: DataFrame with options data
            current_price: Current underlying price
        
        Returns:
            Filtered DataFrame
        """
        # Calculate bid-ask spread percentage
        options_df['mid_price'] = (options_df['bid'] + options_df['ask']) / 2
        options_df['spread_pct'] = (options_df['ask'] - options_df['bid']) / options_df['mid_price']
        
        # Filter by liquidity constraints
        filtered = options_df[
            (options_df['volume'] > 0) &  # Has volume
            (options_df['openInterest'] >= config.MIN_OPEN_INTEREST) &  # Min OI
            (options_df['spread_pct'] <= config.MAX_BID_ASK_SPREAD_PCT) &  # Max spread
            (options_df['bid'] > 0) &  # Valid bid
            (options_df['ask'] > 0)  # Valid ask
        ].copy()
        
        return filtered
    
    def get_greeks_estimate(self, option_type: str, strike: float, current_price: float, 
                           dte: int, iv: float = 0.30) -> Dict:
        """
        Estimate option Greeks using simplified Black-Scholes approximations
        
        Args:
            option_type: 'call' or 'put'
            strike: Strike price
            current_price: Current underlying price
            dte: Days to expiration
            iv: Implied volatility (decimal, e.g., 0.30 for 30%)
        
        Returns:
            Dict with delta, gamma, theta, vega estimates
        """
        from scipy.stats import norm
        
        # Convert to years
        t = dte / 365.0
        
        if t <= 0:
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
        
        # Risk-free rate (approximate)
        r = 0.05
        
        # Calculate d1 and d2
        d1 = (np.log(current_price / strike) + (r + 0.5 * iv**2) * t) / (iv * np.sqrt(t))
        d2 = d1 - iv * np.sqrt(t)
        
        # Calculate Greeks
        if option_type.lower() == 'call':
            delta = norm.cdf(d1)
            theta = (-(current_price * norm.pdf(d1) * iv) / (2 * np.sqrt(t)) 
                    - r * strike * np.exp(-r * t) * norm.cdf(d2)) / 365
        else:  # put
            delta = -norm.cdf(-d1)
            theta = (-(current_price * norm.pdf(d1) * iv) / (2 * np.sqrt(t)) 
                    + r * strike * np.exp(-r * t) * norm.cdf(-d2)) / 365
        
        gamma = norm.pdf(d1) / (current_price * iv * np.sqrt(t))
        vega = current_price * norm.pdf(d1) * np.sqrt(t) / 100
        
        return {
            'delta': round(delta, 3),
            'gamma': round(gamma, 4),
            'theta': round(theta, 3),
            'vega': round(vega, 3),
        }
