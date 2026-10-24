"""
TrafficIQ - AI-Powered Adaptive Traffic Management System
=========================================================
A complete, dynamic Machine Learning and Traffic Signal Optimization Application.
Technologies: Python, Streamlit, Scikit-learn, Plotly, Pandas, NumPy, Joblib
Theme: Professional Smart-City Light Management Dashboard
"""

from datetime import datetime
import io
import os
import sys
import pandas as pd
import streamlit as st
import importlib
import streamlit.components.v1 as st_components

# Ensure local modules are accessible across platforms
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import components.traffic_intersection as _ti_mod
importlib.reload(_ti_mod)
render_traffic_intersection = _ti_mod.render_traffic_intersection
from src.charts import (
    COLOR_NORTH,
    COLOR_EAST,
    COLOR_SOUTH,
    COLOR_WEST,
    apply_light_theme,
    plot_feature_importances,
    plot_green_timings,
    plot_multi_scenario_analysis,
    plot_queue_length_comparison,
    plot_scenario_comparison_diff,
    plot_simulation_history,
    plot_strategy_overall_comparison,
    plot_traffic_demand,
    plot_traffic_demand_over_time,
    plot_waiting_time_comparison,
)
from src.ml_predictor import TrafficDemandPredictor
from src.optimizer import SignalTimingOptimizer
from src.scenario_manager import PRESET_SCENARIOS, get_scenario, get_scenario_names
from src.simulation_engine import TrafficSimulationEngine

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="TrafficIQ | AI Adaptive Traffic Management",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom Light Theme CSS Styling
css_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "style.css")
if os.path.exists(css_file):
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "selected_scenario" not in st.session_state:
    st.session_state.selected_scenario = "Normal Traffic"
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = True
if "cycle_time" not in st.session_state:
    st.session_state.cycle_time = 120
if "min_green" not in st.session_state:
    st.session_state.min_green = 10
if "max_green" not in st.session_state:
    st.session_state.max_green = 60
if "yellow_time" not in st.session_state:
    st.session_state.yellow_time = 3
if "all_red_time" not in st.session_state:
    st.session_state.all_red_time = 1
if "vehicle_counts" not in st.session_state:
    st.session_state.vehicle_counts = {"North": 24, "South": 22, "East": 20, "West": 18}
if "avg_speed" not in st.session_state:
    st.session_state.avg_speed = 38.0
if "hour_of_day" not in st.session_state:
    st.session_state.hour_of_day = 14
if "day_of_week" not in st.session_state:
    st.session_state.day_of_week = 2
if "weather_factor" not in st.session_state:
    st.session_state.weather_factor = 1.0
if "simulation_history" not in st.session_state:
    st.session_state.simulation_history = []

# Synchronize slider widget keys with vehicle counts
for r in ["North", "South", "East", "West"]:
    slider_k = f"slider_veh_{r.lower()}"
    if slider_k not in st.session_state:
        st.session_state[slider_k] = st.session_state.vehicle_counts[r]

# Instantiate Engines (cached for optimal performance)
@st.cache_resource
def get_ml_predictor():
    return TrafficDemandPredictor()

@st.cache_resource
def get_optimizer():
    return SignalTimingOptimizer()

@st.cache_resource
def get_sim_engine():
    return TrafficSimulationEngine()

try:
    predictor = get_ml_predictor()
    model_metrics = predictor.get_metrics()
except Exception as e:
    st.error(f"Error loading ML model: {e}. Please ensure train_model.py has been run.")
    st.stop()

optimizer = get_optimizer()
sim_engine = get_sim_engine()


# -----------------------------------------------------------------------------
# HELPER CALLBACKS FOR INTERACTIVE VEHICLE CONTROLS & STATE MUTATIONS
# -----------------------------------------------------------------------------
def on_slider_change(road_name: str):
    k = f"slider_veh_{road_name.lower()}"
    st.session_state.vehicle_counts[road_name] = int(st.session_state[k])

def adjust_vehicle_count(road_name: str, delta: int):
    k = f"slider_veh_{road_name.lower()}"
    cur = int(st.session_state.vehicle_counts.get(road_name, 20))
    new_val = max(1, min(100, cur + delta))
    st.session_state.vehicle_counts[road_name] = new_val
    st.session_state[k] = new_val

def select_scenario(sc_name: str):
    st.session_state.selected_scenario = sc_name
    sc_data = get_scenario(sc_name)
    st.session_state.vehicle_counts = sc_data["vehicle_counts"].copy()
    for r in ["North", "South", "East", "West"]:
        st.session_state[f"slider_veh_{r.lower()}"] = sc_data["vehicle_counts"][r]
    st.session_state.avg_speed = float(sc_data["avg_speed"])
    st.session_state.hour_of_day = int(sc_data["hour_of_day"])
    st.session_state.day_of_week = int(sc_data["day_of_week"])

def reset_simulation():
    sc_data = get_scenario(st.session_state.selected_scenario)
    st.session_state.vehicle_counts = sc_data["vehicle_counts"].copy()
    for r in ["North", "South", "East", "West"]:
        st.session_state[f"slider_veh_{r.lower()}"] = sc_data["vehicle_counts"][r]
    st.session_state.simulation_history.clear()

def toggle_simulation(running: bool):
    st.session_state.simulation_running = running


