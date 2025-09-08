import json
import matplotlib.pyplot as plt
import sys

# mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
# mode = "normal"
folder_name = sys.argv[1] if len(sys.argv) > 1 else "normal_40_9_0_20"

# Load the JSON data
with open(f'sim_output/{folder_name}/allocation_results.json') as f:
    data = json.load(f)

# Extract capacities and allocations
capacities = data['capacities']
allocations = data['allocations']

# Organize data by ward
wards = set(item['ward'] for item in capacities)
ward_data = {ward: {'capacities': {}, 'allocations': {}} for ward in wards}

for item in capacities:
    ward_data[item['ward']]['capacities'][item['time_step']] = item['total_capacity']

for item in allocations:
    ward_data[item['ward']]['allocations'][item['time_step']] = item['allocations']

# Combine capacities and allocations into a single dataset
for ward, values in ward_data.items():
    combined_data = []
    combined_data.append({
        'time_step': 0,
        'capacity': values['capacities'].get(0, 0),
        'allocation': values['allocations'].get(0, 0)
    })
    time_steps = sorted(set(values['capacities'].keys()).union(values['allocations'].keys()))
    for time_step in time_steps:
        combined_data.append({
            'time_step': time_step,
            'capacity': values['capacities'].get(time_step, 0),
            'allocation': values['allocations'].get(time_step, 0)
        })
    ward_data[ward]['combined'] = combined_data

# Plot the data using the combined dataset
plt.figure(figsize=(15, 7))

# Offset bars for different wards to display them side by side
bar_width = 0.6
colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']

for i, (ward, values) in enumerate(ward_data.items()):
    combined_data = values['combined']
    time_steps = [item['time_step'] for item in combined_data]
    capacities = [item['capacity'] for item in combined_data]
    allocations = [item['allocation'] for item in combined_data]
    x_indices = range(len(time_steps))

    # Plot capacities as bars (touching, shifted left by half width)
    shifted_x = [x - bar_width / 2 for x in x_indices]
    plt.bar(shifted_x, capacities, width=bar_width, label=f'{ward.split("_")[0]} Capacities', color=colors[i % len(colors)+1], alpha=0.7, align='edge')
    # plt.plot(x_indices, capacities, label=f'{ward.split("_")[0]} Capacities', marker='s', linestyle='--')

    # Plot allocations as lines
    plt.plot(x_indices, allocations, label=f'{ward.split("_")[0]} Allocations', marker='o', color=colors[i % len(colors)], linestyle='--')

plt.title('Capacities and Allocations requests for all wards')
plt.xlabel('Time step')
plt.ylabel('Count')
plt.grid(True)
plt.xticks(x_indices, time_steps)
plt.axhline(y=40, color='green', linestyle='--', linewidth=1, label='Adaptation threshold')
plt.axhline(y=45, color='purple', linestyle='--', linewidth=1, label='Initial capacity')
plt.legend()
plt.show()
