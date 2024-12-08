import pandas as pd

def calculate_production(working_time, item_name, number_of_item, df):
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
    if item_name not in df.columns:
        return ""
    
    # Determine the other_item
    item_columns = [col for col in df.columns if col != 'Person']
    if len(item_columns) != 2:
        return ""
    
    other_item = [col for col in item_columns if col != item_name][0]
    
    # Sort the DataFrame by item_time ascendingly (most efficient producers first)
    df_sorted = df.sort_values(by=item_name, ascending=True).reset_index(drop=True)
    
    items_remaining = number_of_item
    other_item_total = 0.0

    for idx, row in df_sorted.iterrows():
        if items_remaining > 0:
            # Maximum items this worker can produce
            max_items_worker_can_produce = items_remaining
            time_needed = max_items_worker_can_produce * row[item_name]
            
            if time_needed <= working_time:
                # Assign the required number of items to this worker
                items_assigned = max_items_worker_can_produce
                time_spent = time_needed
            else:
                # Assign as many items as possible within working_time
                items_assigned = working_time / row[item_name]
                time_spent = items_assigned * row[item_name]
            
            # Update the remaining items to assign
            items_remaining -= items_assigned
            
            # Calculate remaining time for other_item production
            remaining_time = working_time - time_spent
            
            # Calculate other_item produced by this worker
            other_item_produced = remaining_time / row[other_item]
            other_item_total += other_item_produced
        else:
            # No items to assign, assign full time to produce other_item
            other_item_produced = working_time / row[other_item]
            other_item_total += other_item_produced
    
    # Check if all items have been assigned
    if items_remaining > 1e-6:
        return ""
    
    # Prepare the result dictionary with pluralized item names
    production_totals = {
        f"{item_name}s": number_of_item,
        f"{other_item}s": round(other_item_total, 2)
    }
    
    # Convert the dictionary to a string for output
    result = ', '.join([f"{value} {key}" for key, value in production_totals.items()])

    return result


# Create the DataFrame based on the problem
data = {
    'Person': ['Clara', 'Kant', 'Leo'],
    'hat': [15, 17, 9],
    'tie': [7.65, 11.54, 23.33]
}

df = pd.DataFrame(data)

# Parameters
working_time = 630  # minutes per day
item_name = 'hat'
number_of_item = 69

# Calculate production
production = calculate_production(working_time, item_name, number_of_item, df)

print(production)