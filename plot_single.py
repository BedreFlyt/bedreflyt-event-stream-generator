import json
import matplotlib.pyplot as plt
# import argparse
import numpy as np
import sys

# parser = argparse.ArgumentParser("plot-multi.py")
# parser.add_argument("--std", help="Standard deviation", type=int, default="1")
# parser.add_argument("--mean", help="Mean", type=int, default="5")
# parser.add_argument("--mode", help="Mode from [normal, crisis, medium-crisis]", type=str, default="normal")
# parser.add_argument("--iterations", help="Iterations", type=int, default="10")
# parser.add_argument("--time_steps", help="Time steps to run", type=int, default="10")
# parser.add_argument("--adaptive", help="Use adaptive capacity", action=argparse.BooleanOptionalAction, default=True)
# parser.add_argument("--base", help="Base folder name", type=str, default="sim_output")
# args = parser.parse_args()

# std = args.std
# mean = args.mean
# mode = args.mode
# iterations = args.iterations
# max_time_steps = args.time_steps
# input_folder_name = args.base

folder = sys.argv[1]

# Dictionary to accumulate capacity data across all iterations
accumulated_ward_data = {}

# Load and accumulate data from all iterations
# for i in range(iterations+1):
#     if i == iterations:
#         break
#     folder_name = f"{mode}_{mean}_{std}_{i}_{max_time_steps}_{args.adaptive}"

#     with open(f'{input_folder_name}/{folder_name}/allocation_results.json') as f:
#         data = json.load(f)

#     # Extract allocations only
#     allocations = data['allocations']

#     # Organize data by ward
#     wards = set(item['ward'] for item in allocations)

#     for item in allocations:
#         ward = item['ward']
#         time_step = item['time_step']
#         allocation = item['allocations']

#         # Initialize ward data structure if not exists
#         if ward not in accumulated_ward_data:
#             accumulated_ward_data[ward] = {}
        
#         # Initialize time step data if not exists
#         if time_step not in accumulated_ward_data[ward]:
#             accumulated_ward_data[ward][time_step] = []

#         # Accumulate allocation values
#         accumulated_ward_data[ward][time_step].append(allocation)

with open(f'{folder}/allocation_results.json') as f:
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

print(accumulated_ward_data)

# Calculate averages, 25th and 75th percentiles and prepare plot data
ward_statistics = {}
for ward, time_data in accumulated_ward_data.items():
    ward_statistics[ward] = {
        'averages': {},
        'percentile_25': {},
        'percentile_75': {}
    }
    ward_statistics[ward]['averages'][0] = 0  # Ensure time step 0 is included with 0 allocation
    ward_statistics[ward]['percentile_25'][0] = 0
    ward_statistics[ward]['percentile_75'][0] = 0
    
    for time_step, capacity_list in time_data.items():
        # ward_statistics[ward]['averages'][time_step] = np.mean(capacity_list)
        ward_statistics[ward]['averages'][time_step] = np.percentile(capacity_list, 50)
        ward_statistics[ward]['percentile_25'][time_step] = np.percentile(capacity_list, 25)
        ward_statistics[ward]['percentile_75'][time_step] = np.percentile(capacity_list, 75)


accumulated_capacity_data = {}

# Load and accumulate data for capacities from all iterations
# for i in range(iterations+1):
#     if i == iterations:
#         break
#     folder_name = f"{mode}_{mean}_{std}_{i}_{max_time_steps}_{args.adaptive}"

with open(f'{folder}/allocation_results.json') as f:
    data = json.load(f)

# Extract capacities
capacities = data['capacities']

# Organize data by ward
for item in capacities:
    ward = item['ward']
    time_step = item['time_step']
    capacity = item['total_capacity']

    # Initialize ward data structure if not exists
    if ward not in accumulated_capacity_data:
        accumulated_capacity_data[ward] = {}
    
    # Initialize time step data if not exists
    if time_step not in accumulated_capacity_data[ward]:
        accumulated_capacity_data[ward][time_step] = []

    # Accumulate capacity values
    accumulated_capacity_data[ward][time_step].append(capacity)


# Calculate averages, 25th and 75th percentiles for capacities
capacity_statistics = {}
for ward, time_data in accumulated_capacity_data.items():
    capacity_statistics[ward] = {
        'averages': {},
        'percentile_25': {},
        'percentile_75': {}
    }
    capacity_statistics[ward]['averages'][0] = 0  # Ensure time step 0 is included with 0 capacity
    capacity_statistics[ward]['percentile_25'][0] = 0
    capacity_statistics[ward]['percentile_75'][0] = 0
    
    for time_step, capacity_list in time_data.items():
        # capacity_statistics[ward]['averages'][time_step] = np.mean(capacity_list)
        capacity_statistics[ward]['averages'][time_step] = np.percentile(capacity_list, 50)
        capacity_statistics[ward]['percentile_25'][time_step] = np.percentile(capacity_list, 25)
        capacity_statistics[ward]['percentile_75'][time_step] = np.percentile(capacity_list, 75)

