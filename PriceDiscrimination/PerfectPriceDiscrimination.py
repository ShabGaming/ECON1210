import pandas as pd

def PerfectPriceDiscrimination(df, MC, FixedCost=None, CouponBreakPoint=None):
    if df is None:
        return ""
    
    if FixedCost is None:
        FixedCost = 0

    # Set the first row as column headers
    df.columns = df.iloc[0]
    # Remove the first row
    df = df[1:]
    # Reset the index to start from 0
    df = df.reset_index(drop=True)

    # Ensure DataFrame has the required columns
    if 'WTP' not in df.columns:
        raise ValueError("The DataFrame must have a 'WTP' column.")
        
    # Convert WTP to a list and sort descending for convenience
    df_sorted = df.sort_values(by='WTP', ascending=False).reset_index(drop=True)
    WTP_list = df_sorted['WTP'].tolist()
    
    # Perfect price discrimination scenario:
    # Serve all with WTP >= MC
    served_PPD = [w for w in WTP_list if w >= MC]
    # Producer Surplus under perfect price discrimination
    PS_PPD = sum([w - MC for w in served_PPD]) - FixedCost
    
    output = f"Perfect price discrimination the profit (Producer Surplus) is: {PS_PPD}"
    
    # If no coupon break point is given, we're done.
    if CouponBreakPoint is None:
        return output
    
    # If coupon break point is given:
    # Split customers into high and low groups
    high_group = [w for w in WTP_list if w >= CouponBreakPoint]
    low_group = [w for w in WTP_list if w < CouponBreakPoint]
    
    # If there are no high group customers, set posted price as the highest WTP overall
    # (Though this scenario is unusual, we'll handle it.)
    if len(high_group) == 0:
        # Then the posted price is chosen to maximize profit ignoring the break?
        # For simplicity, if no high group, we can just pick posted price = max(WTP) to ensure at least one sells.
        # But since the problem scenario usually implies existence of high group, let's handle gracefully.
        posted_price = max(WTP_list)
    else:
        # Choose posted price = min(WTP in high group) to ensure all high-WTP customers buy at that price
        posted_price = min(high_group)
    
    # Profit from high group if served at posted_price:
    # Only those with WTP >= posted_price will buy. (All high group by definition have WTP >= CouponBreakPoint, but let's double-check)
    high_buyers = [w for w in high_group if w >= posted_price]
    PS_high = sum([posted_price - MC for w in high_buyers])
    
    # Now find optimal coupon discount for the low group.
    # We want to find a coupon discount C that maximizes:
    #   sum((posted_price - C - MC) for those w in low group with w >= posted_price - C)
    #
    # The potential coupon prices that matter are determined by the WTP values in the low group.
    # For each candidate discount, we consider coupon_price = posted_price - C.
    # To get at least one low-WTP customer with WTP = w, we need posted_price - C <= w → C >= posted_price - w.
    # We'll check all candidate discounts that make at least one low WTP just indifferent.
    
    low_group_sorted = sorted(low_group, reverse=True)
    # Candidate discounts are such that coupon_price = posted_price - discount
    # We'll iterate through all WTP in low group and consider discount = posted_price - w.
    candidate_discounts = set()
    for w in low_group_sorted:
        # To include this w, we need a discount = posted_price - w
        candidate_discounts.add(round(posted_price - w, 10))  # rounding to handle float precision
    
    # Also consider a discount of 0 (no coupon) scenario
    candidate_discounts.add(0.0)
    
    best_discount = 0.0
    best_PS_total = PS_high - FixedCost  # This is baseline without low group sales
    best_served_low = []
    
    for C in candidate_discounts:
        coupon_price = posted_price - C
        # Who from the low group buys?
        low_buyers = [w for w in low_group if w >= coupon_price]
        # Producer surplus from low group with this coupon:
        PS_low = sum([coupon_price - MC for w in low_buyers])
        PS_total = PS_high + PS_low - FixedCost
        if PS_total > best_PS_total:
            best_PS_total = PS_total
            best_discount = C
            best_served_low = low_buyers
    
    # Now we have:
    # best_discount: the optimal coupon amount
    # best_PS_total: the producer surplus at that discount scenario
    # best_served_low: the served low group customers
    # high_buyers: the served high group customers
    
    # Compute Consumer Surplus and Deadweight Loss under the chosen coupon scenario
    coupon_price = posted_price - best_discount
    served_all = high_buyers + best_served_low
    
    # Consumer Surplus:
    # CS = Σ(WTP_i - Price_paid_i)
    # High group pays posted_price, low group pays coupon_price
    CS_high = sum([w - posted_price for w in high_buyers])
    CS_low = sum([w - coupon_price for w in best_served_low])
    CS = CS_high + CS_low
    
    # Total surplus under coupon scenario:
    # TS_coupon = Σ(WTP_i - MC for served)
    TS_coupon = sum([w - MC for w in served_all])
    
    # Total surplus under perfect price discrimination scenario:
    # TS_ppd = sum(WTP_i - MC for all WTP_i >= MC)
    # We've already computed served_PPD for perfect discrimination
    TS_ppd = sum([w - MC for w in served_PPD])
    
    # DWL = TS_ppd - TS_coupon
    DWL = TS_ppd - TS_coupon
    
    output += (f"\nOptimal coupon discount: {best_discount}\n"
                f"List Price: {posted_price} & Coupon Price: {coupon_price}\n"
                f"Producer Surplus: {best_PS_total} & Consumer Surplus: {CS}\n"
                f"Total Surplus: {TS_coupon}\n"
                f"Deadweight Loss: {DWL}")

    return output

PerfectPriceDiscrimination(arg1, arg2, arg3, arg4)