# =============================================================================
# SIDEBAR CONTROLS: ORGANIZED IN NEAT COLLAPSIBLE SECTIONS
# =============================================================================
with st.sidebar:
    st.markdown("### 🎛️ Traffic Control Center")

    # -------------------------------------------------------------------------
    # SECTION 1: TRAFFIC SCENARIOS
    # -------------------------------------------------------------------------
    with st.expander("📍 1. Traffic Scenarios", expanded=True):
        scenarios = get_scenario_names()
        sc_col1, sc_col2 = st.columns(2)
        for idx, sc_name in enumerate(scenarios):
            col = sc_col1 if (idx % 2 == 0) else sc_col2
            is_current = (st.session_state.selected_scenario == sc_name)
            btn_label = f"● {sc_name}" if is_current else sc_name
            col.button(
                btn_label,
                key=f"btn_scen_{idx}",
                on_click=select_scenario,
                args=(sc_name,),
                use_container_width=True
            )

        active_sc = get_scenario(st.session_state.selected_scenario)
        st.markdown(
            f"<div style='font-size:11.5px; color:#475569; margin-top:6px; line-height:1.4;'>"
            f"<b>Active:</b> <span style='color:#2563EB; font-weight:700;'>{active_sc['badge']}</span><br>"
            f"{active_sc['description']}</div>",
            unsafe_allow_html=True
        )

    # -------------------------------------------------------------------------
    # SECTION 2: INTERACTIVE VEHICLE CONTROLS
    # -------------------------------------------------------------------------
    with st.expander("🚗 2. Vehicle Controls", expanded=True):
        st.caption("Adjust vehicle volumes. Green lights dynamically reallocate based on predicted demand.")

        def render_vehicle_control_unit(road: str, theme_color: str):
            cur = int(st.session_state.vehicle_counts.get(road, 20))
            c_lbl, c_dec, c_val, c_inc = st.columns([3, 1.2, 2, 1.2])

            with c_lbl:
                st.markdown(f"<span style='color:{theme_color}; font-weight:700;'>{road}</span>", unsafe_allow_html=True)
            with c_dec:
                st.button(
                    "-",
                    key=f"side_dec_{road.lower()}",
                    on_click=adjust_vehicle_count,
                    args=(road, -5),
                    use_container_width=True
                )
            with c_val:
                st.markdown(f"<div style='text-align:center; font-weight:700; color:#172033; font-size:13px; padding-top:4px;'>{cur} veh</div>", unsafe_allow_html=True)
            with c_inc:
                st.button(
                    "+",
                    key=f"side_inc_{road.lower()}",
                    on_click=adjust_vehicle_count,
                    args=(road, 5),
                    use_container_width=True
                )

            st.slider(
                f"{road} Count",
                min_value=1,
                max_value=100,
                step=1,
                key=f"slider_veh_{road.lower()}",
                on_change=on_slider_change,
                args=(road,),
                label_visibility="collapsed"
            )

        render_vehicle_control_unit("North", "#2563EB")
        render_vehicle_control_unit("South", "#0F766E")
        render_vehicle_control_unit("East", "#8B5CF6")
        render_vehicle_control_unit("West", "#16A34A")

    # -------------------------------------------------------------------------
    # SECTION 3: SIGNAL TIMING & CYCLE CONSTRAINTS
    # -------------------------------------------------------------------------
    with st.expander("⏱️ 3. Signal Timing Settings", expanded=False):
        c_time = st.slider(
            "Cycle Duration (seconds)",
            min_value=60,
            max_value=180,
            value=st.session_state.cycle_time,
            step=5,
            help="Total cycle duration allocated across all 4 phases including clearance."
        )
        st.session_state.cycle_time = c_time

        c_col1, c_col2 = st.columns(2)
        min_g = c_col1.slider("Min Green (s)", 5, 25, st.session_state.min_green, step=1)
        max_g = c_col2.slider("Max Green (s)", 20, 90, st.session_state.max_green, step=5)
        st.session_state.min_green = min_g
        st.session_state.max_green = max_g

        c_col3, c_col4 = st.columns(2)
        y_time = c_col3.slider("Yellow (s)", 2, 5, st.session_state.yellow_time, step=1)
        ar_time = c_col4.slider("All-Red (s)", 0, 3, st.session_state.all_red_time, step=1)
        st.session_state.yellow_time = y_time
        st.session_state.all_red_time = ar_time

        if min_g >= max_g:
            st.warning(f"⚠️ Min Green ({min_g}s) ≥ Max Green ({max_g}s). Automatically protected.")

    # -------------------------------------------------------------------------
    # SECTION 4: ENVIRONMENTAL & TEMPORAL CONDITIONS
    # -------------------------------------------------------------------------
    with st.expander("🌐 4. Environmental Conditions", expanded=False):
        speed_in = st.slider(
            "Average Speed (km/h)",
            min_value=10.0,
            max_value=60.0,
            value=float(st.session_state.avg_speed),
            step=1.0
        )
        st.session_state.avg_speed = speed_in

        hour_in = st.slider("Hour of the Day (24h)", 0, 23, int(st.session_state.hour_of_day), step=1)
        st.session_state.hour_of_day = hour_in

        day_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_in = st.selectbox(
            "Day of the Week",
            range(7),
            format_func=lambda x: day_options[x],
            index=st.session_state.day_of_week
        )
        st.session_state.day_of_week = day_in

        weather_choice = st.selectbox(
            "Weather Condition",
            ["Clear / Dry (Factor: 1.0)", "Cloudy / Damp (Factor: 0.95)", "Rainy / Wet (Factor: 0.85)"],
            index=0
        )
        w_factor = 1.0 if "1.0" in weather_choice else (0.95 if "0.95" in weather_choice else 0.85)
        st.session_state.weather_factor = w_factor


