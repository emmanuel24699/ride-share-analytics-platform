import pandas as pd
import random
from faker import Faker
from vehicles import generate_vehicles  # For pool
from zones import generate_zones  # For zone pool

fake = Faker()

def generate_drivers(n_drivers=10_000, vehicle_pool=None, zone_pool=None, seed=42):
    if vehicle_pool is None:
        _, vehicle_pool = generate_vehicles()
    if zone_pool is None:
        _, zone_pool = generate_zones()
    zone_ids = [z['zone_id'] for z in zone_pool]
    random.seed(seed)
    statuses = ["active", "offline", "blocked"]
    drivers = []
    for i in range(n_drivers):
        driver_id = f"D{str(i+1).zfill(6)}"
        # Deterministic assignment: 90% get a vehicle from pool (no modulo randomness)
        current_vehicle_id = random.choice(vehicle_pool) if random.random() < 0.9 else None
        home_zone = random.choice(zone_ids)
        joined_at = fake.date_between(start_date='-2y', end_date='today')
        drivers.append({
            "driver_id": driver_id,
            "name": fake.name(),
            "phone": fake.phone_number(),
            "status": random.choices(statuses, weights=[0.6, 0.3, 0.1])[0],
            "rating": round(random.uniform(3.5, 5.0), 2),
            "lifetime_trips": random.randint(0, 15000),
            "current_vehicle_id": current_vehicle_id,  # Valid FK or None
            "home_zone_id": home_zone,  # FK
            "joined_at": joined_at.isoformat(),
            "version": 1,
            "valid_from": "2023-01-01T00:00:00Z",
            "valid_to": None
        })
    df = pd.DataFrame(drivers)
    # Validation: FKs valid (ignore None for optional)
    assigned_vehicles = df['current_vehicle_id'].dropna()
    assert assigned_vehicles.isin(vehicle_pool).all(), "Driver vehicle FK invalid!"
    assert df['home_zone_id'].isin(zone_ids).all(), "Driver zone FK invalid!"
    assert df['driver_id'].nunique() == len(df), "Driver ID collision!"
    # Stat check: ~90% assigned
    assert abs(df['current_vehicle_id'].notna().mean() - 0.9) < 0.05, "Assignment rate off!"
    return df, list(df['driver_id'])  # Pool for trips

if __name__ == "__main__":
    df, pool = generate_drivers()
    df.to_parquet("../../data_samples/drivers.parquet", compression="snappy")
    print(f"Generated {len(df)} drivers with valid FKs → data_samples/")