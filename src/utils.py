def normalise_time(t: float, time_intervals: list[tuple[float, float]]) -> float:
    """Normalises time t to the first interval in time_intervals."""
    wrap_around_number = time_intervals[-1][1]
    if t >= wrap_around_number:
        t = t%wrap_around_number
    return t


def get_index_in_time_intervals(time_intervals, t):
    """Finds the index in time_intervals corresponding to time t."""
    t = normalise_time(t, time_intervals)
    try:
        return next(i for i, (t1, t2) in enumerate(time_intervals) if t1 < t <= t2)
    except StopIteration:
        raise ValueError(f"Time t={t} is not within any defined time interval.")