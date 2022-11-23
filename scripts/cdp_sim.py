"""
  Sim of CDP System

  ### SYSTEM STATE ###

  Global Collateral Ratio
  Total Deposits
  Total Debt

  ### SYSTEM CONFIG ###

  Max MAX_LTV
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
import math
import random
from rich.pretty import pprint

from lib.names import name_list


MAX_BPS = 10_000
SECONDS_SINCE_DEPLOY = 0
SECONDS_PER_TURN = 12 ## One block in POS
INITIAL_FEED = 1000
SPEED_RANGE = 10

## TODO: CHANGE
MAX_LTV = 8500

## Randomness seed for multiple runs
SEED = 123

random.seed(SEED)

### ARCHITECURE ###
"""
    Ultimately we're loosely OOP, because OOP can become a mess follow these rules:

    - User and Trove can Log, add logs to System only if you need to snapshot.
        User and Trove are responsible for logging their state
    
    - System tracks all Users and Troves

    - System Triggers -> Users, which Triggers Troves and sync up with System

    - Users are the Agents, create a class that extends User (e.g. Borrower)
    
    - Write the logic in take_action and you will be able to extend the rest of the system


    TODO:
    - Basic invariant / unit tests to make sure system is fine
    - Extend more Classes to Sim
    - Decide if we want to add UniV2 / V3 Pool and simulate arbs there as well
