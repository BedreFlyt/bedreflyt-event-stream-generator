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
        print(f"self.spacings: {self.spacings}")
        self.ideal_timestamps = [0]
        self.timestamps = []
        self.timestamp_id = 1
    
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
        # Get latest timestamp
        latest_ts = self.ideal_timestamps[-1]
        # Find interval index including start
        index_period = self._find_interval_including_start(latest_ts)
        # Get period
        period = self.periods[index_period]
        # Calculate new ideal timestamp
        new_ideal_ts = latest_ts + period
        self.ideal_timestamps.append(new_ideal_ts)

        # Get interval including end
        index_spacing = self._find_interval_including_end(new_ideal_ts)
        # Retrieve spacing
        spacing = self.spacings[index_spacing]
        # Shift by spacing
        shifted = self.ideal_timestamps[-2] + spacing
        # Add noise and return
        noisy = shifted + self.sample_noise(new_ideal_ts)
        print(f"latest_ts: {latest_ts}, index_period: {index_period}, period: {period}, new_ideal_ts: {new_ideal_ts}, index_spacing: {index_spacing}, spacing: {spacing}, shifted: {shifted}, noisy: {noisy}")
        self.timestamp_id += 1
        return noisy
    
    
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
            

            
    