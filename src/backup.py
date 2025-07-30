from abc import ABC, abstractmethod
from bisect import insort_right
import numpy as np
from time import sleep

class EventTimestampGenerator(ABC):
    def __init__(self, occurrences, time_intervals):
        self.occurrences = occurrences
        self.time_intervals = time_intervals
        self.timestamps = []
        self.occurrence_counter = 0
        self.current_interval = 0
        self.timestamp = 0

        # Initialize and update right after
        self.sampled_occurrences = self.__get_sampled_occurrences()
        self.spacings = self.__calculate_spacings()
    

    def __sample_occurrences_and_calculate_new_spacings(self) -> None:
        """Resamples occurrences and calculates corresponding spacings. 
        
        :returns: None. Modifies class properties, returns nothing.""" 
        self.sampled_occurrences = self.__get_sampled_occurrences()
        self.spacings = self.__calculate_spacings()

    def __get_sampled_occurrences(self) -> list[int]:
        """Samples occurrences.
        
        :returns: A list of the sampled occurrences in each interval"""
        return [self.sample_occurrences(self.occurrences[i], i) for i in range(len(self.occurrences))]
    
    def __calculate_spacings(self) -> list[int]:
        """Calculates spacings.
        
        :returns: A list of the calculated spacings corresponding to each interval"""
        return [(t2-t1) / (o+1) for (t1, t2), o in zip(self.time_intervals, self.sampled_occurrences)]
    
    def get_new_timestamp(self) -> float:
        """Calculates a new timestamp"""
        # Check if occurrences in interval have been met and updates accordingly
        if self.occurrence_counter == self.sampled_occurrences[self.current_interval]:
            self.occurrence_counter = 0
            # Check if interval is about to overflow
            if self.current_interval+1 == len(self.occurrences):
                self.current_interval = 0
                self.__update_intervals()
                self.__sample_occurrences_and_calculate_new_spacings()
            else:
                self.current_interval += 1 
            
            self.timestamp = self.time_intervals[self.current_interval][0]
        
        # Compute new timestamp
        self.timestamp += self.spacings[self.current_interval] + self.sample_noise(self.current_interval)
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
    
    @abstractmethod
    def sample_noise (self, i):
        """Samples noise in i'th interval. Must be implemented in subclasses."""
        pass

    @abstractmethod
    def sample_occurrences (self, occurrences_i, i):
        """Samples occurrences in i'th interval given the number of occurrences in the i'th interval. Must be implemented in subclasses."""
        pass

class EventSampleSpace(ABC):
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

    def run (self, stop_time, real_time=False):
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
            
            if (real_time):
                sleep(t)

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