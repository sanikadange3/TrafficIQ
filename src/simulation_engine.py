"""
Traffic Queuing & Performance Simulation Engine
===============================================
Computes realistic traffic engineering performance metrics comparing
Fixed-Time vs Adaptive ML Signal Timing strategies using Webster's
delay formulation and Highway Capacity Manual (HCM) queuing dynamics.

Formulas & Principles:
----------------------
1. Approach Capacity (veh/cycle):
   c_i = s * (g_i / C) * C = s * g_i
   where:
     s = saturation flow rate (e.g., 0.65 veh/second per approach)
     g_i = effective green duration (seconds)

2. Volume-to-Capacity Ratio (Degree of Saturation, x_i):
   x_i = V_i / max(c_i, 1.0)
   where V_i is the arrival volume per cycle.

3. Webster's Average Delay Formula per Vehicle (seconds/veh):
   d_i = [ C * (1 - lambda_i)^2 ] / [ 2 * (1 - min(lambda_i * x_i, 0.95)) ] + [ x_i^2 ] / [ 2 * max(q_i, 0.05) * (1 - min(x_i, 0.95)) ]
   where:
     lambda_i = g_i / C (green ratio)
     q_i = arrival rate (veh/sec)

4. Residual Queue (vehicles remaining unserved):
   Q_rem_i = max(0, V_i - c_i)
   Queue length (meters) = (V_i * 0.5 + Q_rem_i * 0.5) * 6.5m space headway

5. Fuel Consumption & Emissions:
   Idling fuel rate = 0.00035 L/sec per stopped vehicle
   CO2 emission rate = 2.31 kg CO2 per liter of fuel
"""

from typing import Dict, Any, List
import numpy as np


