from email.mime import application
import requests
import random

class APIClient:

    def __init__(self, host="localhost"):
        self.host = host
        self.url = f"http://{self.host}:8090/api/v1"
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_diagnoses(self):
        response = requests.get(f"{self.url}/fuseki/diagnosis", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        print("error: Failed to retrieve diagnosis codes")

    def get_treatments(self):
        response = requests.get(f"{self.url}/fuseki/treatments", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        print("error: Failed to retrieve treatments")

    def create_room(self, room_number, capacity, ward, hospital, category_description):
        create_url = self.url + "/fuseki/rooms"
        payload = {
            "roomNumber": room_number,
            "capacity": capacity,
            "penalty": 0.0,
            "ward": ward,
            "hospital": hospital,
            "categoryDescription": category_description
        }
        response = requests.post(create_url, json=payload, headers=self.headers)
        if response.status_code == 200:
            print(f"Room {room_number} created successfully")
        else:
            print("Error creating room")

    def create_rooms(self, payload):
        create_url = self.url + "/fuseki/rooms/multi"
        response = requests.post(create_url, json=payload, headers=self.headers)
        if response.status_code == 200:
            print(f"Rooms created successfully")
        else:
            print("Error creating room")

    def create_rooms_for_neurosurgery_oslo(self, neurosurgery_oslo_rooms):
        """Create a list of rooms for Neurosurgery in Oslo."""
        payload = []
        for room in neurosurgery_oslo_rooms:
            # set a capacity of a random number between 1 and 15
            capacity = random.randint(1, 15)
            payload.append({
                "roomNumber": room,
                "capacity": capacity,
                "penalty": 0.0,
                "ward": "Neurosurgery",
                "hospital": "OSL-RH",
                "categoryDescription": "Sengepost"
            })
        self.create_rooms(payload=payload)

    def delete_room(self, room_number, ward_name, hospital_code):
        """Delete a room by its number, ward name, and hospital code."""
        delete_url = f"{self.url}/fuseki/rooms/{room_number}/{ward_name}/{hospital_code}"
        response = requests.delete(delete_url, headers=self.headers)
        if response.status_code == 200:
            print(f"Room {room_number} deleted successfully")
        else:
            print(f"Error deleting room {room_number}: {response.status_code}")

    def delete_rooms_for_neurosurgery_oslo(self, neurosurgery_oslo_rooms):
        """Delete all rooms for Neurosurgery in Oslo."""
        for room in neurosurgery_oslo_rooms:
            self.delete_room(room, "Neurosurgery", "OSL-RH")

    def set_host(self, new_host):
        """Set the host for the API."""
        self.host = new_host
        self.url = f"http://{self.host}:8090/api/v1"
        print(f"Host set to {self.host}. URL is now {self.url}")

    def get_users(self):
        """Get all users."""
        response = requests.get(f"{self.url}/patients")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get users: {response.status_code}")
            return []
        
    def get_user(self, user_id):
        """Get a specific user by ID."""
        response = requests.get(f"{self.url}/patients/{user_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get user {user_id}: {response.status_code}")
            return None
        
    def get_allocations(self):
        """Get all allocations."""
        response = requests.get(f"{self.url}/patient-allocations/simulated")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get allocations: {response.status_code}")
            return []

    def get_wards(self):
        """Get all wards."""
        response = requests.get(f"{self.url}/fuseki/wards")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get wards: {response.status_code}")
            return []

    def get_rooms(self):
        """Get all rooms."""
        response = requests.get(f"{self.url}/fuseki/rooms")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get rooms: {response.status_code}")
            return []
        
    def get_rooms_by_ward_hospital(self, ward_name, hospital_code):
        """Get all rooms for a specific ward and hospital."""
        response = requests.get(f"{self.url}/fuseki/rooms/{ward_name}/{hospital_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get rooms for ward {ward_name} in hospital {hospital_code}: {response.status_code}")
            return []

    def get_capacities(self, ward_name, hospital_code):
        rooms = self.get_rooms_by_ward_hospital(ward_name, hospital_code)
        if not rooms:
            return []
        # Get the capacities of the filtered rooms
        capacities = []
        for room in rooms:
            if 'capacity' in room:
                capacities.append(room['capacity'])
            else:
                print(f"No capacity found for room {room['roomName']}")
        if not capacities:
            print(f"No rooms found for ward {ward_name} in hospital {hospital_code}")
            return []
        return capacities

    def delete_allocations(self):
        """Delete all allocations."""
        response = requests.delete(f"{self.url}/patient-allocations/all")
        if response.status_code == 200:
            print("Successfully deleted all allocations.")
        else:
            print(f"Failed to delete allocations: {response.status_code}")

    def get_capacity(self, ward_name, hospital_code):
        """Get the size of the allocation for a specific ward and hospital."""
        return sum([el["capacity"] for el in self.get_rooms_by_ward_hospital(ward_name, hospital_code) if "capacity" in el])