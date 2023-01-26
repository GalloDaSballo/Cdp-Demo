from random import random

## 1k eth
MAX_VALUE = 1000e18

## 2e18 is insta liquidated
MIN_VALUE = 2e18

MAX_BPS = 10_000


MIN_CUT_PERCENT_BPS = 1_000
MAX_BUT_PERCENT_BPS = 10_000

CUT_STEP_SIZE = 1_000

RUNS = 100_000

def main():
  ranges = reversed(range(MIN_CUT_PERCENT_BPS, MAX_BUT_PERCENT_BPS, CUT_STEP_SIZE))
  for cut_percent in ranges:
    print("cut_percent", cut_percent)
    max = 0
    min = 9e99
    sum = 0
    for run in range(RUNS):
      start_value = MAX_VALUE * random() + MIN_VALUE
      remaining = start_value
      rounds = 0

      while (remaining > MIN_VALUE) :
        remaining = remaining - (remaining * cut_percent / MAX_BPS)

        rounds += 1
      
      if rounds > max:
        max = rounds
      
      if rounds < min:
        min = rounds
      
      sum += rounds
  
    print("range", cut_percent)
    print("max", max)
    print("min", min)
    print("avg", sum / RUNS)
      
