import pandas as pd
import itertools

def PriceDiscrimination(df, MC, FixedCost=0, CouponBreakPoint=None):
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

    # Ensure df has columns 'WTP'
    if 'WTP' not in df.columns:
        raise ValueError("The DataFrame must have a 'WTP' column.")

    # Sort by WTP for convenience
    df = df.sort_values('WTP').reset_index(drop=True)

    # Define a helper function to compute surplus and DWL
    def compute_surpluses(sold_customers, price):
        # sold_customers: a subset of df with those who buy
        # price: the price they pay
        # Consumer Surplus = sum(WTP_i - price for all buyers)
        cs = (sold_customers['WTP'] - price).clip(lower=0).sum()
        # Producer Surplus = sum(price - MC for all buyers)
        ps = ((price - MC) * len(sold_customers))
        
        # To compute DWL:
        # Efficiency scenario: serve all customers with WTP >= MC at cost = MC
        # Total potential surplus = sum(WTP_i - MC for WTP_i >= MC)
        total_potential = df.loc[df['WTP'] >= MC, 'WTP'].sum() - MC*len(df[df['WTP'] >= MC])
        # Actual total surplus = CS + PS
        actual_surplus = cs + ps
        dwl = total_potential - actual_surplus
        
        return cs, ps, dwl

    # No coupon segmentation, single price

    # Candidate prices: unique WTP values (offering at other prices won't be optimal)
    candidate_prices = df['WTP'].unique()

    best_profit = -float('inf')
    best_price = None
    best_cs, best_ps, best_dwl = 0,0,0
    best_sold_count = 0

    for p in candidate_prices:
        # Which customers buy?
        sold = df[df['WTP'] >= p]
        Q = len(sold)
        profit = (p - MC)*Q - FixedCost
        if profit > best_profit:
            # Compute surpluses and DWL
            cs, ps, dwl = compute_surpluses(sold, p)
            # Check if PS should exclude fixed cost or not:
            # Producer surplus is typically revenue - variable cost = (p*Q - MC*Q)
            # The profit includes fixed cost. PS as defined above doesn't subtract fixed cost.
            # The problem statements vary in definitions. We'll report PS as computed (not subtracting fixed).
            best_profit = profit
            best_price = p
            best_cs = cs
            best_ps = ps
            best_dwl = dwl
            best_sold_count = Q

    # Construct output
    # Output string (no coupon scenario)
    result = (f"To maximize profit charge {best_price:.2f}, and serve {best_sold_count} customers, "
                f"and make a profit of {best_profit:.2f}\n"
                f"Consumer Surplus = {best_cs:.2f}, Producer Surplus = {best_ps:.2f}, DWL = {best_dwl:.2f}")
    
    if CouponBreakPoint is None:
        return result
    else:
        # With coupon segmentation
        # Split into coupon and non-coupon groups
        coupon_group = df[df['WTP'] < CouponBreakPoint]
        non_coupon_group = df[df['WTP'] >= CouponBreakPoint]

        # Candidate prices:
        # For the non-coupon (list price), consider unique WTP in the non-coupon group
        # For the coupon (discount price), consider unique WTP in the coupon group
        # If either group is empty, handle accordingly
        candidate_list_prices = non_coupon_group['WTP'].unique() if not non_coupon_group.empty else []
        candidate_discount_prices = coupon_group['WTP'].unique() if not coupon_group.empty else []

        # If there's no coupon group or no non-coupon group, revert to single pricing scenario
        # But given the prompt, let's proceed as is:
        if coupon_group.empty:
            # No coupon group, just do single price
            return PriceDiscrimination(df, MC, FixedCost, None)
        if non_coupon_group.empty:
            # All are coupon group, just set a single price from coupon group
            return PriceDiscrimination(df, MC, FixedCost, None)

        best_profit = -float('inf')
        best_list_price = None
        best_discount_price = None
        best_cs, best_ps, best_dwl = 0,0,0
        best_sold_count = 0

        # Try all combinations of list price and discount price
        for lp in candidate_list_prices:
            for dp in candidate_discount_prices:
                # Who buys in coupon group? Those with WTP >= dp
                coupon_buyers = coupon_group[coupon_group['WTP'] >= dp]
                # Who buys in non-coupon group? Those with WTP >= lp
                non_coupon_buyers = non_coupon_group[non_coupon_group['WTP'] >= lp]

                # Total Q
                Q = len(coupon_buyers) + len(non_coupon_buyers)

                # Revenue = lp * number_of_non_coupon_buyers + dp * number_of_coupon_buyers
                revenue = lp*len(non_coupon_buyers) + dp*len(coupon_buyers)
                variable_cost = MC*Q
                profit = revenue - variable_cost - FixedCost

                if profit > best_profit:
                    # Compute CS, PS, DWL
                    # Note: Different customers pay different prices now.
                    # CS = sum(WTP - paid_price for each buyer)
                    # PS = sum(paid_price - MC for each buyer)
                    # We'll compute these directly.

                    buyers = pd.concat([coupon_buyers.copy(), non_coupon_buyers.copy()])
                    # For each buyer in coupon group, price paid = dp
                    buyers['PaidPrice'] = buyers['WTP'].apply(lambda x: dp if x < CouponBreakPoint else lp)
                    # Actually, we know coupon group pays dp, non-coupon pays lp:
                    buyers.loc[buyers['WTP'] < CouponBreakPoint, 'PaidPrice'] = dp
                    buyers.loc[buyers['WTP'] >= CouponBreakPoint, 'PaidPrice'] = lp

                    cs = (buyers['WTP'] - buyers['PaidPrice']).clip(lower=0).sum()
                    ps = ((buyers['PaidPrice'] - MC).sum())  # sum of price - MC for all
                    # Compute DWL:
                    # Potential: sum(WTP_i - MC for all WTP_i >= MC)
                    total_potential = df.loc[df['WTP'] >= MC, 'WTP'].sum() - MC*len(df[df['WTP'] >= MC])
                    actual_surplus = cs + ps
                    dwl = total_potential - actual_surplus

                    best_profit = profit
                    best_list_price = lp
                    best_discount_price = dp
                    best_cs = cs
                    best_ps = ps
                    best_dwl = dwl
                    best_sold_count = Q

        # Construct output (with coupon scenario)
        result2 = (f"To maximize profit: list price at {best_list_price:.2f} and discount price at {best_discount_price:.2f}.\n"
                  f"Serve {best_sold_count} customers, and make a profit of {best_profit:.2f}\n"
                  f"Consumer Surplus = {best_cs:.2f}, Producer Surplus = {best_ps:.2f}, DWL = {best_dwl:.2f}")
        return result + '\n' + '----------------------------------------------------' + '\n' + result2

PriceDiscrimination(arg1, arg2, arg3, arg4)