class TrafficSimulationEngine:
    """
    Simulates intersection queuing dynamics and evaluates performance
    deltas between Fixed-Time and Adaptive ML strategies.
    """

    def __init__(
        self,
        saturation_flow_rate: float = 0.65,  # veh/sec discharge rate during green
        veh_length_headway: float = 6.5     # meters per vehicle in queue
    ):
        self.sat_rate = saturation_flow_rate
        self.veh_headway = veh_length_headway
        self.roads = ["North", "South", "East", "West"]

    def evaluate_approach_performance(
        self,
        road: str,
        vehicle_count: int,
        green_time: int,
        cycle_time: int
    ) -> Dict[str, Any]:
        """
        Evaluate queue dissipation, delay, and capacity for a single approach.
        """
        # Capacity provided this cycle
        capacity = float(self.sat_rate * green_time)

        # Vehicles served vs residual queue
        served = min(float(vehicle_count), capacity)
        residual_queue = max(0.0, float(vehicle_count) - capacity)

        # Green ratio
        green_ratio = green_time / max(1, cycle_time)

        # Arrival rate
        q_rate = vehicle_count / max(1.0, float(cycle_time))  # veh/s

        # Degree of saturation
        deg_of_sat = min(1.3, vehicle_count / max(1.0, capacity))

        # Webster's delay model
        term1_num = cycle_time * ((1.0 - green_ratio) ** 2)
        term1_den = 2.0 * (1.0 - min(0.95, green_ratio * deg_of_sat))
        d1 = term1_num / max(0.05, term1_den)

        # Random delay / overflow term
        overflow_factor = max(0.0, deg_of_sat - 0.7)
        d2 = (overflow_factor ** 2) * 18.0 + (residual_queue / max(0.1, self.sat_rate)) * 0.4

        avg_delay = float(np.clip(d1 + d2, 4.0, 180.0))
        total_delay_seconds = float(avg_delay * vehicle_count)

        queue_length_meters = float(round(vehicle_count * self.veh_headway, 1))

        # Fuel and emissions from idling during delay
        idle_fuel_liters = float(total_delay_seconds * 0.00035)
        co2_emissions_kg = float(idle_fuel_liters * 2.31)

        return {
            "road": road,
            "vehicle_count": vehicle_count,
            "green_time": green_time,
            "green_ratio": round(green_ratio, 3),
            "capacity": round(capacity, 1),
            "vehicles_served": round(served, 1),
            "residual_queue": round(residual_queue, 1),
            "degree_of_saturation": round(deg_of_sat, 2),
            "avg_delay_seconds": round(avg_delay, 1),
            "total_delay_seconds": round(total_delay_seconds, 1),
            "queue_length_meters": queue_length_meters,
            "idle_fuel_liters": round(idle_fuel_liters, 3),
            "co2_emissions_kg": round(co2_emissions_kg, 3)
        }

    def evaluate_intersection(
        self,
        vehicle_counts: Dict[str, int],
        timings: Dict[str, int],
        cycle_time: int
    ) -> Dict[str, Any]:
        """
        Evaluate all 4 approaches for a given timing schedule.
        """
        approach_results = {}
        total_vehicles = sum(vehicle_counts.values())
        total_served = 0.0
        total_delay_sec = 0.0
        total_fuel = 0.0
        total_co2 = 0.0
        total_residual_queue = 0.0

        for road in self.roads:
            v = vehicle_counts.get(road, 20)
            g = timings.get(road, 25)
            res = self.evaluate_approach_performance(road, v, g, cycle_time)
            approach_results[road] = res
            total_served += res["vehicles_served"]
            total_delay_sec += res["total_delay_seconds"]
            total_fuel += res["idle_fuel_liters"]
            total_co2 += res["co2_emissions_kg"]
            total_residual_queue += res["residual_queue"]

        avg_intersection_delay = total_delay_sec / max(1, total_vehicles)

        return {
            "approaches": approach_results,
            "total_vehicles": total_vehicles,
            "total_served": round(total_served, 1),
            "total_residual_queue": round(total_residual_queue, 1),
            "total_delay_seconds": round(total_delay_sec, 1),
            "total_delay_hours": round(total_delay_sec / 3600.0, 3),
            "avg_intersection_delay": round(avg_intersection_delay, 1),
            "total_fuel_liters": round(total_fuel, 3),
            "total_co2_kg": round(total_co2, 3),
            "cycle_throughput_rate": round((total_served / max(1, total_vehicles)) * 100.0, 1)
        }

    def compare_strategies(
        self,
        vehicle_counts: Dict[str, int],
        fixed_timings: Dict[str, int],
        adaptive_timings: Dict[str, int],
        cycle_time: int
    ) -> Dict[str, Any]:
        """
        Produce comprehensive side-by-side benchmark comparing Fixed-Time vs Adaptive ML.
        """
        fixed_perf = self.evaluate_intersection(vehicle_counts, fixed_timings, cycle_time)
        adaptive_perf = self.evaluate_intersection(vehicle_counts, adaptive_timings, cycle_time)

        # Delta improvements
        delay_diff = fixed_perf["avg_intersection_delay"] - adaptive_perf["avg_intersection_delay"]
        delay_improvement_pct = (
            (delay_diff / max(0.1, fixed_perf["avg_intersection_delay"])) * 100.0
            if fixed_perf["avg_intersection_delay"] > 0 else 0.0
        )

        fuel_saved = max(0.0, fixed_perf["total_fuel_liters"] - adaptive_perf["total_fuel_liters"])
        co2_saved = max(0.0, fixed_perf["total_co2_kg"] - adaptive_perf["total_co2_kg"])

        queue_diff = fixed_perf["total_residual_queue"] - adaptive_perf["total_residual_queue"]
        queue_reduction_pct = (
            (queue_diff / max(0.1, fixed_perf["total_residual_queue"])) * 100.0
            if fixed_perf["total_residual_queue"] > 0 else 0.0
        )

        return {
            "fixed": fixed_perf,
            "adaptive": adaptive_perf,
            "improvements": {
                "delay_saved_seconds": round(delay_diff, 1),
                "delay_reduction_pct": round(delay_improvement_pct, 1),
                "fuel_saved_liters": round(fuel_saved, 3),
                "co2_saved_kg": round(co2_saved, 3),
                "residual_queue_reduced": round(queue_diff, 1),
                "queue_reduction_pct": round(queue_reduction_pct, 1)
            }
        }