"""


class Move:
    def __init__(self, time, actor, label, values):
        self.time = time
        self.actor = actor
        self.label = label
        self.values = values ## []
    
    def __repr__(self):
        return str(self.__dict__)

class Logger:
    def __init__(self):
        self.moves = []
    
    def add_move(self, time, actor, label, values):
        move = Move(time, actor, label, values)
        self.moves.append(move)
    
    def __repr__(self):
        return str(self.__dict__)
class Ebtc:
    def __init__(self, logger):
        self.MAX_LTV = 15000  ## 150%
        self.FEE_PER_SECOND = 0  ## No fee for borrows
        self.ORIGINATION_FEE = 50  ## 50BPS

        self.total_deposits = 0
        self.total_debt = 0
        self.feed = INITIAL_FEED
        self.time = SECONDS_SINCE_DEPLOY
        self.turn = 0
        
        self.logger = logger

    def __repr__(self):
        return str(self.__dict__)

    def collateral_ratio(self):
        return self.total_debt * MAX_BPS / self.total_deposits

    def max_borrow(self):
        return self.total_deposits * self.feed * MAX_LTV / MAX_BPS

    def is_in_emergency_mode(self):
        ## TODO: When are we in emergency mode?
        return False

    def is_solvent(self):
        ## NOTE: Strictly less to avoid rounding, etc..
        return self.total_debt < self.max_borrow()

    def get_feed(self):
        return self.feed

    def set_feed(self, value):
      self.feed = value

    
    def take_turn(self, users, troves):
        print("Turn", self.turn, ": Second: ", self.time)

        ## Do w/e
        self.sort_users(users)

        self.take_actions(users, troves)

        ## NOTE: Logging is done by each actor
        ## NO LOGS IN SYSTEM, only in Trove / User
        
        ## Increase counter
        self.next_turn()

        ## End of turn checks
        if(not self.is_solvent()):
            print("INSOLVENT")
        
    
    def sort_users(self, users):
        def get_key(user):
            ## TODO: Swing size (+- to impact randomness, simulate sorting, front-running etc..)
            return user.speed * random.random()
        users.sort(key=get_key)
    
    def take_actions(self, users, troves):
        ## TODO: Add User Decisions making / given the list of all trove have user do something
        for user in users:
            user.take_action(self.turn, troves)

    def next_turn(self):
      self.time += SECONDS_PER_TURN
      self.turn += 1
  
    


class Trove:
    def __init__(self, owner, system):
        self.deposits = 0
        self.debt = 0
        self.last_update_ts = system.time
        self.owner = owner
        self.system = system
        self.id = str(random.randint(1, 10**24)) ## Although PRGN odds of clash are unlikely

    def __repr__(self):
        return str(self.__dict__)

    def local_collateral_ratio(self):
        return self.debt * MAX_BPS / self.deposits

    def deposit(self, amount):
        ## Internal
        assert self.is_solvent()
        self.system.total_deposits += amount
        self.deposits += amount

        ## Caller
        self.owner.spend(self.id, False, amount, "Deposit")

        ## Logging
        self.system.logger.add_move(self.system.time, "Trove" + self.id, "Deposit", amount)

    def withdraw(self, amount):
        ## Internal
        self.deposits -= amount
        assert self.is_solvent()
        
        ## Caller
        self.owner.receive(self.id, False, amount, "Withdraw")

        ## Logging
        self.system.logger.add_move(self.system.time, "Trove" + self.id, "Withdraw", amount)

    def borrow(self, amount):
        self.debt += amount
        assert self.is_solvent()
        self.system.total_debt += amount
        assert self.system.is_solvent()

        self.owner.receive(self.id, True, amount, "Borrow")

        ## Logging
        self.system.logger.add_move(self.system.time, "Trove" + self.id, "Borrow", amount)


    def repay(self, amount):
        self.debt -= amount
        assert self.is_solvent()
        self.system.total_debt -= amount
        assert self.system.is_solvent()

        self.owner.spend(self.id, True, amount, "Repay")

        ## Logging
        self.system.logger.add_move(self.system.time, "Trove" + self.id, "Repay", amount)

    def liquidate(self, amount, caller):
        ## Only if not owner
        if caller == self.owner:
            return False
        
        ## TODO: Incorrect / Missing piece / Math
        ## Spend Debt to repay
        caller.spend(self.id, True, amount, "Liquidate")
        ## Receive Collateral for liquidation
        caller.receive(self.id, False, amount, "Liquidate")

        ## Logging
        self.system.logger.add_move(self.system.time, "Trove", "Liquidate", amount)

        return 0

    ## SECURITY CHECKS
    def is_trove(self):
        return True

    def max_borrow(self):
        return self.deposits * self.system.feed * MAX_LTV / MAX_BPS

    def is_solvent(self):
        if self.debt == 0:
            return True
        ## Strictly less to avoid rounding or w/e
        return self.debt < self.max_borrow()
    
    def current_ltv(self):
        if self.deposits == 0 or self.system.feed == 0:
            return 0
        
        return self.debt / (self.deposits * self.system.feed)


class User:
    def __init__(self, system, initial_balance_collateral):
        self.system = system
        self.collateral = initial_balance_collateral
        self.debt = 0
        self.name = random.choice(name_list)
        self.speed = math.floor(random.random() * SPEED_RANGE) + 1

    def __repr__(self):
        return str(self.__dict__)
    
    def spend(self, caller, is_debt, amount, label):
        if is_debt:
            self.debt -= amount

            ## Logging
            self.system.logger.add_move(self.system.time, "User" + self.name, "Spent Debt", amount)

        
        else:
            self.collateral -= amount

            ## Logging
            self.system.logger.add_move(self.system.time, "User" + self.name, "Spent Collateral", amount)
        

    
    def receive(self, caller, is_debt, amount, label):
        if is_debt:
            self.debt += amount

            ## Logging
            self.system.logger.add_move(self.system.time, "User" + self.name, "Receive Debt", amount)

        
        else:
            self.collateral += amount

            ## Logging
            self.system.logger.add_move(self.system.time, "User" + self.name, "Receive Collateral", amount)


    def get_debt(self):
        return self.debt

    def get_balance(self):
        return self.collateral

    def take_action(self, turn, troves):
        print("User" , self.name, " Taking Action")
        print("turn ", turn)

        self.system.logger.add_move(self.system.time, "User" + self.name, "Balance of Collateral", self.collateral)
        self.system.logger.add_move(self.system.time, "User" + self.name, "Balance of Debt", self.debt)


## POOL For Swap

## NOTE: For UniV3 we can use Solidly Math
## Or alternatively just use infinite leverage at price point + .50% price impact

class UniV2Pool():
  def __init__(self, start_x, start_y, start_lp):
    ## NOTE: May or may not want to have a function to hardcode this
    self.reserve_x = start_x
    self.reserve_y = start_y
    self.total_supply = start_lp

  def k(self):
    return self.x * self.y
  
  def get_price_out(self, is_x, amount):
    if (is_x):
      return self.get_price(amount, self.reserve_x, self.reserve_y)
    else:
      return self.get_price(amount, self.reserve_y, self.reserve_x)

  ## UniV2 Formula, can extend the class and change this to create new pools
  def get_price(amount_in, reserve_in, reserve_out):
      amountInWithFee = amount_in * 997
      numerator = amountInWithFee * reserve_out
      denominator = reserve_in * 1000 + amountInWithFee
      amountOut = numerator / denominator

      return amountOut
  
  def withdraw_lp():
    ## TODO
    return False
  
  def lp():
    ## TODO
    return False
  

## TODO: Add Roles ##
"""
    Doc about ways to play
    https://docs.google.com/document/d/1MgqFWCPL1d1_z-8Cohq-h_9N4VEsF4zAFbxuMYq4YwA/edit
