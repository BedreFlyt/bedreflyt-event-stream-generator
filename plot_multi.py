import json
import matplotlib.pyplot as plt
import argparse

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

# Dictionary to accumulate capacity data across all iterations
accumulated_ward_data = {}

# Load and accumulate data from all iterations
for i in range(iterations+1):
    folder_name = f"{mode}_{mean}_{std}_{i}_{max_time_steps}"

    with open(f'sim_output/{folder_name}/allocation_results.json') as f:
        data = json.load(f)

    # Extract allocations only
    allocations = data['allocations']

    # Organize data by ward
    wards = set(item['ward'] for item in allocations)

    for item in allocations:
        ward = item['ward']
        time_step = item['time_step']
        allocation = item['allocations']

        # Initialize ward data structure if not exists
        if ward not in accumulated_ward_data:
            accumulated_ward_data[ward] = {}
        
        # Initialize time step data if not exists
        if time_step not in accumulated_ward_data[ward]:
            accumulated_ward_data[ward][time_step] = []

        # Accumulate allocation values
        accumulated_ward_data[ward][time_step].append(allocation)

# Calculate averages and prepare plot data
ward_averages = {}
for ward, time_data in accumulated_ward_data.items():
    ward_averages[ward] = {}
    ward_averages[ward][0] = 0  # Ensure time step 0 is included with 0 allocation
    for time_step, capacity_list in time_data.items():
        ward_averages[ward][time_step] = sum(capacity_list) / len(capacity_list)

# Create single plot with averaged data
plt.figure(figsize=(15, 7))

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']

# Get all unique time steps for consistent x-axis labeling
all_time_steps = set()
for ward_data in ward_averages.values():
    all_time_steps.update(ward_data.keys())
time_steps_sorted = sorted(all_time_steps)
x_indices = range(len(time_steps_sorted))

for i, (ward, time_data) in enumerate(ward_averages.items()):
    time_steps_sorted = sorted(time_data.keys())
    avg_capacities = [time_data[time_step] for time_step in time_steps_sorted]
    
    # Plot averaged capacities as lines
    plt.plot(time_steps_sorted, avg_capacities, 
             label=f'{ward.split("_")[0]} Avg Capacity', 
             marker='o', 
             color=colors[i % len(colors)], 
             linewidth=2)

plt.title(f'Average Allocations across {iterations+1} iterations ({mode} mode)')
plt.xlabel('Time step')
plt.ylabel('Allocations and Capacity Counts')
plt.grid(True)

# Set x-tick labels to show actual time step values
plt.xticks(x_indices, time_steps_sorted)

plt.axhline(y=40, color='green', linestyle='--', linewidth=1.5, label='Adaptation threshold')
plt.axhline(y=45, color='purple', linestyle='--', linewidth=1.5, label='Initial capacity')
plt.axhline(y=47, color='orange', linestyle='--', linewidth=1.5, label='With extra office 1')
plt.axhline(y=49, color='brown', linestyle='--', linewidth=1.5, label='With extra office 2')
plt.axhline(y=89, color='red', linestyle='--', linewidth=1.5, label='With corridor')
plt.legend()
plt.show()