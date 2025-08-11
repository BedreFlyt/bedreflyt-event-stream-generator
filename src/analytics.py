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


def plot_timeline_with_colors(data, time_intervals, marker_size=100, alpha=1):
    """
    Plot a timeline of events, coloring each point based on the provided color,
    and ensure the points are drawn on top of the timeline and shaded bands.

    :param data: List of (time, color) tuples. `color` may be any matplotlib‐acceptable color.
    :type data: list of (float, str)
    :param time_intervals: List of (start, end) tuples to shade alternating background bands.
    :type time_intervals: list of (float, float)
    :param marker_size: Size of each scatter marker.
    :type marker_size: int, optional
    :param alpha: Alpha transparency for the points.
    :type alpha: float, optional
    :returns: None
    """
    # Unpack times and colors
    times, colors = zip(*data)
    ys = [0] * len(times)

    fig, ax = plt.subplots(figsize=(12, 2))

    # Shade each period for context (drawn at lowest z-order)
    for idx, (start, end) in enumerate(time_intervals):
        alpha_bg = 0.1 if idx % 2 == 0 else 0.05
        ax.axvspan(start, end, color='gray', alpha=alpha_bg, zorder=0)

    # Draw baseline timeline (above shading but below points)
    ax.hlines(0,
              min(times) - 0.5,
              max(times) + 0.5,
              color='black',
              linewidth=1,
              zorder=1)

    # Plot events on top
    ax.scatter(times,
               ys,
               s=marker_size,
               c=colors,
               alpha=alpha,
               edgecolors='k',
               zorder=2)

    # Hide y-axis ticks and labels
    ax.set_yticks([])

    ax.set_xlabel('Time')
    ax.set_title('Event Timeline')

    ax.set_xlim(min(times) - 0.5, max(times) + 0.5)
    ax.set_ylim(-0.5, 0.5)

    plt.tight_layout()
    plt.show()


def plot_timeline_multiple(datasets, time_intervals, colors, titles):
    """
    Plot multiple event-series on a single timeline.

    :param datasets: List of data series; each series is a list of (time, scale) tuples.
    :type datasets: List[List[Tuple[float, float]]]
    :param time_intervals: List of (start, end) intervals to shade for context.
    :type time_intervals: List[Tuple[float, float]]
    :param colors: One matplotlib-acceptable color per data series.
    :type colors: List[str]
    :param titles: One label per data series, shown in the legend.
    :type titles: List[str]
    :raises ValueError: If the lengths of datasets, colors, and titles do not match.
    """
    # Validate inputs
    n = len(datasets)
    if not (len(colors) == len(titles) == n):
        raise ValueError("datasets, colors, and titles must all have the same length")

    fig, ax = plt.subplots(figsize=(12, 2))

    # Draw baseline timeline
    # Determine overall min/max times across all datasets
    all_times = [t for series in datasets for t, _ in series]
    t_min, t_max = min(all_times), max(all_times)
    ax.hlines(0, t_min - 0.5, t_max + 0.5, color='black', linewidth=1)

    # Shade each period for context
    for idx, (start, end) in enumerate(time_intervals):
        alpha = 0.1 if idx % 2 == 0 else 0.05
        ax.axvspan(start, end, color='gray', alpha=alpha)

    # Plot each data series
    for series, color, title in zip(datasets, colors, titles):
        times, scales = zip(*series)
        ys = [0] * len(times)
        marker_sizes = [s * 200 for s in scales]
        ax.scatter(times, ys, s=marker_sizes, color=color, alpha=0.8, label=title)

    # Legend, labels, limits
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=min(n, 4))
    ax.set_yticks([])
    ax.set_xlabel('Time')
    ax.set_title('Event Timeline')
    ax.set_xlim(t_min - 0.5, t_max + 0.5)
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

    # Suppose you have two series of events:
    data1 = [(1, 0.5), (2, 1.0), (3, 0.8)]
    data2 = [(1.5, 0.7), (2.5, 1.2), (3.5, 0.6)]
    intervals = [(0.5, 1.5), (2.0, 3.0)]

    plot_timeline_multiple(
        datasets=[data1, data2],
        time_intervals=intervals,
        colors=['red', 'blue'],
        titles=['Series A', 'Series B']
    )
