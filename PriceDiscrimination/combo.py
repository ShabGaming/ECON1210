import pandas as pd

def compute_profit_details(df, fixed_cost=None, MC=None, PerComboCost=None):

    if df is None:
        return ""

    if fixed_cost is None:
        fixed_cost = 0
    if MC is None:
        MC = 0
    if PerComboCost is None:
        PerComboCost = 0

    # Set the first row as column headers
    df.columns = df.iloc[0]
    # Remove the first row
    df = df[1:]
    # Reset the index to start from 0
    df = df.reset_index(drop=True)

    # Drop the first column
    df = df.drop(df.columns[0], axis=1)

    # Ensure the DataFrame has exactly two product columns
    if df.shape[1] != 2:
        return "Error: The DataFrame must contain exactly two product columns."
    
    # Fill missing WTP values with 0 (assuming no willingness to pay)
    df_filled = df.fillna(0)
    
    # Extract product names
    product1, product2 = df_filled.columns.tolist()
    
    separate_prices = []
    separate_profits = []
    
    # Calculate optimal prices and profits when selling separately
    for product in [product1, product2]:
        wtp = df_filled[product]
        unique_wtp = sorted(wtp.unique(), reverse=True)
        unique_wtp = [price for price in unique_wtp if price > 0]
        
        if not unique_wtp:
            separate_prices.append(0)
            separate_profits.append(0)
            continue
        
        max_profit = -float('inf')
        best_price = 0
        
        for price in unique_wtp:
            buyers = (wtp >= price).sum()
            profit = (price - MC) * buyers
            if profit > max_profit:
                max_profit = profit
                best_price = price
        
        separate_prices.append(best_price)
        separate_profits.append((best_price - MC) * (df_filled[product] >= best_price).sum())
    
    total_separate_profit = sum(separate_profits) - fixed_cost
    
    # Calculate optimal price and profit when selling as a combo
    combo_wtp = df_filled[product1] + df_filled[product2]
    unique_combo_wtp = sorted(combo_wtp.unique(), reverse=True)
    total_cost_combo = 2 * MC + PerComboCost  # Assuming MC for both products in combo
    
    possible_combo_prices = [price for price in unique_combo_wtp if price > total_cost_combo]
    
    if not possible_combo_prices:
        # If no price yields positive profit, set combo price to total cost
        best_combo_price = total_cost_combo
        max_profit_combo = 0
    else:
        max_profit_combo = -float('inf')
        best_combo_price = 0
        for price in possible_combo_prices:
            buyers = (combo_wtp >= price).sum()
            profit = (price - total_cost_combo) * buyers
            if profit > max_profit_combo:
                max_profit_combo = profit
                best_combo_price = price
        # Handle case where no buyers are profitable
        if max_profit_combo < 0:
            max_profit_combo = 0
            best_combo_price = total_cost_combo
    
    total_combo_profit = max_profit_combo - fixed_cost
    
    # Determine the optimal selling strategy
    if total_combo_profit > total_separate_profit:
        recommendation = 'as combo'
    else:
        recommendation = 'separately'
    
    # Extract item names
    itemA, itemB = product1, product2
    
    # Format the output string
    output = (
        f"Maximum Separately: {separate_prices[0]} per {itemA}, {separate_prices[1]} per {itemB}, "
        f"for a Total Profit {total_separate_profit:.2f}\n"
        f"Maximum Combo: {best_combo_price} per combo, for a Total Profit {total_combo_profit:.2f}\n"
        f"Recommended {recommendation}."
    )
    
    return output

compute_profit_details(arg1, arg2, arg3, arg4)