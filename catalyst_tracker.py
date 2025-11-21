"""
Catalyst Tracker - Track earnings, economic events, and Fed activities
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import config


class CatalystTracker:
    """Track market catalysts: earnings, economic data, Fed events"""
    
    def __init__(self):
        self.economic_calendar = self._get_economic_calendar()
    
    def get_earnings_calendar(self, tickers: List[str], days_ahead: int = 3) -> Dict[str, Optional[Dict]]:
        """
        Get earnings dates for specified tickers within the next N days
        
        Args:
            tickers: List of ticker symbols
            days_ahead: Number of days to look ahead
        
        Returns:
            Dict mapping ticker to earnings info (date, time) or None
        """
        earnings_data = {}
        today = datetime.now().date()
        cutoff_date = today + timedelta(days=days_ahead)
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                calendar = stock.calendar
                
                if calendar is not None and not calendar.empty:
                    # Try to get earnings date
                    if 'Earnings Date' in calendar.index:
                        earnings_dates = calendar.loc['Earnings Date']
                        
                        # Handle multiple earnings dates (range)
                        if isinstance(earnings_dates, (list, tuple)):
                            earnings_date = earnings_dates[0]
                        else:
                            earnings_date = earnings_dates
                        
                        # Convert to date if it's a timestamp
                        if hasattr(earnings_date, 'date'):
                            earnings_date = earnings_date.date()
                        elif isinstance(earnings_date, str):
                            try:
                                earnings_date = datetime.strptime(earnings_date, '%Y-%m-%d').date()
                            except:
                                earnings_date = None
                        
                        # Check if within our window
                        if earnings_date and today <= earnings_date <= cutoff_date:
                            days_until = (earnings_date - today).days
                            earnings_data[ticker] = {
                                'date': earnings_date.strftime('%Y-%m-%d'),
                                'days_until': days_until,
                                'time': 'Unknown',  # yfinance doesn't provide time
                                'catalyst_type': 'Earnings',
                            }
                        else:
                            earnings_data[ticker] = None
                    else:
                        earnings_data[ticker] = None
                else:
                    earnings_data[ticker] = None
            
            except Exception as e:
                earnings_data[ticker] = None
        
        return earnings_data
    
    def _get_economic_calendar(self) -> List[Dict]:
        """
        Get upcoming economic events (hardcoded schedule + typical patterns)
        
        Note: For production, integrate with a real economic calendar API
        (e.g., Trading Economics, Investing.com, or Fed's official calendar)
        """
        today = datetime.now()
        events = []
        
        # Typical economic data release schedule
        # CPI: Usually mid-month (around 13th)
        # PPI: Usually mid-month (around 14th)
        # Jobless Claims: Every Thursday at 8:30 AM ET
        # FOMC: 8 times per year (check Fed calendar)
        # GDP: End of each quarter
        
        # Generate next few days of typical events
        for i in range(7):
            check_date = today + timedelta(days=i)
            day_name = check_date.strftime('%A')
            
            # Jobless Claims - Every Thursday
            if day_name == 'Thursday':
                events.append({
                    'event': 'Initial Jobless Claims',
                    'date': check_date.strftime('%Y-%m-%d'),
                    'time': '08:30 AM ET',
                    'days_until': i,
                    'catalyst_type': 'Economic Data',
                })
            
            # Check for mid-month CPI/PPI
            if 12 <= check_date.day <= 15:
                if check_date.day == 13:
                    events.append({
                        'event': 'CPI (Consumer Price Index)',
                        'date': check_date.strftime('%Y-%m-%d'),
                        'time': '08:30 AM ET',
                        'days_until': i,
                        'catalyst_type': 'Economic Data',
                    })
                elif check_date.day == 14:
                    events.append({
                        'event': 'PPI (Producer Price Index)',
                        'date': check_date.strftime('%Y-%m-%d'),
                        'time': '08:30 AM ET',
                        'days_until': i,
                        'catalyst_type': 'Economic Data',
                    })
        
        return events
    
    def get_upcoming_catalysts(self, ticker: str, days_ahead: int = 3) -> List[Dict]:
        """
        Get all upcoming catalysts for a ticker (earnings + relevant economic events)
        
        Args:
            ticker: Ticker symbol
            days_ahead: Number of days to look ahead
        
        Returns:
            List of catalyst dicts sorted by date
        """
        catalysts = []
        
        # Get earnings
        earnings = self.get_earnings_calendar([ticker], days_ahead)
        if earnings.get(ticker):
            catalysts.append(earnings[ticker])
        
        # Add economic events (relevant for all tickers)
        for event in self.economic_calendar:
            if event['days_until'] <= days_ahead:
                catalysts.append(event)
        
        # Sort by days_until
        catalysts.sort(key=lambda x: x['days_until'])
        
        return catalysts
    
    def get_next_catalyst(self, ticker: str, days_ahead: int = 3) -> Optional[Dict]:
        """
        Get the next catalyst for a ticker within the specified window
        
        Args:
            ticker: Ticker symbol
            days_ahead: Number of days to look ahead
        
        Returns:
            Next catalyst dict or None
        """
        catalysts = self.get_upcoming_catalysts(ticker, days_ahead)
        return catalysts[0] if catalysts else None
    
    def format_catalyst_string(self, catalyst: Optional[Dict]) -> str:
        """
        Format catalyst information as a readable string
        
        Args:
            catalyst: Catalyst dict
        
        Returns:
            Formatted string like "CPI (Thu 8:30am)" or "No catalyst"
        """
        if not catalyst:
            return "No catalyst"
        
        event_name = catalyst.get('event', catalyst.get('catalyst_type', 'Unknown'))
        date_str = catalyst.get('date', '')
        time_str = catalyst.get('time', '')
        
        # Parse date to get day of week
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_abbr = date_obj.strftime('%a')  # Mon, Tue, etc.
        except:
            day_abbr = ''
        
        # Simplify time (e.g., "08:30 AM ET" -> "8:30am")
        if time_str:
            time_str = time_str.replace(' AM ET', 'am').replace(' PM ET', 'pm').replace(':00', '')
        
        if day_abbr and time_str:
            return f"{event_name} ({day_abbr} {time_str})"
        elif day_abbr:
            return f"{event_name} ({day_abbr})"
        else:
            return event_name
    
    def get_fed_events(self, days_ahead: int = 7) -> List[Dict]:
        """
        Get upcoming Fed events (FOMC meetings, Fed speakers)
        
        Note: For production, integrate with Fed's official calendar
        This is a placeholder that returns typical Fed event patterns
        """
        # Placeholder - in production, scrape from:
        # https://www.federalreserve.gov/newsevents/calendar.htm
        
        events = []
        today = datetime.now()
        
        # FOMC meetings are typically 8 times per year
        # Check if we're near typical FOMC dates (every ~6 weeks)
        # This is a simplified placeholder
        
        return events
    
    def has_catalyst_in_window(self, ticker: str, hours: int = 72) -> bool:
        """
        Check if ticker has any catalyst in the next N hours
        
        Args:
            ticker: Ticker symbol
            hours: Time window in hours
        
        Returns:
            True if catalyst exists in window
        """
        days = hours // 24 + 1
        catalyst = self.get_next_catalyst(ticker, days)
        
        if not catalyst:
            return False
        
        # Check if catalyst is within the hour window
        days_until = catalyst.get('days_until', 999)
        return days_until * 24 <= hours
