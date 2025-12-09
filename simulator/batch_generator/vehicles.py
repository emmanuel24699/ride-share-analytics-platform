import pandas as pd
import random
from faker import Faker

fake = Faker()

def generate_vehicles(n_vehicles=8000, seed=42):  # More vehicles than drivers for pool
    random.seed(seed)
    types = ["sedan", "suv", "hatchback", "electric"]
    years = list(range(2015, 2026))
    vehicles = []
    for i in range(n_vehicles):
        vehicle_id = f"V{str(i+1).zfill(6)}"
        vehicles.append({
            "vehicle_id": vehicle_id,
            "type": random.choice(types),
            "year": random.choice(years),
            "license_plate": fake.license_plate(),
            "current_driver_id": None,  # Assigned later via batch changelog
            "status": "active" if random.random() < 0.95 else "maintenance"
        })
    df = pd.DataFrame(vehicles)
    # Validation: Unique IDs
    assert df['vehicle_id'].nunique() == len(df), "Vehicle ID collision!"
    return df, list(df['vehicle_id'])  # Return pool for drivers

if __name__ == "__main__":
    df, pool = generate_vehicles()
    df.to_parquet("../../data_samples/vehicles.parquet", compression="snappy")
    print(f"Generated {len(df)} vehicles (pool size {len(pool)}) → data_samples/")