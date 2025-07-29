from typing import Any
import matplotlib.pyplot as plt

def count_number_of_occurrences_in_intervals(intervals: list[tuple[float, float]], data: list[tuple[float, Any]], center_data_in_intervals=True) -> list[int]:
    """Counts the number of occurrences in each interval"""
    # Loop through each interval, then count the occurrences in each
    occurrences: list[int] = [0]*len(intervals)
    for i, (t1, t2) in enumerate(intervals):
        for time, _ in data:
            if time >= t1 and time < t2:
                occurrences[i] += 1

    return occurrences

def extend_intervals(intervals: list, cycles: int=2) -> list:
    """
    Tiles the given list of intervals for the specified number of cycles.

    Parameters:
    - intervals: List of (start, end) tuples.
    - cycles: Total number of cycles (original counts as one).
    """
    if cycles <= 1:
        return intervals.copy()

    result = intervals.copy()
    for _ in range(cycles - 1):
        last_end = result[-1][1]
        for start, end in intervals:
            length = end - start
            new_start = last_end
            new_end = last_end + length
            result.append((new_start, new_end))
            last_end = new_end

    return result

def plot_timeline(data, time_intervals):
    # Assume `data` is a list of (time, scale) tuples,
    # and `time_intervals` is a list of (start, end) tuples, already defined.

    # Unpack times and scales
    times, scales = zip(*data)

    # All events sit on the same horizontal line
    ys = [0] * len(times)

    # Map scales to marker sizes (adjust the multiplier as needed)
    marker_sizes = [s * 200 for s in scales]

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 2))

    # Draw baseline timeline
    ax.hlines(0, min(times) - 0.5, max(times) + 0.5, color='black', linewidth=1)

    # Shade each period for context
    for idx, (start, end) in enumerate(time_intervals):
        alpha = 0.1 if idx % 2 == 0 else 0.05
        ax.axvspan(start, end, color='gray', alpha=alpha)

    # Plot events as red circles
    ax.scatter(times, ys, s=marker_sizes, color='red', alpha=0.8)

    # Hide y-axis ticks and labels
    ax.set_yticks([])

    # Labels and title
    ax.set_xlabel('Time')
    ax.set_title('Event Timeline')

    # Set plot limits
    ax.set_xlim(min(times) - 0.5, max(times) + 0.5)
    ax.set_ylim(-0.5, 0.5)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Example usage
    intervals = [(0, 10), (10, 20), (20, 30)]
    data = [(1, 'a'), (5, 'b'), (9, 'b'), (15, 'c'),  (20, 'd'), (25, 'd')]
    print(count_number_of_occurrences_in_intervals(intervals, data))  # Output: [2, 1, 1]

    # Example usage:
    TI_original = [(1, 2), (2, 4), (4, 10)]
    TI_extended = extend_intervals(TI_original, cycles=2)
    print(TI_extended)
    # → [(1,2), (2,4), (4,10), (10,11), (11,13), (13,19)]

