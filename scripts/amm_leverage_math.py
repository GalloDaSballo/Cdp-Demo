import pandas as pd
import os

## TODO:
"""
  Given the code in AMM

  Given X amount in the pool
  Figure out how much you can loop before you get Y% of slippage
  Meaning, how many times can you buy Z tokens before the price goes up by Y%

"""

MAX_BPS = 10_000

## Since it's % math, accuracy doesn't matter
PRICE = 14.74

## Slippages to test in BPS
SLIPPAGES = [50, 100, 300] # 0.5%, 1% and 3%

## BTC in size values
SIZES = [1, 20, 50, 100, 300]

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

    loops = 0
    while max_in_before_price_limit(limit_price, base_reserve_out, base_reserve_in) < size:
        base_reserve_in *= 2
        base_reserve_out = base_reserve_in * PRICE
        loops += 1
    
    print("base_reserve_in", base_reserve_in)
    print("base_reserve_out", base_reserve_out)

    print("Proof")
    print("Given ", size, "In")
    amount_out = amount_out_given_in(size, base_reserve_in, base_reserve_out)
    print("We get", amount_out, "out in ", loops, "loops")

    return base_reserve_in, base_reserve_out, amount_out, loops
        
    
def main():
    size = int(input("Which Size? In BTC \n"))
    
    slippage_bps = int(input("Which Slippage in BPS? \n"))

    calculate_liquidity_required(size, slippage_bps)

  
def report():
    data = []

    for slippage in SLIPPAGES:
       for size in SIZES:
          base_reserve_in, base_reserve_out, amount_out, loops = calculate_liquidity_required(
             size, slippage
          )
          data.append(
             {
              "slippage (BPS)": slippage,
              "size (BTC)": size,
              "base_reserve_in (BTC)": base_reserve_in,
              "base_reserve_out (ETH)": base_reserve_out,
              "amount_out (BTC)": amount_out,
              "loops": loops
             }
          )

    # build dataframe
    df = pd.DataFrame(data)
    # Dump result
    os.makedirs("logs/amm_leverage_math", exist_ok=True)
    df.to_csv(
        f"logs/amm_leverage_math/amm_leverage_math_results.csv"
    )