"""

## Borrows and Holds
class Borrower(User):
    def __init__(self, system, initial_balance_collateral):
        self.system = system
        self.debt = 0
        self.collateral = initial_balance_collateral
        self.name = random.choice(name_list)
        self.speed = math.floor(random.random() * SPEED_RANGE) + 1
        self.target_ltv = random.random() * MAX_LTV
    
    def take_action(self, turn, troves):
        ## Deposit entire balance
        trove = self.find_trove(troves)

        ## TODO: If insolvent we should do something, perhaps try to redeem as much as possible
        if not trove.is_solvent():
            print("Trove is insolvent, we run away with the money")
            return ## Just revert

        if(trove == False):
            print("Cannot find trove PROBLEM")
            assert False
        
        ## if has collateral spend it
        if(self.collateral > 0):
            trove.deposit(self.collateral)
            
            ## NOTE: Check we did use collateral
            assert self.collateral == 0
    
        
        
        target_borrow = trove.max_borrow() * self.target_ltv / MAX_BPS

        ## If below target, borrow
        if(trove.debt < target_borrow):
            print("We are below target ltv, borrow")
            ## Borrow until we get to ltv
            ## TODO: check math math
            delta_borrow = target_borrow - trove.debt

            print("Borrow ", delta_borrow)
            trove.borrow(delta_borrow)
        
        ## If above target, delever
        if(trove.debt > target_borrow):
            ## TODO: Repay
            return 0
        

        
    
    def find_trove(self, troves):
        for trove in troves:
            if trove.owner.name == self.name:
                return trove

        return False


## Borrow and Sells when price is higher
class LongArbitrager(User):
    def take_action(self, turn, troves):
        pass


## Buys when cheap and sells when higher
class ShortArbitrager(User):
   def take_action(self, turn, troves):
        pass


## Does both arbitrages
class Trader(User):
    def take_action(self, turn, troves):
        pass


def invariant_tests():
    ## TODO: Please fill these in
    """
        If I have X troves, then total debt is sum of each trove debt

        Total borrowed is sum of each trove

        Max_borrow is sum of max borrowed

        LTV is weighted average of each LTV = Sum LTV / $%

        If I take a turn, X seconds pass
    """

def main():
    # init the system
    logger = Logger()
    system = Ebtc(logger)

    # init a user with a balance of 100
    user_1 = Borrower(system, 100)

    # init a trove for this user
    trove_1 = Trove(user_1, system)
    pprint(trove_1.__dict__)

    # make a deposit into the system
    trove_1.deposit(25)
    pprint(trove_1.__dict__)

    # borrow against this deposit
    trove_1.borrow(12.5)
    pprint(trove_1.__dict__)

    assert system.time == 0



    ## Let next time pass
    

    ## Turn System
    users = [user_1]
    troves = [trove_1]

    system.take_turn(users, troves)
    assert system.time == SECONDS_PER_TURN

    system.take_turn(users, troves)
    system.take_turn(users, troves)
    system.take_turn(users, troves)
    system.take_turn(users, troves)

    pprint(logger)

    ## Test for Feed and solvency
    assert trove_1.is_solvent()

    print("LTVL before drop", trove_1.current_ltv())

    ## Minimum amount to be insolvent ## On max leverage
    system.set_feed(system.get_feed() * (MAX_BPS - MAX_LTV - 1) / MAX_BPS)


    print("LTVL after drop", trove_1.current_ltv())

    ## Insane drop
    system.set_feed(0.0001)

    ## User will not invest
    system.take_turn(users, troves)

    print("Debt", trove_1.debt)
    print("Max Debt", trove_1.max_borrow())
    

    ## Because one trove let's verify consistency
    assert system.total_debt == trove_1.debt
    print("system.max_borrow()", system.max_borrow())
    print("trove_1.max_borrow()", trove_1.max_borrow())
    assert system.max_borrow() == trove_1.max_borrow()

    assert not trove_1.is_solvent()

    pprint(logger)
