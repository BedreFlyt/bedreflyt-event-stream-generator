#!/bin/bash

# Script to run bedreflyt synthetic data generator experiments
# Usage: ./execute_experiments.sh --all

if [ "$1" == "--all" ]; then
    echo "Running all experiments..."
    
    echo "============================================================="
    echo "Experiment 1: experiments with lambda=40 and peaks"
    echo "============================================================="
    python main.py --mean 40 --std 15 --iterations 10 --time_steps 20 --adaptive --peak-adaptive
    
    echo ""
    echo "============================================================="
    echo "Experiment 2: experiments with lambda=40 and no peaks"
    echo "============================================================="
    python main.py --mean 40 --std 15 --iterations 10 --time_steps 2 --adaptive
    
    echo ""
    echo "============================================================="
    echo "Plotting graph for peak adaptive"
    echo "============================================================="
    python plot_multi.py --mean 40 --std 15 --mode normal --iterations 5 --time_steps 20 --adaptive --base /output/sim_output
    
    echo ""
    echo "============================================================="
    echo "Plotting graph for single run"
    echo "============================================================="
    python plot_single.py /output/sim_output/normal_40_15_1_20_True
    
    echo ""
    echo "============================================================="
    echo "Plotting time for peak adaptive"
    echo "============================================================="
    python plot_time_multi.py --iterations 10 --mean 40 --std 15 --time_steps 20 --adaptive --peak_adaptive --base /output/sim_output
    
    echo ""
    echo "============================================================="
    echo "Plotting time for non-peak adaptive"
    echo "============================================================="
    python plot_time_multi.py --iterations 10 --mean 40 --std 15 --time_steps 2 --adaptive --base /output/sim_output
    
    echo ""
    echo "============================================================="
    echo "All experiments completed!"
    echo "============================================================="
else
    echo "Usage: ./execute_experiments.sh --all"
    echo "Pass --all parameter to run all experiments"
    exit 1
fi
