from typing import Any

def count_number_of_occurrences_in_intervals(intervals: list[tuple[float, float]], data: list[tuple[float, Any]], center_data_in_intervals=True) -> list[int]:
    """Counts the number of occurrences in each interval"""
    # Loop through each interval, then count the occurrences in each
    occurrences: list[int] = [0]*len(intervals)
    for i, (t1, t2) in enumerate(intervals):
        for time, _ in data:
            if time > t1 and time <= t2:
                occurrences[i] += 1

    return occurrences

if __name__ == "__main__":
    # Example usage
    intervals = [(0, 10), (10, 20), (20, 30)]
    data = [(1, 'a'), (5, 'b'), (9, 'b'), (15, 'c'),  (20, 'd'), (25, 'd')]
    print(count_number_of_occurrences_in_intervals(intervals, data))  # Output: [2, 1, 1]
