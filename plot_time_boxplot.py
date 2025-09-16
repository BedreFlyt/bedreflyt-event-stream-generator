import json
import matplotlib.pyplot as plt
import argparse
import numpy as np

parser = argparse.ArgumentParser("plot-single.py")
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

# Components to plot
components = [
    ('lifecycleManagerTime.dataRetrievalTime', 'Data Retrieval'),
    ('lifecycleManagerTime.minSatProblemTime', 'MinSat Problem'),
    ('lifecycleManagerTime.extraRoomTime', 'SMOL Adaptation'),
    ('componentsRetrievalTime', 'Components Retrieval'),
    ('absTime', 'Abs Time'),
    ('solverTime', 'Allocation Time')
]

# Collect all values for each component (across all time steps and iterations)
component_data = {label: [] for _, label in components}

for i in range(iterations):
    folder_name = f"{mode}_{mean}_{std}_{i}_{max_time_steps}_{args.adaptive}"
    with open(f'sim_output/{folder_name}/executions_time_step_times.json') as f:
        data = json.load(f)
    for entry in data:
        duration = entry['duration']
        component_data['Data Retrieval'].append(duration['lifecycleManagerTime']['dataRetrievalTime'] / 1000)
        component_data['MinSat Problem'].append(duration['lifecycleManagerTime']['minSatProblemTime'] / 1000)
        component_data['SMOL Adaptation'].append(duration['lifecycleManagerTime']['extraRoomTime'] / 1000)
        component_data['Components Retrieval'].append(duration['componentsRetrievalTime'] / 1000)
        component_data['Abs Time'].append(duration['absTime'] / 1000)
        component_data['Allocation Time'].append(sum([duration['solverTime']['prepareDataForSolve'], duration['solverTime']['solverTime'], duration['solverTime']['postProcessTime']]) / 1000)

# Prepare data for box plots
box_data = []
labels = []
for _, label in components:
    if component_data[label]:
        box_data.append(component_data[label])
        labels.append(label)

# Create single plot with all component box plots
fig, ax = plt.subplots(figsize=(12, 8))

if box_data:
    ax.boxplot(box_data, labels=labels)
    ax.set_title(f'Component Timing Distribution')
    ax.set_ylabel('Time (seconds)')
    ax.set_xlabel('Components')
    ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()