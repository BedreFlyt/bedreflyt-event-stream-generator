from src.patient_event_generator import PatientDiagnosisETG, PatientDiagnosisSampleSpace
from src.EventStreamGenerator import EventStreamGenerator
from src.type.api_types import Diagnosis, Treatment
from src.services.api_calls import APIClient
from src.utilities.constraints import timestamp_constraints, occurrences_constraints

from typing import List

import json
import sys
import requests
import random
import time
import argparse
import os
import logging
import math
import numpy as np

import numpy as np

host = "localhost"
url = f"http://{host}:8090/api/v1"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

neurosurgery_oslo_rooms = []

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
)

events = {}

# Callback function to handle events
def event_handler(event):
    global events
    # save the event into the events dictionary using the timestamp as key appending the event if present, or creating a new list
    timestamp = math.floor(event[0])
    if timestamp in events:
        events[timestamp].append(event)
    else:
        events[timestamp] = [event]

def create_allocation_batches(
        mean: int,
        sds: int,
        mode: str,
        time_steps: int,
        peaks: bool,
        client: APIClient,
        seed: int = 42):
    global events
    events = {}

    intervals = [(i, i+1) for i in range(time_steps)]
    occurrences = []

    # If we have peaks, we need to alternate between high and low occurrences every 5 time steps
    if peaks:
        for i in range(time_steps):
            if (i // 5) % 2 == 0:
                occurrences.append(mean * 1.5)
            else:
                occurrences.append(mean / 1.5)
    else:
        occurrences = [mean] * time_steps

    time_scaling = 100 # 1 is real-time

    # Occurrence Noise Standard Deviation
    occurrence_noise_sds = [sds] * time_steps

    patients = client.get_users()
    if not patients:
        logger.warning("No patients found")
        return

    temp_diagnoses = client.get_diagnoses()
    if not temp_diagnoses:
        logger.warning("No diagnoses found")
        return
    else:
        diagnoses = [Diagnosis(el["diagnosisName"]) for el in temp_diagnoses]

    # Filter diagnosis based on mode
    if mode == "normal":
        diagnoses = diagnoses
    elif mode == "crisis":
        diagnoses = [{
                "diagnosis_name": "C71.2"
            }, {
                "diagnosis_name": "I60.1"
            }, {
                "diagnosis_name": "I60.0"
            }]
    elif mode == 'medium-crisis':
        diagnoses = [{
                "diagnosis_name": "C71.2"
            }, {
                "diagnosis_name": "I60.1"
            }, {
                "diagnosis_name": "I60.0"
            }]
        for diagnosis in random.sample(diagnoses, k=2):
            diagnoses.append({"diagnosis_name": diagnosis["diagnosis_name"]})
    else:
        print(f"Invalid mode: {mode}")
        assert False

    treatments = client.get_treatments() or []

    etg = PatientDiagnosisETG(
        occurrences=occurrences,
        time_intervals=intervals,
        noise_sds=[0] * time_steps,
        occurrences_sds=occurrence_noise_sds,
        seed=seed,
        timestamp_constraints=timestamp_constraints,
        occurrences_constraints=occurrences_constraints
    )
    ess = PatientDiagnosisSampleSpace(
        patient_ids=[patient["patientId"] for patient in patients],
        diagnosis_codes=diagnoses,
        treatments=treatments,
        seed=seed
    )
    event = (etg, ess)

    time_series_generator = EventStreamGenerator([event], event_handler)
    # Run the generator to produce data for "max_time" time with a time-scaling of 100
    data = time_series_generator.run(time_steps, time_scaling)

    # Log results
    logger.info(f"Generated data: {data}")

def test_allocation(
        mode: str,
        mean: int,
        std: int,
        iteration: int,
        time_steps: int,
        adaptive: bool,
        peaks: bool,
        starts_at: int,
        client: APIClient):
    time_step_times = []
    total_capacities = []
    total_allocations = []
    total_completes = []
    total_times_results = []

    print(f"Testing allocation with mode: {mode}, mean: {mean}, std: {std}, iteration: {iteration}, time_steps: {time_steps}")

    allocations_number = 0
    create_allocation_batches(mean, std, mode, time_steps, peaks, client, iteration)

    global events
    for k in events:
        allocations = []
        start_time = time.time()  # Start timing the time_step
        print(f"Starting time_step {k + 1}")
        
        wards = client.get_wards()
        if not wards:
            print("No wards found")
            return
        
        capacities = {}
        for ward in wards:
            capacities[f"{ward['wardName']}_&_{ward['wardHospital']['hospitalCode']}"] = client.get_capacities(ward['wardName'], ward['wardHospital']['hospitalCode']) if ward['wardName'] == "Neurosurgery" else []

        for ward_key, ward_capacities in capacities.items():
            if not ward_capacities:
                print(f"No capacities found for ward {ward_key}")
                continue

            total_capacity = sum(ward_capacities)
            allocation_count = max(0, int(np.random.normal(mean, std, 1)[0]))

        for batch in events[k]:
            _, event_data = batch
            
            # event_data contains the patient information we need
            # Convert np.str_ to regular string
            patient_id = str(event_data["patient_id"])
            
            # Handle the diagnosis_code which is a Diagnosis object
            diagnosis_obj = event_data["diagnosis_code"]
            if hasattr(diagnosis_obj, 'diagnosis_name'):
                diagnosis = diagnosis_obj.diagnosis_name
            elif hasattr(diagnosis_obj, 'name'):
                diagnosis = diagnosis_obj.name
            else:
                # Fallback: convert to string
                diagnosis = str(diagnosis_obj)
            
            # Create a single allocation for this event
            allocations.append({
                "batch": int(k + 1),
                "patientId": patient_id,
                "diagnosis": diagnosis
            })

        ward_name, hospital_code = ward_key.split("_&_")
        # ward_name = "Neurosurgery"
        logging.info(f"Allocating {len(allocations)} patients for ward {ward_name} with total capacity {total_capacity}")
        allocations_number += len(allocations)
        payload = {
            "scenario": allocations,
            "mode": "worst",
            "smtMode": "changes",
            "wardName": ward_name,
            "hospitalCode": hospital_code,
            "timeStep": k,
            "adaptiveCapacity": adaptive
        }

        with open(f"requests/{mean}_{std}_{mode}_{iteration}_{k}_{time_steps}_payload.json", "w") as file:
            json.dump(payload, file)

        # client.delete_allocations()
        # os.system("redis-cli FLUSHALL")  # Clear Redis cache before each allocation
        response = requests.post(f"{url}/allocation/simulate", json=payload)
        if response.status_code == 200:
            print(f"Successfully allocated patients for ward {ward_name} in hospital {hospital_code}")
            response_data = response.json()
            executions_data = response_data.get("executions")
            total_times_results.append({
                "time_step": k + 1,
                "ward": ward_key,
                "duration": executions_data
            })
            total_completes.append({
                "time_step": k + 1,
                "ward": ward_key,
                "completes": True
            })
        else:
            print(f"Failed to allocate patients for ward {ward_name} in hospital {hospital_code}: {response.status_code}")
            total_completes.append({
                "time_step": k + 1,
                "ward": ward_key,
                "completes": False
            })
        
        # Save the total capacity and allocations for this ward
        total_capacities.append({
            "time_step": k + 1,
            "ward": ward_key,
            "total_capacity": client.get_capacity(ward_name, hospital_code)
        })
        total_allocations.append({
            "time_step": k + 1,
            "ward": ward_key,
            "allocations": len(client.get_allocations())
        })

    end_time = time.time()  # End timing the time_step
    time_step_duration = end_time - start_time
    time_step_times.append({"time_step": k + 1, "duration": time_step_duration})
    print(f"time_step {k + 1} took {time_step_duration:.2f} seconds")

    # Write the capacities, allocations, and time_step times to files
    output_data = {
        "capacities": total_capacities,
        "allocations": total_allocations,
        "completion": total_completes
    }

    folder_name = f"{mode}_{mean}_{std}_{iteration}_{time_steps}_{adaptive}"

    # Create folder {mode}_{mean}_{std}_{iteration}_{time_steps}
    os.makedirs(f"sim_output/{folder_name}", exist_ok=True)

    with open(f"sim_output/{folder_name}/allocation_results.json", "w") as file:
        json.dump(output_data, file, indent=4)

    with open(f"sim_output/{folder_name}/time_step_times.json", "w") as file:
        json.dump(time_step_times, file, indent=4)

    with open(f"sim_output/{folder_name}/executions_time_step_times.json", "w") as file:
        json.dump(total_times_results, file, indent=4)

    logging.info("Execution completed. Results saved to 'allocation_results.json' and 'time_step_times.json'.")

if __name__ == "__main__":
    # Test the event generator with different modes
    
    parser = argparse.ArgumentParser("event-generator.py")
    parser.add_argument("--host", help="Host to connect to", type=str, default="localhost")
    parser.add_argument("--std", help="Standard deviation", type=int, default="1")
    parser.add_argument("--mean", help="Mean", type=int, default="5")
    parser.add_argument("--mode", help="Mode from [normal, crisis, medium-crisis]", type=str, default="normal")
    parser.add_argument("--iterations", help="Iterations", type=int, default="10")
    parser.add_argument("--time_steps", help="Time steps to run", type=int, default="10")
    parser.add_argument("--rooms", help="Create rooms for Neurosurgery in Oslo", type=int, default=0)
    parser.add_argument("--starts_at", help="Start execution at a specific time step", type=int, default=0)
    parser.add_argument("--adaptive", help="Use adaptive capacity", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--peak-adaptive", help="Use peak adaptive capacity", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    
    if args.mode not in ["normal", "crisis", "medium-crisis", "variable"]:
        logger.error("Usage: python event-generator.py [normal|crisis|medium-crisis|variable]")
        sys.exit(1)

    if args.host:
        client = APIClient(args.host)
    else:
        client = APIClient()

    if args.starts_at > 0:
        if args.starts_at >= args.time_steps:
            print(f"starts_at {args.starts_at} must be less than time_steps {args.time_steps}")
            sys.exit(1)
        print(f"Starting execution at time step {args.starts_at}")
        starts_at = args.starts_at
    else:
        starts_at = 0

    if args.rooms > 0:
        for i in range(args.rooms):
            neurosurgery_oslo_rooms.append(330 + i)
        print(f"Creating {args.rooms} rooms for Neurosurgery in Oslo")
        client.create_rooms_for_neurosurgery_oslo()
        # os.system("redis-cli FLUSHALL")

    for iteration in range(args.iterations):
        print('Iteration', iteration)
        if iteration < starts_at:
            print(f"Skipping iteration {iteration} as it is before starts_at {starts_at}")
            continue

        client.delete_allocations()
        print("Deleted all previous allocations")
        print("Waiting for 1 seconds to reset before starting the allocation test...")
        time.sleep(1)
        print("Starting allocation test")

        test_allocation(args.mode, args.mean, args.std, iteration, args.time_steps, args.adaptive, args.peak_adaptive, starts_at, client)

        # client.delete_rooms_for_neurosurgery_oslo()