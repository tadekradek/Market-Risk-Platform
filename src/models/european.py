import math
from scipy.stats import norm
from src.base_option import FinancialOption
from src.pricing import black_scholes_price
import datetime

class EuropeanOption(FinancialOption):
    def __init__(self, ticker, strike, expiry_date, option_type):
        super().__init__(ticker, strike, expiry_date, option_type)
        self.option_price = self.price(spot = self.spot, volatility=self.volatility)

    def price(self, spot, volatility, **kwargs):
        return black_scholes_price(
            spot,
            strike=self.strike,
            t_maturity=self.get_time_to_maturity(self.spot_date),
            risk_free_rate=self.risk_free_rate,
            volatility=volatility,
            option_type=self.option_type
        )
    
    def __repr__(self):
        # Reuses the parent string but appends the child-specific 'steps' variable
        parent_repr = super().__repr__()
        # Strip the trailing ")" from the parent string, add steps, and close it
        return f"{parent_repr[:-1]}, option_price={self.option_price:.4f})"