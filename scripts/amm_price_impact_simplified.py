from random import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from math import sqrt

from scripts.loggers.amm_price_impact_logger import AmmPriceImpactLogger, AmmPriceImpactEntry, AmmBruteForceLogger, AMMBruteForceEntry

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = 15, 30

"""
  Basic sim, that given a target LTV shows the maximum amounts liquidatable
  Is cognizant of price impact on UniV2 Like AMM
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

def max_in_before_price_limit_sqrt(price_limit, reserve_in, reserve_out):
  return sqrt(reserve_out * reserve_in * price_limit) - reserve_in



LTV = 8_500 ## 85%
MAX_BPS = 10_000
MAX_LIQUIDITY = 9_500 #95%

START_PRICE = 13 ## e.g. 13 eth to btc


AMT_ETH = 1000e18

# 70 BPS (roughly greater than fees)
MIN_PROFIT = 70
MAX_PROFIT = MAX_BPS - LTV


def main():
  ## From 5% to 95%
  RANGE_LIQUIDITY = reversed(range(500, MAX_LIQUIDITY, 500))

  ## 1k ETH as base value
  ETH_BASE = 1000e18

  ## We need this to start the sim, this value is necessary for relative math
  AVG_LTV = random() * LTV

  BTC_BASE = ETH_BASE * AVG_LTV / MAX_BPS

  price_ratio = START_PRICE

  ## NOTE: No extra decimals cause Python handles them
  DEBUG = False

  for liquidity in RANGE_LIQUIDITY:
    print("")
    print("")
    print("")

    x = BTC_BASE * liquidity / MAX_BPS
    y = x / price_ratio ## 13 times more ETH than BTC

    print("### === CASE LIQUIDITY BPS === ###", liquidity)
    print("Given premium BPS betweem", MIN_PROFIT, MAX_PROFIT)

    spot_price = price_given_in(1, x, y)
    print("spot_price", spot_price)

    ### === BEST CASE SCENARIO === ###
    print("")
    print("### === BEST CASE SCENARIO === ###")
    max_price = spot_price * (MAX_BPS + MAX_PROFIT) / MAX_BPS
    print("max_price", max_price)

    max_eth_before_insolvent = max_in_before_price_limit(max_price, x, y)
    max_eth_before_insolvent_sqrt = max_in_before_price_limit_sqrt(max_price, x, y)
    max_btc_liquidatable = amount_out_given_in(max_eth_before_insolvent, x, y)
    max_btc_liquidatable_sqrt = amount_out_given_in(max_eth_before_insolvent_sqrt, x, y)

    print("You can liquidate at most", max_btc_liquidatable)
    print("As portion of Total Supply BPS", max_btc_liquidatable / BTC_BASE * MAX_BPS)
    print("As portion of Total Liquidity BPS", max_btc_liquidatable / x * MAX_BPS)

    print("")
    print("SQRT FORMULA")
    print("You can liquidate at most", max_btc_liquidatable_sqrt)
    print("As portion of Total Supply BPS", max_btc_liquidatable_sqrt / BTC_BASE * MAX_BPS)
    print("As portion of Total Liquidity BPS", max_btc_liquidatable_sqrt / x * MAX_BPS)

    if DEBUG:
      print("")
      print("")
      print("DEBUG")
      print("price_given_in(normal)", price_given_in(max_eth_before_insolvent, x, y))
      print("price_given_in(sqrt)", price_given_in(max_eth_before_insolvent_sqrt, x, y))

      print("")
      print("")
      print("")


    ### === WORST CASE SCENARIO === ###
    print("")
    print("### === WORST CASE SCENARIO === ###")
    min_price = spot_price * (MAX_BPS + MIN_PROFIT) / MAX_BPS
    print("min_price", min_price)
    
    min_max_eth_before_insolvent = max_in_before_price_limit(min_price, x, y)
    min_max_eth_before_insolvent_sqrt = max_in_before_price_limit_sqrt(min_price, x, y)
    min_max_btc_liquidatable = amount_out_given_in(min_max_eth_before_insolvent, x, y)
    min_max_btc_liquidatable_sqrt = amount_out_given_in(min_max_eth_before_insolvent_sqrt, x, y)


    print("You can liquidate at worst", min_max_btc_liquidatable)
    print("As portion of Total Supply BPS", min_max_btc_liquidatable / BTC_BASE * MAX_BPS)
    print("As portion of Total Liquidity BPS", min_max_btc_liquidatable / x * MAX_BPS)

    print("")
    print("SQRT FORMULA")
    print("You can liquidate at worst", min_max_btc_liquidatable_sqrt)
    print("As portion of Total Supply BPS", min_max_btc_liquidatable_sqrt / BTC_BASE * MAX_BPS)
    print("As portion of Total Liquidity BPS", min_max_btc_liquidatable_sqrt / x * MAX_BPS)


    ### === RECOVERY MODE === ###
    print("")
    print("### === RECOVERY MODE === ###")
    RECOVERY_MODE_BUFFER = 5_000
    max_price_recovery = spot_price * (MAX_BPS + MAX_PROFIT + RECOVERY_MODE_BUFFER) / MAX_BPS
    print("max_price_recovery", max_price_recovery)

    recovery_max_eth_before_insolvent = max_in_before_price_limit(max_price_recovery, x, y)
    recovery_max_eth_before_insolvent_sqrt = max_in_before_price_limit_sqrt(max_price_recovery, x, y)
    recovery_max_btc_liquidatable = amount_out_given_in(recovery_max_eth_before_insolvent, x, y)
    recovery_max_btc_liquidatable_sqrt = amount_out_given_in(recovery_max_eth_before_insolvent_sqrt, x, y)

    print("You can liquidate at most", recovery_max_btc_liquidatable)
    print("As portion of Total Supply BPS", recovery_max_btc_liquidatable / BTC_BASE * MAX_BPS)
    print("As portion of Total Liquidity BPS", recovery_max_btc_liquidatable / x * MAX_BPS)

    print("")
    print("SQRT FORMULA")
    print("You can liquidate at most", recovery_max_btc_liquidatable_sqrt)
    print("As portion of Total Supply BPS", recovery_max_btc_liquidatable_sqrt / BTC_BASE * MAX_BPS)
    print("As portion of Total Liquidity BPS", recovery_max_btc_liquidatable_sqrt / x * MAX_BPS)


  

if __name__ == '__main__':
  main()


"""
  Specifically to check -> First insolvency at
  Relation between changes in these 3 variables
"""