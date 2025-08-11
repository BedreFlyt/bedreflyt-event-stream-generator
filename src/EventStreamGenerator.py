from abc import ABC, abstractmethod
from bisect import insort_right
import numpy as np
from time import sleep, time
import logging
from typing import Any, Callable, Set

from utils import validate_wrt_constraints, DEFAULT_CONSTRAINTS


# Create a module‑level logger
logger = logging.getLogger(__name__)

class EventTimestampGenerator(ABC):
    """
    Class that generates event timestamps based on a frequency distribution, that might be randomized, stochastic noise and constraints.
    
    :param occurrences: number of occurrences of the event inside the various time-intervals.
    :type occurrences: list[int]
    :param time_intervals: time intervals in which the events occur, as a list of tuples (start, end).
    :type time_intervals: list[tuple[float, float]]
    :param timestamp_constraints: constraints on the timestamps, as a list of functions that take the current state and a timestamp and return True if the timestamp is valid.
    :type timestamp_constraints: set[callable]
    :param occurrences_constraints: constraints on the occurrences, as a list of functions that take the current state and an occurrence count and return True if the occurrence count is valid.
    :type occurrences_constraints: set[callable]
    """
    def __init__(self, 
                 occurrences: list[int], 
                 time_intervals: list[tuple[float, float]],
                 timestamp_constraints: Set[Callable[[dict, Any], bool]] = {},
                 occurrences_constraints: Set[Callable[[dict, Any], bool]] = {},
                 use_default_constraints: bool = False
                 ):
        self.occurrences = occurrences
        self.time_intervals = time_intervals
        self.timestamps = []
        self.occurrence_counter = 0
        self.current_interval = 0
        self.timestamp = 0
        self.timestamp_constraints = timestamp_constraints if not use_default_constraints else DEFAULT_CONSTRAINTS.timestamp
        self.occurrences_constraints = occurrences_constraints if not use_default_constraints else DEFAULT_CONSTRAINTS.occurrences

        # Initialize and update right after
        self.sampled_occurrences = self.__get_sampled_occurrences()
        self.spacings = self.__calculate_spacings()
        

    def set_timestamp_constraints (self, constraints) -> None:
        """Sets timestamp constraints. To extend constraints, retrieve a copy of current constraints, extend that and then set it here."""
        self.timestamp_constraints = constraints
    
    def set_occurrences_constraints (self, constraints) -> None:
        """Sets occurrences constraints. To extend constraints, retrieve a copy of current constraints, extend that and then set it here."""
        self.occurrences_constraints = constraints

    def __sample_occurrences_and_calculate_new_spacings(self) -> None:
        """Resamples occurrences and calculates corresponding spacings. 
        
        :returns: None. Modifies class properties, returns nothing.""" 
        self.sampled_occurrences = self.__get_sampled_occurrences()
        self.spacings = self.__calculate_spacings()

    def __get_sampled_occurrences(self) -> list[int]:
        """Samples occurrences.
        
        :returns: A list of the sampled occurrences in each interval"""
        occurrences = [
            validate_wrt_constraints(vars(self), self.occurrences_constraints, lambda: self.sample_occurrences(self.occurrences[i], i)) 
            for i in range(len(self.occurrences))
        ]
        logger.debug(f"new occurrences: {occurrences}")
        return occurrences
    
    def __calculate_spacings(self) -> list[int]:
        """Calculates spacings.
        
        :returns: A list of the calculated spacings corresponding to each interval"""
        spacings = [(t2-t1) / (o+1) for (t1, t2), o in zip(self.time_intervals, self.sampled_occurrences)]
        logger.debug(f"new spacings: {spacings}")
        return spacings
    
    def __move_to_next_interval(self) -> None:
        """Moves to the next interval, wrapping and resampling if needed."""
        if self.current_interval+1 == len(self.occurrences):
            self.current_interval = 0
            self.__update_intervals()
            self.__sample_occurrences_and_calculate_new_spacings()
        else:
            self.current_interval += 1 
    
    def __advance_to_next_nonempty_interval(self) -> None:
        """Keeps moving to the next interval until occurrences > 0."""
        while self.sampled_occurrences[self.current_interval] == 0:
            self.__move_to_next_interval()
    
    def get_new_timestamp(self) -> float:
        """Calculates a new timestamp"""
        if self.occurrence_counter == self.sampled_occurrences[self.current_interval]:
            self.occurrence_counter = 0
            self.__move_to_next_interval()
            self.__advance_to_next_nonempty_interval()
        
        # Derive timestamp generator function
        current_interval_lower_bound = self.time_intervals[self.current_interval][0]
        ideal_position = current_interval_lower_bound + self.spacings[self.current_interval]*(self.occurrence_counter+1)
        timestamp_generator = lambda: ideal_position + self.sample_noise(self.current_interval)
        # Generate new timestamp wrt constraints using generator
        new_timestamp = validate_wrt_constraints(vars(self), self.timestamp_constraints, timestamp_generator)
        self.timestamp = new_timestamp
        self.timestamps.append(self.timestamp)

        # Increment number of occurrences
        self.occurrence_counter += 1

        return self.timestamp

    def __update_intervals (self) -> None:
        """Updates the intervals to match increasing time"""
        upper_boundary = self.time_intervals[-1][1]
        new_intervals = []
        for i, (t1, t2) in enumerate(self.time_intervals):
            t1_new = upper_boundary if i==0 else new_intervals[i-1][1]
            t2_new = (t2-t1)+t1_new 
            new_intervals.append((t1_new, t2_new))
        self.time_intervals = new_intervals
        logger.debug(f"new intervals: {new_intervals}")
    
    @abstractmethod
    def sample_noise (self, i) -> float:
        """Samples noise in i'th interval. Must be implemented in subclasses.
        
        :param i: index of interval
        :returns: A float representing the noise in the i'th interval. Defaults to 0 if not implemented.
        """
        return 0.0

    @abstractmethod
    def sample_occurrences (self, occurrences_i: float, i: int) -> int:
        """Samples occurrences in i'th interval given the number of occurrences in the i'th interval. Must be implemented in subclasses.
        
        :param occurrences_i: occurrences in i'th interval.
        :param i: index i
        :returns: A sampled number of occurrences in the i'th interval.
        Defaults to the expected number of occurrences if not implemented.
        """
        return occurrences_i

