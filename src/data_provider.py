import datetime
import pandas as pd
import yfinance as yf
import random

def get_current_risk_free_rate():
    t_bill = yf.Ticker("^IRX")
    latest_history = t_bill.history(period="1d")
    if latest_history.empty:
        return 0.045 # Absolute fallback
    raw_yield = latest_history['Close'].iloc[-1]
    return raw_yield / 100.0

def get_market_implied_volatility(ticker_symbol, expiry_date, strike, option_type):
    ticker_symbol = ticker_symbol.upper().strip()
    option_type = option_type.lower().strip()
    target_strike = float(strike)
    
    ticker = yf.Ticker(ticker_symbol)
    if isinstance(expiry_date, datetime.date) or isinstance(expiry_date, datetime.datetime):
        expiry_str = expiry_date.strftime("%Y-%m-%d")
    else:
        expiry_str = str(expiry_date)
        
    chain = ticker.option_chain(expiry_str)
    df = chain.calls if option_type == "call" else chain.puts
    
    contract_row = df[df['strike'] == target_strike]
    if not contract_row.empty:
        return float(contract_row['impliedVolatility'].iloc[0])
    
    # Nearest strike fallback
    closest_strike = df['strike'].iloc[(df['strike'] - target_strike).abs().argsort()[:1]].values[0]
    return float(df[df['strike'] == closest_strike]['impliedVolatility'].iloc[0])

def get_live_spot_price(ticker_symbol):
    """
    Connects to Yahoo Finance to retrieve the current live spot price for a given ticker.
    
    Parameters:
    -----------
    ticker_symbol : str -> e.g., "NVDA", "AAPL"
    
    Returns:
    --------
    float -> The latest market spot price
    """
    clean_ticker = ticker_symbol.upper().strip()
    try:
        ticker_obj = yf.Ticker(clean_ticker)
        # fast_info provides low-latency access to the latest traded price
        spot_price = ticker_obj.fast_info['lastPrice']
        
        if spot_price is None or spot_price <= 0:
            # Fallback to history if fast_info returns edge-case empty data
            historical_data = ticker_obj.history(period="1d")
            if not historical_data.empty:
                spot_price = historical_data['Close'].iloc[-1]
            else:
                raise ValueError(f"No pricing data found for ticker {clean_ticker}")
                
        return float(spot_price)
        
    except Exception as err:
        raise RuntimeError(f"CRITICAL: Failed to retrieve live market spot for {clean_ticker}. Error: {err}")
    

def resolve_strike(strike, spot):
    """
    Processes strike generation logic. Safely catches string flags 
    before any float conversion happens. If 'random', it simulates a realistic 
    exchange-listed strike bracket based on standardized price intervals.
    """
    if isinstance(strike, str):
        flag = strike.lower().strip()
        
        if flag == "random":
            # Establish standard exchange pricing intervals
            if spot <= 25.0:
                interval = 1.0
            elif spot <= 200.0:
                interval = 2.5 if spot < 100.0 else 5.0
            else:
                interval = 10.0

            # Anchor the ATM strike node
            atm_strike = round(spot / interval) * interval
            
            # Generate the exchange bracket array (±5 strikes)
            strike_grid = [atm_strike + (i * interval) for i in range(-5, 6)]
            
            # Select a random strike node from the grid
            return random.choice(strike_grid)
        else:
            raise ValueError(f"Unknown string flag passed to strike: '{strike}'")
            
    # If it's already a number (int or float), pass it through safely
    return float(strike)