# =============================================================================
# DYNAMIC ML INFERENCE & CONSTRAINED OPTIMIZATION CALCULATIONS
# =============================================================================
optimizer.set_parameters(
    cycle_time=st.session_state.cycle_time,
    min_green=st.session_state.min_green,
    max_green=st.session_state.max_green,
    yellow_time=st.session_state.yellow_time,
    all_red_time=st.session_state.all_red_time
)

# 1. Approach feature representation
road_states = {}
for r, count in st.session_state.vehicle_counts.items():
    density = float(count * 1.8)
    queue = float(count * 6.5)
    speed = float(st.session_state.avg_speed * st.session_state.weather_factor)
    wait_est = float(count * 1.2)
    road_states[r] = {
        "vehicle_count": count,
        "traffic_density": density,
        "queue_length": queue,
        "avg_speed": speed,
        "prev_waiting_time": wait_est
    }

# 2. ML Traffic Demand Predictions (PCU/hr)
predicted_demands = predictor.predict_intersection_demands(
    road_states=road_states,
    hour_of_day=st.session_state.hour_of_day,
    day_of_week=st.session_state.day_of_week
)

# 3. Dynamic Constrained Webster Optimization
optimization_result = optimizer.optimize_green_timings(predicted_demands)
adaptive_timings = optimization_result["adaptive_timings"]
fixed_timings = optimization_result["fixed_timings"]
budget_info = optimization_result["budget"]
optimizer_warnings = optimization_result["warnings"]

# 4. Queuing Dynamics & Comparative Delay Modeling
comparison = sim_engine.compare_strategies(
    vehicle_counts=st.session_state.vehicle_counts,
    fixed_timings=fixed_timings,
    adaptive_timings=adaptive_timings,
    cycle_time=st.session_state.cycle_time
)

total_vehicles = sum(st.session_state.vehicle_counts.values())
peak_road = max(predicted_demands, key=predicted_demands.get)
peak_demand = predicted_demands[peak_road]

# Append snapshot to live simulation session history
history_entry = {
    "step": len(st.session_state.simulation_history) + 1,
    "timestamp": datetime.now().strftime("%H:%M:%S"),
    "total_vehicles": total_vehicles,
    "avg_delay": round(comparison['adaptive']['avg_intersection_delay'], 1),
    "residual_queue": round(comparison['adaptive']['total_residual_queue'], 1),
    "peak_demand": round(peak_demand, 0)
}
if not st.session_state.simulation_history or (
    st.session_state.simulation_history[-1]["total_vehicles"] != total_vehicles
    or st.session_state.simulation_history[-1]["avg_delay"] != history_entry["avg_delay"]
):
    st.session_state.simulation_history.append(history_entry)
    if len(st.session_state.simulation_history) > 30:
        st.session_state.simulation_history.pop(0)

# Calculate Traffic Level of Service (LOS)
avg_delay_val = comparison['adaptive']['avg_intersection_delay']
if avg_delay_val < 15.0:
    los_code, los_label, los_css = "LOS A", "Free Flow (Minimal Delay)", "los-a"
elif avg_delay_val < 25.0:
    los_code, los_label, los_css = "LOS B", "Reasonably Free Flow", "los-b"
elif avg_delay_val < 38.0:
    los_code, los_label, los_css = "LOS C", "Stable Flow (Moderate)", "los-c"
elif avg_delay_val < 52.0:
    los_code, los_label, los_css = "LOS D", "Approaching Congestion", "los-d"
elif avg_delay_val < 70.0:
    los_code, los_label, los_css = "LOS E", "Unstable Flow (Heavy Delay)", "los-e"
else:
    los_code, los_label, los_css = "LOS F", "Forced Breakdown Gridlock", "los-f"


