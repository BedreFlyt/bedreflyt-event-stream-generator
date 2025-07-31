import logging

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
                break
        if satisfied: 
            logger.debug("Constraint satisfied")
            return value
        else: satisfied = True

