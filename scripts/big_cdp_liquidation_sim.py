from random import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from math import sqrt

from scripts.loggers.amm_price_impact_logger import AmmPriceImpactLogger, AmmPriceImpactEntry, AmmBruteForceLogger, AMMBruteForceEntry

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = 15, 30

"""
  FORK of AMM Price Impact Simplified

  The following sim aims to show:
  - A CDP of 50 - 99% size needing to get liquidated
  - In a scenario of 0 AMM Liquidity (Liquidator needs to take on the debt)
  - With TCR at 150% (slightly above Recovery Mode)
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

## TODO: Change to correct value
MINT_LTV = 7_500
MAX_BPS = 10_000
MAX_LIQUIDITY = 9_500 #95%

## TODO: Change back to 13
START_PRICE = 1 ## e.g. 13 eth to btc


AMT_ETH = 1000e18

# 70 BPS (roughly greater than fees)
## We set at 0 for now
MIN_PROFIT = 0
MAX_PROFIT = MAX_BPS - LTV


def main():
  ## TODO: Can add Liquidity to show what could be redeemed immediately
  RANGE_LIQUIDITY = range(0, 0)

  ## 1k ETH as base value
  TOTAL_ETH_COLL = 1000e18

  ## MAX LTV AT LTV means we're at the edge of Recovery Mode
  ## TODO: Prob need to change
  AVG_LTV = LTV
  price_ratio = START_PRICE

  ## Divide by 13 as it's 13 ETH per BTC
  TOTAL_BTC_DEBT = TOTAL_ETH_COLL / price_ratio * AVG_LTV / MAX_BPS
  print("TOTAL_BTC_DEBT", TOTAL_BTC_DEBT)

  ## TODO: COULD CHANGE IN THE FUTURE TO SHOW SMOOTHER LANDING
  liquidity = 0
  
  ## TODO: The above will not properly work as we have 0 liquidity
  ## Let's add the logic to perform a liquidation

  ## Profit Liquidity / Bounds
  lower_bound_profit = 0
  ## That's the max profit TODO: fees
  higher_bound_profit = MAX_BPS - LTV

  ## Between 50 and 99.999999999%
  liquidation_percent = random() * 5_000 + 5_000
  print("Assuming CDP Whale is", liquidation_percent, "percent of all debt")

  liquidation_debt_amount = TOTAL_BTC_DEBT * liquidation_percent / MAX_BPS
  ## TODO: Maybe wrong, maybe valid for now as we have same ratios everywhere
  ## Definitely wrong later as we have different % of debt
  liquidation_collateral_amount = TOTAL_ETH_COLL * liquidation_percent / MAX_BPS
  print("Puts the Debt to Liquidate at", liquidation_debt_amount)
  print("Which allows redemption of", liquidation_collateral_amount, "Collateral")

  ## TODO: TCR HIGHER
  TCR_HIGHER = TOTAL_BTC_DEBT * price_ratio / (TOTAL_ETH_COLL)
  print("TCR_HIGHER", TCR_HIGHER)

  ## TCR LOWER ## TODO: Is this correct?
  ## TODO: Whole math is off
  ## Rest of CDPs should be all solvent
  ## But the Big one should be insolvent, so this math is off
  price_worst_case = (price_ratio * (MAX_BPS + MAX_BPS - LTV) / MAX_BPS)
  TCR_LOWER = TOTAL_BTC_DEBT * price_worst_case / (TOTAL_ETH_COLL)
  print("TCR_LOWER", TCR_LOWER)

  ## Sanity check, we are not inventing debt
  assert liquidation_debt_amount < TOTAL_BTC_DEBT

  ## TODO: How do we figure out liquidation logic?

  collateral_for_liquidation = liquidation_debt_amount * price_ratio / MINT_LTV * MAX_BPS
  print("To Liquidate, we need", collateral_for_liquidation)

  ## Compute new TCR
  ## TCR if profit is 0, is basically critical
  ## TCR if profit is max, is basically in Recovery Mode

  ## Always the same
  ## Debt doesn't change because you're liquidating a CDP but creating the same amount in another
  debt_after_liq = TOTAL_BTC_DEBT

  ## TODO: 0% vs 20%
  ## Total - Sent to Liquidator + collateral used to create new cdp
  collateral_after_liq = TOTAL_ETH_COLL - liquidation_collateral_amount + collateral_for_liquidation

  ## See new Liquidation threshold
  ## NOTE: Should be known as it's LTV - MINT_LTV
  ## SO it's trivial
  TCR_HIGHER_AFTER_LIQ = debt_after_liq * price_ratio / (collateral_after_liq)
  TCR_LOWER_AFTER_LIQ = debt_after_liq * price_worst_case / (collateral_after_liq)

  print("TCR_HIGHER_AFTER_LIQ", TCR_HIGHER_AFTER_LIQ)
  print("TCR_LOWER_AFTER_LIQ", TCR_LOWER_AFTER_LIQ)
  

if __name__ == '__main__':
  main()


"""
  Specifically to check -> First insolvency at
  Relation between changes in these 3 variables
"""