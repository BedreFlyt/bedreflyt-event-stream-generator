from typing import Any, Callable, Set

# Timestamp Constraints
timestamp_constraints: Set[Callable[[dict, Any], bool]]={
                     # Every timestamp (ts) must be non-negative
                     lambda state, ts: ts > 0, 
                     # Every timestamp (ts) must be greater than the prior expect for the first datapoint
                     lambda state, ts: ts > state["timestamps"][-1] if (len(state["timestamps"])) != 0 else True,
                     # Every timestamp (ts) must be within its own interval
                     lambda state, ts: state["time_intervals"][state["current_interval"]][0] <= ts < state["time_intervals"][state["current_interval"]][1]
                }
# Occurrence Constraints
occurrences_constraints: Set[Callable[[dict, Any], bool]]={
    # The number of occurrences must be non-negative
    lambda state, o: o >= 0
}