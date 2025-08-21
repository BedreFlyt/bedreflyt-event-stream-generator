import numpy as np
import logging
import math

from EventStreamGenerator import EventTimestampGenerator, EventSampleSpace, EventStreamGenerator
from analytics import plot_timeline_with_colors, count_number_of_occurrences_in_intervals
from patient_event_generator import PatientDiagnosisETG, PatientDiagnosisSampleSpace

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,                            
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)

events = {}

max_time = 3
intervals = [(i, i+1) for i in range(max_time)]
occurrences = [i+1 for i in range(max_time)]
time_scaling = 100 # 1 is real-time

print("Time intervals:", intervals)
print("Occurrences:", occurrences)

# Callback function to handle events
def event_handler(event):
    # save the event into the events dictionary using the timestamp as key appending the event if present, or creating a new list
    timestamp = math.floor(event[0])
    if timestamp in events:
        events[timestamp].append(event)
    else:
        events[timestamp] = [event]

# NEW INPUTS
# Event Noise Standard Deviation
__noise_sd = .5
noise_sds = [__noise_sd]*max_time

# Occurrence Noise Standard Deviation
__occurrence_noise_sd = 1
occurrence_noise_sds = [__occurrence_noise_sd]*max_time

print("Noise Standard Deviations:", noise_sds)
print("Occurrence Noise Standard Deviations:", occurrence_noise_sds)

from typing import Any, Callable, Set
# Timestamp Constraints
timestamp_constraints: Set[Callable[[dict, Any], bool]]={
                     # Every timestamp (ts) must be non-negative
                     lambda state, ts: ts > 0, 
                     # Every timestamp (ts) must be greater than the prior expect for the first datapoint
                     lambda state, ts: ts > state["timestamps"][-1] if (len(state["timestamps"])) != 0 else True,
                     # Every timestamp (ts) must be within its own interval
                     lambda state, ts: state["time_intervals"][state["current_interval"]][0] <= ts < state["time_intervals"][state["current_interval"]][1]
                }
# Occurrence Constraints
occurrences_constraints: Set[Callable[[dict, Any], bool]]={
    # The number of occurrences must be non-negative
    lambda state, o: o >= 0
}

etg = PatientDiagnosisETG(
    occurrences=occurrences,
    time_intervals=intervals,
    noise_sds=noise_sds,
    occurrences_sds=occurrence_noise_sds)
ess = PatientDiagnosisSampleSpace()
event = (etg, ess)

# Initialize the TimeSeriesGenerator with the ETG and ESS
time_series_generator = EventStreamGenerator([event], event_handler)
# Run the generator to produce data for "max_time" time with a time-scaling of 100
data = time_series_generator.run(max_time, time_scaling)

# Log results
logger.info(f"Generated data: {data}")

print(f"Occurrences in intervals: {count_number_of_occurrences_in_intervals(intervals, data)}")

# exit()

# Extract timestamps from data for plotting
if isinstance(data, list) and len(data) > 0:
    # Check if data contains tuples with dictionaries as the second element
    if isinstance(data[0], tuple) and len(data[0]) == 2 and isinstance(data[0][1], dict):
        # Extract timestamps and create color mappings from dictionary data
        formatted_data = []
        for timestamp, event_dict in data:
            # Use diagnosis_code to determine color, or use a default color
            diagnosis_code = event_dict.get('diagnosis_code', 'unknown')
            # Map diagnosis codes to colors (you can customize this mapping)
            color_map = {
                "G91.2": 'red',     # Normaltrykkshydrocephalus
                "C71.2": 'blue',    # Ondartet svulst i tinninglapp  
                "C71.3": 'green',   # Ondartet svulst i isselapp
                "M50.0": 'orange',  # Lidelse i cervikalskive, med myelopati
                "M50.1": 'purple',  # Lidelse i cervikalskive, med radikulopati
                "S06.5": 'brown',   # Traumatisk eller uspesifisert subduralblødning
                "G50.0": 'pink',    # Trigeminusnevralgi
                "I67.1": 'gray',    # Hjerneaneurisme uten ruptur
                "I60.0": 'cyan',    # Subaraknoidalblødning fra carotissifong
                "I60.1": 'yellow'   # Subaraknoidalblødning fra arteria cerebri media
            }
            color = color_map.get(diagnosis_code, 'black')  # Default to black for unknown codes
            formatted_data.append((timestamp, color))
        plot_timeline_with_colors(formatted_data, intervals)
    elif isinstance(data[0], tuple) and len(data[0]) == 2 and not isinstance(data[0][1], dict):
        # Data is already in (timestamp, color) format
        plot_timeline_with_colors(data, intervals)
    else:
        # Handle other data formats or log an error
        print(f"Unexpected data format: {type(data[0]) if data else 'empty list'}")
        print(f"First element: {data[0] if data else 'N/A'}")
else:
    print("No data to plot")

print(events)