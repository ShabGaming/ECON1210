import pandas as pd

def TaxDiscrete(tax, df):

    df.columns = df.iloc[0]
    df = df[1:]

    # If tax is empty or not a number, or df is empty or not numeric reutrn nothing
    if not isinstance(tax, (int, float)) or tax < 0:
        return
    if not isinstance(df, pd.DataFrame) or df.empty:
        return

    # Ensure the DataFrame has the correct columns
    if not set(['Price', 'Quantity Demanded', 'Quantity Supplied']).issubset(df.columns):
        return 

    # Iterate through the DataFrame to find equilibrium under tax
    for i in range(len(df)):
        price_consumer = df.loc[i, 'Price']  # Price paid by consumer
        price_producer = price_consumer - tax  # Price received by producer

        # Match quantities for equilibrium
        quantity_demanded = df.loc[i, 'Quantity Demanded']
        quantity_supplied = df.loc[df['Price'] == price_producer, 'Quantity Supplied'].values

        if len(quantity_supplied) > 0 and quantity_demanded == quantity_supplied[0]:
            units_transacted = quantity_demanded
            gov_revenue = units_transacted * tax

            return (f"Price paid by consumer: {price_consumer}, "
                    f"Price received by producer: {price_producer}, "
                    f"Units transacted: {units_transacted}, "
                    f"Gov Revenue: {gov_revenue}")

    return

TaxDiscrete(arg1, arg2)