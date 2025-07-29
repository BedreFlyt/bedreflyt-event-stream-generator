from abc import ABC, abstractmethod
from bisect import insort_right
import numpy as np
from numpy import random
from utils import get_index_in_time_intervals

class EventTimestampGenerator:
    def __init__(self, occurrences, time_intervals):
        self.occurrences = occurrences
        self.time_intervals = time_intervals
        self.periods = [(t2 - t1)/o for (t1, t2), o in zip(self.time_intervals, self.occurrences)]
        self.spacings = [(t2-t1) / (o+1) for (t1, t2), o in zip(self.time_intervals, self.occurrences)]
        self.timestamps = []
        self.occurrence_counter = 0
        self.current_interval = 0
        self.timestamp = 0
    
    def __get_wrap_around_time(self, t) -> float:
        """Wraps around time t if it exceeds the wrap around number. Protected method."""
        wrap_around_number = self.time_intervals[-1][1]
        wrap_around_time = t % wrap_around_number if t >= wrap_around_number else t
        return wrap_around_time
    
    def _find_interval_including_start(self, t) -> int:
        """Finds the index in time intervals corresponding to time t. Protected method."""
        try:
            index = next(i for i, (t1, t2) in enumerate(self.time_intervals) if t1 <= self.__get_wrap_around_time(t) < t2)
        except StopIteration:
            raise ValueError(f"Time t={t} is not within any defined time interval.")
        return index
    
    def _find_interval_including_end(self, t) -> int:
        """Finds the index in time intervals corresponding to time t. Protected method."""
        try:
            index = next(i for i, (t1, t2) in enumerate(self.time_intervals) if t1 < self.__get_wrap_around_time(t) <= t2)
        except StopIteration:
            raise ValueError(f"Time t={t} is not within any defined time interval.")
        return index
    
    
    def get_new_timestamp(self) -> float:
        """Calculates a new timestamp"""
        # Check if occurrences in interval have been met and updates accordingly
        if self.occurrence_counter == self.occurrences[self.current_interval]:
            self.occurrence_counter = 0
            # Check if interval is about to overflow
            if self.current_interval+1 == len(self.occurrences):
                self.current_interval = 0
                self.update_intervals()
            else:
                self.current_interval += 1 
            
            self.timestamp = self.time_intervals[self.current_interval][0]
        
        # Compute new timestamp
        self.timestamp += self.spacings[self.current_interval] + self.sample_noise(self.current_interval)
        self.timestamps.append(self.timestamp)

        # Increment number of occurrences
        self.occurrence_counter += 1

        return self.timestamp
        
    def update_intervals (self):
        """Updates the intervals to match increasing time"""
        upper_boundary = self.time_intervals[-1][1]
        new_intervals = []
        for i, (t1, t2) in enumerate(self.time_intervals):
            t1_new = upper_boundary if i==0 else new_intervals[i-1][1]
            t2_new = (t2-t1)+t1_new 
            new_intervals.append((t1_new, t2_new))
        self.time_intervals = new_intervals
    
    @abstractmethod
    def sample_noise (self, i):
        """Samples from the temporal distribution. Must be implemented in subclasses."""
        pass

class EventSampleSpace:
    def __init__(self):
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

    def run (self, stop_time):
        # Initialize
        future_events: list[tuple[float, tuple[EventTimestampGenerator, EventSampleSpace]]] = []

        for event in self.events:
            event_tg, _ = event
            insort_right(future_events, (event_tg.get_new_timestamp(), event))
        
        # Loop through events
        while True:
            # Retrieve
            timed_event = future_events.pop(0)
            t, event = timed_event
            event_tg, event_SS = event

            if (t >= stop_time): 
                return self.events_log 

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
    time_intervals = [(i, i+1) for i in range(N)]
    occurrences = [i+1 for i in range(N)]
    noise_sds = [0]*N
    no_occurrences_sds = [0]*N

    print("Time intervals:", time_intervals)
    print("Occurrences:", occurrences)
    print("Period standard deviations:", noise_sds)
    print("Number of occurrences standard deviations:", no_occurrences_sds)         

    class ExampleETG(EventTimestampGenerator):
        """Class representing the frequency of events over time, defined by occurrences and time intervals"""
        def __init__(self, occurrences, time_intervals, noise_sds):
            super().__init__(occurrences, time_intervals)
            self.noise_sds = noise_sds
            
        def sample_noise (self, i):
            """Samples a timing interval"""
            return np.random.normal(loc=0, scale=self.noise_sds[i])


    class ExampleSampleSpace(EventSampleSpace):
        def __init__(self):
            super().__init__()
        
        def sample(self, t):
            return np.random.normal(loc=1, scale=0)
    
    etg = ExampleETG(occurrences, time_intervals, noise_sds)
    ess = ExampleSampleSpace()  

    def on_event(event):
        print(f"event: {event}")
        print("--------")

    time_series_generator = TimeSeriesGenerator([(etg, ess)], on_event)
    data = time_series_generator.run(N*2)
    print("Generated data:", data)