MAX_PERCENT = 100

LTV = 150
PERCENT = 10

PERCENT_DRAWDOWN = 10
PARTIAL_LIQ_PROFIT = 10

def cr(debt, coll):
    return coll / debt * 100

def main():
    ## LTV 150
    DEBT = 100
    COLL = DEBT * LTV / MAX_PERCENT
    print("COLL", COLL)

    ## Assume already at edge
    cdp_debt = DEBT * PERCENT / MAX_PERCENT
    cdp_coll = DEBT * PERCENT / MAX_PERCENT

    print("cdp_debt", cdp_debt)
    print("cdp_coll", cdp_coll)

    ## CR
    initial_icr = cr(cdp_debt, cdp_coll)
    print("initial_icr", initial_icr)

    total_debt = DEBT + cdp_debt
    total_coll = COLL + cdp_coll

    initial_cr = cr(total_debt, total_coll)
    print("GLOBAL initial_cr", initial_cr)

    ## Drawdown
    new_cdp_coll = cdp_coll * (MAX_PERCENT - PERCENT_DRAWDOWN) / MAX_PERCENT
    print("new_cdp_coll", new_cdp_coll)
    
    after_drawdown_icr = cr(cdp_debt, new_cdp_coll)
    print("after_drawdown_icr", after_drawdown_icr)

    ## Global CR
    total_debt = DEBT + cdp_debt
    total_coll = COLL + new_cdp_coll
    after_drawdown_cr = cr(total_debt, total_coll)
    print("GLOBAL after_drawdown_cr", after_drawdown_cr)


    ## Try with % reabsorption
    debt_after_reabsorption = cdp_debt * PARTIAL_LIQ_PROFIT / MAX_PERCENT
    print("debt_after_reabsorption", debt_after_reabsorption)
    collateral_after_reabsorption = 0
    
    total_debt = DEBT + debt_after_reabsorption
    total_coll = COLL + collateral_after_reabsorption
    after_partial_cr = cr(total_debt, total_coll)
    print("GLOBAL after_partial_cr", after_partial_cr)









