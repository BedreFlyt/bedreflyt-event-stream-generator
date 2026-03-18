#!/bin/bash

# Script to run bedreflyt synthetic data generator experiments
# Usage: ./execute_experiments.sh --all [output_folder]
# Example: ./execute_experiments.sh --all ./my_output

# Set output folder from second argument or default to ./output
OUTPUT_FOLDER="${2:-./output}"

echo "Using output folder: $OUTPUT_FOLDER"

if [ "$1" == "--all" ]; then
    echo "Running all experiments..."
    
    echo "============================================================="
    echo "Experiment 1: experiments with lambda=40 and peaks"
    echo "============================================================="
    python main.py --mean 40 --std 15 --iterations 10 --time_steps 20 --adaptive --peak-adaptive --enable-sbl --output "$OUTPUT_FOLDER"
    
    echo ""
    echo "============================================================="
    echo "Experiment 2: experiments with lambda=40 and no peaks"
    echo "============================================================="
    python main.py --mean 40 --std 15 --iterations 10 --time_steps 2 --adaptive --enable-sbl --output "$OUTPUT_FOLDER"
    
    echo ""
    echo "============================================================="
    echo "Plotting graph for peak adaptive"
    echo "============================================================="
    python plot_multi.py --mean 40 --std 15 --mode normal --iterations 5 --time_steps 20 --adaptive --base "$OUTPUT_FOLDER/sim_output"
    
    echo ""
    echo "============================================================="
    echo "Plotting graph for single run"
    echo "============================================================="
    python plot_single.py "$OUTPUT_FOLDER/sim_output/normal_40_15_1_20_True"
    
    echo ""
    echo "============================================================="
    echo "Plotting time for peak adaptive"
    echo "============================================================="
    python plot_time_multi.py --iterations 10 --mean 40 --std 15 --time_steps 20 --adaptive --peak_adaptive --base "$OUTPUT_FOLDER/sim_output"
    
    echo ""
    echo "============================================================="
    echo "Plotting time for non-peak adaptive"
    echo "============================================================="
    python plot_time_multi.py --iterations 10 --mean 40 --std 15 --time_steps 2 --adaptive --base "$OUTPUT_FOLDER/sim_output"

    echo ""
    echo "============================================================="
    echo "Plotting SBL supply management maps"
    echo "============================================================="
    python plot_sbl.py --mean 40 --std 15 --mode normal --iterations 10 --time_steps 20 --base "$OUTPUT_FOLDER"

    echo ""
    echo "============================================================="
    echo "All experiments completed!"
    echo "============================================================="
else
    echo "Usage: ./execute_experiments.sh --all [output_folder]"
    echo "Pass --all parameter to run all experiments"
    echo "Optionally specify output folder (defaults to /app/output)"
    echo "Example: ./execute_experiments.sh --all ./my_output"
    exit 1
fi
