import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

sample = lambda v, p: np.random.choice(v, p=p)

def monte_carlo_simulation(num_trials, values, probabilities):
    results = []
    for _ in range(num_trials):
        result = sample(values, probabilities)
        results.append(result)
    return results

def main():
    
    values = [1, 2, 3, 4]
    probabilities = [0.1, 0.2, 0.3, 0.4]
    num_trials = 1000000
    results = monte_carlo_simulation(num_trials, values, probabilities)
    print(results)

    # Convert to frequencies using Counter
    counter = Counter(results)
    sorted_values = sorted(values)  # keep consistent order
    print(sorted_values)
    frequencies = [counter[v] for v in sorted_values]
    percentage_frequencies = [f / num_trials * 100 for f in frequencies]
    print(percentage_frequencies)

    # Bar plot
    plt.figure(figsize=(8, 4))
    plt.bar(sorted_values, frequencies, tick_label=sorted_values)
    plt.title("Bar Plot of Monte Carlo Results")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.show()
    

if __name__ == "__main__":
    main()