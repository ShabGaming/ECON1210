def PriceControl(price_ceiling=None, price_floor=None, df=None):
    df.columns = df.iloc[0]
    df = df[1:]

    # Ensure the DataFrame has the correct columns
    if df is None or not set(['Price', 'Quantity Demanded', 'Quantity Supplied']).issubset(df.columns):
        raise ValueError("DataFrame must contain 'Price', 'Quantity Demanded', and 'Quantity Supplied' columns.")

    ceiling_result = None
    floor_result = None

    if price_ceiling == 0:
        price_ceiling = None
    if price_floor == 0:
        price_floor = None

    # Handle price ceiling
    if price_ceiling is not None:
        for i in range(len(df)):
            if df.loc[i, 'Price'] <= price_ceiling:
                quantity_transacted = min(df.loc[i, 'Quantity Demanded'], df.loc[i, 'Quantity Supplied'])
                ceiling_result = f"Price Ceiling: {price_ceiling}, Quantity Transacted: {quantity_transacted}"
                break

    # Handle price floor
    if price_floor is not None:
        for i in range(len(df)):
            if df.loc[i, 'Price'] >= price_floor:
                quantity_transacted = min(df.loc[i, 'Quantity Demanded'], df.loc[i, 'Quantity Supplied'])
                floor_result = f"Price Floor: {price_floor}, Quantity Transacted: {quantity_transacted}"
                break

    results = []
    if ceiling_result:
        results.append(ceiling_result)
    if floor_result:
        results.append(floor_result)

    return results

PriceControl(arg1, arg2, arg3)