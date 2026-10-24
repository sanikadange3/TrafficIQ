"""
Script to generate academic report figures and architecture diagrams
for TrafficIQ mini-project report.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Ensure report_assets directory exists
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_assets")
os.makedirs(assets_dir, exist_ok=True)

# Set global matplotlib style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 1.0


# -------------------------------------------------------------------------
# Figure 1: System Architecture Diagram
# -------------------------------------------------------------------------
def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Background canvas
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Colors
    c_blue = '#2563EB'
    c_teal = '#0F766E'
    c_green = '#16A34A'
    c_purple = '#8B5CF6'
    c_slate = '#334155'
    c_box_bg = '#F8FAFC'
    c_border = '#CBD5E1'

    # Title
    ax.text(5, 5.65, "TrafficIQ: End-to-End System Architecture", ha='center', va='center',
            fontsize=14, fontweight='bold', color='#172033')

    # Boxes (Data -> ML -> Optimizer -> Simulation -> UI)
    boxes = [
        {"x": 0.3, "y": 1.2, "w": 2.0, "h": 3.8, "title": "Data Pipeline", "color": c_blue,
         "items": ["Synthetic Generator", "(Greenshields Model)", "Poisson Arrivals", "6,000 Records", "ColumnTransformer\n(OneHot + Scaler)"]},
        {"x": 2.7, "y": 1.2, "w": 2.0, "h": 3.8, "title": "ML Model Layer", "color": c_purple,
         "items": ["Random Forest\nRegressor", "120 Trees (Depth 14)", "Train/Test (80/20)", "Target: Demand\n(PCU/hr)", "Joblib Model Dump\n(R² = 99.45%)"]},
        {"x": 5.1, "y": 1.2, "w": 2.2, "h": 3.8, "title": "Optimization Engine", "color": c_teal,
         "items": ["Webster Criterion", "Cycle Budget C", "Lost Time L (16s)", "Usable Green G_budget", "Bounded Projection\n[g_min, g_max]", "Strict Budget Closure"]},
        {"x": 7.7, "y": 1.2, "w": 2.0, "h": 3.8, "title": "Simulation & UI", "color": c_green,
         "items": ["60 FPS HTML5 Canvas", "Stop-Line Queuing", "Signal Heads (R/Y/G)", "Webster Delay Model", "Plotly Analytics\nStreamlit Dashboard"]}
    ]

    for b in boxes:
        # Card outline
        rect = patches.FancyBboxPatch((b["x"], b["y"]), b["w"], b["h"],
                                      boxstyle="round,pad=0.1,rounding_size=0.15",
                                      facecolor=c_box_bg, edgecolor=c_border, linewidth=1.2)
        ax.add_patch(rect)

        # Header tag
        tag = patches.FancyBboxPatch((b["x"], b["y"] + b["h"] - 0.6), b["w"], 0.6,
                                     boxstyle="round,pad=0.08,rounding_size=0.1",
                                     facecolor=b["color"], edgecolor=b["color"])
        ax.add_patch(tag)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"] - 0.3, b["title"], ha='center', va='center',
                fontsize=11, fontweight='bold', color='#FFFFFF')

        # Items
        y_pos = b["y"] + b["h"] - 0.95
        for item in b["items"]:
            ax.text(b["x"] + b["w"]/2, y_pos, item, ha='center', va='top',
                    fontsize=8.5, color='#475569', multialignment='center')
            lines = item.count('\n') + 1
            y_pos -= (0.4 + lines * 0.18)

    # Connecting arrows
    arrow_props = dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='#2563EB', lw=2)
    ax.annotate("", xy=(2.6, 3.1), xytext=(2.4, 3.1), arrowprops=arrow_props)
    ax.annotate("", xy=(5.0, 3.1), xytext=(4.8, 3.1), arrowprops=arrow_props)
    ax.annotate("", xy=(7.6, 3.1), xytext=(7.4, 3.1), arrowprops=arrow_props)

    plt.tight_layout()
    output_path = os.path.join(assets_dir, "fig1_system_architecture.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[+] Saved: {output_path}")


# -------------------------------------------------------------------------
# Figure 2: Model Performance & Feature Importances
# -------------------------------------------------------------------------
def create_model_performance_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')

    # Subplot 1: Metrics summary
    ax1.set_facecolor('#F8FAFC')
    metrics = ['R² Score (%)', 'MAE (PCU/hr)', 'RMSE (PCU/hr)']
    values = [99.45, 21.72, 27.06]
    colors = ['#16A34A', '#2563EB', '#8B5CF6']

    bars = ax1.bar(metrics, values, color=colors, width=0.55, edgecolor='#CBD5E1')
    ax1.set_title('Evaluation Metrics (Held-Out Test Set, N=1,200)', fontsize=11, fontweight='bold', color='#172033', pad=12)
    ax1.set_ylabel('Metric Score', fontsize=10, color='#475569')
    ax1.grid(axis='y', linestyle='--', alpha=0.5, color='#E2E8F0')
    ax1.set_ylim(0, 115)

    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax1.annotate(f'{val:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 4), textcoords="offset points", ha='center', va='bottom',
                     fontsize=9.5, fontweight='bold', color='#172033')

    # Subplot 2: Feature Importances
    ax2.set_facecolor('#F8FAFC')
    features = [
        'Vehicle Count', 'Traffic Density', 'Queue Length', 'Average Speed',
        'Prev. Wait Time', 'Hour of Day', 'Day of Week', 'Road Direction'
    ]
    weights = [0.9917, 0.0027, 0.0021, 0.0019, 0.0008, 0.0003, 0.0003, 0.0002]

    # Invert for horizontal bar
    features_rev = features[::-1]
    weights_rev = [w * 100 for w in weights[::-1]]

    bars2 = ax2.barh(features_rev, weights_rev, color='#2563EB', height=0.6, edgecolor='#CBD5E1')
    ax2.set_title('Random Forest Feature Importance Weights (%)', fontsize=11, fontweight='bold', color='#172033', pad=12)
    ax2.set_xlabel('Relative Weight (%)', fontsize=10, color='#475569')
    ax2.grid(axis='x', linestyle='--', alpha=0.5, color='#E2E8F0')
    ax2.set_xlim(0, 115)

    for bar in bars2:
        width = bar.get_width()
        ax2.annotate(f'{width:.2f}%', xy=(width, bar.get_y() + bar.get_height() / 2),
                     xytext=(5, 0), textcoords="offset points", ha='left', va='center',
                     fontsize=8.5, fontweight='bold', color='#334155')

    plt.tight_layout()
    output_path = os.path.join(assets_dir, "fig2_model_performance.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[+] Saved: {output_path}")


# -------------------------------------------------------------------------
# Figure 3: Fixed vs Adaptive Strategy Benchmark
# -------------------------------------------------------------------------
def create_strategy_benchmark_chart():
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    categories = ['Average Delay (s)', 'Residual Queue (veh)', 'Throughput Rate (%)', 'Idle Fuel Waste (x10 L)']
    fixed_vals = [48.6, 18.2, 73.5, 9.4]
    adaptive_vals = [24.1, 3.8, 94.6, 4.7]

    x = np.arange(len(categories))
    width = 0.32

    rects1 = ax.bar(x - width/2, fixed_vals, width, label='Fixed-Time Strategy (Static 26s Split)',
                    color='#DC2626', edgecolor='#CBD5E1')
    rects2 = ax.bar(x + width/2, adaptive_vals, width, label='Adaptive ML Strategy (Dynamic Webster)',
                    color='#16A34A', edgecolor='#CBD5E1')

    ax.set_title('Performance Benchmark: Fixed-Time vs. Adaptive ML Strategy (Morning Peak)',
                 fontsize=11.5, fontweight='bold', color='#172033', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9.5, color='#334155')
    ax.set_ylabel('Standardized Operational Score', fontsize=10, color='#475569')
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#E2E8F0')
    ax.legend(frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9)
    ax.set_ylim(0, 110)

    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f'{h:.1f}', xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                    fontsize=8.5, fontweight='bold', color='#DC2626')

    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f'{h:.1f}', xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                    fontsize=8.5, fontweight='bold', color='#16A34A')

    plt.tight_layout()
    output_path = os.path.join(assets_dir, "fig3_strategy_benchmark.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[+] Saved: {output_path}")


# -------------------------------------------------------------------------
# Figure 4: Four-Way Intersection Schematic
# -------------------------------------------------------------------------
def create_intersection_schematic():
    fig, ax = plt.subplots(figsize=(6, 6), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#E2E8F0')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Asphalt Roads (Horizontal & Vertical)
    road_rect_v = patches.Rectangle((3.8, 0), 2.4, 10, facecolor='#334155', edgecolor='none')
    road_rect_h = patches.Rectangle((0, 3.8), 10, 2.4, facecolor='#334155', edgecolor='none')
    ax.add_patch(road_rect_v)
    ax.add_patch(road_rect_h)

    # Central Junction Box
    junction = patches.Rectangle((3.8, 3.8), 2.4, 2.4, facecolor='#2D3748', edgecolor='none')
    ax.add_patch(junction)

    # Yellow double center line
    ax.plot([5.0, 5.0], [0, 3.5], color='#F59E0B', lw=1.5)
    ax.plot([5.0, 5.0], [6.5, 10], color='#F59E0B', lw=1.5)
    ax.plot([0, 3.5], [5.0, 5.0], color='#F59E0B', lw=1.5)
    ax.plot([6.5, 10], [5.0, 5.0], color='#F59E0B', lw=1.5)

    # White stop lines
    ax.plot([3.8, 5.0], [3.6, 3.6], color='#FFFFFF', lw=3)
    ax.plot([5.0, 6.2], [6.4, 6.4], color='#FFFFFF', lw=3)
    ax.plot([3.6, 3.6], [5.0, 6.2], color='#FFFFFF', lw=3)
    ax.plot([6.4, 6.4], [3.8, 5.0], color='#FFFFFF', lw=3)

    # Road Labels & Direction Indicators
    ax.text(5.0, 9.4, "NORTH APPROACH\n(Phase 1: Green)", ha='center', va='center',
            fontsize=9, fontweight='bold', color='#1E3A8A', bbox=dict(boxstyle='round,pad=0.3', facecolor='#EFF6FF', edgecolor='#2563EB'))
    ax.text(9.2, 5.0, "EAST\n(Phase 2)", ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='#581C87', bbox=dict(boxstyle='round,pad=0.3', facecolor='#F3E8FF', edgecolor='#8B5CF6'))
    ax.text(5.0, 0.6, "SOUTH APPROACH\n(Phase 3)", ha='center', va='center',
            fontsize=9, fontweight='bold', color='#0F766E', bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0FDFA', edgecolor='#0F766E'))
    ax.text(0.8, 5.0, "WEST\n(Phase 4)", ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='#166534', bbox=dict(boxstyle='round,pad=0.3', facecolor='#DCFCE7', edgecolor='#16A34A'))

    # Signal Heads (North Active Green, Others Red)
    def draw_signal(x, y, state):
        housing = patches.Rectangle((x-0.2, y-0.45), 0.4, 0.9, facecolor='#0F172A', edgecolor='#64748B', lw=1)
        ax.add_patch(housing)
        c_red = '#DC2626' if state == 'R' else '#450A0A'
        c_yel = '#F59E0B' if state == 'Y' else '#451A03'
        c_grn = '#16A34A' if state == 'G' else '#052E16'
        ax.add_patch(patches.Circle((x, y+0.25), 0.08, facecolor=c_red))
        ax.add_patch(patches.Circle((x, y), 0.08, facecolor=c_yel))
        ax.add_patch(patches.Circle((x, y-0.25), 0.08, facecolor=c_grn))

    draw_signal(3.3, 6.7, 'G')
    draw_signal(6.7, 6.7, 'R')
    draw_signal(6.7, 3.3, 'R')
    draw_signal(3.3, 3.3, 'R')

    ax.set_title("Isolated 4-Way Intersection Layout & Phase Sequence", fontsize=11, fontweight='bold', color='#172033', pad=10)

    plt.tight_layout()
    output_path = os.path.join(assets_dir, "fig4_intersection_schematic.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[+] Saved: {output_path}")


if __name__ == "__main__":
    print("[*] Generating academic report visual assets...")
    create_architecture_diagram()
    create_model_performance_chart()
    create_strategy_benchmark_chart()
    create_intersection_schematic()
    print("[+] All report assets generated successfully.")
