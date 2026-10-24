"""
Plotly Data Visualization Module - Professional Light Theme
============================================================
Generates clean, publication-quality Plotly charts for traffic analysis,
signal allocations, queuing delays, scenario comparison, and history tracking.

Design System (Smart-City Light Theme):
- Main Card / Plot Background: #FFFFFF
- Primary Color: #2563EB
- Secondary Color: #0F766E
- Success / Adaptive: #16A34A
- Warning / Queue: #F59E0B
- Error / Stopped: #DC2626
- Secondary Chart Accent: #8B5CF6
- Neutral / Fixed Baseline: #94A3B8
- Titles: #172033
- Body / Axis Text: #475569
- Gridlines: #E2E8F0
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Theme Color Tokens
THEME_FONT = "Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, sans-serif"
BG_COLOR = "#FFFFFF"
PAPER_COLOR = "#FFFFFF"
GRID_COLOR = "#E2E8F0"
TEXT_TITLE = "#172033"
TEXT_LABEL = "#475569"

COLOR_NORTH = "#2563EB"   # Primary blue
COLOR_EAST = "#8B5CF6"    # Purple
COLOR_SOUTH = "#0F766E"   # Teal
COLOR_WEST = "#16A34A"    # Green
COLOR_FIXED = "#94A3B8"   # Slate gray baseline
COLOR_DELAY = "#DC2626"   # Red
COLOR_WARN = "#F59E0B"    # Amber

ROAD_COLORS = {
    "North": COLOR_NORTH,
    "East": COLOR_EAST,
    "South": COLOR_SOUTH,
    "West": COLOR_WEST
}


def apply_light_theme(fig: go.Figure, title: str, height: int = 360) -> go.Figure:
    """Apply uniform smart-city light theme layout to a Plotly figure."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "y": 0.94,
            "x": 0.02,
            "xanchor": "left",
            "yanchor": "top",
            "font": {"size": 13.5, "color": TEXT_TITLE, "family": THEME_FONT}
        },
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        height=height,
        margin={"l": 45, "r": 25, "t": 55, "b": 40},
        font={"family": THEME_FONT, "color": TEXT_LABEL},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 11, "color": TEXT_LABEL}
        },
        hoverlabel={
            "bgcolor": "#1E293B",
            "bordercolor": "#2563EB",
            "font": {"family": THEME_FONT, "size": 12, "color": "#FFFFFF"}
        }
    )
    fig.update_xaxes(
        gridcolor=GRID_COLOR,
        showline=True,
        linecolor="#CBD5E1",
        tickfont={"size": 11, "color": TEXT_LABEL},
        title_font={"size": 11.5, "color": TEXT_TITLE}
    )
    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        showline=True,
        linecolor="#CBD5E1",
        tickfont={"size": 11, "color": TEXT_LABEL},
        title_font={"size": 11.5, "color": TEXT_TITLE}
    )
    return fig


def plot_traffic_demand(predicted_demands: Dict[str, float]) -> go.Figure:
    """
    Chart 1: Traffic demand by road (Predicted PCU/hr).
    """
    roads = ["North", "South", "East", "West"]
    demands = [round(predicted_demands.get(r, 0.0), 1) for r in roads]
    colors = [ROAD_COLORS.get(r, COLOR_NORTH) for r in roads]

    fig = go.Figure(
        data=[
            go.Bar(
                x=roads,
                y=demands,
                marker=dict(
                    color=colors,
                    line=dict(color="#CBD5E1", width=1)
                ),
                text=[f"<b>{d:,.0f}</b>" for d in demands],
                textposition="outside",
                hoverinfo="x+y"
            )
        ]
    )
    fig.update_layout(
        yaxis_title="Traffic Demand (PCU/hr)",
        xaxis_title="Approach Road"
    )
    return apply_light_theme(fig, "ML-Predicted Traffic Demand by Approach")


