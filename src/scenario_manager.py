"""
Preset Traffic Scenario Manager
===============================
Provides realistic, domain-grounded traffic scenarios representing typical
urban intersection conditions (normal traffic, rush hours, late night, and unilateral gridlock).
"""

from typing import Dict, Any, List


PRESET_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "Normal Traffic": {
        "name": "Normal Traffic",
        "badge": "Balanced Flow",
        "description": "Midday baseline with balanced vehicle arrival rates across all four approaches.",
        "hour_of_day": 14,
        "day_of_week": 2,  # Wednesday
        "avg_speed": 40.0,
        "condition": "Medium",
        "vehicle_counts": {"North": 24, "South": 22, "East": 20, "West": 18},
        "traffic_density": {"North": 42.0, "South": 38.0, "East": 35.0, "West": 32.0},
        "queue_length": {"North": 85.0, "South": 75.0, "East": 68.0, "West": 62.0},
        "prev_waiting_time": {"North": 24.0, "South": 22.0, "East": 20.0, "West": 18.0}
    },
    "Morning Rush Hour": {
        "name": "Morning Rush Hour",
        "badge": "N-S Arterial Inflow",
        "description": "Heavy commuter inbound flow from suburban corridors into downtown (North & South choked).",
        "hour_of_day": 8,
        "day_of_week": 1,  # Tuesday
        "avg_speed": 22.0,
        "condition": "High",
        "vehicle_counts": {"North": 68, "South": 60, "East": 16, "West": 14},
        "traffic_density": {"North": 92.0, "South": 85.0, "East": 28.0, "West": 25.0},
        "queue_length": {"North": 240.0, "South": 210.0, "East": 55.0, "West": 48.0},
        "prev_waiting_time": {"North": 65.0, "South": 58.0, "East": 18.0, "West": 15.0}
    },
    "Evening Rush Hour": {
        "name": "Evening Rush Hour",
        "badge": "E-W Arterial Outflow",
        "description": "Outbound evening exodus towards eastern and western residential districts.",
        "hour_of_day": 18,
        "day_of_week": 4,  # Friday
        "avg_speed": 24.0,
        "condition": "High",
        "vehicle_counts": {"North": 18, "South": 15, "East": 72, "West": 65},
        "traffic_density": {"North": 32.0, "South": 28.0, "East": 96.0, "West": 88.0},
        "queue_length": {"North": 60.0, "South": 52.0, "East": 260.0, "West": 235.0},
        "prev_waiting_time": {"North": 18.0, "South": 16.0, "East": 70.0, "West": 62.0}
    },
    "Low Traffic": {
        "name": "Low Traffic",
        "badge": "Night Off-Peak",
        "description": "Late night quiet streets with sparse vehicular arrivals; ideal for energy-conserving fast cycles.",
        "hour_of_day": 2,
        "day_of_week": 6,  # Sunday
        "avg_speed": 48.0,
        "condition": "Low",
        "vehicle_counts": {"North": 6, "South": 5, "East": 7, "West": 4},
        "traffic_density": {"North": 12.0, "South": 10.0, "East": 14.0, "West": 8.0},
        "queue_length": {"North": 20.0, "South": 18.0, "East": 24.0, "West": 15.0},
        "prev_waiting_time": {"North": 10.0, "South": 8.0, "East": 11.0, "West": 7.0}
    },
    "Heavy North Traffic": {
        "name": "Heavy North Traffic",
        "badge": "North Bottleneck",
        "description": "Major bottleneck or upstream construction on North approach creating severe localized queue spillback.",
        "hour_of_day": 12,
        "day_of_week": 3,  # Thursday
        "avg_speed": 18.0,
        "condition": "High",
        "vehicle_counts": {"North": 88, "South": 20, "East": 18, "West": 16},
        "traffic_density": {"North": 118.0, "South": 34.0, "East": 30.0, "West": 28.0},
        "queue_length": {"North": 320.0, "South": 70.0, "East": 62.0, "West": 55.0},
        "prev_waiting_time": {"North": 95.0, "South": 22.0, "East": 19.0, "West": 17.0}
    },
    "Heavy East Traffic": {
        "name": "Heavy East Traffic",
        "badge": "East Bottleneck",
        "description": "Localized surge along East corridor with heavy queues while perpendicular flow remains light.",
        "hour_of_day": 15,
        "day_of_week": 3,  # Thursday
        "avg_speed": 19.0,
        "condition": "High",
        "vehicle_counts": {"North": 18, "South": 16, "East": 86, "West": 22},
        "traffic_density": {"North": 30.0, "South": 28.0, "East": 115.0, "West": 38.0},
        "queue_length": {"North": 58.0, "South": 52.0, "East": 310.0, "West": 72.0},
        "prev_waiting_time": {"North": 18.0, "South": 16.0, "East": 92.0, "West": 22.0}
    },
    "Emergency Congestion": {
        "name": "Emergency Congestion",
        "badge": "Sudden Spike",
        "description": "Sudden surge along West boulevard due to regional detour routing, demanding rapid adaptive reallocation.",
        "hour_of_day": 16,
        "day_of_week": 2,  # Tuesday
        "avg_speed": 20.0,
        "condition": "High",
        "vehicle_counts": {"North": 25, "South": 22, "East": 19, "West": 82},
        "traffic_density": {"North": 44.0, "South": 38.0, "East": 32.0, "West": 112.0},
        "queue_length": {"North": 88.0, "South": 76.0, "East": 65.0, "West": 295.0},
        "prev_waiting_time": {"North": 25.0, "South": 22.0, "East": 19.0, "West": 88.0}
    }
}


def get_scenario_names() -> List[str]:
    """Return list of available preset scenario keys."""
    return list(PRESET_SCENARIOS.keys())


def get_scenario(name: str) -> Dict[str, Any]:
    """Retrieve full configuration for a scenario name."""
    return PRESET_SCENARIOS.get(name, PRESET_SCENARIOS["Normal Traffic"])
