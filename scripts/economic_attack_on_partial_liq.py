from random import random

import matplotlib.pyplot as plt

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
START_PRICE = 13 ## e.g. 13 eth to btc


AMT_ETH = 1000e18

# 70 BPS (roughly greater than fees)
## We set at 0 for now
MIN_PROFIT = 0
MAX_PROFIT = MAX_BPS - MAX_LTV

def perform_partial_liq(total_coll, total_debt, price, repaid_debt):
  new_debt = total_debt - repaid_debt
  ICR = get_icr(total_coll, total_debt, price)
  bonus_coll = 0
  if (ICR > 105):
    print("With bonus")
    bonus_coll = repaid_debt * 1.05 / price
  else:
    bonus_coll = repaid_debt * ICR / 100 / price
  
  new_coll = total_coll - bonus_coll
  if(new_debt == 0):
    new_icr = 999999999
  else:
    new_icr = get_icr(new_coll, new_debt, price)
  return [
    new_coll,
    new_debt,
    bonus_coll,
    new_icr
  ]


def get_icr(coll, debt, price):
  return coll / debt / price * 100

def main():
  
  ## 1k ETH as base value
  TOTAL_ETH_COLL = 1000e18

  ## MAX MAX_LTV AT MAX_LTV means we're at the edge of Recovery Mode
  ## TODO: Prob need to change

  ## Liquidatable TVL for our sim
  ## NOTE: Weird syntax cause we care about % in bps
  ## RANGE from 85 to 99.99
  ## Price drop from 0 to 5% per tick
  LTVS = range(85_00, 100_00, 100)

  PRICE_DRAWDOWNS = range(100, 106, 1)

  for ltv in LTVS:
    for price_drawdown in PRICE_DRAWDOWNS:

      print("New Sim with LTV", ltv)
      print("And Price Drawdown per Loop of", price_drawdown)

      price_ratio = START_PRICE

      ## Divide by 13 as it's 13 ETH per BTC
      TOTAL_BTC_DEBT = TOTAL_ETH_COLL / price_ratio * ltv / MAX_BPS

      initial_ICR = get_icr(TOTAL_ETH_COLL, TOTAL_BTC_DEBT, price_ratio)
      print("CURRENT ICR", initial_ICR)

      total_coll = TOTAL_ETH_COLL
      total_debt = TOTAL_BTC_DEBT
      DEBT_REPAY = random() * total_debt
      new_price = price_ratio

      while DEBT_REPAY != 0:

        ## Check to stop as we cannot liquidate
        current_icr = get_icr(total_coll, total_debt, new_price)
        if(current_icr > 120):
          print("We cannot liquidate anymore")
          break

        print("Initial Collateral", total_coll)
        print("Initial_Debt", total_debt)

        print("DEBT_REPAY", DEBT_REPAY)
        print("DEBT_REPAY as percent", DEBT_REPAY / total_coll * 100)
        

      
        [new_coll, new_debt, bonus_coll, new_icr] = perform_partial_liq(total_coll, total_debt, new_price, DEBT_REPAY)

        print("NEW ICR", new_icr)
        print("new_coll", new_coll)
        print("new_debt", new_debt)
        print("bonus_coll", bonus_coll)
        print("price", new_price)

        print("bonus_coll as percent", bonus_coll / total_coll * 100)
        print("new_coll as percent of old", new_coll / total_coll * 100)


        liquidator_profit = bonus_coll * new_price / DEBT_REPAY
        print("liquidator_profit", liquidator_profit)

        ## Update for next iteration
        total_debt = new_debt
        total_coll = new_coll

        if (total_debt < 1e18):
          DEBT_REPAY = total_debt
        else:
          DEBT_REPAY = random() * total_debt
          ## HUNCH: Debt Repay to permanently leave ICR at current value but extract the bonus
          ## Can we achieve this?


        # Last thing: Update price to assume downward spiral
        ## NOTE: Drawdown in 100s
        temp_new_price = new_price / price_drawdown * 100
        if(total_debt > 0 and get_icr(total_coll, total_debt, temp_new_price) > 100):
          new_price = temp_new_price







