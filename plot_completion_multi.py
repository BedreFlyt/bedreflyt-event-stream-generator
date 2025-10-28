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
args = parser.parse_args()

std = args.std
mean = args.mean
mode = args.mode
iterations = args.iterations
max_time_steps = args.time_steps

# Dictionary to store completion data for each iteration
completion_data_by_iteration = {}

# Load completion data from all iterations
for i in range(iterations):
    folder_name = f"{mode}_{mean}_{std}_{i}_{max_time_steps}_{args.adaptive}"

    with open(f'sim_output/{folder_name}/allocation_results.json') as f:
        data = json.load(f)

    # Extract completion data only
    completions = data['completion']
    
    completion_data_by_iteration[i] = {}
    
    for item in completions:
        ward = item['ward']
        time_step = item['time_step']
        completes = item['completes']

        # Initialize ward data structure if not exists
        if ward not in completion_data_by_iteration[i]:
            completion_data_by_iteration[i][ward] = {}

        # Store completion count (1 if true, 0 if false)
        completion_data_by_iteration[i][ward][time_step] = 1 if completes else 0

# Get all wards and time steps
all_wards = set()
all_time_steps = set()
for iteration_data in completion_data_by_iteration.values():
    all_wards.update(iteration_data.keys())
    for ward_data in iteration_data.values():
        all_time_steps.update(ward_data.keys())

all_wards = sorted(all_wards)
all_time_steps = sorted(all_time_steps)

# Create heatmap for the first ward (or combine all wards if multiple)
ward = all_wards[0]  # For now we only use Neurosurgery, so only one ward exists

# Create matrix for heatmap (iterations x time_steps)
heatmap_data = np.zeros((iterations, len(all_time_steps)))

for i in range(iterations):
    for t_idx, time_step in enumerate(all_time_steps):
        if (i in completion_data_by_iteration and 
            ward in completion_data_by_iteration[i] and 
            time_step in completion_data_by_iteration[i][ward]):
            heatmap_data[i, t_idx] = completion_data_by_iteration[i][ward][time_step]

fig, ax = plt.subplots(figsize=(12, 8))
im = ax.imshow(heatmap_data, cmap='YlGnBu', aspect='auto', vmin=0, vmax=1)

ward_name = ward.split("_")[0]
ax.set_title(f'Completion Status Over Iterations and Time Steps (λ = {mean})\n'
             'Blue=Allocation successful, Yellow=Allocation failed', fontsize=18)
ax.set_xlabel('Time Step', fontsize=16)
ax.set_ylabel('Iteration', fontsize=16)

# Set tick labels
ax.set_xticks(range(len(all_time_steps)))
ax.set_xticklabels(all_time_steps)
ax.set_yticks(range(iterations))
ax.set_yticklabels(range(iterations))

# fig.colorbar(im, ax=ax, label='Completion Status (0=False, 1=True)')

# Save the figure
plt.tight_layout()
plt.savefig(f'plots/multi_completion_{mode}_{mean}_{std}_{iterations}_{max_time_steps}_{args.adaptive}.png', dpi=300)

# plt.show()