# =============================================================================
# CLEAN, COMPACT HEADER & SMART-CITY BRANDING
# =============================================================================
st.markdown(
    """
    <div class="hero-header">
      <div class="hero-top-row">
        <div class="hero-branding">
          <div class="hero-logo">🚦</div>
          <div>
            <div style="display:flex; align-items:baseline; gap:8px;">
              <h1 class="hero-title">TrafficIQ</h1>
              <span class="hero-tagline">AI Adaptive Traffic Signal Control</span>
            </div>
            <div class="hero-meta">
              Dynamic Machine Learning Demand Prediction & Webster Traffic Signal Optimization Platform
            </div>
          </div>
        </div>
        <div class="badge-row">
          <span class="badge-tag blue">🤖 Random Forest Model (R² 99.5%)</span>
          <span class="badge-tag teal">⏱ Dynamic Webster Optimization</span>
          <span class="badge-tag">🎮 60 FPS Canvas Simulation</span>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =============================================================================
# FIVE HIGH-IMPACT OVERVIEW METRIC CARDS
# =============================================================================
m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-card-header">
            <span class="metric-card-title">Total Vehicles</span>
            <span class="metric-card-icon">🚗</span>
          </div>
          <div class="metric-card-value">{total_vehicles}</div>
          <div class="metric-card-desc desc-neutral">
            Across 4 approach corridors
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m2:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-card-header">
            <span class="metric-card-title">Priority Corridor</span>
            <span class="metric-card-icon">⭐</span>
          </div>
          <div class="metric-card-value" style="font-size: 20px;">{peak_road.upper()} ({adaptive_timings[peak_road]}s)</div>
          <div class="metric-card-desc desc-warning">
            {peak_demand:,.0f} PCU/hr predicted
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m3:
    delay_save = comparison["improvements"]["delay_saved_seconds"]
    delay_pct = comparison["improvements"]["delay_reduction_pct"]
    desc_class = "desc-positive" if delay_pct > 0 else "desc-neutral"
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-card-header">
            <span class="metric-card-title">Average Delay</span>
            <span class="metric-card-icon">⏱️</span>
          </div>
          <div class="metric-card-value">{avg_delay_val:.1f}s</div>
          <div class="metric-card-desc {desc_class}">
            {f"↓ {delay_save:.1f}s ({delay_pct:.1f}% vs Fixed)" if delay_save > 0 else "Baseline comparable"}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m4:
    usable_green = budget_info['effective_green_budget']
    lost_t = budget_info['total_lost_time']
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-card-header">
            <span class="metric-card-title">Signal Cycle</span>
            <span class="metric-card-icon">🔄</span>
          </div>
          <div class="metric-card-value">{st.session_state.cycle_time}s</div>
          <div class="metric-card-desc desc-neutral">
            Green: {usable_green}s | Clearance: {lost_t}s
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with m5:
    r2_pct = model_metrics['r2_score'] * 100.0
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-card-header">
            <span class="metric-card-title">ML Predictive R²</span>
            <span class="metric-card-icon">🎯</span>
          </div>
          <div class="metric-card-value">{r2_pct:.1f}%</div>
          <div class="metric-card-desc desc-positive">
            MAE: {model_metrics['mae']:.1f} PCU/hr
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)


# =============================================================================
# FIVE CLEAN ARCHITECTURAL TABS
# =============================================================================
tab_sim, tab_opt, tab_comp, tab_analytics, tab_model = st.tabs([
    "🚦 Live Simulation",
    "⏱️ Signal Timing",
    "⚖️ Performance",
    "📊 Analytics",
    "🧠 ML Model"
])


# -----------------------------------------------------------------------------
# TAB 1: LIVE SIMULATION & INTERACTIVE CONTROLS
# -----------------------------------------------------------------------------
with tab_sim:
    # Congestion Status Alert Banner
    congested_roads = [
        r for r, s in road_states.items()
        if (s["vehicle_count"] >= 45 or s["queue_length"] >= 160.0 or predicted_demands[r] >= 1100.0)
    ]

    if congested_roads:
        cong_names = ", ".join(congested_roads)
        st.markdown(
            f"""
            <div class="congestion-alert-box">
              <div>
                <b>⚠️ Heavy Congestion on {cong_names} Approach:</b>
                Higher vehicle queues detected. Adaptive Webster optimizer has prioritized green split to dissipate queue.
              </div>
              <div>
                <span class="los-badge {los_css}">{los_code}: {los_label}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="flow-stable-box">
              <div>
                <b>✅ Traffic Flow Stable:</b>
                Arrival volumes across all four approaches remain within steady-state saturation capacity.
              </div>
              <div>
                <span class="los-badge {los_css}">{los_code}: {los_label}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Main 4-Way Intersection Visualizer (HTML5 Canvas 60 FPS)
    intersection_html = render_traffic_intersection(
        timings=adaptive_timings,
        vehicle_counts=st.session_state.vehicle_counts,
        predicted_demands=predicted_demands,
        traffic_densities={r: road_states[r]["traffic_density"] for r in road_states},
        queue_lengths={r: road_states[r]["queue_length"] for r in road_states},
        yellow_time=st.session_state.yellow_time,
        all_red_time=st.session_state.all_red_time,
        is_running=st.session_state.simulation_running,
        current_scenario=st.session_state.selected_scenario,
        height=520
    )
    st_components.html(intersection_html, height=530, scrolling=False)

    # Simulation Controls Toolbar directly below intersection
    bar_c1, bar_c2, bar_c3 = st.columns([2, 1.5, 3.5])

    with bar_c1:
        if st.session_state.simulation_running:
            st.button("⏸ Pause Simulation", key="main_sim_pause", on_click=toggle_simulation, args=(False,), use_container_width=True)
        else:
            st.button("▶ Resume Simulation", key="main_sim_resume", on_click=toggle_simulation, args=(True,), use_container_width=True)

    with bar_c2:
        st.button("🔄 Reset Simulation", key="main_sim_reset", on_click=reset_simulation, use_container_width=True)

    with bar_c3:
        st.markdown(
            f"<div style='text-align:right; padding-top:6px; font-size:12px; color:#475569;'>"
            f"<b>Active Timing:</b> North: <b style='color:#2563EB;'>{adaptive_timings['North']}s</b> | "
            f"South: <b style='color:#0F766E;'>{adaptive_timings['South']}s</b> | "
            f"East: <b style='color:#8B5CF6;'>{adaptive_timings['East']}s</b> | "
            f"West: <b style='color:#16A34A;'>{adaptive_timings['West']}s</b> "
            f"(Total: <b>{sum(adaptive_timings.values())}s</b>)"
            f"</div>",
            unsafe_allow_html=True
        )

    # Interactive Approach Quick-Tuning Cards
    st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)
    st.markdown("##### 🎛️ Interactive Approach Quick Tuning")
    st.caption("Click +5 or −5 to change traffic volume on any road and observe real-time signal timing reallocation.")

    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    roads_list = ["North", "East", "South", "West"]
    color_map = {"North": "#2563EB", "East": "#8B5CF6", "South": "#0F766E", "West": "#16A34A"}

    for idx, r in enumerate(roads_list):
        col = [t_col1, t_col2, t_col3, t_col4][idx]
        with col:
            v_cnt = st.session_state.vehicle_counts[r]
            g_sec = adaptive_timings[r]
            d_pcu = predicted_demands[r]
            q_m = road_states[r]["queue_length"]

            st.markdown(
                f"""
                <div class="content-box" style="padding: 10px 12px; margin-bottom: 8px;">
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size: 12px; font-weight: 700; color: {color_map[r]};">{r.upper()}</span>
                    <span style="background:#DCFCE7; color:#166534; font-size:10px; font-weight:700; padding:2px 6px; border-radius:8px;">
                      🟢 {g_sec}s Green
                    </span>
                  </div>
                  <div style="font-size: 12px; color: #172033; line-height: 1.5;">
                    <b>Volume:</b> {v_cnt} veh &nbsp;|&nbsp; <b>Queue:</b> {q_m:.0f} m<br>
                    <b>Demand:</b> {d_pcu:,.0f} PCU/hr
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            b_dec, b_inc = st.columns(2)
            with b_dec:
                st.button(
                    f"-5 {r}",
                    key=f"quick_dec_{r.lower()}",
                    on_click=adjust_vehicle_count,
                    args=(r, -5),
                    use_container_width=True
                )
            with b_inc:
                st.button(
                    f"+5 {r}",
                    key=f"quick_inc_{r.lower()}",
                    on_click=adjust_vehicle_count,
                    args=(r, 5),
                    use_container_width=True
                )


# -----------------------------------------------------------------------------
# TAB 2: SIGNAL OPTIMIZATION & WEBSTER SCHEDULE
# -----------------------------------------------------------------------------
with tab_opt:
    st.markdown("#### ⏱️ Traffic Signal Timing Optimization & Schedule")
    st.caption("Adaptive signal timings calculated via Webster proportional demand allocation under safety clearance bounds.")

    if optimizer_warnings:
        for w in optimizer_warnings:
            st.warning(f"⚠️ {w}")

    opt_col_table, opt_col_summary = st.columns([3, 2])

    with opt_col_table:
        st.markdown("##### Recommended Signal Timing Schedule")

        table_rows = []
        for r in ["North", "South", "East", "West"]:
            veh = st.session_state.vehicle_counts[r]
            dem = predicted_demands[r]
            q_len = road_states[r]["queue_length"]
            g_rec = adaptive_timings[r]
            g_fix = fixed_timings[r]
            is_peak = (r == peak_road)

            table_rows.append({
                "Road Approach": f"⭐ {r}" if is_peak else r,
                "Vehicle Count": f"{veh} veh",
                "Predicted Demand": f"{dem:,.0f} PCU/hr",
                "Queue Length": f"{q_len:.1f} m",
                "Recommended Green": f"{g_rec}s ({(g_rec / budget_info['effective_green_budget']) * 100:.1f}%)",
                "Fixed Duration": f"{g_fix}s",
                "Priority Status": "Highest Demand Priority" if is_peak else "Standard Adaptive"
            })

        df_table = pd.DataFrame(table_rows)
        st.dataframe(df_table, use_container_width=True, hide_index=True)
        st.caption("⭐ Approach with highest predicted traffic demand receives optimized priority green allocation.")

    with opt_col_summary:
        st.markdown("##### Optimization Cycle Budget Summary")
        st.markdown(
            f"""
            <div class="content-box">
              <div style="font-size: 13px; line-height: 1.9; color: #172033;">
                <b>Total Cycle Duration:</b> <span style="font-weight:700; color:#2563EB;">{st.session_state.cycle_time} seconds</span><br>
                <b>Total Clearance Time:</b> <span style="font-weight:700; color:#DC2626;">{budget_info['total_lost_time']} seconds</span> (4 phases × {st.session_state.yellow_time + st.session_state.all_red_time}s)<br>
                <b>Usable Green Budget:</b> <span style="font-weight:700; color:#16A34A;">{budget_info['effective_green_budget']} seconds</span><br>
                <b>Safety Constraints:</b> [{budget_info['effective_min_green']}s min, {budget_info['effective_max_green']}s max]<br>
                <b>Final Green Allocated:</b> {sum(adaptive_timings.values())}s (100% budget closed)
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Adaptive Signal Explanations ("Why This Timing?")
    st.markdown("##### 💡 Adaptive Signal Timing Explanations (\"Why This Timing?\")")
    st.caption("Automated natural language justifications derived directly from calculated demand ratios and boundary constraints.")

    tot_demand_sum = sum(predicted_demands.values())
    exp_col1, exp_col2 = st.columns(2)

    for idx, r in enumerate(["North", "South", "East", "West"]):
        col = exp_col1 if (idx % 2 == 0) else exp_col2
        ratio_pct = (predicted_demands[r] / max(1.0, tot_demand_sum)) * 100.0
        g_val = adaptive_timings[r]
        f_val = fixed_timings[r]
        diff_s = g_val - f_val

        if diff_s > 0:
            exp_text = (
                f"**{r} Approach ({g_val}s green):** Allocated +{diff_s}s above fixed baseline "
                f"because its predicted demand ({predicted_demands[r]:,.0f} PCU/hr) represents **{ratio_pct:.1f}%** of total intersection arrival flow."
            )
        elif diff_s < 0:
            exp_text = (
                f"**{r} Approach ({g_val}s green):** Scaled down by {abs(diff_s)}s compared to baseline "
                f"due to lower relative demand ({predicted_demands[r]:,.0f} PCU/hr), transferring idle green seconds to congested perpendicular corridors."
            )
        else:
            exp_text = (
                f"**{r} Approach ({g_val}s green):** Matches fixed timing baseline ({g_val}s) "
                f"as its arrival demand ({predicted_demands[r]:,.0f} PCU/hr) aligns symmetrically with mean intersection volume."
            )

        with col:
            st.info(exp_text)

    st.markdown("---")
    st.markdown("##### Allocation & Demand Visualizations")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.plotly_chart(
            plot_green_timings(adaptive_timings, fixed_timings),
            use_container_width=True,
            key="tab2_chart_green_alloc"
        )
    with col_c2:
        st.plotly_chart(
            plot_traffic_demand(predicted_demands),
            use_container_width=True,
            key="tab2_chart_traffic_demand"
        )


# -----------------------------------------------------------------------------
# TAB 3: PERFORMANCE ANALYSIS (FIXED VS ADAPTIVE)
# -----------------------------------------------------------------------------
with tab_comp:
    st.markdown("#### ⚖️ Performance Analysis: Fixed-Time vs Adaptive Signals")
    st.markdown(
        """
        Evaluation comparing **Strategy 1: Fixed-Time Signals** (equal static green splits regardless of demand fluctuations)
        against **Strategy 2: Adaptive ML Signals** (dynamic Webster optimization responding to Random Forest demand forecasts).
        """
    )

    bc1, bc2, bc3, bc4 = st.columns(4)
    with bc1:
        st.metric(
            label="Average Delay Reduction",
            value=f"{comparison['adaptive']['avg_intersection_delay']:.1f} s/veh",
            delta=f"-{comparison['improvements']['delay_saved_seconds']:.1f}s ({comparison['improvements']['delay_reduction_pct']:.1f}%)"
        )
    with bc2:
        st.metric(
            label="Residual Queue Reduction",
            value=f"{comparison['adaptive']['total_residual_queue']:.1f} veh",
            delta=f"-{comparison['improvements']['residual_queue_reduced']:.1f} veh ({comparison['improvements']['queue_reduction_pct']:.1f}%)"
        )
    with bc3:
        st.metric(
            label="Cycle Throughput Rate",
            value=f"{comparison['adaptive']['cycle_throughput_rate']:.1f}%",
            delta=f"+{comparison['adaptive']['cycle_throughput_rate'] - comparison['fixed']['cycle_throughput_rate']:.1f}%"
        )
    with bc4:
        st.metric(
            label="Idle Fuel Waste Avoided",
            value=f"{comparison['improvements']['fuel_saved_liters']:.3f} L/cycle",
            delta=f"-{comparison['improvements']['co2_saved_kg']:.3f} kg CO2"
        )

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Detailed Approach-by-Approach Table
    st.markdown("##### Detailed Simulation Results per Approach")
    comp_rows = []
    for r in ["North", "South", "East", "West"]:
        f_app = comparison["fixed"]["approaches"][r]
        a_app = comparison["adaptive"]["approaches"][r]
        d_saved = f_app["avg_delay_seconds"] - a_app["avg_delay_seconds"]

        comp_rows.append({
            "Approach": r,
            "Vehicles": f"{st.session_state.vehicle_counts[r]} veh",
            "Fixed Green": f"{f_app['green_time']}s",
            "Fixed Delay": f"{f_app['avg_delay_seconds']:.1f}s",
            "Fixed Resid. Queue": f"{f_app['residual_queue']:.1f} veh",
            "Adaptive Green": f"{a_app['green_time']}s",
            "Adaptive Delay": f"{a_app['avg_delay_seconds']:.1f}s",
            "Adaptive Resid. Queue": f"{a_app['residual_queue']:.1f} veh",
            "Delay Saved": f"{d_saved:.1f}s ({((d_saved / max(0.1, f_app['avg_delay_seconds']))*100):.1f}%)"
        })

    df_comp = pd.DataFrame(comp_rows)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("##### Performance Benchmark Visualizations")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.plotly_chart(
            plot_waiting_time_comparison(comparison),
            use_container_width=True,
            key="tab3_chart_waiting_time"
        )
    with col_b2:
        st.plotly_chart(
            plot_strategy_overall_comparison(comparison),
            use_container_width=True,
            key="tab3_chart_overall_comp"
        )


# -----------------------------------------------------------------------------
# TAB 4: TRAFFIC ANALYTICS & SCENARIO COMPARISON
# -----------------------------------------------------------------------------
with tab_analytics:
    st.markdown("#### 📊 Traffic Analytics & History")
    st.caption("Deep-dive analytics on spatial demand, unserved queues, 24-hour diurnal patterns, and simulation history.")

    an_c1, an_c2 = st.columns(2)
    with an_c1:
        st.plotly_chart(
            plot_traffic_demand(predicted_demands),
            use_container_width=True,
            key="tab4_chart_demand_by_road"
        )
    with an_c2:
        st.plotly_chart(
            plot_green_timings(adaptive_timings, fixed_timings),
            use_container_width=True,
            key="tab4_chart_green_allocations"
        )

    an_c3, an_c4 = st.columns(2)
    with an_c3:
        st.plotly_chart(
            plot_queue_length_comparison(comparison),
            use_container_width=True,
            key="tab4_chart_queue_comparison"
        )
    with an_c4:
        st.plotly_chart(
            plot_traffic_demand_over_time(st.session_state.hour_of_day, predicted_demands),
            use_container_width=True,
            key="tab4_chart_demand_over_time"
        )

    st.markdown("---")

    # Live Simulation History Tracking
    st.markdown("##### 📈 Live Simulation History (Time-Series Tracking)")
    st.caption("Tracks how vehicle counts, residual queues, and average waiting time evolve during your session.")

    st.plotly_chart(
        plot_simulation_history(st.session_state.simulation_history),
        use_container_width=True,
        key="tab4_chart_history"
    )

    st.markdown("---")

    # Scenario Comparison Tool
    st.markdown("##### 🔄 Scenario Comparison Tool")
    st.caption("Directly compare signal timings and traffic demands between any two operational scenarios.")

    cmp_col1, cmp_col2 = st.columns(2)
    with cmp_col1:
        scen_a = st.selectbox("Select Scenario A", scenarios, index=0, key="select_scen_a")
    with cmp_col2:
        scen_b = st.selectbox("Select Scenario B", scenarios, index=1, key="select_scen_b")

    def get_scenario_results(s_name):
        s_data = get_scenario(s_name)
        s_states = {}
        for r, cnt in s_data["vehicle_counts"].items():
            s_states[r] = {
                "vehicle_count": cnt,
                "traffic_density": s_data["traffic_density"][r],
                "queue_length": s_data["queue_length"][r],
                "avg_speed": s_data["avg_speed"],
                "prev_waiting_time": s_data["prev_waiting_time"][r]
            }
        s_demands = predictor.predict_intersection_demands(s_states, s_data["hour_of_day"], s_data["day_of_week"])
        s_opt = optimizer.optimize_green_timings(s_demands)
        return s_demands, s_opt["adaptive_timings"], s_data["vehicle_counts"]

    dem_a, timings_a, counts_a = get_scenario_results(scen_a)
    dem_b, timings_b, counts_b = get_scenario_results(scen_b)

    # Comparison Table
    diff_table_rows = []
    for r in ["North", "South", "East", "West"]:
        diff_table_rows.append({
            "Road Approach": r,
            f"{scen_a} Vehicles": f"{counts_a[r]} veh",
            f"{scen_a} Demand": f"{dem_a[r]:,.0f} PCU/hr",
            f"{scen_a} Green": f"{timings_a[r]}s",
            f"{scen_b} Vehicles": f"{counts_b[r]} veh",
            f"{scen_b} Demand": f"{dem_b[r]:,.0f} PCU/hr",
            f"{scen_b} Green": f"{timings_b[r]}s",
            "Green Time Difference": f"{timings_b[r] - timings_a[r]:+d}s"
        })
    st.dataframe(pd.DataFrame(diff_table_rows), use_container_width=True, hide_index=True)

    st.plotly_chart(
        plot_scenario_comparison_diff(scen_a, timings_a, scen_b, timings_b),
        use_container_width=True,
        key="tab4_chart_scenario_diff"
    )

    st.markdown("---")
    st.markdown("##### All-Scenario Green Allocation Benchmark")
    scenario_demands = {}
    scenario_timings = {}
    for s_name in scenarios:
        s_dem, s_tim, _ = get_scenario_results(s_name)
        scenario_demands[s_name] = s_dem
        scenario_timings[s_name] = s_tim

    st.plotly_chart(
        plot_multi_scenario_analysis(scenarios, scenario_demands, scenario_timings),
        use_container_width=True,
        key="tab4_chart_scenarios_comparison"
    )


# -----------------------------------------------------------------------------
# TAB 5: MACHINE LEARNING MODEL SPECIFICATIONS
# -----------------------------------------------------------------------------
with tab_model:
    st.markdown("#### 🧠 Machine Learning Model Specifications & Architecture")

    m_col1, m_col2 = st.columns(2)

    with m_col1:
        st.markdown("##### 1. Model Configuration & Test Evaluation")
        st.markdown(
            f"""
            - **Algorithm:** Random Forest Regressor (`sklearn.ensemble.RandomForestRegressor`)
            - **Ensemble Configuration:** 120 Estimator Trees, Max Depth 14, Min Samples Split 4
            - **Evaluation Protocol:** 80% Training (4,800 records), 20% Held-Out Testing (1,200 records)
            - **Reproducibility Seed:** Fixed seed `42`
            - **Evaluation Metrics on Held-Out Test Set:**
              - **R² Score:** `{model_metrics['r2_score'] * 100:.2f}%` (Explains 99.45% of variance in traffic demand)
              - **Mean Absolute Error (MAE):** `{model_metrics['mae']:.2f} PCU/hr`
              - **Root Mean Squared Error (RMSE):** `{model_metrics['rmse']:.2f} PCU/hr`
            - **Target Variable:** Traffic Demand ($D_i$, PCU/hr) representing imminent green phase service requirement.
            """
        )

        st.markdown("##### Feature Importance Ranking")
        feat_df = pd.DataFrame(
            list(model_metrics.get("feature_importances", {}).items()),
            columns=["Feature", "Importance"]
        ).head(8)
        st.dataframe(feat_df, use_container_width=True, hide_index=True)

        st.plotly_chart(
            plot_feature_importances(model_metrics.get("feature_importances", {})),
            use_container_width=True,
            key="tab5_chart_features"
        )

    with m_col2:
        st.markdown("##### 2. Architectural Separation of Concerns")
        st.markdown(
            """
            **Critical Traffic Engineering Principle:**  
            The Random Forest model **does not directly predict green seconds**; instead, it forecasts **Traffic Demand (PCU/hr)**
            from raw road metrics. Then, a mathematically rigorous Webster optimization algorithm computes green-light timings.

            **Optimization Cycle Equation:**
            """
        )
        st.latex(
            r"C = \sum_{i=1}^{4} g_i + L, \quad L = 4 \times (y + r_{\text{all}})"
        )
        st.latex(
            r"g_i = \text{clamp}\left( G_{\text{budget}} \times \frac{D_i}{\sum_{j} D_j}, \, g_{\min}, \, g_{\max} \right)"
        )
        st.markdown(
            """
            Where:
            - $C$: Total Cycle Time (e.g. 120s)
            - $L$: Lost clearance time ($4 \\times 4\\text{s} = 16\\text{s}$)
            - $G_{\\text{budget}}$: Usable green budget ($C - L$)
            - $g_{\\min}, g_{\\max}$: Safe bounds enforced via iterative projection.
            """
        )

        # Export Reports (CSV)
        st.markdown("---")
        st.markdown("##### 📥 Export Traffic Performance Report (CSV)")
        st.caption("Generate a structured CSV audit report documenting inputs, ML predictions, optimization schedule, and performance metrics.")

        csv_buffer = io.StringIO()
        csv_buffer.write("# TrafficIQ Traffic Performance Audit Report\n")
        csv_buffer.write(f"# Timestamp: {datetime.now().isoformat()}\n")
        csv_buffer.write(f"# Active Scenario: {st.session_state.selected_scenario}\n")
        csv_buffer.write(f"# Total Vehicles: {total_vehicles}\n")
        csv_buffer.write(f"# Cycle Time: {st.session_state.cycle_time}s\n")
        csv_buffer.write(f"# Usable Green Budget: {budget_info['effective_green_budget']}s\n")
        csv_buffer.write(f"# Total Lost Clearance Time: {budget_info['total_lost_time']}s\n")
        csv_buffer.write(f"# Average Delay Reduction: {comparison['improvements']['delay_saved_seconds']:.1f}s ({comparison['improvements']['delay_reduction_pct']:.1f}%)\n")
        csv_buffer.write(f"# Model R2 Score: {model_metrics['r2_score']:.4f}\n\n")

        report_df = pd.DataFrame([
            {
                "Road": r,
                "Vehicle_Count": st.session_state.vehicle_counts[r],
                "Predicted_Demand_PCU_hr": round(predicted_demands[r], 1),
                "Queue_Length_m": round(road_states[r]["queue_length"], 1),
                "Recommended_Green_s": adaptive_timings[r],
                "Fixed_Green_s": fixed_timings[r],
                "Adaptive_Delay_s": comparison["adaptive"]["approaches"][r]["avg_delay_seconds"],
                "Fixed_Delay_s": comparison["fixed"]["approaches"][r]["avg_delay_seconds"],
                "Residual_Queue_veh": comparison["adaptive"]["approaches"][r]["residual_queue"]
            }
            for r in ["North", "South", "East", "West"]
        ])
        report_df.to_csv(csv_buffer, index=False)

        st.download_button(
            label="📥 Download CSV Report",
            data=csv_buffer.getvalue(),
            file_name=f"TrafficIQ_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="btn_download_report_csv"
        )

    st.markdown("---")
    st.markdown("##### 3. Research Context & Physical Constraints Disclaimer")
    st.info(
        """
        **Research Simulation Context:** The training dataset (6,000 samples) was generated synthetically based on
        established traffic flow theory (Greenshields speed-density relationships, Poisson vehicle arrival rates,
        and diurnal commuter profiles). The simulation results and estimated waiting-time savings reflect analytical
        queuing models (Webster's delay equations) and are intended for academic demonstration, not physical municipal deployment.
        """
    )
