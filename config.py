"""
Configuration for Options Vertical Spreads Scanner
"""

# Tickers to scan
TICKERS = [
    'SPY',   # S&P 500 ETF
    'QQQ',   # Nasdaq 100 ETF
    'IWM',   # Russell 2000 ETF
    'GLD',   # Gold ETF
    'SLV',   # Silver ETF
    'XLE',   # Energy Sector ETF
    'AAPL',  # Apple
    'MSFT',  # Microsoft
    'NVDA',  # Nvidia
    'TSLA',  # Tesla
    'AMZN',  # Amazon
]

# Account size configurations
ACCOUNT_SIZES = {
    100: {'min_risk': 20, 'max_risk': 40},
    200: {'min_risk': 30, 'max_risk': 50},
    300: {'min_risk': 30, 'max_risk': 50},
    400: {'min_risk': 30, 'max_risk': 50},
    500: {'min_risk': 30, 'max_risk': 50},
}

# Risk management constraints
MAX_POSITION_SIZE_PCT = 0.20  # 20% of account per trade

# Liquidity filters
MIN_OPTIONS_VOLUME_NOTIONAL = 150000  # $150k daily notional volume
MIN_OPEN_INTEREST = 50  # contracts per strike
MAX_BID_ASK_SPREAD_PCT = 0.15  # 15% of mid-price

# Greeks requirements
LONG_LEG_DELTA_MIN = 0.40
LONG_LEG_DELTA_MAX = 0.70
SHORT_LEG_DELTA_MIN = 0.15
SHORT_LEG_DELTA_MAX = 0.35
NET_SPREAD_DELTA_MIN = 0.25
NET_SPREAD_DELTA_MAX = 0.50

# Volatility filters
MAX_IV_RANK = 70  # Prefer ≤50% for debit spreads
PREFERRED_IV_RANK = 50
MAX_IMPLIED_MOVE_MULTIPLIER = 1.5  # 1.5x ATR

# Technical filters
RSI_MIN = 30
RSI_MAX = 70
RSI_PERIOD = 14
ATR_PERIOD = 14

# DTE (Days to Expiration) range
MIN_DTE = 1
MAX_DTE = 5

# ROI requirements
MIN_ROI_PCT = 30  # 30% minimum
TARGET_ROI_PCT = 100  # 100% target

# Required underlying move
MIN_MOVE_PCT = 1.0  # 1% minimum
MAX_MOVE_PCT = 4.0  # 4% maximum

# Catalyst window (hours)
CATALYST_WINDOW_HOURS = 72  # Next 48-72 hours

# Economic calendar events to track
ECONOMIC_EVENTS = [
    'CPI',
    'PPI',
    'Jobless Claims',
    'Initial Jobless Claims',
    'Fed Minutes',
    'FOMC',
    'GDP',
    'Non-Farm Payrolls',
    'NFP',
    'Retail Sales',
    'Consumer Confidence',
]

# Output settings
MAX_SPREADS_TO_DISPLAY = 7
MIN_SPREADS_TO_DISPLAY = 3
