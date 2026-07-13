import datetime
import random
import yfinance as yf
from src.data_provider import *

class FinancialOption:
    def __init__(self, ticker, strike, expiry_date, option_type="call", volatility="market"):
        self.ticker = ticker.upper().strip()
        self.expiry_date = datetime.datetime.strptime(expiry_date, "%Y-%m-%d")
        self.option_type = option_type.lower().strip()
        self.spot = get_live_spot_price(self.ticker)
        self.strike = resolve_strike(strike, self.spot)
        self.volatility = self.resolve_volatility(volatility)
        self.risk_free_rate = get_current_risk_free_rate()
        self.spot_date = datetime.datetime.today().strftime("%Y-%m-%d")


    def resolve_volatility(self, volatility_input):
        if isinstance(volatility_input, str) and volatility_input.lower() == "market":
            try:
                # Fallback to self.strike if it has already been resolved, otherwise look up via target parameters
                target_strike = self.strike if self.strike else float(self.resolve_strike(self.spot))
                return get_market_implied_volatility(
                    self.ticker, self.expiry_date, self.strike, self.option_type
                )
            except Exception as err:
                print(f"⚠️ Market IV Fetch Failed ({err}). Defaulting to 30% baseline proxy.")
                return 0.30
        return float(volatility_input)
    
    def get_time_to_maturity(self, evaluation_date_str):
        eval_date = datetime.datetime.strptime(evaluation_date_str, "%Y-%m-%d")
        time_delta = self.expiry_date - eval_date
        return max(time_delta.days / 365.0, 0.0)
    
    def __repr__(self):
        # Dynamically grabs "FinancialOption", "AmericanOption", etc.
        class_name = self.__class__.__name__
        
        # Formats the date back to a clean string representation
        expiry_str = self.expiry_date.strftime("%Y-%m-%d")
        
        return (
            f"{class_name}("
            f"ticker='{self.ticker}', "
            f"strike='{self.strike}', "
            f"expiry_date='{expiry_str}', "
            f"spot_date='{self.spot_date}', "
            f"option_type='{self.option_type}', "
            f"underlying_spot='{self.spot:.2f}', "
            f"volatility='{self.volatility:.4f}', "
            f"risk_free_rate='{self.risk_free_rate:.4f}', "
            f")"
        )

    def calculate_greeks(self):
        ds = 0.01 * self.spot  
        dv = 0.01        

        p_base = self.option_price
        p_plus_s = self.price(spot = self.spot + ds, volatility=self.volatility, steps=100)
        p_minus_s = self.price(spot = self.spot - ds, volatility=self.volatility, steps=100)

        delta = (p_plus_s - p_minus_s) / (2 * ds)
        gamma = (p_plus_s - 2 * p_base + p_minus_s) / (ds ** 2)
        p_plus_v = self.price(spot = self.spot, volatility=self.volatility + dv, steps=100)
        vega = (p_plus_v - p_base) / (dv * 100)

        return {
            "spot": self.spot,
            "strike": self.strike,
            "volatility": self.volatility,
            "price": p_base,
            "delta": delta,
            "gamma": gamma,
            "vega": vega
        }