def plot_green_timings(adaptive_timings: Dict[str, int], fixed_timings: Dict[str, int]) -> go.Figure:
    """
    Chart 2: Adaptive versus fixed-time green-light allocation.
    """
    roads = ["North", "South", "East", "West"]
    adapt_vals = [adaptive_timings.get(r, 25) for r in roads]
    fixed_vals = [fixed_timings.get(r, 25) for r in roads]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Adaptive ML Green",
                x=roads,
                y=adapt_vals,
                marker=dict(color=COLOR_WEST, line=dict(color="#CBD5E1", width=1)),
                text=[f"<b>{v}s</b>" for v in adapt_vals],
                textposition="inside",
                insidetextfont=dict(color="#FFFFFF", size=11)
            ),
            go.Bar(
                name="Fixed-Time Baseline",
                x=roads,
                y=fixed_vals,
                marker=dict(color=COLOR_FIXED, line=dict(color="#CBD5E1", width=1)),
                text=[f"{v}s" for v in fixed_vals],
                textposition="inside",
                insidetextfont=dict(color="#FFFFFF", size=11)
            )
        ]
    )
    fig.update_layout(
        barmode="group",
        yaxis_title="Green Duration (seconds)",
        xaxis_title="Approach Road"
    )
    return apply_light_theme(fig, "Green-Light Allocation: Adaptive ML vs Fixed Baseline")


def plot_waiting_time_comparison(comparison_data: Dict[str, Any]) -> go.Figure:
    """
    Chart 3: Estimated waiting time by road (Fixed vs Adaptive per approach).
    """
    roads = ["North", "South", "East", "West"]
    fixed_delays = [comparison_data["fixed"]["approaches"][r]["avg_delay_seconds"] for r in roads]
    adapt_delays = [comparison_data["adaptive"]["approaches"][r]["avg_delay_seconds"] for r in roads]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Fixed-Time Delay",
                x=roads,
                y=fixed_delays,
                marker=dict(color=COLOR_DELAY, line=dict(color="#CBD5E1", width=1)),
                text=[f"{d:.1f}s" for d in fixed_delays],
                textposition="outside"
            ),
            go.Bar(
                name="Adaptive ML Delay",
                x=roads,
                y=adapt_delays,
                marker=dict(color=COLOR_NORTH, line=dict(color="#CBD5E1", width=1)),
                text=[f"{d:.1f}s" for d in adapt_delays],
                textposition="outside"
            )
        ]
    )
    fig.update_layout(
        barmode="group",
        yaxis_title="Average Delay (seconds/veh)",
        xaxis_title="Approach Road"
    )
    return apply_light_theme(fig, "Estimated Vehicle Waiting Time by Approach")


def plot_queue_length_comparison(comparison_data: Dict[str, Any]) -> go.Figure:
    """
    Chart 4: Queue length comparison (Residual Queue & Queue Length in meters).
    """
    roads = ["North", "South", "East", "West"]
    fixed_res = [comparison_data["fixed"]["approaches"][r]["residual_queue"] for r in roads]
    adapt_res = [comparison_data["adaptive"]["approaches"][r]["residual_queue"] for r in roads]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Fixed Residual Queue",
                x=roads,
                y=fixed_res,
                marker=dict(color=COLOR_WARN, line=dict(color="#CBD5E1", width=1)),
                text=[f"{q:.1f} veh" for q in fixed_res],
                textposition="outside"
            ),
            go.Bar(
                name="Adaptive Residual Queue",
                x=roads,
                y=adapt_res,
                marker=dict(color=COLOR_SOUTH, line=dict(color="#CBD5E1", width=1)),
                text=[f"{q:.1f} veh" for q in adapt_res],
                textposition="outside"
            )
        ]
    )
    fig.update_layout(
        barmode="group",
        yaxis_title="Unserved Residual Queue (vehicles)",
        xaxis_title="Approach Road"
    )
    return apply_light_theme(fig, "Unserved Residual Queue: Fixed vs Adaptive")


