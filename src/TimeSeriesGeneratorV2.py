from abc import ABC, abstractmethod
from bisect import insort_right
import numpy as np
from numpy import random
from utils import get_index_in_time_intervals

class EventTimestampGenerator:
    def __init__(self, occurrences, time_intervals):
        self.occurrences = occurrences
        self.time_intervals = time_intervals
        self.period_spacing_in_intervals = [(t2-t1) / (o+1) for (t1, t2), o in zip(self.time_intervals, self.occurrences)]
        self.ideal_timestamps = [0]
    
    def __get_wrap_around_time(self, t):
        """Wraps around time t if it exceeds the wrap around number. Protected method."""
        wrap_around_number = self.time_intervals[-1][1]
        return t % wrap_around_number if t >= wrap_around_number else t
    
    def _get_current_time_interval_index(self, t):
        """Finds the index in time intervals corresponding to time t. Protected method."""
        try:
            return next(i for i, (t1, t2) in enumerate(self.time_intervals) if t1 <= self.__get_wrap_around_time(t) < t2)
        except StopIteration:
            raise ValueError(f"Time t={t} is not within any defined time interval.")
    
    def _get_current_period(self, t):
        return self.period_spacing_in_intervals[self._get_current_time_interval_index(t)]
    
    def _get_current_no_occurrences(self, t):
        return self.occurrences[self._get_current_time_interval_index(t)]
    
    def _get_current_time_interval_width(self, t):
        t1, t2 = self.time_intervals[self._get_current_time_interval_index(t)]
        return t2 - t1
    
    def get_new_timestamp(self):
        clock = self.ideal_timestamps[-1]
        ideal_timestamp = clock + self._get_current_period(clock)
        self.ideal_timestamps.append(ideal_timestamp)
        return  ideal_timestamp + self.sample_noise(clock)
    
    @abstractmethod
    def sample_noise (self, t):
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
        
        # Loop through events (foreverrrr)
        while True:
            # Retrieve
            timed_event = future_events.pop(0)
            t, event = timed_event
            event_tg, event_SS = event

            if (t > stop_time): 
                return self.events_log 

            # Sample
            sample = event_SS.sample(t)
            result = (t, sample)
            
            # Log
            self.events_log.append(result)
            self.on_event(result)

            # Add future event
            insort_right(future_events, (event_tg.get_new_timestamp(), event))
            

            
    