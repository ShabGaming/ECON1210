import pandas as pd

def SubsidyDiscrete(subsidy, df):

    # Ensure df is a DataFrame before proceeding
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    # Set the first row as column headers
    df.columns = df.iloc[0]
    # Remove the first row
    df = df[1:]
    # Reset the index to start from 0
    df = df.reset_index(drop=True)

    # If subsidy is not a number or is negative, return nothing
    if not isinstance(subsidy, (int, float)) or subsidy < 0:
        return ""
    # If df is empty, return nothing
    if df.empty:
        return ""

    # Ensure the DataFrame has the correct columns
    required_columns = {'Price', 'Quantity Demanded', 'Quantity Supplied'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    # Convert columns to numeric types to avoid comparison issues
    for column in required_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # Drop rows with NaN values in required columns
    df = df.dropna(subset=required_columns)

    # Iterate through the DataFrame to find equilibrium under subsidy
    for i in range(len(df)):
        price_consumer = df.loc[i, 'Price']  # Price paid by consumer
        price_producer = price_consumer + subsidy  # Price received by producer

        # Match quantities for equilibrium
        quantity_demanded = df.loc[i, 'Quantity Demanded']
        matching_suppliers = df[df['Price'] == price_producer]['Quantity Supplied']

        if not matching_suppliers.empty:
            quantity_supplied = matching_suppliers.iloc[0]
            if quantity_demanded == quantity_supplied:
                units_transacted = quantity_demanded
                gov_subsidy = units_transacted * subsidy

                return (f"Price paid by consumer: {price_consumer}, "
                        f"Price received by producer: {price_producer}, "
                        f"Units transacted: {units_transacted}, "
                        f"Gov Subsidy Expense: {gov_subsidy}")

    return ""


SubsidyDiscrete(arg1, arg2)