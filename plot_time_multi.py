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
args = parser.parse_args()

std = args.std
mean = args.mean
mode = args.mode
iterations = args.iterations
max_time_steps = args.time_steps

# Components to plot
components = [
    ('lifecycleManagerTime.dataRetrievalTime', 'Data Retrieval'),
    ('lifecycleManagerTime.minSatProblemTime', 'MinSat Problem'),
    ('lifecycleManagerTime.extraRoomTime', 'Extra Room'),
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
    folder_name = f"{mode}_{mean}_{std}_{i}_{max_time_steps}_True"
    with open(f'sim_output/{folder_name}/executions_time_step_times.json') as f:
        data = json.load(f)
    for entry in data:
        ts = entry['time_step']
        time_steps_set.add(ts)
        duration = entry['duration']
        if ts not in accumulator:
            accumulator[ts] = {label: [] for _, label in components}
        accumulator[ts]['Data Retrieval'].append(duration['lifecycleManagerTime']['dataRetrievalTime'] / 1000)
        accumulator[ts]['MinSat Problem'].append(duration['lifecycleManagerTime']['minSatProblemTime'] / 1000)
        accumulator[ts]['Extra Room'].append(duration['lifecycleManagerTime']['extraRoomTime'] / 1000)
        accumulator[ts]['Components Retrieval'].append(duration['componentsRetrievalTime'] / 1000)
        accumulator[ts]['Abs Time'].append(duration['absTime'] / 1000)
        accumulator[ts]['Allocation Time'].append(duration['solverTime']['solverTime'] / 1000)

print(accumulator[19]['Extra Room'])

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
        print(f"  25th percentile: {percentiles[0]:.4f} seconds")
        print(f"  50th percentile (median): {percentiles[1]:.4f} seconds")
        print(f"  75th percentile: {percentiles[2]:.4f} seconds")
        
        # Store results for export
        percentile_results[label] = {
            "25th_percentile": round(percentiles[0], 4),
            "50th_percentile": round(percentiles[1], 4),
            "75th_percentile": round(percentiles[2], 4),
            "total_samples": len(all_values)
        }
    else:
        print("  No data available.")
        percentile_results[label] = {
            "25th_percentile": None,
            "50th_percentile": None,
            "75th_percentile": None,
            "total_samples": 0
        }

# Export to JSON
output_filename = f"{mode}_{mean}_{std}_{iterations}_{max_time_steps}_percentiles"
with open(f'sim_output/{output_filename}.json', 'w') as f:
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
with open(f'sim_output/{output_filename}.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Component', '25th_Percentile_Seconds', '50th_Percentile_Seconds', '75th_Percentile_Seconds', 'Total_Samples'])
    for label, stats in percentile_results.items():
        writer.writerow([
            label,
            stats['25th_percentile'],
            stats['50th_percentile'], 
            stats['75th_percentile'],
            stats['total_samples']
        ])

print(f"\nPercentile statistics exported to:")
print(f"  JSON: sim_output/{output_filename}.json")
print(f"  CSV: sim_output/{output_filename}.csv")

plt.tight_layout()
plt.show()