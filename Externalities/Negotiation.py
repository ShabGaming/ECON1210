import pandas as pd

def Negotiation(df, cost_neg_beneficiary=None, cost_neg_affected=None):
    if df is None:
        return ""

    # Set the first row as column headers
    df.columns = df.iloc[0]
    # Remove the first row
    df = df[1:]
    # Reset the index to start from 0
    df = df.reset_index(drop=True)

    # Drop the first column
    df = df.drop(df.columns[0], axis=1)

    processes = df.columns
    
    # We assume the first column is already the first process column (no extra index column)
    # If there's an index column or different structure, adjust as necessary.
    
    # Calculate net benefits for each process
    beneficiary_values = df.iloc[0]
    affected_values = df.iloc[1]
    
    # Social efficiency: Choose process with max (BeneficiaryGain - AffectedDamage)
    net_benefits = beneficiary_values - affected_values
    socially_efficient_process = net_benefits.idxmax()
    
    # Scenario 1: Beneficiary has full rights (not liable), zero negotiation cost
    # Beneficiary initially chooses the process that maximizes their gain alone.
    beneficiary_initial_choice = beneficiary_values.idxmax()
    # With zero negotiation cost, they will bargain to achieve the socially efficient outcome.
    chosen_when_beneficiary_not_liable_zero_cost = socially_efficient_process
    
    # Scenario 2: Affected has full rights (Beneficiary liable), zero negotiation cost
    # Beneficiary chooses process to maximize (Gain - Damage)
    chosen_when_beneficiary_liable_zero_cost = net_benefits.idxmax()
    
    # Scenario 3 (optional): Beneficiary has full rights (not liable) with affected negotiation cost
    if cost_neg_affected is not None:
        # Check if switching from initial choice to socially efficient choice is beneficial after negotiation cost
        if beneficiary_initial_choice != socially_efficient_process:
            damage_saved = affected_values[beneficiary_initial_choice] - affected_values[socially_efficient_process]
            compensation_needed = beneficiary_values[beneficiary_initial_choice] - beneficiary_values[socially_efficient_process]
            surplus = damage_saved - compensation_needed
            
            if surplus > cost_neg_affected:
                # They will negotiate and switch to socially efficient
                chosen_when_beneficiary_not_liable_with_affected_cost = socially_efficient_process
            else:
                # Not worth negotiating, stay at beneficiary's initial choice
                chosen_when_beneficiary_not_liable_with_affected_cost = beneficiary_initial_choice
        else:
            # Already at socially efficient, no need to negotiate
            chosen_when_beneficiary_not_liable_with_affected_cost = beneficiary_initial_choice
    else:
        chosen_when_beneficiary_not_liable_with_affected_cost = None
    
    # Scenario 4 (optional): Affected has full rights (beneficiary liable) with beneficiary negotiation cost
    # If beneficiary is liable, they pick the socially efficient from the start.
    # Negotiation cost for beneficiary is irrelevant because no negotiation needed.
    if cost_neg_beneficiary is not None:
        chosen_when_beneficiary_liable_with_beneficiary_cost = chosen_when_beneficiary_liable_zero_cost
    else:
        chosen_when_beneficiary_liable_with_beneficiary_cost = None

    # Build output string
    output = []
    output.append(f"Socially Efficient to adopt: {socially_efficient_process}")
    output.append(f"Beneficiary has full rights (Not liable) (negotiation costs are negligible), Process Chosen: {chosen_when_beneficiary_not_liable_zero_cost}")
    output.append(f"AffectedPerson has full rights (Beneficiary liable) (negotiation costs are negligible), Process Chosen: {chosen_when_beneficiary_liable_zero_cost}")
    
    if chosen_when_beneficiary_not_liable_with_affected_cost is not None:
        output.append(f"Beneficiary has full rights (Not liable) (negotiation costs for Affected Entity = {cost_neg_affected}), Process Chosen: {chosen_when_beneficiary_not_liable_with_affected_cost}")
        
    if chosen_when_beneficiary_liable_with_beneficiary_cost is not None:
        output.append(f"AffectedPerson has full rights (Beneficiary liable) (negotiation costs for Beneficiary = {cost_neg_beneficiary}), Process Chosen: {chosen_when_beneficiary_liable_with_beneficiary_cost}")

    return "\n".join(output)

Negotiation(arg1, arg2, arg3)