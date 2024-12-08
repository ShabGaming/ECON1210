import pandas as pd

def PriceControl(price_ceiling=None, price_floor=None, df=None):
    if df is None:
        return ""
    
    # Set the first row as column headers
    df.columns = df.iloc[0]
    # Remove the first row
    df = df[1:]
    # Reset the index to start from 0
    df = df.reset_index(drop=True)
    
    # Convert columns to appropriate data types
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Quantity Demanded'] = pd.to_numeric(df['Quantity Demanded'], errors='coerce')
    df['Quantity Supplied'] = pd.to_numeric(df['Quantity Supplied'], errors='coerce')
    
    # Ensure the DataFrame has the correct columns
    required_columns = {'Price', 'Quantity Demanded', 'Quantity Supplied'}
    if not required_columns.issubset(df.columns):
        return ""
    
    ceiling_result = None
    floor_result = None

    # Handle price ceiling and floor being zero
    if price_ceiling == 0:
        price_ceiling = None
    if price_floor == 0:
        price_floor = None

    # Sort DataFrame by Price in ascending order
    df_sorted = df.sort_values(by='Price', ascending=True).reset_index(drop=True)
    
    # Handle price ceiling
    if price_ceiling is not None:
        ceiling_df = df_sorted[df_sorted['Price'] <= price_ceiling]
        if not ceiling_df.empty:
            # Select the row with the highest price <= ceiling
            selected_row = ceiling_df.iloc[-1]
            quantity_transacted = min(selected_row['Quantity Demanded'], selected_row['Quantity Supplied'])
            # Check if ceiling is above equilibrium price
            equilibrium_row = df_sorted[df_sorted['Quantity Demanded'] == df_sorted['Quantity Supplied']]
            if not equilibrium_row.empty:
                equilibrium_price = equilibrium_row.iloc[0]['Price']
                equilibrium_quantity = equilibrium_row.iloc[0]['Quantity Demanded']
                if price_ceiling >= equilibrium_price:
                    quantity_transacted = equilibrium_quantity
            ceiling_result = f"At Price Ceiling: {price_ceiling}, Quantity Transacted: {quantity_transacted}"
        else:
            # If ceiling is below all prices, no transaction occurs
            ceiling_result = f"At Price Ceiling: {price_ceiling}, Quantity Transacted: 0"

    # Handle price floor
    if price_floor is not None:
        floor_df = df_sorted[df_sorted['Price'] >= price_floor]
        if not floor_df.empty:
            # Select the row with the lowest price >= floor
            selected_row = floor_df.iloc[0]
            quantity_transacted = min(selected_row['Quantity Demanded'], selected_row['Quantity Supplied'])
            # Check if floor is below equilibrium price
            equilibrium_row = df_sorted[df_sorted['Quantity Demanded'] == df_sorted['Quantity Supplied']]
            if not equilibrium_row.empty:
                equilibrium_price = equilibrium_row.iloc[0]['Price']
                equilibrium_quantity = equilibrium_row.iloc[0]['Quantity Demanded']
                if price_floor <= equilibrium_price:
                    quantity_transacted = equilibrium_quantity
            floor_result = f"Price Floor: {price_floor}, Quantity Transacted: {quantity_transacted}"
        else:
            # If floor is above all prices, no transaction occurs
            floor_result = f"Price Floor: {price_floor}, Quantity Transacted: 0"

    results = []
    if ceiling_result:
        results.append(ceiling_result)
    if floor_result:
        results.append(floor_result)

    # Convert results to string
    results = " | ".join(results)

    return results

PriceControl(arg1, arg2, arg3)