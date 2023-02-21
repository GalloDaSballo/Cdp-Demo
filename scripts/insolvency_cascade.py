"""
  Simulation around insolvency and risks involved with it

  Assumptions:
  - Redemptions and Partial Liquidations can be performed from 100 <= ICR < MCR
  - They could be performed after, but would be unprofitable
  - If ICR < 100 we need to redistribute the insolvency to avoid further bad debt from the abandoned CDP
    - TODO: Challenge the above, find scenarios where leaving as is can be better

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
"""

## Fixed % means that there is a specific % at which we already lock in bad debt
## Floating premium means that there is no % at which we lock bad debt, 
# but there is a % at which liquidation calls are unprofitable

