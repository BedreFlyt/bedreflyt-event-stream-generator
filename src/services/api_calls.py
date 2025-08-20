import requests
import os

url = os.environ.get("API_URL", "http://localhost:8090/api/v1")

def get_diagnosis_codes():
    response = requests.get(f"{url}/fuseki/diagnosis")
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to retrieve diagnosis codes"}

def get_treatments():
    response = requests.get(f"{url}/fuseki/treatments")
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to retrieve treatments"}