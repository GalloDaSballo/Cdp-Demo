from random import random
import csv
import os
import time

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = 15, 30

"""
  Sim of Price Impact of an AMM
  To simulate Availability of Profitable Liquidations based on AMM Liquidity.
  We assume ETH -> eBTC -> ETH Pure Arb to be the only way to liquidate
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


## Assume we have a 10k eth deposit
AMT_ETH = 10_000
ETH_DECIMALS = 18
BTC_DECIMALS = 8
MAX_LTV = 8_500 ## 85% LTV
MAX_BPS = 10_000

MAX_LP_PERCENT = MAX_BPS

## At risk BTC -> Needs to be liquidated
## Available in AMM BTC -> Can be bought at price impact before thinking about taking debt
"""
  ETH FL -> Deposit -> eBTC -> Repay -> ETH * 1.3 -> Repay the FL
  Your profit = ETH in eBTC or eBTC you are left with
  NO

  100 to liquidate
  100 / LTV * MAX_BPS in borrows


  Some people could flashloan to take on the debt themselves, while liquidating
  Other MM would not want to engage with that, and would rather liquidate and make a arb ETH -> ETH
"""

MORE_RISK = False

def sim():
  AVG_LTV = random() * MAX_LTV

  LP_PERCENT = random() * MAX_LP_PERCENT
  MAX_RISK_PERCENT = random() * LP_PERCENT

  ## NOTE / TODO:
  ## We separate higher risk to zoom into insolvency where 1/1 of liquidity is available
  ## As this is more interesting for the Exponential AMM Math
  if MORE_RISK:
    ## Of the whole thing vs of the LP %
    MAX_RISK_PERCENT = random() * MAX_BPS

  
  
  ## Always greater than MAX_LTV
  ## But smaller than 100%
  ## At 100% + 1 we have no economic incentive to save
  AT_RISK_LTV = MAX_LTV + random() * (MAX_BPS - MAX_LTV)

  deposited_eth = AMT_ETH * 10 ** ETH_DECIMALS
  print("deposited_eth", deposited_eth)
  borrowed_btc = deposited_eth / (10 ** ETH_DECIMALS - BTC_DECIMALS) * AVG_LTV / MAX_BPS
  print("borrowed_btc", borrowed_btc)

  max_liquidatable = borrowed_btc * MAX_RISK_PERCENT / MAX_BPS

  print("max_liquidatable", max_liquidatable)
  print("as percent", MAX_RISK_PERCENT)

  ## TODO: Check if correct or if it's just floating math
  # assert MAX_RISK_PERCENT == max_liquidatable * MAX_BPS / borrowed_btc

  ## Assume 13 ETH = 1 BTC to KIS
  ## NOTE: Assume LP value is 1/1 which technically is naive, but for sim purposes should be sufficient
  price_ratio = 13

  btc_in_amm = LP_PERCENT * borrowed_btc / MAX_BPS
  print("btc_in_amm", btc_in_amm)
  eth_in_amm = btc_in_amm * price_ratio
  print("as_eth", eth_in_amm)

  reserve_btc = btc_in_amm
  reserve_eth = eth_in_amm

  print("price_given_in(1, reserve_btc, reserve_eth", price_given_in(1, reserve_eth, reserve_btc))
  initial_price = price_given_in(1, reserve_eth, reserve_btc)
  
  ## Price makes sense
  ## NOTE: I have times where I get a initial price of 152, etc..
  ## For this reason we let it revert as liquidity is so thin you get crazy values
  ## TODO: Decide if worth investigating for those edge case
  ##    Hunch is it's not worth it as they are not realistic / are too extreme (1 eth in liqudity)
  assert initial_price >= 12 and initial_price <= 15


  ## What is the maximum I'm willing to pay to get eBTC to liquidate to ETH, if debt is N and I get M out?

  """
    TODO: Simulate % insolvent
    Figure out % Profit
    Given that, figure out max price impact (Which is effectively the same as a reduction in profit as a %)
    Given that, figure out max purchaseable given the pool
    Given that buy max and liquidate max
    Then output those info
  """

  ## max_liquidatable is the percent we want to liquidate
  liquidatable_debt = max_liquidatable
  print("liquidatable_debt", liquidatable_debt)
  ## TODO: Check MATH
  liquidatable_collataeral = liquidatable_debt / price_ratio / AT_RISK_LTV * MAX_BPS
  print("liquidatable_collataeral", liquidatable_collataeral)

  ## Check if we can liquidate all before it being unprofitable

  ## MAX_BPS - AT_RISK_LTV is the BPS Profitability
  profitability_bps = MAX_BPS - AT_RISK_LTV
  print("profitability_bps", profitability_bps)

  ## Check current AMM Price * the delta above
  current_price = price_ratio

  ## Assume we want at least 1 BPS for profitability
  ## TODO: When adding fees, prob add here a opportunity cost / MEV cost of business
  max_price = current_price * (MAX_BPS + profitability_bps - 1) / MAX_BPS
  print("max_price", max_price)

  ## Check amount we can buy
  max_amount = max_in_before_price_limit(max_price, reserve_eth, reserve_btc)
  print("max_amount", max_amount)

  ## If we can buy all, then we good
  if(max_amount > liquidatable_debt):
    print("We can safely liquidate")
    return True
  else:
    ## Else liquidate only up to what's profitable
    print("")
    print("")
    print("----- We are capped -----")

    print("liquidatable_debt - max_amount", liquidatable_debt - max_amount)
    ## TODO: More math around how capped, and what's the risk

    as_percent = (liquidatable_debt - max_amount) / liquidatable_debt * 100
    print("as_percent we can only liquidate up to", as_percent)
    
    print("MAX_RISK_PERCENT / MAX_BPS * 100 was", MAX_RISK_PERCENT / MAX_BPS * 100)
    print("LP_PERCENT / MAX_BPS * 100 was", LP_PERCENT / MAX_BPS * 100)

    print("-----  -----")
    print("")
    print("")
    
    return False
  


  
RUNS = 10_000

def main():
  counter = 0
  exc = 0
  insolvent = 0
  for i in range(RUNS):
    try:
      if sim():
        print("")
        print("")
        print("")
        counter += 1
      else:
        insolvent += 1
    except:
      print("Something went wrong")
      exc += 1
  
  print("Can safely liquidate", counter, "out of ", RUNS)
  print("Exceptions (not necessarily insolvent)", exc)


if __name__ == '__main__':
  main()
  

