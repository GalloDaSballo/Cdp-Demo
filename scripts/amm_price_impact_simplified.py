from random import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from scripts.loggers.amm_price_impact_logger import AmmPriceImpactLogger, AmmPriceImpactEntry, AmmBruteForceLogger, AMMBruteForceEntry

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = 15, 30

"""
  Sim of Price Impact of an AMM
  To simulate Availability of Profitable Liquidations based on AMM Liquidity.
  We assume ETH -> eBTC -> ETH Pure Arb to be the only way to liquidate

  TODO: Find relations with this chart
  https://www.desmos.com/calculator/jfctve72w9
  
"""

def price_given_in(amount_in, reserve_in, reserve_out):
  out = amount_out_given_in(amount_in, reserve_in, reserve_out)
  return amount_in / out

def amount_out_given_in(amount_in, reserve_in, reserve_out):
  amount_out = reserve_out * amount_in / (reserve_in + amount_in)
  return amount_out


"""
  Derived by the above
"""
def amount_in_give_out(amount_out, reserve_in, reserve_out):
  amount_in = reserve_in * amount_out / (reserve_out - amount_out)
  return amount_in

def max_in_before_price_limit(price_limit, reserve_in, reserve_out):
  return reserve_out * price_limit - reserve_in



LTV = 8_500 ## 85%
MAX_BPS = 10_000
MAX_LIQUIDITY = 5_000 #50%

START_PRICE = 13 ## e.g. 13 eth to btc


AMT_ETH = 1000e18

def main():
  ## From 50% to 1%
  RANGE_LIQUIDITY = reversed(range(100, MAX_LIQUIDITY, 100))

  ## From 15% to 0%
  PROFITABILITY_RANGE = reversed(range(100, MAX_BPS - LTV, 100))

  ## 1k ETH as base value
  ETH_BASE = 1000e18

  ## We need this to start the sim, this value is necessary for relative math
  AVG_LTV = random() * LTV

  BTC_BASE = ETH_BASE * AVG_LTV / MAX_BPS

  price_ratio = 13

  ## NOTE: No extra decimals cause Python handles them

  for liquidity in RANGE_LIQUIDITY:
    for premium in PROFITABILITY_RANGE:
      x = BTC_BASE * liquidity / MAX_BPS
      y = x * price_ratio ## 13 times more ETH than BTC

      spot_price = price_given_in(1, x, y)
      print("spot_price", spot_price)
      max_price = spot_price * (MAX_BPS + premium) / MAX_BPS
      print("max_price", max_price)

      max_eth_before_insolvent = max_in_before_price_limit(max_price, x, y)
      btc_liquidatable = amount_out_given_in(max_eth_before_insolvent, x, y)

      print("You can liquidate", btc_liquidatable)
      print("As portion of Total Supply BPS", btc_liquidatable / BTC_BASE * MAX_BPS)
      print("As portion of Total Liquidity BPS", btc_liquidatable / x * MAX_BPS)


  

if __name__ == '__main__':
  main()


"""
  Specifically to check -> First insolvency at
  Relation between changes in these 3 variables
"""