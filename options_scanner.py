#!/usr/bin/env python3
"""
Options Vertical Spreads Scanner
Identify high-probability vertical spreads with 30-100% ROI potential
"""

import sys
from typing import List, Dict, Optional
from tabulate import tabulate
from datetime import datetime
import config
from market_data import MarketDataFetcher
from catalyst_tracker import CatalystTracker
from spread_analyzer import SpreadAnalyzer


class OptionsScanner:
    """Main scanner orchestrator"""
    
    def __init__(self, account_size: int = 100):
        self.account_size = account_size
        self.market_data = MarketDataFetcher()
        self.catalyst_tracker = CatalystTracker()
        self.spread_analyzer = SpreadAnalyzer(self.market_data)
        
        # Get risk limits for account size
        if account_size not in config.ACCOUNT_SIZES:
            # Find closest account size
            closest = min(config.ACCOUNT_SIZES.keys(), key=lambda x: abs(x - account_size))
            self.risk_limits = config.ACCOUNT_SIZES[closest]
        else:
            self.risk_limits = config.ACCOUNT_SIZES[account_size]
    
    def scan_all_tickers(self) -> List[Dict]:
        """
        Scan all configured tickers for qualifying spreads
        
        Returns:
            List of qualifying spreads sorted by score
        """
        all_spreads = []
        
        print(f"\n{'='*80}")
        print(f"OPTIONS VERTICAL SPREADS SCANNER")
        print(f"Account Size: ${self.account_size} | Max Risk: ${self.risk_limits['max_risk']} per trade")
        print(f"Scanning {len(config.TICKERS)} tickers for {config.MIN_DTE}-{config.MAX_DTE} DTE spreads...")
        print(f"{'='*80}\n")
        
        for ticker in config.TICKERS:
            print(f"Scanning {ticker}...", end=' ')
            
            # Get underlying data
            underlying_data = self.market_data.get_underlying_data(ticker)
            if not underlying_data:
                print("❌ Failed to fetch data")
                continue
            
            # Get catalysts
            catalyst = self.catalyst_tracker.get_next_catalyst(ticker, days_ahead=3)
            has_catalyst = catalyst is not None
            
            # Get options chains
            options_chains = self.market_data.get_options_chain(
                ticker, 
                dte_min=config.MIN_DTE, 
                dte_max=config.MAX_DTE
            )
            
            if not options_chains:
                print("❌ No options chains available")
                continue
            
            # Determine spread direction
            direction = self.spread_analyzer.determine_spread_direction(underlying_data)
            
            # Calculate spreads for each expiration
            ticker_spreads = []
            for chain in options_chains:
                # Try bull call spreads
                if direction == 'bull':
                    spreads = self.spread_analyzer.calculate_vertical_spreads(
                        ticker, underlying_data, chain, 'bull_call'
                    )
                    ticker_spreads.extend(spreads)
                else:
                    # Try bear put spreads
                    spreads = self.spread_analyzer.calculate_vertical_spreads(
                        ticker, underlying_data, chain, 'bear_put'
                    )
                    ticker_spreads.extend(spreads)
            
            # Filter spreads
            filtered_spreads = self.spread_analyzer.filter_spreads(ticker_spreads, underlying_data)
            
            # Filter by account risk limits
            filtered_spreads = [
                s for s in filtered_spreads 
                if s['max_risk'] <= self.risk_limits['max_risk']
            ]
            
            # Rank spreads
            ranked_spreads = self.spread_analyzer.rank_spreads(filtered_spreads, has_catalyst)
            
            # Add catalyst info to each spread
            for spread in ranked_spreads:
                spread['catalyst'] = catalyst
                spread['underlying_data'] = underlying_data
            
            all_spreads.extend(ranked_spreads[:2])  # Top 2 per ticker
            
            print(f"✓ Found {len(ranked_spreads)} qualifying spreads")
        
        # Final ranking across all tickers
        all_spreads.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit to configured range
        max_display = config.MAX_SPREADS_TO_DISPLAY
        return all_spreads[:max_display]
    
    def format_output(self, spreads: List[Dict]) -> str:
        """
        Format spreads as table + detailed analysis
        
        Args:
            spreads: List of spread dicts
        
        Returns:
            Formatted string output
        """
        if not spreads:
            return "\n❌ No qualifying spreads found matching all criteria.\n"
        
        output = []
        output.append(f"\n{'='*80}")
        output.append(f"FOUND {len(spreads)} HIGH-PROBABILITY VERTICAL SPREADS")
        output.append(f"{'='*80}\n")
        
        # Summary table
        table_data = []
        for i, spread in enumerate(spreads, 1):
            catalyst_str = self.catalyst_tracker.format_catalyst_string(spread.get('catalyst'))
            
            table_data.append([
                spread['ticker'],
                self._format_spread_type(spread['spread_type']),
                catalyst_str,
                f"${spread['entry_price']:.2f}",
                f"${spread['max_risk']:.0f}",
                f"${spread['max_profit']:.0f}",
                f"{spread['roi_pct']:.0f}%",
                spread['dte'],
                f"+{spread['net_delta']:.0f}",
                f"${spread['breakeven']:.2f}",
                f"{spread['underlying_data'].get('iv_rank', 0):.0f}%",
            ])
        
        headers = ['Ticker', 'Type', 'Catalyst', 'Entry', 'Max Risk', 'Max Profit', 
                  'ROI', 'DTE', 'Delta', 'Breakeven', 'IV Rank']
        
        output.append(tabulate(table_data, headers=headers, tablefmt='grid'))
        output.append("\n")
        
        # Detailed analysis for each spread
        output.append(f"{'='*80}")
        output.append("DETAILED ANALYSIS")
        output.append(f"{'='*80}\n")
        
        for i, spread in enumerate(spreads, 1):
            output.append(self._format_spread_details(i, spread))
            output.append("\n")
        
        return "\n".join(output)
    
    def _format_spread_type(self, spread_type: str) -> str:
        """Format spread type for display"""
        type_map = {
            'bull_call': 'Bull Call',
            'bull_put': 'Bull Put',
            'bear_call': 'Bear Call',
            'bear_put': 'Bear Put',
        }
        return type_map.get(spread_type, spread_type)
    
    def _format_spread_details(self, index: int, spread: Dict) -> str:
        """Format detailed analysis for a single spread"""
        lines = []
        
        # Header
        lines.append(f"[{index}] {spread['ticker']} - {self._format_spread_type(spread['spread_type'])} Spread")
        lines.append("-" * 80)
        
        # Entry details
        if spread['spread_type'] in ['bull_call', 'bear_put']:
            lines.append(f"Entry: Buy {spread['buy_strike']}C @ ${spread['buy_price']:.2f} / "
                        f"Sell {spread['sell_strike']}C @ ${spread['sell_price']:.2f} "
                        f"→ Net Debit: ${spread['entry_price']:.2f}")
        else:
            lines.append(f"Entry: Sell {spread['sell_strike']}P @ ${spread['sell_price']:.2f} / "
                        f"Buy {spread['buy_strike']}P @ ${spread['buy_price']:.2f} "
                        f"→ Net Credit: ${spread['entry_price']:.2f}")
        
        # P&L
        lines.append(f"Max P&L: Risk ${spread['max_risk']:.0f} | "
                    f"Profit ${spread['max_profit']:.0f} | "
                    f"ROI {spread['roi_pct']:.0f}%")
        
        # Greeks
        lines.append(f"Greeks: Delta +{spread['net_delta']:.0f}, "
                    f"Theta {spread['net_theta']:.2f}/day, "
                    f"Vega {spread['net_vega']:.2f}")
        
        # Breakeven & move required
        current_price = spread['current_price']
        breakeven = spread['breakeven']
        move_pct = spread['move_pct']
        
        lines.append(f"Breakeven: ${breakeven:.2f} (needs {move_pct:.1f}% move from ${current_price:.2f})")
        
        # Thesis
        thesis = self._generate_thesis(spread)
        lines.append(f"Thesis: {thesis}")
        
        # Exit plan
        exit_plan = self._generate_exit_plan(spread)
        lines.append(f"Exit Plan: {exit_plan}")
        
        # Risk warning
        risk = self._generate_risk_warning(spread)
        lines.append(f"Risk: {risk}")
        
        return "\n".join(lines)
    
    def _generate_thesis(self, spread: Dict) -> str:
        """Generate one-sentence thesis for the spread"""
        catalyst = spread.get('catalyst')
        underlying = spread['underlying_data']
        rsi = underlying.get('rsi', 50)
        
        catalyst_str = self.catalyst_tracker.format_catalyst_string(catalyst) if catalyst else "technical setup"
        
        direction = "bullish" if spread['spread_type'] in ['bull_call', 'bull_put'] else "bearish"
        
        if rsi < 40:
            technical = f"oversold (RSI {rsi:.0f})"
        elif rsi > 60:
            technical = f"overbought (RSI {rsi:.0f})"
        else:
            technical = f"neutral (RSI {rsi:.0f})"
        
        return f"{catalyst_str} expected to drive {direction} move; {technical} supports direction"
    
    def _generate_exit_plan(self, spread: Dict) -> str:
        """Generate exit plan for the spread"""
        entry = spread['entry_price']
        
        # 50% profit target
        target_50 = entry * 1.5
        
        # 70% profit target
        target_70 = entry * 1.7
        
        return (f"Take 50% profit at ${target_50:.2f} (+50% gain), "
                f"close remainder at ${target_70:.2f} (+70%) or expiration")
    
    def _generate_risk_warning(self, spread: Dict) -> str:
        """Generate risk warning for the spread"""
        catalyst = spread.get('catalyst')
        
        if catalyst:
            return "Catalyst disappoints or market gaps against position"
        else:
            return "No immediate catalyst; relies on technical momentum"
    
    def run(self):
        """Main execution method"""
        try:
            # Scan for spreads
            spreads = self.scan_all_tickers()
            
            # Format and display output
            output = self.format_output(spreads)
            print(output)
            
            # Summary
            if spreads:
                print(f"\n{'='*80}")
                print(f"✓ Scan complete. Found {len(spreads)} qualifying spreads.")
                print(f"  Account: ${self.account_size} | Max risk per trade: ${self.risk_limits['max_risk']}")
                print(f"  Position sizing: Max {config.MAX_POSITION_SIZE_PCT*100:.0f}% of account per trade")
                print(f"{'='*80}\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Scan interrupted by user.\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n\n❌ Error during scan: {e}\n")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Options Vertical Spreads Scanner - Find high-probability spreads',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python options_scanner.py --account 100
  python options_scanner.py --account 500
  python options_scanner.py --account 200

Account sizes: $100, $200, $300, $400, $500
        """
    )
    
    parser.add_argument(
        '--account',
        type=int,
        default=100,
        help='Account size in dollars (default: 100)'
    )
    
    args = parser.parse_args()
    
    # Validate account size
    if args.account < 100 or args.account > 10000:
        print("❌ Account size must be between $100 and $10,000")
        sys.exit(1)
    
    # Run scanner
    scanner = OptionsScanner(account_size=args.account)
    scanner.run()


if __name__ == '__main__':
    main()