class EventSampleSpace(ABC):
    """TBD"""
    def __init__(self, constraints={}):
        self.constraints = constraints

    def get_sample(self, t: float) -> Any:
        """Retrieves a sample valid w.r.t. constraints"""
        return validate_wrt_constraints(vars(self), self.constraints, lambda: self.sample(t))

    @abstractmethod
    def sample (self, t: float) -> Any:
        """Samples from the sample space. Must be implemented in subclasses."""
        pass


class EventStreamGenerator:
    """Generates time series events.

    :param events: the events as a list of tuples including an instances of EventTimestampGenerator and EventSampleSpace.
    :param on_event: event callback invoked with event time and event result when an event is occurring.
    """
    def __init__(self, events: list[tuple[EventTimestampGenerator, EventSampleSpace]], on_event):
        self.events = set(events)
        self.on_event = on_event
        self.clock = 0
        self.events_log = []

    def run (self, stop_time, time_scale:None|float=None):
        # Initialize
        future_events: list[tuple[float, tuple[EventTimestampGenerator, EventSampleSpace]]] = []

        for event in self.events:
            event_tg, _ = event
            insort_right(future_events, (event_tg.get_new_timestamp(), event))
        
        start_time = time()
        # Loop through events
        while True:
            # Retrieve
            timed_event = future_events.pop(0)
            t, event = timed_event
            event_tg, event_SS = event

            if (t >= stop_time): 
                logger.debug(f"Total time: {time()-start_time}s")
                return self.events_log 
            
            # Real-time sleep
            sleep_init_logged = False
            while time_scale != None:
                current_time = (time() - start_time)*time_scale
                if current_time >= t: break
                elif not sleep_init_logged:
                    logger.debug(f"Waiting {t-current_time} seconds.")
                    sleep_init_logged = True

            # Sample
            sample = event_SS.get_sample(t)
            result = (t, sample)
            
            # Log
            self.events_log.append(result)
            self.on_event(result)

            # Add future event
            insort_right(future_events, (event_tg.get_new_timestamp(), event))


            
if __name__ == "__main__":
    import numpy as np

    N = 3
    cycles = 2
    time_intervals = [(i, i+1) for i in range(N)]
    occurrences = [i+1 for i in range(N)]
    noise_sds = [0]*N
    no_occurrences_sds = [1]*N

    print("Time intervals:", time_intervals)
    print("Occurrences:", occurrences)
    print("Period standard deviations:", noise_sds)
    print("Number of occurrences standard deviations:", no_occurrences_sds)
    
    class ExampleETG(EventTimestampGenerator):
        """Class representing the frequency of events over time, defined by occurrences and time intervals"""
        def __init__(self, occurrences, time_intervals, noise_sds, occurrences_sds):
            self.noise_sds = noise_sds
            self.occurrences_sds = occurrences_sds
            super().__init__(occurrences, time_intervals)
            
            
        def sample_noise (self, i):
            """Samples a timing interval"""
            return np.random.normal(loc=0, scale=self.noise_sds[i])
        
        def sample_occurrences(self, occurrences_i, i):
            sample = int(np.round(np.random.normal(loc=occurrences_i, scale=self.occurrences_sds[i])))
            return sample


    class ExampleSampleSpace(EventSampleSpace):
        def __init__(self):
            super().__init__()
        
        def sample(self, t):
            sample = np.random.normal(loc=1, scale=0)
            return .5 if sample <= .5 else sample
    
    etg = ExampleETG(occurrences, time_intervals, noise_sds, no_occurrences_sds)
    ess = ExampleSampleSpace()  
    def on_event(event):
        print(f"event: {event}")
        print("--------")

    time_series_generator = EventTimestampGenerator([(etg, ess)], on_event)
    data = time_series_generator.run(cycles*N, real_time=True)
    print("Generated data:", data)