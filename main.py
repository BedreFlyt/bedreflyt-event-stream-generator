from src.patient_event_generator import PatientDiagnosisETG, PatientDiagnosisSampleSpace
import src.type.api_types
from src.services.api_calls import APICalls

import json
import sys
import requests
import random
import time
import argparse
import os

import numpy as np

host = "localhost"
url = f"http://{host}:8090/api/v1"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

neurosurgery_oslo_rooms = []

def test_allocation(
        mode: str,
        mean: int,
        std: int,
        iteration: int,
        time_steps: int,
        client: APICalls):
    
    time_step_times = []
    patients = client.get_users()
    if not patients:
        print("No patients found")
        return

    diagnoses = client.get_diagnoses()
    if not diagnoses:
        print("No diagnoses found")
        return
    
    # Filter diagnosis based on mode
    if mode == "normal":
        diagnoses = diagnoses
    elif mode == "crisis":
        diagnoses = [{
                "diagnosisName": "C71.2"
            }, {
                "diagnosisName": "I60.1"
            }, {
                "diagnosisName": "I60.0"
            }]
    elif mode == 'medium-crisis':
        diagnoses = [{
                "diagnosisName": "C71.2"
            }, {
                "diagnosisName": "I60.1"
            }, {
                "diagnosisName": "I60.0"
            }]
        for diagnosis in random.sample(diagnoses, k=2):
            diagnoses.append({"diagnosisName": diagnosis["diagnosisName"]})
    else:
        print(f"Invalid mode: {mode}")
        assert False
    
    total_capacities = []
    total_allocations = []

    allocations_number = 0
    for time_step in range(time_steps):  # Perform 10 time_steps
        start_time = time.time()  # Start timing the time_step
        print(f"Starting time_step {time_step + 1}")
        
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
            
            allocation_count = max(0, int(np.random.normal(mean, std, 1)[0]))  # Ensure allocation_count is non-negative
            selected_patients = random.sample(patients, min(allocation_count, len(patients)))
            
            allocations = []
            for patient in selected_patients:
                allocations.append({
                    "batch": int(time_step + 1),
                    "patientId": patient["patientId"],
                    "diagnosis": random.choice(diagnoses)["diagnosisName"]
                })
            
            
            ward_name, hospital_code = ward_key.split("_&_")
            # ward_name = "Neurosurgery"
            print(f"Allocating {len(allocations)} patients for ward {ward_name} with total capacity {total_capacity}")
            allocations_number += len(allocations)
            payload = {
                "scenario": allocations,
                "mode": "worst",
                "smtMode": "changes",
                "wardName": ward_name,
                "hospitalCode": hospital_code,
                "iteration": time_step,
            }
            
            # os.system("redis-cli FLUSHALL")  # Clear Redis cache before each allocation
            response = requests.post(f"{url}/allocation/simulate", json=payload)
            if response.status_code == 200:
                print(f"Successfully allocated patients for ward {ward_name} in hospital {hospital_code}")
            else:
                print(f"Failed to allocate patients for ward {ward_name} in hospital {hospital_code}: {response.status_code}")
            
            # Save the total capacity and allocations for this ward
            total_capacities.append({
                "time_step": time_step + 1,
                "ward": ward_key,
                "total_capacity": client.get_capacity(ward_name, hospital_code)
            })
            total_allocations.append({
                "time_step": time_step + 1,
                "ward": ward_key,
                "allocations": len(client.get_allocations())
            })
        
        end_time = time.time()  # End timing the time_step
        time_step_duration = end_time - start_time
        time_step_times.append({"time_step": time_step + 1, "duration": time_step_duration})
        print(f"time_step {time_step + 1} took {time_step_duration:.2f} seconds")

        # Wait for 30 seconds before the next time_step
        time.sleep(30)

    # Write the capacities, allocations, and time_step times to files
    output_data = {
        "capacities": total_capacities,
        "allocations": total_allocations
    }
    with open(f"allocation_results_{mode}_{mean}_{std}_{iteration}_{time_steps}.json", "w") as file:
        json.dump(output_data, file, indent=4)

    with open(f"time_step_times_{mode}_{mean}_{std}_{iteration}_{time_steps}.json", "w") as file:
        json.dump(time_step_times, file, indent=4)

    print("Execution completed. Results saved to 'allocation_results.json' and 'time_step_times.json'.")

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
    args = parser.parse_args()
    
    if args.mode not in ["normal", "crisis", "medium-crisis", "variable"]:
        print("Usage: python event-generator.py [normal|crisis|medium-crisis|variable]")
        sys.exit(1)

    if args.host:
        client = APICalls(args.host)
    else:
        client = APICalls()

    for iteration in range(args.iterations):
        print('Iteration', i)
        if args.rooms > 0:
            for i in range(args.rooms):
                neurosurgery_oslo_rooms.append(330 + i)
            print(f"Creating {args.rooms} rooms for Neurosurgery in Oslo")
            client.create_rooms_for_neurosurgery_oslo()
            # os.system("redis-cli FLUSHALL")

        client.delete_allocations()
        print("Deleted all previous allocations")
        print("Waiting for 10 seconds to reset before starting the allocation test...")
        time.sleep(10)
        print("Starting allocation test")

        test_allocation(args.mode, args.mean, args.std, iteration, args.time_steps)

        client.delete_rooms_for_neurosurgery_oslo()