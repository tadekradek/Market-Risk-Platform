import math
from scipy.stats import norm

def binomial_tree_price(spot, strike, t_maturity, risk_free_rate, volatility, option_type, steps):
    """
    Standalone Cox-Ross-Rubinstein Binomial Tree pricing engine for American options.
    """
    S = float(spot)
    K = float(strike)
    T = float(t_maturity)
    r = float(risk_free_rate)
    sigma = float(volatility)
    opt_type = option_type.lower().strip()
    
    # Boundary safety check: if expired, return intrinsic value
    if T <= 0:
        return max(S - K, 0.0) if opt_type == "call" else max(K - S, 0.0)
        
    dt = T / steps
    u = math.exp(sigma * math.sqrt(dt))
    d = 1.0 / u
    p = (math.exp(r * dt) - d) / (u - d)
    disc = math.exp(-r * dt)
    
    # Generate stock prices and terminal payoffs at expiration step N
    asset_prices = [S * (u ** j) * (d ** (steps - j)) for j in range(steps + 1)]
    option_values = [
        max(price - K, 0.0) if opt_type == "call" else max(K - price, 0.0) 
        for price in asset_prices
    ]
        
    # Step backward through the tree levels
    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            hold_value = disc * (p * option_values[j + 1] + (1 - p) * option_values[j])
            current_S = S * (u ** j) * (d ** (i - j))
            exercise_value = max(current_S - K, 0.0) if opt_type == "call" else max(K - current_S, 0.0)
            option_values[j] = max(hold_value, exercise_value)
            
    return option_values[0]


def black_scholes_price(spot, strike, t_maturity, risk_free_rate, volatility, option_type):
    """
    Standalone Black-Scholes closed-form pricing engine for European options.
    """
    S = float(spot)
    K = float(strike)
    T = float(t_maturity)
    r = float(risk_free_rate)
    sigma = float(volatility)
    opt_type = option_type.lower().strip()
    
    # Boundary safety check: if expired, return intrinsic value
    if T <= 0:
        return max(S - K, 0.0) if opt_type == "call" else max(K - S, 0.0)
        
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if opt_type == "call":
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif opt_type == "put":
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")