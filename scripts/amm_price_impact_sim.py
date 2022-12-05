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

"""
  New math to test out
"""

def max_liquidatable(reserve_in, reserve_out, liquidation_premium_bps, ltv_bps, price_token_in):
  return reserve_out - (1 + liquidation_premium_bps / MAX_BPS) *  reserve_in * ltv_bps / MAX_BPS * price_token_in

def max_buyable_given_liquidatable(reserve_in, reserve_out, liquidation_premium_bps, ltv_bps, price_token_in):
  return (reserve_out) / ((1 + liquidation_premium_bps / MAX_BPS) * ltv_bps / MAX_BPS * price_token_in) - reserve_in

def profit_from_liquidation(reserve_in, reserve_out, ltv_bps, price_token_in, debt_to_liquidate):
  return (reserve_out - debt_to_liquidate) / (ltv_bps / MAX_BPS * price_token_in * reserve_in) - 1

## Assume we have a 10k eth deposit
AMT_ETH = 10_000
ETH_DECIMALS = 18
BTC_DECIMALS = 8

MAX_BPS = 10_000

SETTING_MAX_LTV = 8_500 ## 85% LTV
SETTING_MAX_LP_BPS = MAX_BPS

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


"""
  Logger Class
  TODO: Change to library
  
"""
class SimResult():
  def __init__(self, is_solvent, log_entry) -> None:
    self.is_solvent = is_solvent
    self.log_entry = log_entry

MORE_RISK = False

"""
  Bulk of the logic
"""


def sim(run, MAX_LTV, MAX_LP_BPS, LIQUIDATABLE_BPS, AT_RISK_LTV) -> SimResult:
  """
    Variables to fix / linearly test
    - MAX_LTV (5_000 <= MAX_LTV <= 9_998) // Between 50% and 9_998 LTV || 200% - 100.020004001% CR
    - MAX_LP_BPS (0 <= MAX_LP_BPS <= 10_000) Up to 100% Available in AMM
    - LIQUIDATABLE_BPS (with 0 < LIQUIDATABLE_BPS <= MAX_LP_BPS) Up to 100% of liquid to be liquidated

    TODO: 
    Move those 3 as variables
    Change the Loop to 3 var loop and increase by 1 bps
    Stop the loop once you get insolvency (????)

    Safe -> Risky

    MAX_LTV -> 5_000 -> 9_998
    MAX_LP_BPS -> 10_000 -> 0
    LIQUIDATABLE_BPS -> 0 -> MAX_LP_BPS
  """

  ## TODO: Do we need this?
  AVG_LTV = random() * MAX_LTV

  LP_BPS = MAX_LP_BPS
  LIQUIDATABLE_BPS = LIQUIDATABLE_BPS

  ## NOTE / TODO:
  ## We separate higher risk to zoom into insolvency where 1/1 of liquidity is available
  ## As this is more interesting for the Exponential AMM Math
  if MORE_RISK:
    ## Of the whole thing vs of the LP %
    LIQUIDATABLE_BPS = random() * MAX_BPS

  ## Always greater than MAX_LTV
  ## But smaller than 100%
  ## At 100% + 1 we have no economic incentive to save
  ## TODO: Do we need this? I Think we need to also pass this as this is the profitability %

  ## NOTE: No extra decimals cause Python handles them
  deposited_eth = AMT_ETH
  print("deposited_eth", deposited_eth)
  borrowed_btc = deposited_eth * AVG_LTV / MAX_BPS
  print("borrowed_btc", borrowed_btc)

  max_liquidatable = borrowed_btc * LIQUIDATABLE_BPS / MAX_BPS

  print("max_liquidatable", max_liquidatable)
  print("as percent", LIQUIDATABLE_BPS)

  ## TODO: Check if correct or if it's just floating math
  # assert LIQUIDATABLE_BPS == max_liquidatable * MAX_BPS / borrowed_btc

  ## Assume 13 ETH = 1 BTC to KIS
  ## NOTE: Assume LP value is 1/1 which technically is naive, but for sim purposes should be sufficient
  price_ratio = 13

  btc_in_amm = LP_BPS * borrowed_btc / MAX_BPS
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
  liquidatable_collateral = liquidatable_debt / price_ratio / AT_RISK_LTV * MAX_BPS
  print("liquidatable_collateral", liquidatable_collateral)

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


  ## TODO: Add Logging
  log_entry = AmmPriceImpactEntry(run, deposited_eth=deposited_eth, borrowed_btc=borrowed_btc, max_liquidatable=max_liquidatable, reserve_btc=reserve_btc, reserve_eth=reserve_eth, initial_price=initial_price, liquidatable_collateral=liquidatable_collateral, profitability_bps=profitability_bps, max_price=max_price, max_amount=max_amount)

  ## If we can buy all, then we good
  if(max_amount > liquidatable_debt):
    print("We can safely liquidate")
    return SimResult(is_solvent=True, log_entry=log_entry)
  else:
    ## Else liquidate only up to what's profitable
    print("")
    print("")
    print("----- We are capped -----")

    print("liquidatable_debt - max_amount", liquidatable_debt - max_amount)
    ## TODO: More math around how capped, and what's the risk

    as_percent = (max_amount) / liquidatable_debt * 100
    print("as_percent we can only liquidate up to", as_percent)
    
    print("LIQUIDATABLE_BPS / MAX_BPS * 100 was", LIQUIDATABLE_BPS / MAX_BPS * 100)
    print("LP_BPS / MAX_BPS * 100 was", LP_BPS / MAX_BPS * 100)

    print("-----  -----")
    print("")
    print("")
    
    return SimResult(is_solvent=False, log_entry=log_entry)
  
