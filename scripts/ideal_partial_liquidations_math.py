from random import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from math import sqrt

from scripts.loggers.amm_price_impact_logger import AmmPriceImpactLogger, AmmPriceImpactEntry, AmmBruteForceLogger, AMMBruteForceEntry

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = 15, 30

"""
  Simulation around the ideal partial liquidation behavior

  The following sim aims to show:
  - A CDP of 50 - 99% size needing to get liquidated
  - In a scenario of 0 AMM Liquidity (Liquidator needs to take on the debt)
  - With TCR at 150% (slightly above Recovery Mode)

  Minimal Liquidation Size (MLS)
  Partial Liquidations from MLS to 100%
  Modelling of fees and profit profile based on the value
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


def main():
  ## TODO: RANGE FOR INSOLVENCY

  ## 1k ETH as base value
  TOTAL_ETH_COLL = 1000e18

  ## MAX MAX_LTV AT MAX_LTV means we're at the edge of Recovery Mode
  ## TODO: Prob need to change

  ## Add 10% just in case
  AVG_LTV = random() * MINT_LTV + MIN_LTV
  ## Take it back if too much
  if(AVG_LTV > MINT_LTV):
    AVG_LTV -= MIN_LTV
  
  price_ratio = START_PRICE

  ## Divide by 13 as it's 13 ETH per BTC
  TOTAL_BTC_DEBT = TOTAL_ETH_COLL / price_ratio * AVG_LTV / MAX_BPS
  print("TOTAL_BTC_DEBT", TOTAL_BTC_DEBT)

  ## Between 50 and 99.999999999%
  liquidation_percent = random() * 5_000 + 5_000
  print("Assuming CDP Whale is", liquidation_percent / MAX_BPS * 100, "percent of all debt")

  liquidation_collateral_amount = TOTAL_ETH_COLL * liquidation_percent / MAX_BPS
  
  ## TODO: Add Discrete Liquidation amounts
  ## ASSUME 1% Insolvency
  ## TODO: Convert 100 as param to make sim generalizeable
  INSOLVENT_LTV = MAX_LTV + 100 ## 1% over Max

  liquidation_debt_amount = liquidation_collateral_amount / price_ratio * (INSOLVENT_LTV) / MAX_BPS
  print("Puts the Debt to Liquidate at", liquidation_debt_amount)
  print("Which allows redemption of", liquidation_collateral_amount, "Collateral")

  ## SANITY CHECKS
  ## RATIO BETWEEN DEBT AND COLL IS GREATER MAX
  ICR = liquidation_collateral_amount / price_ratio / liquidation_debt_amount * 100
  print("ICR", ICR)
  print("MIN_ICR", MIN_ICR)
  assert ICR < MIN_ICR

  ## WHILE CDP IS INSOLVENT, SYSTEM IS FINE
  INITIAL_SYSTEM_CR = TOTAL_ETH_COLL / price_ratio / TOTAL_BTC_DEBT * 100
  assert INITIAL_SYSTEM_CR > MIN_ICR

  ## Liquidate CDP
  ## Compute new values as well as profit for liquidation
  debt_to_repay = liquidation_debt_amount
  collateral_received = liquidation_collateral_amount

  collateral_necessary = debt_to_repay / price_ratio / MIN_LTV * MAX_BPS
  print("collateral_necessary", collateral_necessary)

  system_coll_after_liq = TOTAL_ETH_COLL - collateral_received + collateral_necessary
  system_debt_after_liq = TOTAL_BTC_DEBT ## NOTE: Unchanged, the liquidator took the debt as their own
  print("system_coll_after_liq", system_coll_after_liq)
  print("system_debt_after_liq", system_debt_after_liq)


  SYSTEM_CR_AFTER_LIQ = system_coll_after_liq / price_ratio / system_debt_after_liq * 100
  print("SYSTEM_CR_AFTER_LIQ", SYSTEM_CR_AFTER_LIQ)

  assert SYSTEM_CR_AFTER_LIQ > INITIAL_SYSTEM_CR

  roi = collateral_received / (debt_to_repay * price_ratio) * 100
  print("roi for total liq", roi)

  profit = collateral_received - (debt_to_repay * price_ratio)
  print("profit for total liq")

  ## Partial Liquidations
  ## TODO: Generalize into Range + Loops

  ## Partial Liquidation Base Case - We repay the debt and get nothing
  ## MIN Debt to repay, that would bring the CDP to MIN_ICR
  maximum_debt_for_liquidatable_collateral = liquidation_collateral_amount / price_ratio / MIN_ICR * 100
  assert maximum_debt_for_liquidatable_collateral < liquidation_debt_amount

  min_partial_debt_to_liquidate_healthily = liquidation_debt_amount - maximum_debt_for_liquidatable_collateral
  print("If we repay", min_partial_debt_to_liquidate_healthily, "we will get a healthy CDP")

  ## SANITY CHECK FOR HEALTHY CR AFTER MIN DEBT
  new_debt_after_min_repay = maximum_debt_for_liquidatable_collateral
  new_coll_after_min_repay = liquidation_collateral_amount

  ICR_AFTER_MIN_REPAY = new_coll_after_min_repay / price_ratio / new_debt_after_min_repay * 100
  print("ICR_AFTER_MIN_REPAY", ICR_AFTER_MIN_REPAY)
  assert ICR_AFTER_MIN_REPAY >= MIN_ICR

  print("This is the base case, our profit is 0")
  print("Our price paid for out is infinite")
  
  ## Basically same as Full Liq, so we will skip
  max_partial = liquidation_debt_amount
  min_partial = min_partial_debt_to_liquidate_healthily

  delta = max_partial - min_partial

  ## RANGES for Auto
  ## [25, 50, 75]
  partial_liq_ranges = range(25, 100, 25)

  for percent_partial_liq in partial_liq_ranges:
    debt_to_repay = min_partial + (delta * percent_partial_liq / 100)
    debt_left_to_cdp = liquidation_debt_amount - debt_to_repay
    print(percent_partial_liq, "% liquidation")
    
    collateral_left_to_cdp = debt_left_to_cdp * price_ratio * MIN_ICR / 100
    collateral_received = liquidation_collateral_amount - collateral_left_to_cdp
    print("debt_to_repay", debt_to_repay)
    print("collateral_left_to_cdp", collateral_left_to_cdp)
    print("collateral_received", collateral_received)

    ICR_AFTER_PARTIAL_REPAY = collateral_left_to_cdp / price_ratio / debt_left_to_cdp * 100
    print("ICR_AFTER_PARTIAL_REPAY", ICR_AFTER_PARTIAL_REPAY)
    
    ## Is strictly greater because it relieves more than min repay
    assert ICR_AFTER_PARTIAL_REPAY >= MIN_ICR

    print("ASSUME WE MAGICALLY GOT THE STUFF")
    system_coll_after_partial_liq = TOTAL_ETH_COLL - collateral_received
    system_debt_after_partial_liq = TOTAL_BTC_DEBT - debt_to_repay

    SYSTEM_CR_AFTER_LIQ = system_coll_after_partial_liq / price_ratio / system_debt_after_partial_liq * 100
    print("SYSTEM_CR_AFTER_LIQ", SYSTEM_CR_AFTER_LIQ)

    ## It relieved some risk
    assert SYSTEM_CR_AFTER_LIQ > INITIAL_SYSTEM_CR

    ## ROI and PROFIT
    roi = collateral_received / (debt_to_repay * price_ratio) * 100
    print("roi", roi)

    profit = collateral_received - (debt_to_repay * price_ratio)
    print("profit in ETH", profit)


  

if __name__ == '__main__':
  main()