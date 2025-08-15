import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Set
from time import sleep


logger = logging.getLogger(__name__)

def validate_wrt_constraints(state: dict, constraints: set, value_generator):
    while True:
        value = value_generator()
        satisfied = True
        logger.debug(f"Checks if constraint is satisfied with value: {value}")
        for constraint in constraints:
            if not constraint(state, value): 
                satisfied = False
                logger.debug("Constraint not satisfied")
                sleep(0.01)
                break
        if satisfied: 
            logger.debug("Constraint satisfied")
            return value
        else: satisfied = True

@dataclass
class DEFAULT_CONSTRAINTS:
    """Default constraints data class"""
    timestamp: Set[Callable[[dict, Any], bool]]=field(default_factory=lambda: {
                     # Every timestamp (ts) must be non-negative
                     lambda state, ts: ts > 0, 
                     # Every timestamp (ts) must be greater than the prior expect for the first datapoint
                     lambda state, ts: ts > state["timestamps"][-1] if (len(state["timestamps"])) != 0 else True,
                     # Every timestamp (ts) must be within its own interval
                     lambda state, ts: state["time_intervals"][state["current_interval"]][0] <= ts < state["time_intervals"][state["current_interval"]][1]
                })
    # Occurrence Constraints
    occurrences: Set[Callable[[dict, Any], bool]]=field(default_factory=lambda: {
        # The number of occurrences must be non-negative
        lambda state, o: o >= 0
    })
    

    
