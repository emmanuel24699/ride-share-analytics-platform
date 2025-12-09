import pandas as pd
import random
from pathlib import Path
from zones import generate_zones
from vehicles import generate_vehicles
from riders import generate_riders
from drivers import generate_drivers
from historical_trips import generate_historical_trips

def main(output_date="20251209"):  # Current date format
    print("Generating consistent batch data...")
    output_dir = Path(__file__).resolve().parent / ".." / ".." / "data_samples"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Static
    zones_df, zone_pool = generate_zones()
    vehicles_df, vehicle_pool = generate_vehicles()
    zones_df.to_parquet(output_dir / "zones.parquet", compression="snappy")
    vehicles_df.to_parquet(output_dir / "vehicles.parquet", compression="snappy")
    
    # Step 2: Entities with FKs
    riders_df, rider_pool = generate_riders(zone_pool=zone_pool)
    drivers_df, driver_pool = generate_drivers(vehicle_pool=vehicle_pool, zone_pool=zone_pool)
    riders_df.to_parquet(output_dir / "riders.parquet", compression="snappy")
    drivers_df.to_parquet(output_dir / "drivers.parquet", compression="snappy")
    
    # Step 3: Historical
    trips_df = generate_historical_trips(driver_pool=driver_pool, rider_pool=rider_pool, zone_pool=zone_pool)
    trips_df.to_parquet(output_dir / "historical_trips.parquet", compression="snappy")
    
    # Simulate Changelog (e.g., batch update: reassign 5% vehicles)
    changelog = drivers_df.sample(frac=0.05).copy()
    changelog['current_vehicle_id'] = [random.choice(vehicle_pool) for _ in changelog.index]
    changelog['version'] += 1
    changelog['valid_from'] = pd.Timestamp.now().isoformat()
    changelog_path = output_dir / f"drivers_changelog_{output_date}.parquet"
    changelog.to_parquet(changelog_path, compression="snappy")
    
    # Global Validation: Cross-entity stats
    assigned_drivers = drivers_df['current_vehicle_id'].notna().sum()
    print(f"Success: {assigned_drivers}/{len(drivers_df)} drivers assigned vehicles.")
    trips_per_driver = len(trips_df) / len(driver_pool)
    print(f"Realistic load: ~{trips_per_driver:.1f} historical trips/driver over {24} months.")
    
    print("Batch generation complete! Files in data_samples/")

if __name__ == "__main__":
    main()