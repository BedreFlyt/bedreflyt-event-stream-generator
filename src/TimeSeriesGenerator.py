from abc import ABC, abstractmethod
from bisect import insort_right

from numpy import random

class EventFrequency:
    def __init__(self, occurrences, time_intervals, variances):
        self.variances = variances
        self.time_intervals = time_intervals
        time_deltas = [t2-t1 for t1, t2 in time_intervals]
        self.periods = [time_delta/occurrence for (occurrence, time_delta) in zip(occurrences, time_deltas)] 

    def sample (self, t):
        """Samples from the sample space. Must be implemented in subclasses."""
        # Update time intervals if time is larger than largest number
        wrap_around_number = self.time_intervals[-1][1]
        t = t%wrap_around_number
        
        # Find index in periods corresponding to time t
        try:
            i = next(i for i, (t1, t2) in enumerate(self.time_intervals) if t1 <= t < t2)
        except StopIteration:
            raise ValueError(f"Time t={t} is not within any defined time interval.")

        # Do sample
        return random.normal(loc=self.periods[i], scale=self.variances[i])

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
        self.events_log = []

    def run (self, stop_time):
        # Initialize
        future_events: list[tuple[float, tuple[EventFrequency, EventSampleSpace]]] = []
        for event in self.events:
            event_F, _ = event
            insort_right(future_events, (abs(event_F.sample(0)), event))
        
        # Loop through events (foreverrrr)
        while True:
            # Retrieve
            timed_event = future_events.pop(0)
            t, event = timed_event
            event_F, event_SS = event

            # Update simulation clock
            self.clock = t

            # Sample
            sample = event_SS.sample(self.clock)
            result = (self.clock, sample)
            
            # Log
            self.events_log.append(result)
            self.on_event(result)

            # Add future event
            insort_right(future_events, (self.clock + abs(event_F.sample(self.clock)), event))

            if (self.clock > stop_time): break
    