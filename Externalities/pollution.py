import re
import pandas as pd

def calculate_equilibrium(df, allow_trade=None, negotiation_cost=None):
    if df.empty:
        return ""
    
    if allow_trade is None:
        allow_trade = True
    
    if negotiation_cost is None:
        negotiation_cost = 0

    # Set the first row as column headers
    df.columns = df.iloc[0]
    # Remove the first row
    df = df[1:]
    # Reset the index to start from 0
    df = df.reset_index(drop=True)

    initial_emissions = {}

    # Reterive initial emissions from the dataframe
    for _, row in df.iterrows():
        firm = row['Firm']
        emissions = row['Initial']
        initial_emissions[firm] = emissions

    # Parse MC equations to extract 'a' and 'b' from the format "MC = a + b x".
    # We assume each equation is well-formed.
    a_params = {}
    b_params = {}
    firm_permits = {}
    firm_names = df['Firm'].tolist()

    # Parse each row
    for _, row in df.iterrows():
        firm = row['Firm']
        eq_str = row['MC Equation']
        permits = row['permits']

        # Extract a and b from the equation "MC = a + b x"
        # Using a regex to find numeric values
        # We expect something like: MC = 862 + 2.4x
        # We can split by '=' and parse the right-hand side
        # A quick approach: remove 'MC = ' then split by '+' and parse out numbers
        # Another approach: a regex like r'MC = ([0-9.]+)\s*\+\s*([0-9.]+)x'
        match = re.search(r'MC\s*=\s*([0-9\.]+)\s*\+\s*([0-9\.]+)x', eq_str)
        if not match:
            raise ValueError(f"MC equation format not recognized for firm {firm}")

        a = float(match.group(1))
        b = float(match.group(2))

        a_params[firm] = a
        b_params[firm] = b
        firm_permits[firm] = permits

    # If trading is not allowed:
    # Each firm just emits the amount of permits they have.
    # If trading is allowed:
    # We solve for the equilibrium price p and find each firm's emissions.

    total_permits = sum(firm_permits.values())

    # Q_i are initial emissions
    total_initial = sum(initial_emissions[firm] for firm in firm_names)

    if not allow_trade:
        # Without trading, each firm emits exactly its permits.
        results = []
        for firm in firm_names:
            emissions = firm_permits[firm]
            results.append(f"{firm} will produce {emissions:.2f} tons of smoke.")
        return " ".join(results)

    else:
        # With trading, find the equilibrium MC (p).
        # p = [ (sum(Q_i)-sum(permits) + sum(a_i/b_i)) / sum(1/b_i) ]
        sum_a_over_b = sum(a_params[firm]/b_params[firm] for firm in firm_names)
        sum_one_over_b = sum(1/b_params[firm] for firm in firm_names)

        numerator = (total_initial - total_permits) + sum_a_over_b
        p = numerator / sum_one_over_b

        # Now find each firm's reduction and emissions
        # R_i = (p - a_i)/b_i
        # E_i = Q_i - R_i
        results = []
        for firm in firm_names:
            a = a_params[firm]
            b = b_params[firm]
            Q_i = initial_emissions[firm]

            R_i = (p - a) / b
            E_i = Q_i - R_i

            results.append(f"{firm} will produce {E_i:.2f} tons of smoke.")
        return " ".join(results)

calculate_equilibrium(arg1, arg2)