import uuid
import random
import time
from datetime import datetime
import h3
from faker import Faker
from .models import DriverLocationPing, TripEvent, SurgeEvent

fake = Faker()
random.seed(42)  # Consistent with batch

class SimulatorEngine:
    def __init__(self, state):
        self.state = state
        self.active_trips = {}  # trip_id: {"state": "requested", "events": [], ...}
        self.zone_demand = {z["zone_id"]: 1.0 for z in self.state["zones"]}  # Baseline

    def generate_ping(self, driver_id: str):
        driver_state = self.state["driver_states"][driver_id]
        if driver_state["status"] != "active":
            return None  # Only active drivers ping

        # Simulate movement: random walk to neighbor H3 cell
        current_h3 = driver_state["h3_index"]
        neighbors = list(h3.grid_disk(current_h3, 1))  # Adjacent cells (v4 API)
        new_h3 = random.choice(neighbors) if neighbors else current_h3
        (new_lat, new_lng) = h3.cell_to_latlng(new_h3)

        # Update state
        driver_state["current_lat"] = new_lat
        driver_state["current_lng"] = new_lng
        driver_state["h3_index"] = new_h3

        return DriverLocationPing(
            event_id=str(uuid.uuid4()),
            driver_id=driver_id,
            vehicle_id=driver_state["vehicle_id"],
            lat=new_lat,
            lng=new_lng,
            h3_index=new_h3
        )

    def generate_trip_event(self):
        # Simulate new trip or advance existing
        if random.random() < 0.3 or not self.active_trips:  # 30% chance new trip
            trip_id = f"T{str(random.randint(1000000, 9999999)).zfill(7)}"  # New unique
            rider_id = random.choice(self.state["riders"])
            pickup_zone_id = random.choice([z["zone_id"] for z in self.state["zones"]])
            dropoff_zone_id = random.choice([z["zone_id"] for z in self.state["zones"]])
            self.active_trips[trip_id] = {
                "state": "requested",
                "rider_id": rider_id,
                "pickup_zone_id": pickup_zone_id,
                "dropoff_zone_id": dropoff_zone_id,
                "driver_id": None,
                "events": []
            }
            trip = self.active_trips[trip_id]
            event_type = "request"
        else:
            # Advance random active trip
            trip_id = random.choice(list(self.active_trips.keys()))
            trip = self.active_trips[trip_id]
            if trip["state"] == "requested":
                # Match to driver
                available_drivers = [d for d, s in self.state["driver_states"].items() if s["status"] == "active"]
                if available_drivers:
                    driver_id = random.choice(available_drivers)
                    trip["driver_id"] = driver_id
                    self.state["driver_states"][driver_id]["status"] = "in_trip"
                    event_type = "matched"
                    trip["state"] = "matched"
                else:
                    # No drivers available; mark as cancelled
                    event_type = "cancel"
                    del self.active_trips[trip_id]
            elif trip["state"] == "matched":
                event_type = "pickup"
                trip["state"] = "pickup"
            elif trip["state"] == "pickup":
                if random.random() < 0.15:  # Cancel rate
                    event_type = "cancel"
                    del self.active_trips[trip_id]
                    if trip["driver_id"]:
                        self.state["driver_states"][trip["driver_id"]]["status"] = "active"
                else:
                    event_type = "dropoff"
                    trip["state"] = "dropoff"
                    del self.active_trips[trip_id]
                    if trip["driver_id"]:
                        self.state["driver_states"][trip["driver_id"]]["status"] = "active"
            else:
                return None

        # Update demand for surge sim
        self.zone_demand[trip["pickup_zone_id"]] += 0.1  # Increment demand

        return TripEvent(
            event_id=str(uuid.uuid4()),
            trip_id=trip_id,
            event_type=event_type,
            driver_id=trip.get("driver_id"),
            rider_id=trip["rider_id"],
            pickup_zone_id=trip["pickup_zone_id"],
            dropoff_zone_id=trip["dropoff_zone_id"]
        )

    def generate_surge_event(self):
        zone_id = random.choice([z["zone_id"] for z in self.state["zones"]])
        demand = self.zone_demand[zone_id]
        surge = 1.0 if demand < 1.5 else random.uniform(1.2, 3.0)
        # Decay demand over time
        self.zone_demand[zone_id] = max(1.0, demand * 0.99)
        return SurgeEvent(
            event_id=str(uuid.uuid4()),
            zone_id=zone_id,
            surge_multiplier=surge,
            demand_score=demand
        )

    def run_simulation(self, event_type: str, count: int = 1):
        events = []
        for _ in range(count):
            if event_type == "ping":
                driver_id = random.choice(self.state["drivers"])
                event = self.generate_ping(driver_id)
            elif event_type == "trip":
                event = self.generate_trip_event()
            elif event_type == "surge":
                event = self.generate_surge_event()
            if event:
                events.append(event)
            time.sleep(random.uniform(0.2, 1.0))  # Simulate interval
        return events