from random import random

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

def main():
  AVG_LTV = random() * MAX_LTV
  MAX_RISK_PERCENT = random() * MAX_LTV
  LP_PERCENT = random() * MAX_BPS

  deposited_eth = AMT_ETH * 10 ** ETH_DECIMALS
  print("deposited_eth", deposited_eth)
  borrowed_btc = deposited_eth / (10 ** ETH_DECIMALS - BTC_DECIMALS) * AVG_LTV / MAX_BPS
  print("borrowed_btc", borrowed_btc)

  max_liquidatable = borrowed_btc * MAX_RISK_PERCENT

  ## Assume 13 ETH = 1 BTC to KIS
  price_ratio = 13

  in_amm = LP_PERCENT * borrowed_btc / MAX_BPS
  as_eth = in_amm * price_ratio

  reserve_btc = in_amm
  reserve_eth = as_eth

  print("price_given_in(1, reserve_btc, reserve_eth", price_given_in(1, reserve_btc, reserve_eth))
  initial_price = price_given_in(1, reserve_btc, reserve_eth)
  ## Price makes sense
  assert 1 / initial_price > 12 and 1 / initial_price < 13


  ## What is the maximum I'm willing to pay to get eBTC to liquidate to ETH, if debt is N and I get M out?


  

if __name__ == '__main__':
    main()