def plot_traffic_demand_over_time(current_hour: int, current_demands: Dict[str, float]) -> go.Figure:
    """
    Chart 5: Traffic demand over time (24-hour diurnal flow profile with active observation marker).
    """
    hours = list(range(24))

    def diurnal_multiplier(h):
        if 7 <= h <= 9:
            return 2.4  # Morning rush
        elif 16 <= h <= 19:
            return 2.5  # Evening rush
        elif 11 <= h <= 15:
            return 1.4  # Midday
        elif 0 <= h <= 5:
            return 0.35 # Night
        else:
            return 1.0  # Shoulder

    mean_cur = sum(current_demands.values()) / 4.0
    ref_base = mean_cur / max(0.5, diurnal_multiplier(current_hour))

    hourly_n_s = [ref_base * diurnal_multiplier(h) * (1.15 if 7 <= h <= 9 else 0.9) for h in hours]
    hourly_e_w = [ref_base * diurnal_multiplier(h) * (1.2 if 16 <= h <= 19 else 0.85) for h in hours]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=hourly_n_s,
            mode="lines+markers",
            name="North-South Arterial Flow",
            line=dict(color=COLOR_NORTH, width=2.5),
            marker=dict(size=4)
        )
    )

    fig.add_trace(
        go.Scatter(
            x=hours,
            y=hourly_e_w,
            mode="lines+markers",
            name="East-West Arterial Flow",
            line=dict(color=COLOR_EAST, width=2.5),
            marker=dict(size=4)
        )
    )

    fig.add_vline(
        x=current_hour,
        line_width=2,
        line_dash="dash",
        line_color=COLOR_WARN,
        annotation_text=f"Current: {current_hour}:00",
        annotation_position="top right",
        annotation_font=dict(size=11, color=COLOR_WARN)
    )

    fig.update_layout(
        xaxis=dict(tickmode="linear", tick0=0, dtick=2),
        xaxis_title="Hour of Day (00:00 - 23:00)",
        yaxis_title="Estimated Traffic Demand (PCU/hr)"
    )
    return apply_light_theme(fig, "24-Hour Diurnal Traffic Demand Profile")


def plot_strategy_overall_comparison(comparison_data: Dict[str, Any]) -> go.Figure:
    """
    Chart 6: Before-and-after strategy comparison.
    """
    fixed = comparison_data["fixed"]
    adapt = comparison_data["adaptive"]

    categories = [
        "Avg Delay (s/veh)",
        "Residual Queue (veh)",
        "Throughput Rate (%)",
        "Fuel Waste (x10 L)"
    ]

    fixed_vals = [
        fixed["avg_intersection_delay"],
        fixed["total_residual_queue"],
        fixed["cycle_throughput_rate"],
        fixed["total_fuel_liters"] * 10
    ]

    adapt_vals = [
        adapt["avg_intersection_delay"],
        adapt["total_residual_queue"],
        adapt["cycle_throughput_rate"],
        adapt["total_fuel_liters"] * 10
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Fixed-Time Strategy",
            x=categories,
            y=fixed_vals,
            marker=dict(color=COLOR_DELAY, line=dict(color="#CBD5E1", width=1)),
            text=[f"{v:.1f}" for v in fixed_vals],
            textposition="outside"
        )
    )
    fig.add_trace(
        go.Bar(
            name="Adaptive ML Strategy",
            x=categories,
            y=adapt_vals,
            marker=dict(color=COLOR_WEST, line=dict(color="#CBD5E1", width=1)),
            text=[f"{v:.1f}" for v in adapt_vals],
            textposition="outside"
        )
    )

    fig.update_layout(
        barmode="group",
        yaxis_title="Standardized Performance Value",
        xaxis_title="Operational Indicator"
    )
    return apply_light_theme(fig, "Overall System Performance: Fixed vs Adaptive Strategy")


def plot_multi_scenario_analysis(
    scenario_names: List[str],
    scenario_demands: Dict[str, Dict[str, float]],
    scenario_timings: Dict[str, Dict[str, int]]
) -> go.Figure:
    """
    Chart 7: Scenario comparison across all predefined conditions.
    """
    records = []
    for s_name in scenario_names:
        for road in ["North", "South", "East", "West"]:
            records.append({
                "Scenario": s_name,
                "Road": road,
                "Traffic Demand": round(scenario_demands[s_name][road], 1),
                "Recommended Green": scenario_timings[s_name][road]
            })
    df_scenarios = pd.DataFrame(records)

    fig = px.bar(
        df_scenarios,
        x="Scenario",
        y="Recommended Green",
        color="Road",
        barmode="group",
        color_discrete_map=ROAD_COLORS,
        text="Recommended Green",
        hover_data=["Traffic Demand"]
    )
    fig.update_traces(
        textposition="outside",
        textfont_size=10,
        marker_line_color="#CBD5E1",
        marker_line_width=1
    )
    fig.update_layout(
        yaxis_title="Allocated Green Time (seconds)",
        xaxis_title="Traffic Scenario"
    )
    return apply_light_theme(fig, "Signal Green Allocations Across Preset Scenarios", height=380)


