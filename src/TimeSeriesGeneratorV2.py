from abc import ABC, abstractmethod
from bisect import insort_right
import numpy as np
from time import sleep, time
import logging

from utils import validate_wrt_constraints


# Create a module‑level logger
logger = logging.getLogger(__name__)

class EventTimestampGenerator(ABC):
    def __init__(self, 
                 occurrences, 
                 time_intervals, 
                 timestamp_constraints={
                     # Every timestamp must be non-negative
                     lambda state, ts: ts > 0, 
                     # Every timestamp must be greater than the prior expect for the first datapoint
                     lambda state, ts: ts > state["timestamps"][-1] if (len(state["timestamps"])) != 0 else True,
                     # Prohibits timestamps from entering other intervals
                     lambda state, ts: state["time_intervals"][state["current_interval"]][0] < ts < state["time_intervals"][state["current_interval"]][1]
                }, 
                 occurrences_constraints={
                     lambda state, o: o >= 0
                 }):
        self.occurrences = occurrences
        self.time_intervals = time_intervals
        self.timestamps = []
        self.occurrence_counter = 0
        self.current_interval = 0
        self.timestamp = 0
        self.timestamp_constraints = timestamp_constraints
        self.occurrences_constraints = occurrences_constraints

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
            self.timestamp = self.time_intervals[self.current_interval][0]
        
        # Compute new timestamp
        timestamp_generator = lambda: self.timestamp + self.spacings[self.current_interval] + self.sample_noise(self.current_interval)
        new_timestamp = validate_wrt_constraints(vars(self), self.timestamp_constraints, timestamp_generator)
        self.timestamp = new_timestamp
        self.timestamps.append(self.timestamp)

        # Increment number of occurrences
        self.occurrence_counter += 1

        return self.timestamp

    def __update_intervals (self):
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
        """Samples noise in i'th interval. Must be implemented in subclasses."""
        pass

    @abstractmethod
    def sample_occurrences (self, occurrences_i: float, i: int) -> int:
        """Samples occurrences in i'th interval given the number of occurrences in the i'th interval. Must be implemented in subclasses."""
        pass

class EventSampleSpace(ABC):
    def __init__(self, constraints=None):
        pass

    @abstractmethod
    def sample (self, t):
        """Samples from the sample space. Must be implemented in subclasses."""
        pass


class TimeSeriesGenerator:
    def __init__(self, events: list[tuple[EventTimestampGenerator, EventSampleSpace]], on_event):
        self.events = set(events)
        self.on_event = on_event
        self.clock = 0
        self.events_log = []

    def run (self, stop_time, real_time=False):
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
            while real_time:
                current_time = time() - start_time
                if current_time >= t: break
                elif not sleep_init_logged:
                    logger.debug(f"Waiting {t-current_time} seconds.")
                    sleep_init_logged = True

            # Sample
            sample = event_SS.sample(t)
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

    time_series_generator = TimeSeriesGenerator([(etg, ess)], on_event)
    data = time_series_generator.run(cycles*N, real_time=True)
    print("Generated data:", data)