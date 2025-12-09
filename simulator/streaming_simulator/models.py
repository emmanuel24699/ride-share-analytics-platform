from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Tuple

class DriverLocationPing(BaseModel):
    event_id: str
    driver_id: str
    vehicle_id: Optional[str]
    lat: float
    lng: float
    h3_index: str
    timestamp: str = datetime.utcnow().isoformat() + "Z"
    event_time: str = timestamp

class TripEvent(BaseModel):
    event_id: str
    trip_id: str
    event_type: str  # request, matched, pickup, dropoff, cancel
    driver_id: Optional[str] = None
    rider_id: str
    pickup_zone_id: str
    dropoff_zone_id: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    timestamp: str = datetime.utcnow().isoformat() + "Z"
    event_time: str = timestamp

class SurgeEvent(BaseModel):
    event_id: str
    zone_id: str
    surge_multiplier: float
    demand_score: float
    timestamp: str = datetime.utcnow().isoformat() + "Z"
    event_time: str = timestamp