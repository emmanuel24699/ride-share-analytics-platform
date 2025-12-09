import h3
import pandas as pd
import random
from faker import Faker

fake = Faker()

def generate_zones(n_zones=500, city_center_lat=40.7128, city_center_lng=-74.0060, resolution=8):  # NYC-like
    random.seed(42)
    zones = []
    for i in range(n_zones):
        # Generate points around NYC center with jitter
        lat = city_center_lat + random.uniform(-0.5, 0.5)
        lng = city_center_lng + random.uniform(-0.5, 0.5)
        zone_id = f"ZONE_{str(i+1).zfill(3)}"
        h3_index = h3.latlng_to_cell(lat, lng, resolution)
        polygon = h3.cell_to_boundary(h3_index)  # List of [lat, lng]
        zones.append({
            "zone_id": zone_id,
            "h3_index": h3_index,
            "name": fake.city() + f" Zone {i+1}",
            "polygon": str(polygon),  # Serialize for storage
            "city": "NYC",
            "density": random.uniform(0.5, 2.0)  # Simulated pop density
        })
    df = pd.DataFrame(zones)
    # Validation: All IDs unique
    assert df['zone_id'].nunique() == len(df), "Zone ID collision!"
    return df, zones  # Return both DataFrame and raw zone pool for reuse

if __name__ == "__main__":
    df, _ = generate_zones()
    df.to_parquet("../../data_samples/zones.parquet", compression="snappy")
    print(f"Generated {len(df)} consistent zones → data_samples/")