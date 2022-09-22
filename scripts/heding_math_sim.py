from random import random

"""
  Basic Hedging Math Sim based on:
  https://lambert-guillaume.medium.com/how-to-deploy-delta-neutral-liquidity-in-uniswap-or-why-euler-finance-is-a-game-changer-for-lps-1d91efe1e8ac

  Adapted to use Balancer assuming
  CapitalEfficiency(Bal) >= CapitalEfficiency(UniV2)
"""
MAX_BPS = 10_000

MAX_VOLATILITY = 4870 ## 99% swing is max

MAX_APR_FOR_BORROW_BPS = 2_775 ## 27.75% Happens before huge COMP Cliff
## If you go above cliff, GTFO

COST_OF_TRADE_BPS = 100 ## 1% as bigger trade WILL require 1Inch, UniV3 PI is above 10% for 100 ETH

LTV_BPS = 7_500 ## 75% | 82% is Limit

LIQUIDATION_TRESHOLD = 8_200 ## 82%. If we reach this, we get liquidated

INITIAL_DEPOSIT_ETH = 100
ETH_DECIMALS = 18

## NOTE: Copy paste latest from here: https://data.chain.link/ethereum/mainnet/crypto-eth/comp-eth
COMP_ETH_RATIO = 0.045247352 ## 1 COMP = 21.sth 

## We use this initial K to simulate price impact that makes sense
## NOTE: Real liquidty with added zeros to soften price impact
## TODO: We may not need any of this just use ratios
UNIV2_START_ETH = 617926109481837621890000
UNIV2_START_COMP = 13644469479558227835520000
UNIV2_K = UNIV2_START_ETH * UNIV2_START_COMP


def sim(volatility_bps):
  """
    volatility_bps. How much to lose, and How much to gain for the sim to check if we're within bounds
  """
  print("volatility_bps", volatility_bps)
  
  initial_amount = INITIAL_DEPOSIT_ETH * 10 ** ETH_DECIMALS

  print("Starting Price", 1 / COMP_ETH_RATIO)


  ## Deposit 2/3 into COMP
  deposit_into_comp = initial_amount * 2 / 3

  liquid_amount = initial_amount - deposit_into_comp

  comp_borrowable_in_eth = deposit_into_comp * LTV_BPS / MAX_BPS

  ## Borrow only half to reduce risk || 50% Hedge
  comp_we_will_borrow_in_eth = comp_borrowable_in_eth / 2

  all_comp_borrowable = comp_we_will_borrow_in_eth / COMP_ETH_RATIO

  ## If this ever reaches LIQUIDATION_TRESHOLD we get liquidated
  borrow_ratio = comp_we_will_borrow_in_eth / deposit_into_comp * 10_000

  ## We did not get liquidated yet
  assert (borrow_ratio < LIQUIDATION_TRESHOLD)
  print("Starting Borrow Ratio ", borrow_ratio)

  ## Assume LP at 50/50
  ## We do have more than we borrowed meaning we can afford to LP
  ## NOTE: We are not as capital efficient as possible, 
  ## if you know how, I got a job for you -> alex@badger.com
  assert(liquid_amount > comp_we_will_borrow_in_eth)

  eth_in_lp = comp_we_will_borrow_in_eth
  comp_in_lp = all_comp_borrowable
  print("eth_in_lp", eth_in_lp)
  print("comp_in_lp", comp_in_lp)

  ## We are in LP
  ## TODO: Add Math to estimate gain over time vs IL vs borrow rate

  ## Scenario 1, loss of X%
  loss_in_eth = UNIV2_START_ETH * volatility_bps / MAX_BPS
  print("loss_in_eth", loss_in_eth)

  ## Compute new Ratios ## NOTE: Assumes UniV2
  ## Increase 
  new_eth_in_lp = UNIV2_START_ETH - loss_in_eth
  print("new_eth_in_lp", new_eth_in_lp)

  new_comp_in_lp = UNIV2_K / new_eth_in_lp
  print("new_comp_in_lp", new_comp_in_lp)

  new_price = new_comp_in_lp / new_eth_in_lp
  print("new_price", new_price)

  ## Compute new Health Factor
  borrow_ratio = all_comp_borrowable / new_price / deposit_into_comp * 10_000
  print("Loss Borrow Ratio ", borrow_ratio)
  assert (borrow_ratio < LIQUIDATION_TRESHOLD)

  ## Scenario 2, gain of X%
  gain_in_eth = UNIV2_START_ETH * volatility_bps / MAX_BPS
  print("gain_in_eth", gain_in_eth)

  ## Increase 
  new_eth_in_lp = UNIV2_START_ETH + gain_in_eth
  print("new_eth_in_lp", new_eth_in_lp)

  new_comp_in_lp = UNIV2_K / new_eth_in_lp
  print("new_comp_in_lp", new_comp_in_lp)

  new_price = new_comp_in_lp / new_eth_in_lp
  print("new_price", new_price)

  ## Compute new Health Factor
  borrow_ratio = all_comp_borrowable / new_price / deposit_into_comp * 10_000
  print("Gain Borrow Ratio ", borrow_ratio)
  assert (borrow_ratio < LIQUIDATION_TRESHOLD)


  ## Compute gain vs loss

  






ROUNDS = 10_000


def main():
  max = 0
  for i in range(ROUNDS):
    try:
      vol = round(random() * MAX_VOLATILITY) + 1
      sim(vol)

      if vol > max:
        max = vol
    except:
        x = 0 ## Nothing

  print("max", max)
