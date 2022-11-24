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
import csv
import os
from random import random
import time

import pandas as pd
import matplotlib.pyplot as plt


MAX_BPS = 10_000

## How much can the price change between turns?
## 5%
MAX_SWING = 500

MAX_MINT_FEE = 200 ## 2%
MAX_LIQ_FEE = 1_000 ## 10%

MAX_AMM_FEE = 300 ## 3%, avg AMM is 30 BPS

## 1 eth, 1200 usd
INITIA_PRICE = 1200 ## TODO: ADD Dynamic Price

## 1k steps before we end
MAX_STEPS = 1000

## 1k eth
MAX_INITIAL_COLLAT = 1_000

## Output to CSV and PNG
TO_CSV = True

## Slow down the Terminal so you can read it
ROLEPLAY = False

class CsvEntry():
  def __init__(
    self,
    time,
    system_collateral,
    system_price,
    target_LTV,
    target_debt,
    system_debt,
    liquidator_fees_paid,
    liquidator_profit,
    swap_collateral_fees,
    swap_stable_fees,
    at_risk_debt,
    at_risk_collateral,
    current_cr,
    current_insolvent_cr
  ):
    self.time = time
    self.system_collateral = system_collateral
    self.system_price = system_price
    self.target_LTV = target_LTV
    self.target_debt = target_debt
    self.system_debt = system_debt
    self.liquidator_fees_paid = liquidator_fees_paid
    self.liquidator_profit = liquidator_profit
    self.swap_collateral_fees = swap_collateral_fees
    self.swap_stable_fees = swap_stable_fees
    self.at_risk_debt = at_risk_debt
    self.at_risk_collateral = at_risk_collateral
    self.current_cr = current_cr
    self.current_insolvent_cr = current_insolvent_cr

  def __repr__(self):
    return str(self.__dict__)

  def to_entry(self):
    return [
      self.time,
      self.system_collateral,
      self.system_price,
      self.target_LTV,
      self.target_debt,
      self.system_debt,
      self.liquidator_fees_paid,
      self.liquidator_profit,
      self.swap_collateral_fees,
      self.swap_stable_fees,
      self.at_risk_debt,
      self.at_risk_collateral,
      self.current_cr,
      self.current_insolvent_cr
    ]