RUNS = 10_000
LOG = True

def random_run():
  counter = 0
  exc = 0
  insolvent = 0

  logger = AmmPriceImpactLogger()

  for i in range(RUNS):
    try:
      sim_result = sim(i)
      if sim_result.is_solvent:
        print("")
        print("")
        print("")
        counter += 1
      else:
        insolvent += 1
      logger.add_entry(sim_result.log_entry)
    except:
      print("Something went wrong")
      exc += 1
  
  print("Can safely liquidate", counter, "out of ", RUNS)
  print("Exceptions (not necessarily insolvent)", exc)
  print("Logging to CSV")
  if(LOG):
    logger.to_csv()

def main():
  counter = 0
  exc = 0
  insolvent = 0
  runs = 0

  logger = AmmBruteForceLogger()

  ## Must be non-zero as 0 liquidty means a revert
  RANGE_MAX_LP_BPS = reversed(range(100, 10_000, 100))
  
  max_ltv = SETTING_MAX_LTV

  ## NOTE: Effectively the profitability value
  AT_RISK_LTV_RANGE = range(SETTING_MAX_LTV + 1, MAX_BPS - 1, 500)
  ## NOTE: Quickly see LTV ranges
  # for x in AT_RISK_LTV_RANGE:
  #   print("x", x)
  # return 

  ## Each entry is a tuple of 3 values
  ## max_ltv, max_lp_bps, liquidatable_bps, at_risk_ltv
  combinations = []


  for max_lp_bps in RANGE_MAX_LP_BPS:
    RANGE_LIQUIDATABLE_BPS = (range(0, MAX_BPS, 100))
    for at_risk_ltv in  AT_RISK_LTV_RANGE:
      for liquidatable_bps in RANGE_LIQUIDATABLE_BPS:
        runs += 1
        try:
          sim_result = sim(runs, max_ltv, max_lp_bps, liquidatable_bps, at_risk_ltv)
          if sim_result.is_solvent:
            print("")
            print("")
            print("")
            counter += 1
          else:
            insolvent += 1
            log_entry = AMMBruteForceEntry(
              runs,
              max_ltv, max_lp_bps, liquidatable_bps, at_risk_ltv
            )
            logger.add_entry(log_entry)
            break ## Go to next range
        except:
          print("Something went wrong")
          exc += 1
    

  
  print("Can safely liquidate", counter, "out of ", runs)
  print("Exceptions (not necessarily insolvent)", exc)
  print("Logging to CSV")
  if(LOG):
    logger.to_csv()
  
  print("combinations", combinations)

if __name__ == '__main__':
  main()


"""
  Specifically to check -> First insolvency at
  Relation between changes in these 3 variables
"""