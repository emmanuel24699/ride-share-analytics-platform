import pandas as pd
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / ".." / ".." / "data_samples"

def load_state():
    required_files = [
        "zones.parquet",
        "vehicles.parquet",
        "riders.parquet",
        "drivers.parquet",
    ]
    missing = [f for f in required_files if not (DATA_DIR / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing data files: {', '.join(missing)}. "
            "Run the batch generator: python simulator/batch_generator/main_batch.py"
        )

    zones_df = pd.read_parquet(DATA_DIR / "zones.parquet")
    vehicles_df = pd.read_parquet(DATA_DIR / "vehicles.parquet")
    riders_df = pd.read_parquet(DATA_DIR / "riders.parquet")
    drivers_df = pd.read_parquet(DATA_DIR / "drivers.parquet")
    # Optional: Load historical for baseline, but not needed for live sim

    # Pools for quick access
    zone_pool = zones_df.to_dict(orient="records")
    vehicle_pool = list(vehicles_df["vehicle_id"])
    rider_pool = list(riders_df["rider_id"])
    driver_pool = list(drivers_df["driver_id"])

    # Driver state: current position (init from home_zone)
    driver_states = {}
    for _, driver in drivers_df.iterrows():
        home_zone = next(z for z in zone_pool if z["zone_id"] == driver["home_zone_id"])
        # Parse polygon str back to list of tuples
        polygon = eval(home_zone["polygon"])  # Safe since we control it
        # Init pos: random point in polygon (simple centroid approx)
        lats, lngs = zip(*polygon)
        init_lat = sum(lats) / len(lats)
        init_lng = sum(lngs) / len(lngs)
        driver_states[driver["driver_id"]] = {
            "status": driver["status"],
            "vehicle_id": driver["current_vehicle_id"],
            "current_lat": init_lat + random.uniform(-0.01, 0.01),  # Small jitter
            "current_lng": init_lng + random.uniform(-0.01, 0.01),
            "h3_index": home_zone["h3_index"]
        }

    return {
        "zones": zone_pool,
        "vehicles": vehicle_pool,
        "riders": rider_pool,
        "drivers": driver_pool,
        "driver_states": driver_states
    }