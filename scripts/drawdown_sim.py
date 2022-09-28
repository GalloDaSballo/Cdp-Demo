from random import random

"""
  Max Drawdown sim for Single Asset CDP based Synthetic Tokens (Stables or w/e)

  The goal of the sim is to figure out how much volatility is necessary for the loss of value to warrant not repaying the debt
  And for liquidator to be unprofitable in covering debt
"""
MAX_BPS = 10_000

MAX_LTV = 15_000 ## 150%
LIQUIDATION_THRESHOLD = 11_000 ## 110% If LTV goes below that we can liquidate

INSOLVENCY_THRESHOLD = MAX_BPS ## 1 point below this means we're under collateralized = we failed

GIVE_IN = 100_000 ## Assume w/e

DRAWDOWN_MAX = 9_999 ## Can only go down to 100%

def sim(drawdown_value):
  print("Drawdown value", drawdown_value)
  ## TODO: Add random but it's fine for now
  given_in = GIVE_IN
  max_ltv = given_in / MAX_LTV * MAX_BPS

  drawdown = given_in * drawdown_value / MAX_BPS

  new_in = given_in - drawdown
  new_max_ltv = new_in / MAX_LTV * MAX_BPS

  ## Hole in the sheet
  outstanding_ltv = max_ltv - new_max_ltv

  print("New Hole", outstanding_ltv)

  new_ratio = new_in / max_ltv * MAX_BPS
  print("New Collateralization Ratio", new_ratio)

  return new_ratio < INSOLVENCY_THRESHOLD





def main():
  for x in range(0, DRAWDOWN_MAX, 1):
    if(x == 0):
      continue
    
    res = sim(x)
    if(res):
      print("First Insolvency at", x)
      return 