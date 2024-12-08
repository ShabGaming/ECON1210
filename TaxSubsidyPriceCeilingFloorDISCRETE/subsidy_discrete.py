import pandas as pd

def SubsidyDiscrete(subsidy, df):
    
    df.columns = df.iloc[0]
    df = df[1:]

    # If subsidy is empty or not a number, or df is empty or not numeric reutrn nothing
    if not isinstance(subsidy, (int, float)) or subsidy < 0:
        return
    if not isinstance(subsidy, pd.DataFrame) or df.empty:
        return

    # Ensure the DataFrame has the correct columns
    if not set(['Price', 'Quantity Demanded', 'Quantity Supplied']).issubset(df.columns):
        raise ValueError("DataFrame must contain 'Price', 'Quantity Demanded', and 'Quantity Supplied' columns.")

    # Iterate through the DataFrame to find equilibrium under subsidy
    for i in range(len(df)):
        price_consumer = df.loc[i, 'Price']  # Price paid by consumer
        price_producer = price_consumer + subsidy  # Price received by producer

        # Match quantities for equilibrium
        quantity_demanded = df.loc[i, 'Quantity Demanded']
        quantity_supplied = df.loc[df['Price'] == price_producer, 'Quantity Supplied'].values

        if len(quantity_supplied) > 0 and quantity_demanded == quantity_supplied[0]:
            units_transacted = quantity_demanded
            gov_subsidy = units_transacted * subsidy

            return (f"Price paid by consumer: {price_consumer}, "
                    f"Price received by producer: {price_producer}, "
                    f"Units transacted: {units_transacted}, "
                    f"Gov Subsidy Expense: {gov_subsidy}")

    return

SubsidyDiscrete(arg1, arg2)