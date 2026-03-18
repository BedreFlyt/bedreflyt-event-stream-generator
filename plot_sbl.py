import json
import matplotlib
matplotlib.use("pgf")
import matplotlib.pyplot as plt

# Use LaTeX for text rendering
plt.rcParams.update({
    "pgf.texsystem": "pdflatex",
    "text.usetex": True,
    "font.family": "serif",
    "pgf.rcfonts": False,
})
import argparse
import numpy as np
import os
import glob

parser = argparse.ArgumentParser("plot-sbl.py")
parser.add_argument("--std", help="Standard deviation", type=int, default=1)
parser.add_argument("--mean", help="Mean", type=int, default=5)
parser.add_argument("--mode", help="Mode from [normal, crisis, medium-crisis]", type=str, default="normal")
parser.add_argument("--iterations", help="Number of iterations", type=int, default=10)
parser.add_argument("--time_steps", help="Time steps to run", type=int, default=10)
parser.add_argument("--base", help="Base folder containing sbl_output/", type=str, default=".")
args = parser.parse_args()

output_base = os.getenv("OUTPUT_FOLDER", args.base)
sbl_folder = os.path.join(output_base, "sbl_output")

# accumulated[supply_name][metric][time_step] = [values across iterations]
accumulated = {}

for iteration in range(args.iterations):
    for time_step in range(args.time_steps):
        filepath = os.path.join(sbl_folder, f"sbl_res_{time_step}_{iteration}.json")
        if not os.path.exists(filepath):
            continue

        with open(filepath) as f:
            data = json.load(f)

        for supply_name, records in data.items():
            if supply_name not in accumulated:
                accumulated[supply_name] = {
                    "max_capacity": {},
                    "current_capacity": {},
                    "orders": {},
                    "current_capacity_baseline": {},
                    "baseline": {},
                }

            # Each record corresponds to one time step entry in the list;
            # use the list index as a sub-time-step, but here we use the
            # outer time_step (k) as the x-axis and average over iterations.
            # If there are multiple records per file we take the last one
            # (most up-to-date state for that time step).
            record = records[-1] if records else {}
            for metric in accumulated[supply_name]:
                if metric not in record:
                    continue
                ts_data = accumulated[supply_name][metric]
                if time_step not in ts_data:
                    ts_data[time_step] = []
                ts_data[time_step].append(record[metric])

if not accumulated:
    print(f"No SBL data found in {sbl_folder}. Make sure the simulation ran with --enable-sbl.")
    raise SystemExit(1)

# For each supply, compute median + 25/75 percentiles per time step
def compute_statistics(ts_dict):
    stats = {"median": {}, "p25": {}, "p75": {}}
    for ts, values in ts_dict.items():
        stats["median"][ts] = np.percentile(values, 50)
        stats["p25"][ts] = np.percentile(values, 25)
        stats["p75"][ts] = np.percentile(values, 75)
    return stats

# Colour palette for the three variable series
LINE_COLORS = {
    "current_capacity": "tab:blue",
    "orders": "tab:orange",
    "current_capacity_baseline": "tab:green",
}
DASHED_COLORS = {
    "max_capacity": "tab:red",
    "baseline": "tab:purple",
}

plots_dir = os.path.join(output_base, "plots")
os.makedirs(plots_dir, exist_ok=True)

for supply_name, metrics in accumulated.items():
    fig, ax = plt.subplots(figsize=(14, 6))

    # Collect all time steps for x-axis
    all_ts = set()
    for ts_dict in metrics.values():
        all_ts.update(ts_dict.keys())
    sorted_ts = sorted(all_ts)
    x_idx = list(range(len(sorted_ts)))
    ts_to_x = {ts: i for i, ts in enumerate(sorted_ts)}

    # --- Dashed constant-ish lines (max_capacity and baseline) ---
    for metric_name, color in DASHED_COLORS.items():
        ts_dict = metrics.get(metric_name, {})
        if not ts_dict:
            continue
        stats = compute_statistics(ts_dict)
        xs = sorted(stats["median"].keys())
        ys = [stats["median"][t] for t in xs]
        xi = [ts_to_x[t] for t in xs]

        ax.plot(xi, ys,
                label=metric_name.replace("_", " ").title(),
                color=color,
                linestyle="--",
                linewidth=2.5)
        # Light shade for variability across iterations
        p25 = [stats["p25"][t] for t in xs]
        p75 = [stats["p75"][t] for t in xs]
        ax.fill_between(xi, p25, p75, color=color, alpha=0.12)

    # --- Solid lines with shade (current_capacity, orders, current_capacity_baseline) ---
    for metric_name, color in LINE_COLORS.items():
        ts_dict = metrics.get(metric_name, {})
        if not ts_dict:
            continue
        stats = compute_statistics(ts_dict)
        xs = sorted(stats["median"].keys())
        ys_med = [stats["median"][t] for t in xs]
        p25 = [stats["p25"][t] for t in xs]
        p75 = [stats["p75"][t] for t in xs]
        xi = [ts_to_x[t] for t in xs]

        ax.plot(xi, ys_med,
                label=f"{metric_name.replace('_', ' ').title()} (median)",
                color=color,
                marker="o",
                linewidth=2)
        ax.fill_between(xi, p25, p75, color=color, alpha=0.2,
                        label=f"{metric_name.replace('_', ' ').title()} (25–75th pct)")

    ax.set_title(f"Supply: {supply_name}", fontsize=24)
    ax.set_xlabel("Time step", fontsize=20)
    ax.set_ylabel("Units", fontsize=20)
    ax.set_xticks(x_idx)
    ax.set_xticklabels(sorted_ts)
    ax.grid(True)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=14)
    plt.tight_layout()

    safe_name = supply_name.replace(" ", "_").replace("/", "-")
    out_path = os.path.join(plots_dir, f"sbl_{safe_name}.pgf")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved plot for '{supply_name}' -> {out_path}")

print("SBL plotting complete.")
