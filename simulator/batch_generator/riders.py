import pandas as pd
import random
from faker import Faker
from zones import generate_zones  # Import for zone pool

fake = Faker()

def generate_riders(n_riders=100_000, seed=42, zone_pool=None):
    random.seed(seed)
    if zone_pool is None:
        _, zone_pool = generate_zones()  # Get zone IDs
    zone_ids = [z['zone_id'] for z in zone_pool]  # Wait, fix: actually load or pass
    # Temp: assume zones generated first
    riders = []
    for i in range(n_riders):
        rider_id = f"R{str(i+1).zfill(6)}"
        home_zone = random.choice(zone_ids)
        riders.append({
            "rider_id": rider_id,
            "name": fake.name(),
            "phone": fake.phone_number(),
            "rating": round(random.uniform(4.0, 5.0), 2),  # Beta dist for realism
            "lifetime_trips": random.choices([0, 5, 20, 100, 500], weights=[0.1, 0.2, 0.3, 0.3, 0.1])[0],
            "preferred_payment": random.choice(["card", "cash", "wallet"]),
            "home_zone_id": home_zone  # FK to zones
        })
    df = pd.DataFrame(riders)
    # Validation: All home_zone_id exist
    assert df['home_zone_id'].isin(zone_ids).all(), "Rider zone FK invalid!"
    assert df['rider_id'].nunique() == len(df), "Rider ID collision!"
    return df, list(df['rider_id'])  # Pool for trips

if __name__ == "__main__":
    df, pool = generate_riders()
    df.to_parquet("../../data_samples/riders.parquet", compression="snappy")
    print(f"Generated {len(df)} riders → data_samples/")