# Create single plot with averaged data and percentiles
plt.figure(figsize=(15, 7))

allocation_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']
capacity_colors = ['tab:red', 'tab:pink', 'tab:cyan', 'tab:gray', 'tab:blue', 'tab:red']

# Get all unique time steps for consistent x-axis labeling
all_time_steps = set()
for ward_data in ward_statistics.values():
    all_time_steps.update(ward_data['averages'].keys())
for ward_data in capacity_statistics.values():
    all_time_steps.update(ward_data['averages'].keys())
time_steps_sorted = sorted(all_time_steps)
x_indices = range(len(time_steps_sorted))

for i, (ward, stats) in enumerate(ward_statistics.items()):
    ward_time_steps = sorted(stats['averages'].keys())
    avg_allocations = [stats['averages'][time_step] for time_step in ward_time_steps]
    p25_allocations = [stats['percentile_25'][time_step] for time_step in ward_time_steps]
    p75_allocations = [stats['percentile_75'][time_step] for time_step in ward_time_steps]
    
    # Map ward time steps to global x indices
    ward_x_indices = [time_steps_sorted.index(ts) for ts in ward_time_steps]
    
    color = allocation_colors[i % len(allocation_colors)]
    ward_name = ward.split("_")[0]
    
    # Plot averaged allocations as lines using indices
    plt.plot(ward_x_indices, avg_allocations, 
             label=f'Allocations', 
             marker='o', 
             color=color, 
             linewidth=2)
    
    # Plot percentiles as lighter lines using indices
    # plt.plot(ward_x_indices, p25_allocations, 
    #          color=color, 
    #          linestyle='-.', 
    #          alpha=0.7, 
    #          linewidth=1.3,
    #          label=f'Allocations 25th percentile')
    
    # plt.plot(ward_x_indices, p75_allocations, 
    #          color=color, 
    #          linestyle=':', 
    #          alpha=0.7, 
    #          linewidth=1.3,
    #          label=f'Allocations 75th percentile')
    
    # Fill area between 25th and 75th percentiles using indices
    plt.fill_between(ward_x_indices, p25_allocations, p75_allocations, 
                     color=color, alpha=0.2)
    
# Add capacities to the same plot
for i, (ward, stats) in enumerate(capacity_statistics.items()):
    ward_time_steps = sorted(stats['averages'].keys())
    avg_capacities = [stats['averages'][time_step] for time_step in ward_time_steps]
    # p25_capacities = [stats['percentile_25'][time_step] for time_step in ward_time_steps]
    # p75_capacities = [stats['percentile_75'][time_step] for time_step in ward_time_steps]
    
    # Map ward time steps to global x indices
    ward_x_indices = [time_steps_sorted.index(ts) for ts in ward_time_steps]
    
    color = capacity_colors[i % len(capacity_colors)]
    ward_name = ward.split("_")[0]
    
    # Plot capacities with dashed lines using indices
    plt.plot(ward_x_indices, avg_capacities, 
             label=f'Capacities', 
             marker='x', 
             color=color, 
             linestyle='--', 
             linewidth=2)
    # Plot percentiles as lighter lines using indices
    # plt.plot(ward_x_indices, p25_capacities, 
    #          color=color, 
    #          linestyle='-.', 
    #          alpha=0.7, 
    #          linewidth=1.3,
    #          label=f'Capacity 25th percentile')
    
    # plt.plot(ward_x_indices, p75_capacities, 
    #          color=color, 
    #          linestyle=':', 
    #          alpha=0.7, 
    #          linewidth=1.3,
    #          label=f'Capacity 75th percentile')
    # plt.fill_between(ward_x_indices, p25_capacities, p75_capacities, 
    #                  color=color, alpha=0.2)

plt.title(f'Adaptation of capacity over time with varying allocations', fontsize=14)
plt.xlabel('Time step', fontsize=12)
plt.ylabel('Allocations and Capacity Counts', fontsize=12)
plt.grid(True)

# Set x-tick labels to show actual time step values
plt.xticks(x_indices, time_steps_sorted)

plt.axhline(y=40, color='green', linestyle='--', linewidth=2.5, label='Load threshold')
plt.axhline(y=45, color='purple', linestyle='-', linewidth=2.5, label='Initial ward capacity')
plt.axhline(y=49, color='brown', linestyle=':', linewidth=2.5, label='Ward capacity with office 1')
plt.axhline(y=53, color='silver', linestyle='-.', linewidth=2.5, label='Ward capacity with office 1 and 2')
plt.axhline(y=93, color='red', linestyle=(0, (3, 5, 1, 5)), linewidth=2.5, label='Maximum ward capacity')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()