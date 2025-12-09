import pandas as pd
import random
from faker import Faker
from drivers import generate_drivers  # Chains pools
from riders import generate_riders
from zones import generate_zones

fake = Faker()

def generate_historical_trips(n_trips=1_000_000, driver_pool=None, rider_pool=None, zone_pool=None, months_back=24, seed=42):
    if driver_pool is None:
        _, driver_pool = generate_drivers()
    if rider_pool is None:
        _, rider_pool = generate_riders()
    if zone_pool is None:
        _, zone_pool = generate_zones()
    zone_ids = [z['zone_id'] for z in zone_pool]
    random.seed(seed)
    statuses = ["completed", "cancelled"]
    trips = []
    for i in range(n_trips):
        trip_id = f"T{str(i+1).zfill(7)}"
        start_time = fake.date_time_between(start_date=f'-{months_back}m', end_date='now')
        duration_min = random.expovariate(1/15)  # Avg 15 min, exponential dist
        # Triangular keeps most trips short, tail to ~30km, mean ≈14km
        distance_km = random.triangular(1, 30, 12)
        pickup_zone = random.choice(zone_ids)
        dropoff_zone = random.choice(zone_ids)  # Allow same for short trips
        driver_id = random.choice(driver_pool)
        rider_id = random.choice(rider_pool)
        surge_multiplier = 1.0 if random.random() < 0.8 else random.uniform(1.2, 3.0)
        trips.append({
            "trip_id": trip_id,
            "driver_id": driver_id,  # FK
            "rider_id": rider_id,  # FK
            "pickup_zone_id": pickup_zone,  # FK
            "dropoff_zone_id": dropoff_zone,  # FK
            "start_time": start_time.isoformat(),
            "duration_minutes": round(duration_min, 2),
            "distance_km": round(distance_km, 2),
            "status": random.choices(statuses, weights=[0.85, 0.15])[0],  # 15% cancel rate
            "surge_multiplier": surge_multiplier,
            "fare_usd": round((distance_km * 1.5 + duration_min * 0.5) * surge_multiplier, 2)
        })
    df = pd.DataFrame(trips)
    # Validation: All FKs valid
    assert df['driver_id'].isin(driver_pool).all(), "Trip driver FK invalid!"
    assert df['rider_id'].isin(rider_pool).all(), "Trip rider FK invalid!"
    assert df['pickup_zone_id'].isin(zone_ids).all(), "Trip pickup zone FK invalid!"
    assert df['dropoff_zone_id'].isin(zone_ids).all(), "Trip dropoff zone FK invalid!"
    assert df['trip_id'].nunique() == len(df), "Trip ID collision!"
    # Stat check: Realistic aggregates
    assert 8 < df['distance_km'].mean() < 20, "Avg distance unrealistic!"
    assert 0.1 < df['status'].value_counts(normalize=True)['cancelled'] < 0.2, "Cancel rate off!"
    return df

if __name__ == "__main__":
    df = generate_historical_trips()
    df.to_parquet("../../data_samples/historical_trips.parquet", compression="snappy")
    print(f"Generated {len(df)} historical trips with valid FKs → data_samples/")