"""
Traffic Dataset Generator for AI-Based Traffic Signal Timing Optimization
========================================================================
This module generates a realistic synthetic traffic dataset based on standard
traffic flow theory principles (Greenshields speed-density model, Poisson-derived
vehicle arrival patterns, and peak-hour diurnal traffic curves).

Assumptions & Physical Constraints:
1. Four-way urban intersection approaches: North, South, East, West.
2. Diurnal flow patterns:
   - Morning Peak (07:00 - 10:00): Primary North-South commuter inflow.
   - Evening Peak (16:30 - 19:30): Primary East-West commuter outflow.
   - Midday Inter-peak (11:00 - 15:00): Moderate, uniform commercial traffic.
   - Night / Off-peak (22:00 - 05:00): Low background traffic.
3. Greenshields Speed-Density Model:
   - Free-flow speed v_f = 50 km/h.
   - Jam density k_jam = 140 veh/km.
   - Observed speed v = v_f * (1 - k / k_jam).
4. Queue Dynamics:
   - Effective vehicle spacing = 6.5 meters per Passenger Car Unit (PCU).
   - Previous cycle wait time correlated with residual queue and upstream arrival rate.
5. Target Variable (Traffic Demand, veh/hr):
   - Represents the imminent arrival demand rate (PCU/hr) requiring green service time
     in the subsequent observation window.
"""

import os
import numpy as np
import pandas as pd


def generate_traffic_data(num_samples: int = 6000, random_seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic intersection traffic dataset.

    Parameters:
    -----------
    num_samples : int
        Total number of observation rows to generate (default: 6000).
    random_seed : int
        Seed for reproducibility (default: 42).

    Returns:
    --------
    pd.DataFrame
        Synthetic dataset with features and target traffic demand.
    """
    np.random.seed(random_seed)

    roads = ["North", "South", "East", "West"]
    hours = np.random.randint(0, 24, size=num_samples)
    days = np.random.randint(0, 7, size=num_samples)  # 0=Monday, 6=Sunday
    road_choices = np.random.choice(roads, size=num_samples)

    records = []

    for i in range(num_samples):
        hour = hours[i]
        day = days[i]
        road = road_choices[i]
        is_weekend = day >= 5

        # Base diurnal arrival rate multiplier
        if 7 <= hour <= 9:
            # Morning rush
            base_multiplier = 2.4 if road in ["North", "South"] else 1.3
        elif 16 <= hour <= 19:
            # Evening rush
            base_multiplier = 2.6 if road in ["East", "West"] else 1.4
        elif 11 <= hour <= 15:
            # Midday
            base_multiplier = 1.3 if not is_weekend else 1.5
        elif 0 <= hour <= 5:
            # Night off-peak
            base_multiplier = 0.35
        else:
            # Regular shoulder hours
            base_multiplier = 1.0

        if is_weekend:
            # Weekend diurnal shifts (flatter, peak in afternoon)
            base_multiplier = base_multiplier * 0.8 + 0.3

        # Mean vehicle arrival count
        lambda_vehicles = 18 * base_multiplier
        vehicle_count = int(np.clip(np.random.poisson(lam=lambda_vehicles), 3, 95))

        # Density (veh/km) - linked to vehicle count with spatial variation
        # Normal road section: 500m approach segment
        traffic_density = float(np.clip(vehicle_count * 1.8 + np.random.normal(0, 3), 5.0, 135.0))

        # Greenshields speed model: v = v_f * (1 - k / k_jam) + noise
        v_free_flow = 52.0  # km/h
        k_jam = 140.0       # veh/km
        density_ratio = np.clip(traffic_density / k_jam, 0.05, 0.95)
        avg_speed = float(np.clip(v_free_flow * (1.0 - density_ratio) + np.random.normal(0, 2.5), 8.0, 55.0))

        # Queue length in meters (vehicle count in queue * 6.5m space headway)
        queue_vehicles = int(np.clip(vehicle_count * (0.35 + 0.5 * (traffic_density / 100.0)) + np.random.normal(0, 2), 0, vehicle_count))
        queue_length = float(np.clip(queue_vehicles * 6.5 + np.random.normal(0, 2.0), 0.0, 450.0))

        # Previous waiting time (seconds) based on queue depth and service rate
        # Saturated flow rate ~ 1800 veh/hr = 0.5 veh/s per lane
        discharge_rate = 0.45  # veh/s
        prev_waiting_time = float(np.clip((queue_vehicles / max(discharge_rate, 0.1)) + np.random.normal(0, 4.0), 4.0, 160.0))

        # Traffic Demand (Target in PCU/hr)
        # Demand represents upstream flow arriving that must be cleared in subsequent cycle
        # Standard hourly demand = vehicle count scaled to hourly equivalent + arrival trend factor
        hourly_equiv = vehicle_count * 22.0  # each observation represents roughly ~2.5 min sample
        speed_impedance = (55.0 - avg_speed) * 4.5
        queue_pressure = queue_length * 0.9
        noise = np.random.normal(0, 25.0)

        traffic_demand = float(np.clip(
            hourly_equiv + speed_impedance + queue_pressure + noise,
            80.0,
            2400.0
        ))

        records.append({
            "road": road,
            "vehicle_count": vehicle_count,
            "traffic_density": round(traffic_density, 2),
            "queue_length": round(queue_length, 2),
            "avg_speed": round(avg_speed, 2),
            "hour_of_day": int(hour),
            "day_of_week": int(day),
            "is_weekend": int(is_weekend),
            "prev_waiting_time": round(prev_waiting_time, 2),
            "traffic_demand": round(traffic_demand, 2)
        })

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "traffic_dataset.csv")

    print("[*] Generating synthetic traffic dataset with documented physical constraints...")
    traffic_df = generate_traffic_data(num_samples=6000, random_seed=42)
    traffic_df.to_csv(csv_path, index=False)

    print(f"[+] Dataset successfully created: {csv_path}")
    print(f"    - Total Rows: {len(traffic_df)}")
    print(f"    - Features: {list(traffic_df.columns)}")
    print("\nSummary Statistics:")
    print(traffic_df.describe().T[["mean", "std", "min", "50%", "max"]])
