import pandas as pd

def AllocateMinimizeCost(NumOfHours, cost_df, BenefitPerResource=None):

    # The first row are the headers
    cost_df.columns = cost_df.iloc[0]
    cost_df = cost_df[1:]

    print(cost_df.head())

    # Calculate marginal costs
    marginal_costs = cost_df.iloc[:, 1:].diff().fillna(cost_df.iloc[:, 1:])

    # Flatten marginal costs to allocate for minimizing cost
    flattened_costs = []
    for col in marginal_costs.columns:
        flattened_costs.extend([(marginal_costs.at[i, col], i + 1, col) for i in range(len(marginal_costs))])
    
    # Sort by marginal cost
    flattened_costs.sort()

    allocation = {worker: 0 for worker in cost_df.columns[1:]}
    for cost, hour, worker in flattened_costs:
        if NumOfHours > 0:
            allocation[worker] += 1
            NumOfHours -= 1
        else:
            break

    minimize_allocation_result = "To minimize cost allocate " + ", ".join(
        f"{hours} hour{'s' if hours > 1 else ''} to {worker}"
        for worker, hours in allocation.items()
        if hours > 0
    )

    maximize_allocation_result = ""

    # Economic surplus calculation if BenefitPerResource is provided
    if BenefitPerResource:
        surplus_allocation = {worker: 0 for worker in cost_df.columns[1:]}

        for worker in cost_df.columns[1:]:
            for hour in range(len(cost_df)):
                if BenefitPerResource >= marginal_costs.at[hour, worker]:
                    surplus_allocation[worker] = hour + 1
                else:
                    break

        maximize_allocation_result = "\nTo maximize economic surplus allocate " + ", ".join(
            f"{worker}: {hours} hour{'s' if hours > 1 else ''}"
            for worker, hours in surplus_allocation.items()
            if hours > 0
        )

    return minimize_allocation_result + maximize_allocation_result


AllocateMinimizeCost(arg1, arg2, arg3)