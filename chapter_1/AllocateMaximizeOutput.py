import pandas as pd

def AllocateMaximizeOutput(NumOfWorkerHired, production_df, ProduceAtleast=None):

    # The first row are the headers
    production_df.columns = production_df.iloc[0]
    production_df = production_df[1:]

    # if NumOfWorkerHired is not a number, or is empty, and if production_df is not a dataframe, or is empty, return nothing
    if not isinstance(NumOfWorkerHired, int) or NumOfWorkerHired <= 0 or not isinstance(production_df, pd.DataFrame) or production_df.empty:
        return None

    # Check the name of the first column, if it is not 'Number of Workers', then rename it
    if production_df.columns[0] != 'Number of Workers':
        production_df.rename(columns={production_df.columns[0]: 'Number of Workers'}, inplace=True)
    
    # Parse the input production dataframe
    lines = production_df.set_index('Number of Workers').to_dict(orient='list')
    print(production_df.head())
    # Function to calculate marginal outputs
    def calculate_marginal_output(workers_allocated):
        marginal_outputs = {}
        for line, output in lines.items():
            current_workers = workers_allocated.get(line, 0)
            if current_workers < len(output):
                marginal_outputs[line] = output[current_workers] - (output[current_workers - 1] if current_workers > 0 else 0)
            else:
                marginal_outputs[line] = 0
        return marginal_outputs

    # Allocate workers to maximize output
    workers_allocated = {line: 0 for line in lines.keys()}
    for _ in range(NumOfWorkerHired):
        marginal_outputs = calculate_marginal_output(workers_allocated)
        best_line = max(marginal_outputs, key=marginal_outputs.get)
        workers_allocated[best_line] += 1

    # Calculate the total output
    total_output = sum(lines[line][workers_allocated[line] - 1] for line in workers_allocated if workers_allocated[line] > 0)

    # Check the minimum workers for producing at least ProduceAtleast output
    min_workers_required = None
    if ProduceAtleast is not None:
        for n in range(1, sum(len(v) for v in lines.values()) + 1):
            temp_workers_allocated = {line: 0 for line in lines.keys()}
            for _ in range(n):
                marginal_outputs = calculate_marginal_output(temp_workers_allocated)
                best_line = max(marginal_outputs, key=marginal_outputs.get)
                temp_workers_allocated[best_line] += 1
            temp_total_output = sum(lines[line][temp_workers_allocated[line] - 1] for line in temp_workers_allocated if temp_workers_allocated[line] > 0)
            if temp_total_output >= ProduceAtleast:
                min_workers_required = (n, temp_workers_allocated)
                break

    # Prepare the result string
    result = ", ".join([f"Allocate {workers_allocated[line]} to {line}" for line in workers_allocated]) + "."
    if min_workers_required:
        min_workers, allocation = min_workers_required
        allocation_string = ", ".join([f"{allocation[line]} to {line}" for line in allocation])
        result += f" | Must allocate at least {min_workers} workers, where {allocation_string}."

    return result

AllocateMaximizeOutput(arg1, arg2, arg3)
