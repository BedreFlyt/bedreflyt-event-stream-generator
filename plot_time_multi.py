import json
import matplotlib.pyplot as plt
import argparse
import numpy as np

parser = argparse.ArgumentParser("plot-multi.py")
parser.add_argument("--std", help="Standard deviation", type=int, default="1")
parser.add_argument("--mean", help="Mean", type=int, default="5")
parser.add_argument("--mode", help="Mode from [normal, crisis, medium-crisis]", type=str, default="normal")
parser.add_argument("--iterations", help="Iterations", type=int, default="10")
parser.add_argument("--time_steps", help="Time steps to run", type=int, default="10")
parser.add_argument("--adaptive", help="Use adaptive capacity", action=argparse.BooleanOptionalAction, default=True)
parser.add_argument("--base", help="Base folder name", type=str, default="sim_output")
args = parser.parse_args()

std = args.std
mean = args.mean
mode = args.mode
iterations = args.iterations
max_time_steps = args.time_steps
input_folder_name = args.base

# Components to plot
components = [
    ('lifecycleManagerTime.dataRetrievalTime', 'Data Retrieval'),
    ('lifecycleManagerTime.minSatProblemTime', 'MinSat Problem'),
    ('lifecycleManagerTime.extraRoomTime', 'SMOL Adaptation'),
    ('componentsRetrievalTime', 'Components Retrieval'),
    ('absTime', 'Abs Time'),
    ('solverTime', 'Allocation Time')
]

# Collect all individual values for box plots
accumulator = {}
time_steps_set = set()
print(iterations)

for i in range(iterations):
    print(i)
    folder_name = f"{mode}_{mean}_{std}_{i}_{max_time_steps}_{args.adaptive}"
    with open(f'{input_folder_name}/{folder_name}/executions_time_step_times.json') as f:
        data = json.load(f)
    for entry in data:
        ts = entry['time_step']
        time_steps_set.add(ts)
        duration = entry['duration']
        if ts not in accumulator:
            accumulator[ts] = {label: [] for _, label in components}
        accumulator[ts]['Data Retrieval'].append(duration['lifecycleManagerTime']['dataRetrievalTime'] / 1000)
        accumulator[ts]['MinSat Problem'].append(duration['lifecycleManagerTime']['minSatProblemTime'] / 1000)
        accumulator[ts]['SMOL Adaptation'].append(duration['lifecycleManagerTime']['extraRoomTime'] / 1000)
        accumulator[ts]['Components Retrieval'].append(duration['componentsRetrievalTime'] / 1000)
        abs_time_seconds = duration['absTime'] / 1000
        if abs_time_seconds <= 1000:
            accumulator[ts]['Abs Time'].append(abs_time_seconds)
        accumulator[ts]['Allocation Time'].append(duration['solverTime']['solverTime'] / 1000)

print(accumulator[19]['SMOL Adaptation'])

# Prepare data for box plots
time_steps = sorted(list(time_steps_set))

# Create subplots for each component
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

for i, (_, label) in enumerate(components):
    # Prepare data for this component across all time steps
    box_data = []
    labels = []
    for ts in time_steps:
        if ts in accumulator and accumulator[ts][label]:
            box_data.append(accumulator[ts][label])
            labels.append(f'{ts}')
    
    # Create box plot
    if box_data:
        axes[i].boxplot(box_data, labels=labels)
        axes[i].set_title(f'{label} Distribution')
        axes[i].set_ylabel('Time (seconds)')
        axes[i].set_xlabel('Time Step')
        axes[i].tick_params(axis='x', rotation=45)

percentile_results = {}
for i, (_, label) in enumerate(components):
    print(f"{label}:")
    all_values = []
    for ts in time_steps:
        if ts in accumulator and accumulator[ts][label]:
            all_values.extend(accumulator[ts][label])
    if all_values:
        percentiles = np.percentile(all_values, [25, 50, 75])
        average = np.mean(all_values)
        std_dev = np.std(all_values, ddof=1)  # Using sample standard deviation (ddof=1)
        
        print(f"  25th percentile: {percentiles[0]:.4f} seconds")
        print(f"  50th percentile (median): {percentiles[1]:.4f} seconds")
        print(f"  75th percentile: {percentiles[2]:.4f} seconds")
        print(f"  Average: {average:.4f} seconds")
        print(f"  Standard deviation: {std_dev:.4f} seconds")
        print(f"  Max value: {max(all_values):.4f} seconds")
        
        # Store results for export
        percentile_results[label] = {
            "25th_percentile": round(percentiles[0], 4),
            "50th_percentile": round(percentiles[1], 4),
            "75th_percentile": round(percentiles[2], 4),
            "average": round(average, 4),
            "standard_deviation": round(std_dev, 4),
            "total_samples": len(all_values),
            "max_value": round(max(all_values), 4),
            "min_value": round(min(all_values), 4)
        }
    else:
        print("  No data available.")
        percentile_results[label] = {
            "25th_percentile": None,
            "50th_percentile": None,
            "75th_percentile": None,
            "average": None,
            "standard_deviation": None,
            "total_samples": 0,
            "max_value": None,
            "min_value": None
        }

# Export to JSON
output_filename = f"{mode}_{mean}_{std}_{iterations}_{max_time_steps}_percentiles"
with open(f'{input_folder_name}/{output_filename}.json', 'w') as f:
    json.dump({
        "simulation_parameters": {
            "mode": mode,
            "mean": mean,
            "std": std,
            "iterations": iterations,
            "max_time_steps": max_time_steps
        },
        "percentile_statistics": percentile_results
    }, f, indent=2)

# Export to CSV
import csv
with open(f'{input_folder_name}/{output_filename}.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Component', '25th_Percentile_Seconds', '50th_Percentile_Seconds', '75th_Percentile_Seconds', 'Average_Seconds', 'Standard_Deviation_Seconds', 'Total_Samples', 'Max_Value_Seconds', 'Min_Value_Seconds'])
    for label, stats in percentile_results.items():
        writer.writerow([
            label,
            stats['25th_percentile'],
            stats['50th_percentile'], 
            stats['75th_percentile'],
            stats['average'],
            stats['standard_deviation'],
            stats['total_samples'],
            stats['max_value'],
            stats['min_value']
        ])

print(f"\nPercentile statistics exported to:")
print(f"  JSON: {input_folder_name}/{output_filename}.json")
print(f"  CSV: {input_folder_name}/{output_filename}.csv")

plt.tight_layout()
plt.show()