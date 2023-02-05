from random import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from math import sqrt

from scripts.loggers.amm_price_impact_logger import AmmPriceImpactLogger, AmmPriceImpactEntry, AmmBruteForceLogger, AMMBruteForceEntry

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = 15, 30

"""
  Effectively prove that Partial Liq with min(105, ICR) will increase ICR
  However, some increases can be very marginal

  In my opinion this should be looked at deeper to see if the mechanism creates scenarios where the last piece of CDP
  Where pay will be ICR, will only pay that
"""

MAX_LTV = 8_500 ## 85% / 117.647058824% CR

## TODO: Change to correct value
MINT_LTV = 7_500 ## 133.333333333% CR
MIN_LTV = 1_000 ## Minimum Leverage else sim is boring
MAX_BPS = 10_000
MAX_LIQUIDITY = 9_500 #95%

MIN_ICR = 1 / 8_500 * MAX_BPS * 100

## TODO: Change back to 13
START_PRICE = 1 ## e.g. 13 eth to btc


AMT_ETH = 1000e18

# 70 BPS (roughly greater than fees)
## We set at 0 for now
MIN_PROFIT = 0
MAX_PROFIT = MAX_BPS - MAX_LTV

def perform_partial_liq(total_coll, total_debt, price, repaid_debt):
  new_debt = total_debt - repaid_debt
  ICR = price * total_coll / total_debt * 100
  bonus_coll = 0
  if (ICR > 105):
    print("With bonus")
    bonus_coll = repaid_debt * 1.05 / price
  else:
    bonus_coll = repaid_debt * ICR / 100 / price
  
  new_coll = total_coll - bonus_coll
  new_icr = price * new_coll / new_debt * 100
  return [
    new_coll,
    new_debt,
    bonus_coll,
    new_icr
  ]


def main():
  
  ## 1k ETH as base value
  TOTAL_ETH_COLL = 1000e18

  ## MAX MAX_LTV AT MAX_LTV means we're at the edge of Recovery Mode
  ## TODO: Prob need to change

  ## Liquidatable TVL for our sim
  LTV = 8_500
  
  price_ratio = START_PRICE

  ## Divide by 13 as it's 13 ETH per BTC
  TOTAL_BTC_DEBT = TOTAL_ETH_COLL / price_ratio * LTV / MAX_BPS

  initial_ICR = price_ratio * TOTAL_ETH_COLL / TOTAL_BTC_DEBT * 100
  print("CURRENT ICR", initial_ICR)

  DEBT_REPAY = random() * TOTAL_BTC_DEBT

  print("Initial Collateral", TOTAL_ETH_COLL)
  print("Initial_Debt", TOTAL_BTC_DEBT)

  print("DEBT_REPAY", DEBT_REPAY)
  print("DEBT_REPAY as percent", DEBT_REPAY / TOTAL_BTC_DEBT * 100)

  [new_coll, new_debt, bonus_coll, new_icr] = perform_partial_liq(TOTAL_ETH_COLL, TOTAL_BTC_DEBT, price_ratio, DEBT_REPAY)

  print("NEW ICR", new_icr)
  print("new_coll", new_coll)
  print("new_debt", new_debt)
  print("bonus_coll", bonus_coll)

  print("bonus_coll as percent", bonus_coll / TOTAL_ETH_COLL * 100)
  print("new_coll as percent", new_coll / TOTAL_ETH_COLL * 100)