class Logger:
    def __init__(self):
        self.entries = []
        self.headers = [
          "time",
          "system_collateral",
          "system_price",
          "target_LTV",
          "target_debt",
          "system_debt",
          "liquidator_fees_paid",
          "liquidator_profit",
          "swap_collateral_fees",
          "swap_stable_fees",
          "at_risk_debt",
          "at_risk_collateral",
          "current_cr",
          "current_insolvent_cr"
        ]
        os.makedirs('logs/fee_sims/', exist_ok=True)

    def add_move(
      self,
       time,
      system_collateral,
      system_price,
      target_LTV,
      target_debt,
      system_debt,
      liquidator_fees_paid,
      liquidator_profit,
      swap_collateral_fees,
      swap_stable_fees,
      at_risk_debt,
      at_risk_collateral,
      current_cr,
      current_insolvent_cr
    ):
        ## Add entry
        move = CsvEntry(
          time,
          system_collateral,
          system_price,
          target_LTV,
          target_debt,
          system_debt,
          liquidator_fees_paid,
          liquidator_profit,
          swap_collateral_fees,
          swap_stable_fees,
          at_risk_debt,
          at_risk_collateral,
          current_cr,
          current_insolvent_cr
        )
        self.entries.append(move)

    def __repr__(self):
        return str(self.__dict__)

    def to_csv(self):

      ## Create a file with current time as name
      filename = f'logs/fee_sims/{pd.Timestamp.now()}.csv'

      with open(filename, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(self.headers)

        # write the data
        for entry in self.entries:
          writer.writerow(entry.to_entry())

    def plot_to_png(self, filename=f'logs/fee_sims/{pd.Timestamp.now()}.png'):
      # convert CsvEntry objects to a single DataFrame
      df = (pd.DataFrame(self.entries)[0]
        .astype(str)
        .map(eval)
        .apply(pd.Series)
        .set_index('time')
      )
      print(df.info())
      df.style.set_caption("Hello World")


      # generate subplot for every column; save to single png
      constants = ['target_debt', 'target_LTV']
      fig, axes = plt.subplots(nrows=df.columns.size - len(constants))
      df.drop(constants, axis='columns').plot(subplots=True, ax=axes)
      fig.set_size_inches(10, 100)
      title = f'target debt: {df["target_debt"].max()}\ntarget LTV: {df["target_LTV"].max()}\n'
      fig.suptitle(title, fontsize=14, fontweight='bold')
      fig.savefig(filename, dpi=100)


def main():
  ## Maximum Collateral Ratio
  MAX_LTV = random() * MAX_BPS

  LOGGER = Logger()

  ## How risk the trove will get, MAX_BPS = Full send, 0 = We do not even mint
  RISK_PERCENT = random() * MAX_BPS

  MINTING_FEE = random() * MAX_MINT_FEE
  LIQ_FEE = random() * MAX_LIQ_FEE

  AMM_FEE = MAX_AMM_FEE


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

  ## We assume it's a portion of the debt, but we don't need to add
  system_minting_fee = system_debt * MINTING_FEE / MAX_BPS

  ## NOTE: TODO or remove per comment below
  system_liquidation_fee = 0

  ## NOTE: Arguably we could ignore as this is more of a caller incentive, meaningful only for small trades
  ## NOTE: May be worthwhile having a separate sim exclusively about the liquidation fee vs size of CDP
  liquidator_liquidation_fee_receive = 0

  ## TODO: Liquidation fee / Caller incentive

  ## NOTE: Assume infinite ETH, can fine tune later
  liquidator_fees_paid = 0
  liquidator_profit = 0

  ## Fees paid in collateral to get debt
  swap_collateral_fees = 0

  ## Fees paid in collateral to get stable-coin to cash out (ARB)
  swap_stable_fees = 0

  ## NOTE: Simulate one insolvent trove as it's effectively the same
  at_risk_debt = 0
  at_risk_collateral = 0

  current_cr = calculate_collateral_ratio(system_collateral, system_price, system_debt)
  current_insolvent_cr = calculate_collateral_ratio(at_risk_collateral, system_price, at_risk_debt)


  turn = 0
  ## Main Loop
  while(turn < MAX_STEPS):
    print("Turn", turn)

    print("Total Debt", system_debt)
    print("Total Collateral", system_collateral)
    print("Collateral Ratio", calculate_collateral_ratio(system_collateral, system_price, system_debt))


    ## Check insolvency
    ## We are insolvent in this case
    if (calculate_max_debt(at_risk_collateral, system_price, MAX_LTV) < at_risk_debt):
      print("Debt is insolvent")

      if(at_risk_collateral * system_price > at_risk_debt):
        print("Economically worth saving")

        ## TODO: Add check for proper liquidation threshold

        ## Liquidate
        ## For now we do full liquidation
        to_liquidate = at_risk_debt

        ## Cost of swapping from Stable to collateral
        cost_to_liquidate = calculate_swap_fee(at_risk_debt, AMM_FEE)

        ## NOTE: Technically incorrect but works for now

        ## Premium = total collateral - fees - debt
        ## NOTE: Technically missing liquidation fee
        ## TODO: Add liquidation fee
        ## NOTE: If 100% liquidation, technically the fee is the remainder of the position - LTV
        liquidation_premium = at_risk_collateral * system_price - cost_to_liquidate - at_risk_debt

        ## Update System
        system_collateral -= at_risk_collateral
        system_debt -= at_risk_debt

        ## Update Fees

        ## Cost of swapping from Collateral to stable
        second_swap_fees = calculate_swap_fee(liquidation_premium, AMM_FEE)

        ## Update AMM fees
        swap_collateral_fees += cost_to_liquidate
        swap_stable_fees += second_swap_fees

        ## NOTE
        liquidator_fees_paid += cost_to_liquidate + second_swap_fees
        liquidator_profit += liquidation_premium - second_swap_fees

        ## Update Insolvency vars
        at_risk_collateral = 0
        at_risk_debt = 0

        print("New CR After Liquidation", calculate_collateral_ratio(system_collateral, system_price, system_debt))
      else:
        print("Risky debt is insolvent, but not worth saving, skip")
    else:
      print("Risky debt is solvent, skip")

    ## Check for solvency
    is_solvent = calculate_is_solvent(system_debt, system_collateral, system_price, MAX_LTV)
    if not is_solvent:
      print("We are insolvent, RIP")
      # break ## End, no point in looping as it's unprofitable to save the system, we have bad debt

    ## TODO: Separate taking leverage / being insolvent
    ## From price up and down for more dynamic sim
    if (random() * MAX_BPS > RISK_PERCENT):
      print("Simulate Degenerate Borrowing")

      ## Insolvency basic, figure out random debt
      at_risk_collateral = random() * system_collateral

      max_at_risk_debt = calculate_max_debt(at_risk_collateral, system_price, MAX_LTV)

      ## From it figure out max collateral
      ## Levered to the max
      at_risk_debt = max_at_risk_debt

      ## Add debt and collateral to system
      system_collateral += at_risk_collateral
      system_debt += at_risk_debt

    ## Check for Degenerate behavior (Minting more)
    if (random() * 100 % 2 == 0):
      print("Price goes down")

      drawdown_value = random() * MAX_SWING

      print("Drawdown of", drawdown_value)

      ## Bring Price Down
      system_price = system_price * (MAX_BPS - drawdown_value) / MAX_BPS
      print("New Price", system_price)

      print("Drawdown Collateral Ratio of Underwater Debt", calculate_collateral_ratio(at_risk_collateral, system_price, at_risk_debt))
      print("Drawdown Collateral Ratio of System Including Underwater Debt", calculate_collateral_ratio(system_collateral, system_price, system_debt))

    else:
      print("No Bad News Today, simulate price going up")

      pamp_value = random() * MAX_SWING

      print("Pamp of", pamp_value)
      ## Bring Price Up
      ## NOTE: We do this as it may make some liquidations profitable
      system_price = system_price * (MAX_BPS + pamp_value) / MAX_BPS
      print("New Price", system_price)

      print("Pamp Collateral Ratio of Underwater Debt", calculate_collateral_ratio(at_risk_collateral, system_price, at_risk_debt))
      print("Pamp Collateral Ratio of System Including Underwater Debt", calculate_collateral_ratio(system_collateral, system_price, system_debt))


    


    ## TODO: Figure out if we want it here or somewhere else
    current_cr = calculate_collateral_ratio(system_collateral, system_price, system_debt)
    current_insolvent_cr = calculate_collateral_ratio(at_risk_collateral, system_price, at_risk_debt)



    ## TODO: Log all the values
    LOGGER.add_move(
      turn,
      system_collateral,
      system_price,
      target_LTV,
      target_debt,
      system_debt,
      liquidator_fees_paid,
      liquidator_profit,
      swap_collateral_fees,
      swap_stable_fees,
      at_risk_debt,
      at_risk_collateral,
      current_cr,
      current_insolvent_cr
    )


    ## NOTE: Indentation, we're still in the while
    if (ROLEPLAY):
      time.sleep(3)

    ## Next turn
    turn += 1

  ## NOTE: No longer in while, save to file
  if (TO_CSV):
    LOGGER.to_csv()
    LOGGER.plot_to_png()

def calculate_swap_fee(amount_in, fee_bps):
  return amount_in * fee_bps / MAX_BPS

def calculate_collateral_ratio(collateral, price, debt):
  if(collateral == 0):
    return 0
  return debt / (collateral * price)


def calculate_max_debt(collateral, price, max_ltv):
  return collateral * price * max_ltv / MAX_BPS

def calculate_is_solvent(debt, collateral, price, max_ltv):
  ## Strictly greater but no strong opinion on it
  return calculate_max_debt(collateral, price, max_ltv) > debt
