"""
  Sim RE: Fees and Arbitrage

  - Minting Fee (Flat Fee)
  - Liquidation Fee (% Fee)

  - Risk % -> Indicator of how risky the trove will got

  - Max LTV -> Remember that from LTV, we get MAX_DRAWDOWN = 10_000 - MAX_LTV

  ## AMM (Generalized)
  - Swap Fee (Cost of making a swap, BPS)
  - Delta Price (Delta vs the Real Price, BPS, can be negative)

  ## NOT SURE:
  - Redemption Fee
"""
from random import random

MAX_BPS = 10_000

MAX_MINT_FEE = 200 ## 2%
MAX_LIQ_FEE = 1_000 ## 10%

MAX_AMM_FEE = 300 ## 3%, avg AMM is 30 BPS

MAX_EXTRA_LEVERAGE = 1_000 ## 10% extra borrowing when already at target LTV if randomness check passes

## 1 eth, 1200 usd
INITIA_PRICE = 1200 ## TODO: ADD Dynamic Price

## 1k steps before we end
MAX_STEPS = 1_000

## 1k eth
MAX_INITIAL_COLLAT = 1_000

def main():
  ## Maximum Collateral Ratio
  MAX_LTV = random() * MAX_BPS

  ## How risk the trove will get, MAX_BPS = Full send, 0 = We do not even mint
  RISK_PERCENT = random() * MAX_BPS

  MINTING_FEE = random() * MAX_MINT_FEE
  LIQ_FEE = random() * MAX_LIQ_FEE

  AMM_FEE = MAX_AMM_FEE

  EXTRA_LEVERAGE = random() * MAX_EXTRA_LEVERAGE

  
  system_collateral = MAX_INITIAL_COLLAT * random()
  system_price = INITIA_PRICE

  

  print("Initial Setup")
  print("Price", system_price)
  print("Collateral", system_collateral)

  ## Lever to target
  target_LTV = MAX_LTV * RISK_PERCENT / MAX_BPS / MAX_BPS
  target_debt = system_collateral * system_price * target_LTV
  print("Intitial Debt", target_debt)
  print("Initial LTV", target_LTV)
  system_debt = target_debt

  ## NOTE: Assume infinite ETH, can fine tune later
  liquidator_collateral_costs = 0
  liquidator_profit = 0

  ## Fees paid in collateral to get debt
  swap_collateral_fees = 0
  
  ## Fees paid in collateral to get stable-coin to cash out (ARB)
  swap_stable_fees = 0

  ## NOTE: Simulate one insolvent trove as it's effectively the same
  insolvent_debt = 0
  insolvent_collateral = 0




  step = 0
  ## Main Loop
  while(step < MAX_STEPS):
    print("Step", step)
    print("Collateral Ratio", calculate_collateral_ratio(system_collateral, system_price, system_debt))

    ## Check for solvency
    is_solvent = calculate_is_solvent(system_debt, system_collateral, system_price, MAX_LTV)
    if not is_solvent:
      print("We are insolvent, RIP")
      # break ## End, no point in looping as it's unprofitable to save the system, we have bad debt

    ## Check for Degenerate behavior (Minting more)
    if (random() * MAX_BPS > RISK_PERCENT):
      print("Simulate a random insolvency")

      drawdown_value = random() * MAX_BPS

      print("Drawdown of", drawdown_value)

      ## Insolvency basic, figure out random debt
      insolvent_collateral = random() * system_collateral

      max_insolvent_debt = calculate_max_debt(insolvent_collateral, system_price, MAX_LTV)

      ## From it figure out max collateral
      ## Levered to the max
      insolvent_debt = max_insolvent_debt

      ## Add debt and collateral to system
      system_collateral += insolvent_collateral
      system_debt += insolvent_debt

      ## Bring Price Down
      system_price = system_price * (MAX_BPS - drawdown_value) / MAX_BPS
      print("New Price", system_price)

      print("Drawdown Collateral Ratio of Underwater Debt", calculate_collateral_ratio(insolvent_collateral, system_price, insolvent_debt))
      print("Drawdown Collateral Ratio of System Including Underwater Debt", calculate_collateral_ratio(system_collateral, system_price, system_debt))

      ## TODO: Liquidation is profitable if AMM Quote is profitable
      ## And LTV is close enough


      ## TODO: Sim buying AMT of CDP from Pool
      ## Then use CDP to Liquidate (burn CDP, get Collateral)
      ## Then Sell Collateral in Pool again for another Stable
      ## Which shows the arb
    else:
      print("No Bad News Today, simulate price going up")

      pamp_value = random() * MAX_BPS

      print("Pamp of", pamp_value)
      ## Bring Price Up
      ## NOTE: We do this as it may make some liquidations profitable
      system_price = system_price * (MAX_BPS + pamp_value) / MAX_BPS
      print("New Price", system_price)

      print("Drawdown Collateral Ratio of Underwater Debt", calculate_collateral_ratio(insolvent_collateral, system_price, insolvent_debt))
      print("Drawdown Collateral Ratio of System Including Underwater Debt", calculate_collateral_ratio(system_collateral, system_price, system_debt))



    if(insolvent_collateral * system_price > insolvent_debt):
      print("We can save this")
    else:
      print("It's too underwater, let the trove sink")

    


    step += 1


def calculate_swap_fee(amount_in, fee_bps):
  return amount_in * fee_bps / MAX_BPS

def calculate_collateral_ratio(collateral, price, debt):
  return debt / collateral * price
  
  
def calculate_max_debt(collateral, price, max_ltv):
  return collateral * price * max_ltv / MAX_BPS

def calculate_is_solvent(debt, collateral, price, max_ltv):
  ## Strictly greater but no strong opinion on it
  return calculate_max_debt(collateral, price, max_ltv) > debt