def plot_simulation_history(history_records: List[Dict[str, Any]]) -> go.Figure:
    """
    Chart 8: Live simulation history time-series tracking.
    """
    if not history_records:
        fig = go.Figure()
        fig.add_annotation(text="No simulation history recorded yet. Run simulation to collect data points.", showarrow=False)
        return apply_light_theme(fig, "Simulation Performance History Over Time", height=320)

    df_hist = pd.DataFrame(history_records)
    steps = list(range(1, len(df_hist) + 1))

    fig = go.Figure()

    if "total_vehicles" in df_hist.columns:
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=df_hist["total_vehicles"],
                mode="lines+markers",
                name="Total Vehicles",
                line=dict(color=COLOR_NORTH, width=2),
                marker=dict(size=4)
            )
        )

    if "avg_delay" in df_hist.columns:
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=df_hist["avg_delay"],
                mode="lines+markers",
                name="Avg Delay (s/veh)",
                line=dict(color=COLOR_DELAY, width=2),
                marker=dict(size=4)
            )
        )

    if "residual_queue" in df_hist.columns:
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=df_hist["residual_queue"],
                mode="lines+markers",
                name="Residual Queue (veh)",
                line=dict(color=COLOR_WARN, width=2, dash="dash"),
                marker=dict(size=4)
            )
        )

    fig.update_layout(
        xaxis_title="Observation Step / Update Cycle",
        yaxis_title="Operational Value"
    )
    return apply_light_theme(fig, "Simulation Performance Tracking (Live History)", height=340)


def plot_scenario_comparison_diff(
    scen_a_name: str,
    scen_a_timings: Dict[str, int],
    scen_b_name: str,
    scen_b_timings: Dict[str, int]
) -> go.Figure:
    """
    Chart 9: Direct side-by-side comparison between any two user-selected scenarios.
    """
    roads = ["North", "South", "East", "West"]
    a_vals = [scen_a_timings.get(r, 25) for r in roads]
    b_vals = [scen_b_timings.get(r, 25) for r in roads]

    fig = go.Figure(
        data=[
            go.Bar(
                name=scen_a_name,
                x=roads,
                y=a_vals,
                marker=dict(color=COLOR_NORTH, line=dict(color="#CBD5E1", width=1)),
                text=[f"<b>{v}s</b>" for v in a_vals],
                textposition="outside"
            ),
            go.Bar(
                name=scen_b_name,
                x=roads,
                y=b_vals,
                marker=dict(color=COLOR_EAST, line=dict(color="#CBD5E1", width=1)),
                text=[f"<b>{v}s</b>" for v in b_vals],
                textposition="outside"
            )
        ]
    )
    fig.update_layout(
        barmode="group",
        yaxis_title="Recommended Green (seconds)",
        xaxis_title="Approach Road"
    )
    return apply_light_theme(fig, f"Scenario Comparison: {scen_a_name} vs {scen_b_name}", height=340)


def plot_feature_importances(feature_importances: Dict[str, float]) -> go.Figure:
    """
    Chart 10: Horizontal bar chart showing Random Forest feature importance hierarchy.
    """
    top_items = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:8]
    feats = [item[0].replace("num__", "").replace("cat__road_", "Road: ") for item in top_items]
    scores = [item[1] for item in top_items]

    # Reverse so highest is at top
    feats = feats[::-1]
    scores = scores[::-1]

    fig = go.Figure(
        data=[
            go.Bar(
                x=scores,
                y=feats,
                orientation="h",
                marker=dict(color=COLOR_NORTH, line=dict(color="#CBD5E1", width=1)),
                text=[f"{s*100:.1f}%" for s in scores],
                textposition="outside"
            )
        ]
    )
    fig.update_layout(
        xaxis_title="Gini Feature Importance Relative Weight",
        yaxis_title="Input Feature"
    )
    return apply_light_theme(fig, "Random Forest Feature Importance Breakdown", height=320)
