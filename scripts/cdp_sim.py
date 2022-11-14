"""
  Sim of CDP System

  ### SYSTEM STATE ###

  Global Collateral Ratio
  Total Deposits
  Total Debt

  ### SYSTEM CONFIG ###

  Max LTV
  Fee per second (0% on LUSD)
  Origination Fee (Fixed Fee 50 BPS on LUSD)

  ### TROVE STATE ###

  Local Collateral Ratio
  Local Deposits
  Local Debt


  ### USER ACTIONS ###
  Deposit
  Withdraw

  Borrow
  Repay

  Liquidate
"""

MAX_BPS = 10_000



GLOBAL_TOTAL_DEPOSITS = 0
GLOBAL_TOTAL_DEBT = 0

INTERNAL_SECONDS_SINCE_DEPLOY = 0

MAX_LTV = 15000 ## 150%
FEE_PER_SECOND = 0 ## No fee for borrows
ORIGINATION_FEE = 50 ## 50BPS

FEED = 1000

def GLOBAL_COLLATERAL_RATIO():
  return GLOBAL_TOTAL_DEBT * MAX_BPS / GLOBAL_TOTAL_DEPOSITS 

def GLOBAL_MAX_BORROW():
  GLOBAL_TOTAL_DEBT * FEED

def IS_IN_EMERGENCY_MODE():
  ## TODO:
  return False

def IS_SOLVENT():
  ## NOTE: Strictly less to avoid rounding, etc..
  return GLOBAL_TOTAL_DEBT < GLOBAL_MAX_BORROW()


class Trove():
  def __init__(self, owner):
    self.deposits = 0
    self.debt = 0
    self.last_update_ts = INTERNAL_SECONDS_SINCE_DEPLOY
    self.owner = owner
  
  def local_collateral_ratio(self):
    return self.debt * MAX_BPS / self.deposits
  
  def deposit(self, amount):
    GLOBAL_TOTAL_DEPOSITS += amount
    self.deposits += amount

    self.owner.reduce_balance(self, amount)
  
  def withdraw(self, amount):
    self.deposits -= amount

    assert self.is_solvent()
  
  def borrow(self, amount):
    self.debt += amount

    assert self.is_solvent()
  
  def repay(self, amount):
    ## TODO
    return 0
  
  def liquidate(self, amount, caller):
    ## Only if not owner
    if caller == self.owner:
      return False
    
    return 0

  
  ## SECURITY CHECKS
  def is_trove():
    return True

  def max_borrow(self):
    return self.deposits * FEED
  
  def is_solvent(self):
    ## Strictly less to avoid rounding or w/e
    return self.debt < self.max_borrow() 
  

  

class User():
  def __init__(self, initial_balance_collateral, name):
    self.collateral = initial_balance_collateral
    self.name = name ## TODO: Random Name Generator
  
  def increase_balance(self, caller, amount):
    try:
      assert caller.is_trove() == True
      self.collateral += amount

    except:
        ## Do nothing on failure
        print("error")
    
  def reduce_balance(self, caller, amount):
    try:
      assert caller.is_trove() == True
      self.collateral -= amount

    except:
        ## Do nothing on failure
        print("error")
  
  def get_balance(self):
    return self.collateral
  


## TODO: Add Roles ##

## Borrows and Holds
class Borrower(Actor):

    def step():
        pass

## Borrow and Sells when price is higher
class LongArbitrager(Actor):

    def step():
        pass

## Buys when cheap and sells when higher
class ShortArbitrager(Actor):

    def step():
        pass

## Does both arbitrages
class Trader(Actor):

    def step():
        pass


def main():
  user_1 = User(100, "A")

  ## TODO: Proper Print
  print(user_1)

