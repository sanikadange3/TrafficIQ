import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
fig.patch.set_facecolor('#0f172a')
ax.set_facecolor('#0f172a')
ax.axis('off')

# Sidebar
sidebar = patches.FancyBboxPatch((0.02, 0.05), 0.22, 0.90, boxstyle='round,pad=0.01', facecolor='#1e293b', edgecolor='#334155', linewidth=1.5)
ax.add_patch(sidebar)
ax.text(0.13, 0.91, 'TrafficIQ Studio', color='#38bdf8', fontsize=12, fontweight='bold', ha='center')
ax.text(0.13, 0.87, 'Adaptive Control Center', color='#94a3b8', fontsize=8, ha='center')

# Sliders in sidebar
controls = [
    'Scenario: Rush Hour',
    'North Demand: 68 veh',
    'South Demand: 52 veh',
    'East Demand: 44 veh',
    'West Demand: 71 veh',
    'Cycle Time (C): 120s',
    'Min Green: 10s',
    'Lost Clearance: 16s'
]
for i, ctrl in enumerate(controls):
    y = 0.80 - i * 0.08
    ax.text(0.04, y, ctrl, color='#e2e8f0', fontsize=7.5, fontweight='bold')
    bar_bg = patches.Rectangle((0.04, y-0.03), 0.18, 0.012, facecolor='#334155', edgecolor='none')
    bar_fill = patches.Rectangle((0.04, y-0.03), 0.18 * (0.4 + 0.07*i), 0.012, facecolor='#2563eb', edgecolor='none')
    ax.add_patch(bar_bg)
    ax.add_patch(bar_fill)

# Main Header
main_box = patches.FancyBboxPatch((0.26, 0.05), 0.72, 0.90, boxstyle='round,pad=0.01', facecolor='#1e293b', edgecolor='#334155', linewidth=1.5)
ax.add_patch(main_box)

ax.text(0.28, 0.91, 'TrafficIQ Dashboard: Real-Time Adaptive Optimization & Simulation', color='#f8fafc', fontsize=13, fontweight='bold')
ax.text(0.28, 0.88, 'JSPM RSCOE Department of Computer Engineering | Third-Year ML Mini-Project 2026-27', color='#38bdf8', fontsize=8)

# Metric KPI cards
kpis = [
    ('Average Delay', '18.4 s', '-34.2%', '#10b981'),
    ('Throughput', '2,420 veh/h', '+28.5%', '#3b82f6'),
    ('Fuel Saved', '14.8 L/hr', '-29.1%', '#f59e0b'),
    ('CO2 Abated', '34.2 kg/hr', '-29.1%', '#8b5cf6')
]
for i, (title, val, delta, col) in enumerate(kpis):
    x = 0.28 + i * 0.17
    card = patches.FancyBboxPatch((x, 0.74), 0.155, 0.11, boxstyle='round,pad=0.01', facecolor='#0f172a', edgecolor=col, linewidth=1.2)
    ax.add_patch(card)
    ax.text(x+0.01, 0.82, title, color='#94a3b8', fontsize=7)
    ax.text(x+0.01, 0.77, val, color='#f8fafc', fontsize=11, fontweight='bold')
    ax.text(x+0.01, 0.75, delta + ' vs Fixed', color=col, fontsize=7, fontweight='bold')

# Left Panel: Canvas Simulation
sim_box = patches.FancyBboxPatch((0.28, 0.08), 0.33, 0.63, boxstyle='round,pad=0.01', facecolor='#0f172a', edgecolor='#334155', linewidth=1.2)
ax.add_patch(sim_box)
ax.text(0.445, 0.68, 'Dynamic 4-Way Simulation Canvas (60 FPS)', color='#38bdf8', fontsize=9, fontweight='bold', ha='center')

# Road crossing inside sim
road_v = patches.Rectangle((0.41, 0.11), 0.07, 0.54, facecolor='#1e293b')
road_h = patches.Rectangle((0.30, 0.345), 0.29, 0.07, facecolor='#1e293b')
ax.add_patch(road_v)
ax.add_patch(road_h)
# Stoplines & Signals
ax.add_patch(patches.Circle((0.40, 0.425), 0.009, facecolor='#ef4444')) # North red
ax.add_patch(patches.Circle((0.49, 0.335), 0.009, facecolor='#ef4444')) # South red
ax.add_patch(patches.Circle((0.395, 0.335), 0.009, facecolor='#22c55e')) # West green
ax.add_patch(patches.Circle((0.485, 0.425), 0.009, facecolor='#22c55e')) # East green
ax.text(0.445, 0.38, 'Active Phase: E-W (Green: 32s)', color='#fbbf24', fontsize=7, ha='center', fontweight='bold')

# Right Panel: Signal Timing Allocation & Analytics
chart_box = patches.FancyBboxPatch((0.63, 0.08), 0.33, 0.63, boxstyle='round,pad=0.01', facecolor='#0f172a', edgecolor='#334155', linewidth=1.2)
ax.add_patch(chart_box)
ax.text(0.795, 0.68, 'Signal Allocation & Demand Optimization', color='#38bdf8', fontsize=9, fontweight='bold', ha='center')

# Timing Bars
approaches = [
    ('North Approach', 24, 26, '#3b82f6'),
    ('South Approach', 18, 26, '#10b981'),
    ('East Approach', 28, 26, '#f59e0b'),
    ('West Approach', 34, 26, '#8b5cf6')
]
for i, (app_name, adp_t, fxd_t, col) in enumerate(approaches):
    y = 0.59 - i * 0.12
    ax.text(0.65, y+0.04, f'{app_name}: Adaptive {adp_t}s vs Fixed {fxd_t}s', color='#e2e8f0', fontsize=7.5)
    # Fixed bar
    ax.add_patch(patches.Rectangle((0.65, y+0.015), 0.12, 0.018, facecolor='#475569'))
    # Adaptive bar
    ax.add_patch(patches.Rectangle((0.65, y-0.01), 0.12 * (adp_t/26.0), 0.018, facecolor=col))
    ax.text(0.65 + 0.12 * (adp_t/26.0) + 0.01, y-0.008, f'{adp_t}s', color=col, fontsize=7, fontweight='bold')

ax.text(0.795, 0.11, 'Random Forest Demand Predictor (R2: 0.9945 | MAE: 21.72 PCU/hr)', color='#94a3b8', fontsize=7, ha='center', fontstyle='italic')

plt.tight_layout()
plt.savefig('report_assets/fig5_dashboard_interface.png', dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
print('fig5 saved successfully')
