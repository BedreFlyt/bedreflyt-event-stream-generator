from abc import ABC, abstractmethod
from bisect import insort_right
import numpy as np
from numpy import random
from src.utils import get_index_in_time_intervals

class EventFrequency:
    def __init__(self, occurrences, time_intervals, period_variances, no_occurrences_variances):
        self.occurrences = occurrences
        self.time_intervals = time_intervals
        self.period_variances = period_variances
        self.no_occurrences_variances = no_occurrences_variances
        self.periods = self.sample_no_periods()
       
    
    def sample_no_periods (self):
        time_deltas = [t2-t1 for t1, t2 in self.time_intervals]
        return [time_delta/occurrence if occurrence!=0 else 0 for (occurrence, time_delta) in zip(self.__sample_no_occurrences(), time_deltas)] 
    
    def __sample_no_occurrences (self):
        def get_random_normal_geq_0 (o, v):
            s = round(random.normal(loc=o, scale=v))
            if s < 0: return 0
            else: return s
        return [get_random_normal_geq_0(o, v) for o, v in zip(self.occurrences, self.no_occurrences_variances)]

    def sample (self, t, deterministic=False):
        """Samples a timing interval"""
        # Update time intervals if time is larger than largest number
        wrap_around_number = self.time_intervals[-1][1]
        if t >= wrap_around_number:
            self.periods = self.sample_no_periods()
            t = t%wrap_around_number
        
        # Find index in periods corresponding to time t
        try:
            i = next(i for i, (t1, t2) in enumerate(self.time_intervals) if t1 <= t < t2)
        except StopIteration:
            raise ValueError(f"Time t={t} is not within any defined time interval.")

        # Sample: 0 indicates that there is not any events otherwise, sample
        if self.periods[i] == 0: return -1
        elif deterministic: return self.periods[i]
        else: return random.normal(loc=self.periods[i], scale=self.period_variances[i])

class EventSampleSpace:
    def __init__(self):
        pass

    @abstractmethod
    def sample (self, t):
        """Samples from the sample space. Must be implemented in subclasses."""
        pass

class TimeSeriesGenerator:
    def __init__(self, events: list[tuple[EventFrequency, EventSampleSpace]], on_event):
        self.events = set(events)
        self.on_event = on_event
        self.clock = 0
        self.clock_ideal = 0
        self.events_log = []
        self.events_log_shifted = []
        self.events_log_ideal = []
        self.events_log_ideal_shifted = []

    def run (self, stop_time):
        # Initialize
        future_events: list[tuple[float, tuple[EventFrequency, EventSampleSpace]]] = []
        future_events_ideal: list[tuple[float, tuple[EventFrequency, EventSampleSpace]]] = []

        for event in self.events:
            event_F, _ = event
            sampled_t = abs(event_F.sample(0))
            if (sampled_t != -1):
                insort_right(future_events, (sampled_t, event))
            
            # Deterministic case
            sampled_t_ideal = event_F.sample(0, deterministic=True)
            if (sampled_t_ideal != -1):
                insort_right(future_events_ideal, (sampled_t_ideal, event))
        
        # Loop through events (foreverrrr)
        while True:
            # Retrieve
            timed_event = future_events.pop(0)
            t, event = timed_event
            event_F, event_SS = event

            # Retrieve ideal event
            timed_event_ideal = future_events_ideal.pop(0)
            t_ideal, event_ideal = timed_event_ideal
            event_F_ideal, event_SS_ideal = event_ideal

            # Update simulation clock
            self.clock = t
            self.clock_ideal = t_ideal

            if (self.clock_ideal > stop_time): 
                return self.events_log, self.events_log_ideal, self.events_log_shifted, self.events_log_ideal_shifted
            
            # Get ideal index
            i = get_index_in_time_intervals(event_F.time_intervals, self.clock_ideal)
            period = event_F.periods[i]

            # Sample
            sample = event_SS.sample(self.clock)
            result = (self.clock, sample)
            result_ideal = (self.clock_ideal, sample)
            result_shifted = (self.clock - period/2, sample)
            result_ideal_shifted = (self.clock_ideal - period/2, sample)
            
            # Log
            self.events_log.append(result)
            self.events_log_ideal.append(result_ideal)
            self.events_log_shifted.append(result_shifted)
            self.events_log_ideal_shifted.append(result_ideal_shifted)
            self.on_event(result)

            # Add future event
            sampled_t = abs(event_F.sample(self.clock))
            if (sampled_t != -1):
                insort_right(future_events, (self.clock + sampled_t, event))
            
            # Add future event ideal
            sampled_t_ideal = event_F_ideal.sample(self.clock_ideal, deterministic=True)
            if (sampled_t_ideal != -1):
                insort_right(future_events_ideal, (self.clock_ideal + sampled_t_ideal, event_ideal))
            

            
    