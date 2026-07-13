import datetime
import math
from src.base_option import FinancialOption
from src.pricing import binomial_tree_price

class AmericanOption(FinancialOption):
    def __init__(self, ticker, strike, expiry_date, option_type):
        super().__init__(ticker, strike, expiry_date, option_type)
        self.option_price = self.price(spot = self.spot, volatility=self.volatility, steps=100)


    def price(self, spot, volatility, steps=100):
        return binomial_tree_price(
            spot,
            strike=self.strike,
            t_maturity=self.get_time_to_maturity(self.spot_date),
            risk_free_rate=self.risk_free_rate,
            volatility=volatility,
            option_type=self.option_type,
            steps=steps
        )



    
    def __repr__(self):
        # Reuses the parent string but appends the child-specific 'steps' variable
        parent_repr = super().__repr__()
        # Strip the trailing ")" from the parent string, add steps, and close it
        return f"{parent_repr[:-1]}, option_price={self.option_price:.4f})"