from typing import Optional

class Diagnosis:
    def __init__(self, diagnosis_name: str):
        self.diagnosis_name = diagnosis_name

class Treatment:
    def __init__(
            self,
            treatment_name: str,
            treatment_description: Optional[str] = None,
            diagnosis: Diagnosis = None,
            frequency: float = 0.0,
            weight: float = 0.0,
            first_task_name: str = "",
            last_task_name: str = ""):
        self.treatment_name = treatment_name
        self.treatment_description = treatment_description
        self.diagnosis = diagnosis
        self.frequency = frequency
        self.weight = weight
        self.first_task_name = first_task_name
        self.last_task_name = last_task_name