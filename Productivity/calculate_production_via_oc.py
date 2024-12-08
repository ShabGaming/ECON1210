import pandas as pd

def calculate_production(working_time, num_assigned, item, df):  
    # Validate that the 'Person' column exists
    if 'Person' not in df.columns:
        return ""
    
    # Ensure the specified item exists in the DataFrame
    if item not in df.columns:
        return ""
    
    # Identify the other items in the DataFrame (excluding 'Person' and the specified item)
    other_items = [col for col in df.columns if col not in ['Person', item]]
    
    if len(other_items) == 0:
        return ""
    elif len(other_items) > 1:
        return ""    
    other_item = other_items[0]
    
    # Calculate Opportunity Cost for producing the specified item
    # Opportunity Cost = Minutes per item / Minutes per other_item
    df = df.copy()  # To avoid SettingWithCopyWarning
    df['Opportunity Cost'] = df[item] / df[other_item]
    
    # Sort the DataFrame based on Opportunity Cost in ascending order
    df_sorted = df.sort_values('Opportunity Cost')
    
    # Assign the specified number of people to produce the desired item
    assigned = df_sorted.head(num_assigned)
    
    # The rest of the people will produce the other item
    non_assigned = df_sorted.tail(len(df_sorted) - num_assigned)
    
    # Calculate total production for the assigned group
    total_item = (working_time / assigned[item]).sum()
    
    # Calculate total production for the non-assigned group
    total_other_item = (working_time / non_assigned[other_item]).sum()
    
    # Prepare the result dictionary with pluralized item names
    production_totals = {
        f"{item}s": round(total_item, 2),
        f"{other_item}s": round(total_other_item, 2)
    }

    # Convert the dictionary to a string for output
    result = ', '.join([f"{value} {key}" for key, value in production_totals.items()])
    
    return result

calculate_production(arg1, arg2, arg3, arg4)