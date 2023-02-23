from random import random
from scripts.logger import (GenericEntry, GenericLogger)

"""
  Simulation around insolvency and risks involved with it

  Assumptions:
  - Redemptions and Partial Liquidations can be performed from 100 <= ICR < MCR
  - They could be performed after, but would be unprofitable
  - If ICR < 100 we need to redistribute the insolvency to avoid further bad debt from the abandoned CDP
    - TODO: Challenge the above, find scenarios where leaving as is can be better
      - It is better when the price of coll does increase after a while
          In those cases it would have been better to wait
          TODO: This can be backtested

  Redistribution of insolvency:
  - For each CDP, in proportion to debt and collateral (TODO: Should it be only based on 1?)
  - Redistribute  the collateral and debt

  Properties of Redistribution:
  - System is not impacted
  - TCR (VERY) slightly improved, as we can offer the Gas Stipend as Collateral as well
  - Overall Neutral

  Gotcha from Redistribution:
  - TCR was: Bad CDP CR + (Good CDPs)

  - Will now be: No CDP CR + (Good CDPs - Bad CDP CR)
    Meaning it will cause a loss to all CDPs (based on rule above)
    GOTCHA: Some CDPs may become Liquidatable or even in BAD DEBT because of it.

    TODO: Math related to impact of redistribution, specifically in the edge case of cascade liquidations

  
  ## Cases
  - Rest of system is above MCR
  - Rest of system is below MCR -> Goes below
  - Rest of system is below CCR


  ### COUNTER POINT ###
  1) re the first TODO, it is very easy to find scenarios where delay and pray strategy over performs instant liquidation/redestribution. 
  the question is what it the meaning of that? even if it works better on average. can expand the discussion on that if you want.
  
  2) re gas stipend, wouldn't it be used for the guy who invokes the redistribution? 
  btw, more general question is how the gas stipend works with partial liquidations. maybe it should be given to users only if the liquidation bonus is absolute values is small.
  
  3) in redistribution it makes sense to distribute the position according to user's debt, not collateral. 
  in general you don't want to penalise users with big collaterals.
  
  4) re liquidation cascades, should also think a bit to see if there is a potential attack vector here, 
  where user intentionally get liquidated to profit from other trove(s) liquidation(s). on first look it does not sound easy

  ===================================================================

  I do want to propose an alternative/adjustment: let troves be liquidated also when ICR < 100. With fixed liquidation premium. eventually trove with ICR < 100 will end up with 0 collateral and X debt. at this point, redestribute X among all other troves.
  The rationale is that if $100m liquidation ends up with only $500k bad debt, then it is less aggressive for other users if you only distribute $500k among all of them, and not the entire $100m.

  -> X% at which you have 0 coll
  -> That means you are now going to get Y% extra debt without any useful coll
"""

## Fixed % means that there is a specific % at which we already lock in bad debt
## Floating premium means that there is no % at which we lock bad debt, 
# but there is a % at which liquidation calls are unprofitable

## 1 / 13 TODO
PRICE = 1

def get_icr(coll, debt, price):
  return price * coll / debt * 100

def get_debt_value(price, debt):
  return debt / price

def get_coll_value(price, coll):
  return price * coll

def simulate_direct_absorption(start_coll, start_debt, coll_to_distribute, debt_to_distribute):
  ## Verify we're distributing an underwater position
  debt_value = get_debt_value(PRICE, debt_to_distribute)
  print("debt_value", debt_value)
  coll_value = get_coll_value(PRICE, coll_to_distribute)
  print("coll_value", coll_value)
  assert debt_value >= coll_value

  ## Current CR
  GCR = get_icr(start_coll, start_debt, PRICE)


  ## New CR
  new_coll = start_coll + coll_to_distribute
  new_debt = start_debt + debt_to_distribute
  NEW_CR = get_icr(new_coll, new_debt, PRICE)
  print("NEW_CR", NEW_CR)

  ## Because it's underwater, we know it will drag the CR down
  assert NEW_CR < GCR

  return NEW_CR


## 10% premium
LIQ_PREMIUM = 500

def simulate_direct_absorption_with_fixed_premium(start_coll, start_debt, coll_to_distribute, debt_to_distribute, liq_premium):
  underwater_coll_after_premium = 0 ## We sell all
  underwater_debt_removed = debt_to_distribute * MAX_BPS / (MAX_BPS + liq_premium)
  underwater_debt_after_premium = debt_to_distribute - underwater_debt_removed

  print("underwater_debt_after_premium", underwater_debt_after_premium)

  new_coll = start_coll + underwater_coll_after_premium
  new_debt = start_debt + underwater_debt_after_premium

  NEW_CR = get_icr(new_coll, new_debt, PRICE)
  print("NEW_CR_WITH_ABSORPTION", NEW_CR)

  return NEW_CR


## TODO: What do?
LTV = 7_500
MAX_BPS = 10_000
PERCENT_INSOLVENT = 1_000 ## 10%
"""
  Invariants / X values
  - Price
  - LTV


  Variables
  - LIQ_PREMIUM -> Smaller = Better CR after (but more risk of unprofitable operation for liquidator)
  - Percent Insolvent - (This may be a linear var, so not too interesting)
  - Range for How Deeply Insolvent
"""

def main():
  PERCENTS_INSOLVENT = range(100, 11_00, 100)
  PREMIUMS = range(100, 1100, 100)

  logger = GenericLogger("cascade", ["gcr_start" ,"With no partial", "With partial", "% Insolvent", "Liq Premium"])

  for insolvent_percent in PERCENTS_INSOLVENT:
    for premium in PREMIUMS:
      [gcr_start, gcr_base, gcr_premium] = iteration(insolvent_percent, premium)
      assert gcr_base <= gcr_premium

      entry = GenericEntry([gcr_start, gcr_base, gcr_premium, insolvent_percent, premium])
      logger.add_entry(entry)
  
  logger.to_csv()
  


def iteration(percent_insolvent, liq_premium):
  ## 1k ETH as base value
  TOTAL_ETH_COLL = 1000e18
  TOTAL_BTC_DEBT = TOTAL_ETH_COLL * PRICE * LTV / MAX_BPS

  ## Insolvency values
  coll_to_liquidate = TOTAL_ETH_COLL * percent_insolvent / MAX_BPS
  print("coll_to_liquidate", coll_to_liquidate)
  print(coll_to_liquidate * PRICE)

  ## 1 to 1 so we assume we're in bad debt in the best case
  ## TODO: Ranges for bad debt values
  debt_to_liquidate = coll_to_liquidate / PRICE
  print("debt_to_liquidate", debt_to_liquidate)

  ## Current CR
  gcr_start = get_icr(TOTAL_ETH_COLL, TOTAL_BTC_DEBT, PRICE)
  print("gcr_start", gcr_start)

  gcr_after_direct = simulate_direct_absorption(TOTAL_ETH_COLL, TOTAL_BTC_DEBT, coll_to_liquidate, debt_to_liquidate)
  gcr_after_premium_direct = simulate_direct_absorption_with_fixed_premium(TOTAL_ETH_COLL, TOTAL_BTC_DEBT, coll_to_liquidate, debt_to_liquidate, liq_premium)

  return [gcr_start, gcr_after_direct, gcr_after_premium_direct]