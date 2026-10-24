"""
Traffic Signal Timing Optimization Engine
==========================================
Implements Webster-based proportional traffic signal timing optimization
for an isolated 4-way urban intersection (North, South, East, West).

Mathematical Formulation:
-------------------------
1. Signal Cycle Budget:
   C = Total Cycle Time (e.g., 60s - 180s, default 120s)
   N = Number of distinct signal phases = 4 (North, East, South, West)
   y = Yellow clearance interval per phase (default: 3s)
   r_all = All-red safety interval per phase (default: 1s)
   Total Lost Time per cycle:
       L = N * (y + r_all) = 4 * (3 + 1) = 16 seconds
   Available Effective Green Budget:
       G_budget = max(4 * min_green_safe, C - L)

2. Constraint Validation:
   - If min_green >= max_green: auto-adjust max_green to maintain safe margin.
   - If 4 * min_green > G_budget: auto-clamp min_green to avoid cycle overruns.
   - Zero traffic demand is safely floor-clamped to prevent zero-division.

3. Proportional Demand Allocation (Webster's Criterion):
   Let D_i be the predicted traffic demand (PCU/hr) for approach i in {North, South, East, West}.
   Demand Ratio:
       w_i = D_i / sum(D_j)
   Raw Green Time:
       g_raw_i = w_i * G_budget

4. Constrained Bounded Optimization:
   g_min <= g_i <= g_max
   Subject to: sum(g_i) = G_budget

   We solve this via bounded iterative projection:
   - Clamp values to [effective_min_green, effective_max_green]
   - Redistribute residual surplus/deficit proportionally across unconstrained approaches
   - Ensure strictly integer seconds with zero negative timings and exact cycle closure.

5. Baseline Fixed-Time Strategy:
   g_fixed_i = G_budget / 4 for all approaches, irrespective of actual traffic volume.
"""

from typing import Dict, Any, List, Tuple
import numpy as np


