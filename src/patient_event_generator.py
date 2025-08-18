from EventStreamGenerator import EventTimestampGenerator, EventSampleSpace
from typing import List, Tuple, Dict, Set, Callable, Any
import numpy as np

class PatientDiagnosisETG(EventTimestampGenerator):
    """
    Generates synthetic patient diagnosis events.
    """

    def __init__ (self,
                  occurrences: List[int],
                  time_intervals: List[Tuple[int, int]],
                  noise_sds: List[float] = None,
                  occurrences_sds: List[float] = None,
                  timestamp_constraints: Set[Callable[[dict, Any], bool]]={
                     # Every timestamp (ts) must be non-negative
                     lambda state, ts: ts > 0, 
                     # Every timestamp (ts) must be greater than the prior expect for the first datapoint
                     lambda state, ts: ts > state["timestamps"][-1] if (len(state["timestamps"])) != 0 else True,
                     # Every timestamp (ts) must be within its own interval
                     lambda state, ts: state["time_intervals"][state["current_interval"]][0] <= ts < state["time_intervals"][state["current_interval"]][1]
                    },
                  occurrences_constraints: Set[Callable[[dict, Any], bool]]={
                        # The number of occurrences must be non-negative
                        lambda state, o: o >= 0
                    }
                 ) -> None:
        self.noise_sds = noise_sds or [0] * len(time_intervals)
        self.occurrences_sds = occurrences_sds or [0] * len(occurrences)

        super().__init__(occurrences, time_intervals, timestamp_constraints, occurrences_constraints)

    def sample_noise (self, index: int) -> float:
        """
        Samples the noise for timestamp generation.
        """
        return np.random.normal(loc=0, scale=self.noise_sds[index])

    def sample_occurrences (self, occurrences_i: int, index: int) -> float:
        """
        Samples the occurrences for a given index.
        """
        if self.occurrences_sds[index] == 0:
            return occurrences_i

        sample = int(np.round(np.random.normal(
            loc=occurrences_i, scale=self.occurrences_sds[index])))

        return max(0, sample) # Ensure non-negative values

class PatientDiagnosisSampleSpace(EventSampleSpace):
    """
    Defines the sample space for patient diagnosis events.

    Events - generates (patient_id, diagnosis_code) pairs.
    """
    def __init__(self,
                 patient_ids: List[str]=None,
                 diagnosis_codes: List[str]=None) -> None:
        super().__init__()

        self.patient_ids = patient_ids or [f"P{i}" for i in range(100)]

        # Hardcoded from the current implementation of Bedreflyt for testing purposes
        self.diagnosis_codes = diagnosis_codes or [
            "G91.2", # Normaltrykkshydrocephalus
            "C71.2", # Ondartet svulst i tinninglapp
            "C71.3", # Ondartet svulst i isselapp
            "M50.0", # Lidelse i cervikalskive, med myelopati
            "M50.1", # Lidelse i cervikalskive, med radikulopati
            "S06.5", # Traumatisk eller uspesifisert subduralblødning
            "G50.0", # Trigeminusnevralgi
            "I67.1", # Hjerneaneurisme uten ruptur
            "I60.0", # Subaraknoidalblødning fra carotissifong eller carotisbifurkatur
            "I60.1" # Subaraknoidalblødning fra arteria cerebri media
        ]

    def sample(self, timestamp: int) -> Tuple[str, str]:
        """
        Generates a (patient_id, diagnosis_code) pair for timestamp.
        """
        patient_id = np.random.choice(self.patient_ids)
        diagnosis_code = np.random.choice(self.diagnosis_codes)

        return {"patient_id": patient_id, "diagnosis_code": diagnosis_code, "timestamp": timestamp}
