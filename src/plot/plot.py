import json
import matplotlib.pyplot as plt
import argparse
import numpy as np

class Plotter:
    def __init__(self, std, mean, mode, iterations, time_steps, adaptive, base):
        self.std = std
        self.mean = mean
        self.mode = mode
        self.iterations = iterations
        self.time_steps = time_steps
        self.adaptive = adaptive
        self.base = base

    def _accumulate_allocations(self, folders):
        """Accumulate allocations from a list of folder paths.

        Returns: dict ward -> time_step -> [allocations]
        """
        accumulated_ward_data = {}
        for folder in folders:
            try:
                with open(f"{folder}/allocation_results.json") as f:
                    data = json.load(f)
            except Exception:
                # Skip missing or unreadable folders
                continue

            allocations = data.get('allocations', [])
            for item in allocations:
                ward = item['ward']
                time_step = item['time_step']
                allocation = item['allocations']

                if ward not in accumulated_ward_data:
                    accumulated_ward_data[ward] = {}
                if time_step not in accumulated_ward_data[ward]:
                    accumulated_ward_data[ward][time_step] = []
                accumulated_ward_data[ward][time_step].append(allocation)

        return accumulated_ward_data

    def _accumulate_capacities(self, folders):
        """Accumulate capacities from a list of folder paths.

        Returns: dict ward -> time_step -> [total_capacity]
        """
        accumulated_capacity_data = {}
        for folder in folders:
            try:
                with open(f"{folder}/allocation_results.json") as f:
                    data = json.load(f)
            except Exception:
                continue

            capacities = data.get('capacities', [])
            for item in capacities:
                ward = item['ward']
                time_step = item['time_step']
                capacity = item.get('total_capacity')

                if ward not in accumulated_capacity_data:
                    accumulated_capacity_data[ward] = {}
                if time_step not in accumulated_capacity_data[ward]:
                    accumulated_capacity_data[ward][time_step] = []
                accumulated_capacity_data[ward][time_step].append(capacity)

        return accumulated_capacity_data

    def _compute_statistics(self, accumulated_data):
        """Compute median (50th), 25th and 75th percentiles for accumulated data.

        Input: dict ward -> time_step -> [values]
        Output: dict ward -> {'averages':{}, 'percentile_25':{}, 'percentile_75':{}}
        """
        statistics = {}
        for ward, time_data in accumulated_data.items():
            statistics[ward] = {
                'averages': {},
                'percentile_25': {},
                'percentile_75': {}
            }
            # ensure time step 0 present
            statistics[ward]['averages'][0] = 0
            statistics[ward]['percentile_25'][0] = 0
            statistics[ward]['percentile_75'][0] = 0

            for time_step, value_list in time_data.items():
                try:
                    statistics[ward]['averages'][time_step] = np.percentile(value_list, 50)
                    statistics[ward]['percentile_25'][time_step] = np.percentile(value_list, 25)
                    statistics[ward]['percentile_75'][time_step] = np.percentile(value_list, 75)
                except Exception:
                    # If invalid list, default to zeros
                    statistics[ward]['averages'][time_step] = 0
                    statistics[ward]['percentile_25'][time_step] = 0
                    statistics[ward]['percentile_75'][time_step] = 0

        return statistics

    def _plot_combined(self, ward_statistics, capacity_statistics, output_folder_name, title_suffix=None, figsize=(15,7), fontsize=(14,12)):
        """Plot ward statistics and capacity statistics into a combined figure and save to SVG."""
        plt.figure(figsize=figsize)

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
            ward_x_indices = [time_steps_sorted.index(ts) for ts in ward_time_steps]

            color = allocation_colors[i % len(allocation_colors)]
            # Plot averaged allocations
            plt.plot(ward_x_indices, avg_allocations, label=f'Allocations 50th percentile', marker='o', color=color, linewidth=2)
            plt.plot(ward_x_indices, p25_allocations, color=color, linestyle='-.', alpha=0.7, linewidth=1.3, label=f'Allocations 25th percentile')
            plt.plot(ward_x_indices, p75_allocations, color=color, linestyle=':', alpha=0.7, linewidth=1.3, label=f'Allocations 75th percentile')
            plt.fill_between(ward_x_indices, p25_allocations, p75_allocations, color=color, alpha=0.2)

        for i, (ward, stats) in enumerate(capacity_statistics.items()):
            ward_time_steps = sorted(stats['averages'].keys())
            avg_capacities = [stats['averages'][time_step] for time_step in ward_time_steps]
            p25_capacities = [stats['percentile_25'][time_step] for time_step in ward_time_steps]
            p75_capacities = [stats['percentile_75'][time_step] for time_step in ward_time_steps]
            ward_x_indices = [time_steps_sorted.index(ts) for ts in ward_time_steps]

            color = capacity_colors[i % len(capacity_colors)]
            plt.plot(ward_x_indices, avg_capacities, label=f'Capacities 50th percentile', marker='x', color=color, linestyle='--', linewidth=2)
            plt.plot(ward_x_indices, p25_capacities, color=color, linestyle='-.', alpha=0.7, linewidth=1.3, label=f'Capacity 25th percentile')
            plt.plot(ward_x_indices, p75_capacities, color=color, linestyle=':', alpha=0.7, linewidth=1.3, label=f'Capacity 75th percentile')
            plt.fill_between(ward_x_indices, p25_capacities, p75_capacities, color=color, alpha=0.2)

        title = f'Adaptation of capacity over time with varying allocations'
        if title_suffix:
            title = title + ' ' + str(title_suffix)
        plt.title(title, fontsize=22)
        plt.xlabel('Time step', fontsize=18)
        plt.ylabel('Allocations and Capacity Counts', fontsize=18)
        plt.grid(True)
        plt.xticks(x_indices, time_steps_sorted)

        # Decorative threshold lines (kept from original)
        plt.axhline(y=40, color='green', linestyle='--', linewidth=2.5, label='Load threshold')
        plt.axhline(y=45, color='purple', linestyle='-', linewidth=2.5, label='Initial ward capacity')
        plt.axhline(y=49, color='brown', linestyle=':', linewidth=2.5, label='Ward capacity with office 1')
        plt.axhline(y=53, color='silver', linestyle='-.', linewidth=2.5, label='Ward capacity with office 1 and 2')
        plt.axhline(y=93, color='red', linestyle=(0, (3, 5, 1, 5)), linewidth=2.5, label='Maximum ward capacity')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=14)
        plt.tight_layout()

        plt.savefig(f'{output_folder_name}/allocation_capacity_adaptation_{self.mode}_{self.mean}_{self.std}_{self.iterations}_{self.time_steps}_{self.adaptive}.svg')

    def plot_multi(self, output_folder_name):
        # Build list of iteration folders and reuse helpers
        input_folder_name = self.base
        folders = []
        for i in range(self.iterations):
            folder_name = f"{self.mode}_{self.mean}_{self.std}_{i}_{self.time_steps}_{self.adaptive}"
            folders.append(f"{input_folder_name}/{folder_name}")

        accumulated_ward_data = self._accumulate_allocations(folders)
        print(accumulated_ward_data)
        ward_statistics = self._compute_statistics(accumulated_ward_data)

        accumulated_capacity_data = self._accumulate_capacities(folders)
        capacity_statistics = self._compute_statistics(accumulated_capacity_data)

        # Delegate plotting to helper
        self._plot_combined(ward_statistics, capacity_statistics, output_folder_name)

    def plot_single(self, output_folder_name):
        # Reuse accumulation and stats helpers for single-file case
        folder = self.base
        accumulated_ward_data = self._accumulate_allocations([folder])
        print(accumulated_ward_data)
        ward_statistics = self._compute_statistics(accumulated_ward_data)

        accumulated_capacity_data = self._accumulate_capacities([folder])
        capacity_statistics = self._compute_statistics(accumulated_capacity_data)

        # Plot with a small suffix so title differentiates if needed
        self._plot_combined(ward_statistics, capacity_statistics, output_folder_name, title_suffix='(single)')
