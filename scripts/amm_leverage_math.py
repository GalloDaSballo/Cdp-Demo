## TODO:
"""
  Given the code in AMM

  Given X amount in the pool
  Figure out how much you can loop before you get Y% of slippage
  Meaning, how many times can you buy Z tokens before the price goes up by Y%

"""

MAX_BPS = 10_000

## Since it's % math, accuracy doesn't matter
PRICE = 13

def max_in_before_price_limit(price_limit, reserve_in, reserve_out):
  return reserve_out * price_limit - reserve_in

def amount_out_given_in(amount_in, reserve_in, reserve_out):
  amount_out = reserve_out * amount_in / (reserve_in + amount_in)
  return amount_out


def calculate_liquidity_required(size, slippage_bps):
    limit_price = (MAX_BPS + slippage_bps) * PRICE / MAX_BPS

    ## We prob want to find a loop or something
    base_reserve_in = size / PRICE
    base_reserve_out = base_reserve_in * PRICE

    while max_in_before_price_limit(limit_price, base_reserve_out, base_reserve_in) < size:
        base_reserve_in *= 2
        base_reserve_out = base_reserve_in * PRICE
      
    
    print("base_reserve_in", base_reserve_in)
    print("base_reserve_out", base_reserve_out)

    print("Proof")
    print("Given ", size, "In")
    print("We get", amount_out_given_in(size, base_reserve_in, base_reserve_out), "out")
        
    
def main():
    size = int(input("Which Size? In BTC \n"))
    
    slippage_bps = int(input("Which Slippage in BPS? \n"))

    calculate_liquidity_required(size, slippage_bps)
    