class SignalTimingOptimizer:
    """
    Optimizes green-light durations across 4 intersection approaches
    based on ML-predicted traffic demands and physical safety constraints.
    """

    def __init__(
        self,
        cycle_time: int = 120,
        min_green: int = 10,
        max_green: int = 60,
        yellow_time: int = 3,
        all_red_time: int = 1
    ):
        self.cycle_time = int(cycle_time)
        self.min_green = int(min_green)
        self.max_green = int(max_green)
        self.yellow_time = int(yellow_time)
        self.all_red_time = int(all_red_time)
        self.roads = ["North", "South", "East", "West"]
        self.warnings: List[str] = []

    def set_parameters(
        self,
        cycle_time: int = None,
        min_green: int = None,
        max_green: int = None,
        yellow_time: int = None,
        all_red_time: int = None
    ):
        """Update optimizer configuration parameters with input validation."""
        self.warnings.clear()

        if cycle_time is not None:
            self.cycle_time = max(40, int(cycle_time))
        if yellow_time is not None:
            self.yellow_time = max(1, int(yellow_time))
        if all_red_time is not None:
            self.all_red_time = max(0, int(all_red_time))

        raw_min = int(min_green) if min_green is not None else self.min_green
        raw_max = int(max_green) if max_green is not None else self.max_green

        # Validation: min_green vs max_green
        if raw_min >= raw_max:
            self.warnings.append(
                f"Configured Minimum Green ({raw_min}s) exceeds or equals Maximum Green ({raw_max}s). "
                f"Maximum green adjusted to {raw_min + 5}s for safety."
            )
            raw_max = raw_min + 5

        self.min_green = max(5, raw_min)
        self.max_green = max(self.min_green + 5, raw_max)

    def calculate_cycle_budget(self) -> Dict[str, Any]:
        """
        Calculate total lost time and usable green budget, ensuring physical feasibility.
        """
        num_phases = len(self.roads)
        lost_time_per_phase = self.yellow_time + self.all_red_time
        total_lost_time = num_phases * lost_time_per_phase

        raw_budget = self.cycle_time - total_lost_time

        # Validate budget vs min_green
        effective_min = self.min_green
        effective_max = self.max_green

        if raw_budget < num_phases * 5:
            # Emergency minimum floor
            effective_green_budget = num_phases * 5
            effective_min = 5
            self.warnings.append(
                f"Cycle time ({self.cycle_time}s) is too short for clearance lost time ({total_lost_time}s). "
                f"Enforcing minimum feasible green budget of {effective_green_budget}s."
            )
        elif raw_budget < num_phases * self.min_green:
            effective_min = max(5, raw_budget // num_phases)
            effective_green_budget = raw_budget
            self.warnings.append(
                f"Configured Min Green ({self.min_green}s × 4 = {self.min_green * 4}s) exceeds usable green budget ({raw_budget}s). "
                f"Auto-scaled Min Green to {effective_min}s to preserve cycle budget."
            )
        else:
            effective_green_budget = raw_budget

        effective_max = max(effective_min + 5, min(effective_max, effective_green_budget - (num_phases - 1) * effective_min))

        return {
            "cycle_time": self.cycle_time,
            "num_phases": num_phases,
            "yellow_per_phase": self.yellow_time,
            "all_red_per_phase": self.all_red_time,
            "lost_time_per_phase": lost_time_per_phase,
            "total_lost_time": total_lost_time,
            "effective_green_budget": effective_green_budget,
            "effective_min_green": effective_min,
            "effective_max_green": effective_max,
            "warnings": list(self.warnings)
        }

    def optimize_green_timings(
        self,
        predicted_demands: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Compute optimal green-light durations for each approach using proportional demand allocation
        with bounded constraint satisfaction. Handles zero traffic and extreme imbalances safely.

        Parameters:
        -----------
        predicted_demands : dict
            Approach names -> predicted traffic demand (PCU/hr)

        Returns:
        --------
        dict containing:
            - 'adaptive_timings': dict of road -> green seconds
            - 'fixed_timings': dict of road -> green seconds
            - 'demand_ratios': dict of road -> float
            - 'budget': dict of cycle parameters
            - 'yellow_time': int
            - 'all_red_time': int
            - 'warnings': list of warning messages
        """
        budget = self.calculate_cycle_budget()
        G_budget = budget["effective_green_budget"]
        min_g = budget["effective_min_green"]
        max_g = budget["effective_max_green"]

        # Ensure all roads present with valid positive demand floor
        # Minimum baseline demand floor of 50 PCU/hr prevents zero division
        demands = {r: max(50.0, float(predicted_demands.get(r, 100.0))) for r in self.roads}
        total_demand = sum(demands.values())

        demand_ratios = {r: demands[r] / total_demand for r in self.roads}

        # Step 1: Initial proportional allocation
        allocated = {r: demand_ratios[r] * G_budget for r in self.roads}

        # Step 2: Iterative bounded projection to satisfy [min_g, max_g]
        # and sum(allocated) == G_budget
        for _ in range(12):
            clamped = {}
            unconstrained = []
            fixed_sum = 0.0

            for r, g in allocated.items():
                if g <= min_g:
                    clamped[r] = float(min_g)
                    fixed_sum += min_g
                elif g >= max_g:
                    clamped[r] = float(max_g)
                    fixed_sum += max_g
                else:
                    unconstrained.append(r)

            if not unconstrained:
                allocated = clamped
                break

            remaining_budget = max(0.0, G_budget - fixed_sum)
            unconstrained_demand_sum = sum(demands[r] for r in unconstrained)

            if unconstrained_demand_sum > 0:
                for r in unconstrained:
                    clamped[r] = (demands[r] / unconstrained_demand_sum) * remaining_budget
            else:
                for r in unconstrained:
                    clamped[r] = remaining_budget / len(unconstrained)

            allocated = clamped

        # Step 3: Integer rounding while strictly preserving sum == G_budget
        int_timings = {r: int(np.floor(allocated[r])) for r in self.roads}
        remainder = int(G_budget - sum(int_timings.values()))

        # Distribute leftover seconds to roads with highest decimal fractions
        fractional_parts = sorted(
            [(r, allocated[r] - int_timings[r]) for r in self.roads],
            key=lambda x: x[1],
            reverse=True
        )

        for i in range(remainder):
            target_road = fractional_parts[i % len(fractional_parts)][0]
            int_timings[target_road] += 1

        # Final safety bounds check
        for r in self.roads:
            int_timings[r] = max(min_g, min(max_g, int_timings[r]))

        # Exact budget closure adjustment
        diff = G_budget - sum(int_timings.values())
        if diff != 0:
            # Adjust the highest demand road
            highest_road = max(demands, key=demands.get)
            int_timings[highest_road] = max(min_g, int_timings[highest_road] + diff)

        # Baseline Fixed-Time Strategy:
        # Equal split of available green budget across all 4 phases
        base_fixed_green = int(G_budget // len(self.roads))
        fixed_remainder = int(G_budget - (base_fixed_green * len(self.roads)))
        fixed_timings = {r: base_fixed_green for r in self.roads}
        for i in range(fixed_remainder):
            fixed_timings[self.roads[i]] += 1

        return {
            "adaptive_timings": int_timings,
            "fixed_timings": fixed_timings,
            "demand_ratios": {r: round(demand_ratios[r], 4) for r in self.roads},
            "budget": budget,
            "yellow_time": self.yellow_time,
            "all_red_time": self.all_red_time,
            "warnings": budget["warnings"]
        }
