import pandas as pd

def calculate_total_production(working_hours, num_assigned, item, df):
    if df is None:
        return ""
    
    # Set the first row as column headers
    df.columns = df.iloc[0]
    # Remove the first row
    df = df[1:]
    # Reset the index to start from 0
    df = df.reset_index(drop=True)

    # Validate that the 'Person' column exists
    if 'Person' not in df.columns:
        return ""
    
    # Validate that item_name exists in df columns
    if item not in df.columns:
        return ""

    # Calculate Opportunity Cost (ties per hat)
    df['Opportunity_Cost'] = df['tie'] / df['hat']

    # Sort by Opportunity Cost ascendingly
    df_sorted = df.sort_values('Opportunity_Cost').reset_index(drop=True)

    # Assign the specified number of people to specialize in hats
    assigned_workers = df_sorted.head(num_assigned)
    tie_workers = df_sorted.tail(len(df_sorted) - num_assigned)

    # Calculate total hats produced
    total_hats = (assigned_workers['hat'] * working_hours).sum()

    # Calculate total ties produced
    total_ties = (tie_workers['tie'] * working_hours).sum()

    # Convert numpy.float64 to float
    total_hats = float(total_hats)
    total_ties = float(total_ties)

    # Return a string with the total production
    answer = {'hats': round(total_hats, 2), 'ties': round(total_ties, 2)}

    # convert the dictionary to a string for output
    answer = ', '.join([f"{value} {key}" for key, value in answer.items()])
    return answer

calculate_total_production(arg1, arg2, arg3, arg4)