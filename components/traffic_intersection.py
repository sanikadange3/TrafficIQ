"""
Visual Interactive Four-Way Traffic Intersection Component - Light Theme
========================================================================
Renders a 60 FPS HTML5 Canvas interactive simulation of a 4-way urban junction
styled for a modern, professional smart-city traffic dashboard.
Features:
- State persistence across Streamlit reruns (sessionStorage)
- Dynamic signal timing response from ML + Webster optimizer
- Multi-lane independent queuing physics and shockwave queue discharge
- Real-time countdowns, HUD telemetry cards, and interactive speed controls
"""

import json
from typing import Dict, Any


def render_traffic_intersection(
    timings: Dict[str, int],
    vehicle_counts: Dict[str, int],
    predicted_demands: Dict[str, float],
    traffic_densities: Dict[str, float],
    queue_lengths: Dict[str, float],
    yellow_time: int = 3,
    all_red_time: int = 1,
    is_running: bool = True,
    current_scenario: str = "Normal Traffic",
    height: int = 560
) -> str:
    """
    Generate self-contained HTML/CSS/JavaScript for the 4-way intersection simulation.
    """
    config_data = {
        "timings": {
            "North": int(timings.get("North", 25)),
            "East": int(timings.get("East", 25)),
            "South": int(timings.get("South", 25)),
            "West": int(timings.get("West", 25))
        },
        "yellow_time": int(yellow_time),
        "all_red_time": int(all_red_time),
        "vehicle_counts": {
            "North": int(vehicle_counts.get("North", 20)),
            "East": int(vehicle_counts.get("East", 20)),
            "South": int(vehicle_counts.get("South", 20)),
            "West": int(vehicle_counts.get("West", 20))
        },
        "demands": {
            "North": float(predicted_demands.get("North", 500)),
            "East": float(predicted_demands.get("East", 500)),
            "South": float(predicted_demands.get("South", 500)),
            "West": float(predicted_demands.get("West", 500))
        },
        "densities": {
            "North": float(traffic_densities.get("North", 35)),
            "East": float(traffic_densities.get("East", 35)),
            "South": float(traffic_densities.get("South", 35)),
            "West": float(traffic_densities.get("West", 35))
        },
        "queues": {
            "North": float(queue_lengths.get("North", 65)),
            "East": float(queue_lengths.get("East", 65)),
            "South": float(queue_lengths.get("South", 65)),
            "West": float(queue_lengths.get("West", 65))
        },
        "is_running": is_running,
        "scenario": current_scenario
    }

    config_json = json.dumps(config_data)

    html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      user-select: none;
    }}
    body {{
      background: #F4F7FB;
      color: #172033;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      padding: 0;
      margin: 0;
    }}
    #sim-container {{
      position: relative;
      width: 100%;
      max-width: 100%;
      height: 520px;
      background: #F8FAFC;
      border-radius: 10px;
      box-shadow: 0 3px 12px rgba(0,0,0,0.05);
      border: 1px solid #E2E8F0;
      overflow: hidden;
    }}
    canvas {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
    }}

    /* Light Theme HUD Overlays (Frosted Glass) */
    .hud-card {{
      position: absolute;
      z-index: 10;
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      border: 1px solid #E2E8F0;
      border-radius: 7px;
      padding: 6px 9px;
      font-size: 10.5px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
      min-width: 140px;
      max-width: 155px;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
      pointer-events: auto;
    }}
    .hud-card:hover {{
      border-color: #CBD5E1;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.09);
    }}
    .hud-card.north {{ top: 8px; left: 10px; border-left: 3.5px solid #2563EB; }}
    .hud-card.east  {{ top: 8px; right: 10px; border-left: 3.5px solid #8B5CF6; }}
    .hud-card.south {{ bottom: 42px; right: 10px; border-left: 3.5px solid #0F766E; }}
    .hud-card.west  {{ bottom: 42px; left: 10px; border-left: 3.5px solid #16A34A; }}



    .hud-title {{
      font-weight: 700;
      font-size: 11.5px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
      color: #172033;
    }}
    .hud-signal-pill {{
      display: inline-flex;
      align-items: center;
      gap: 3px;
      padding: 1.5px 6px;
      border-radius: 8px;
      font-size: 9.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }}
    .signal-green {{ background: #DCFCE7; color: #16A34A; border: 1px solid #BBF7D0; }}
    .signal-yellow {{ background: #FEF3C7; color: #D97706; border: 1px solid #FDE68A; }}
    .signal-red {{ background: #FEE2E2; color: #DC2626; border: 1px solid #FECACA; }}

    .hud-row {{
      display: flex;
      justify-content: space-between;
      margin: 1.5px 0;
      color: #64748B;
      font-size: 10.5px;
    }}
    .hud-val {{
      color: #172033;
      font-weight: 600;
    }}
    .hud-btn {{
      margin-top: 4px;
      width: 100%;
      background: #F1F5F9;
      border: 1px solid #E2E8F0;
      color: #334155;
      padding: 2.5px 0;
      border-radius: 5px;
      font-size: 9.5px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.15s ease;
    }}
    .hud-btn:hover {{
      background: #E2E8F0;
      color: #1E293B;
      border-color: #CBD5E1;
    }}

    /* Bottom Control Bar */
    #control-bar {{
      position: absolute;
      bottom: 8px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 20;
      display: flex;
      align-items: center;
      gap: 7px;
      background: rgba(255, 255, 255, 0.95);
      border: 1px solid #E2E8F0;
      border-radius: 20px;
      padding: 4px 12px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.07);
      backdrop-filter: blur(8px);
    }}
    .sim-btn {{
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      color: #334155;
      padding: 4px 10px;
      border-radius: 14px;
      font-size: 10.5px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s ease;
    }}
    .sim-btn:hover {{
      background: #E2E8F0;
      color: #0F172A;
    }}
    .sim-btn.active {{
      background: #2563EB;
      border-color: #2563EB;
      color: #FFFFFF;
    }}
    .sim-btn.danger:hover {{
      background: #FEE2E2;
      color: #DC2626;
      border-color: #FECACA;
    }}
    .status-badge {{
      font-size: 10.5px;
      padding: 2.5px 8px;
      border-radius: 10px;
      background: #F1F5F9;
      color: #475569;
      font-weight: 600;
      border: 1px solid #E2E8F0;
    }}
    #phase-display {{
      color: #2563EB;
      font-weight: 700;
    }}
  </style>
</head>
<body>

<div id="sim-container">
  <canvas id="simCanvas"></canvas>

  <!-- HUD North -->
  <div class="hud-card north" id="hud-North">
    <div class="hud-title">
      <span>⬆ NORTH</span>
      <span class="hud-signal-pill signal-red" id="pill-North">RED 0s</span>
    </div>
    <div class="hud-row"><span>Demand:</span><span class="hud-val" id="dem-North">0 PCU/h</span></div>
    <div class="hud-row"><span>Approaching:</span><span class="hud-val" id="cnt-North">0 veh</span></div>
    <div class="hud-row"><span>Queued:</span><span class="hud-val" id="que-North">0 veh</span></div>
    <div class="hud-row"><span>Green Budget:</span><span class="hud-val" id="grn-North" style="color:#16A34A;">0s</span></div>
    <button class="hud-btn" onclick="spawnApproachVehicle('North')">+ Add Vehicle</button>
  </div>

  <!-- HUD East -->
  <div class="hud-card east" id="hud-East">
    <div class="hud-title">
      <span>➡ EAST</span>
      <span class="hud-signal-pill signal-red" id="pill-East">RED 0s</span>
    </div>
    <div class="hud-row"><span>Demand:</span><span class="hud-val" id="dem-East">0 PCU/h</span></div>
    <div class="hud-row"><span>Approaching:</span><span class="hud-val" id="cnt-East">0 veh</span></div>
    <div class="hud-row"><span>Queued:</span><span class="hud-val" id="que-East">0 veh</span></div>
    <div class="hud-row"><span>Green Budget:</span><span class="hud-val" id="grn-East" style="color:#8B5CF6;">0s</span></div>
    <button class="hud-btn" onclick="spawnApproachVehicle('East')">+ Add Vehicle</button>
  </div>

  <!-- HUD South -->
  <div class="hud-card south" id="hud-South">
    <div class="hud-title">
      <span>⬇ SOUTH</span>
      <span class="hud-signal-pill signal-red" id="pill-South">RED 0s</span>
    </div>
    <div class="hud-row"><span>Demand:</span><span class="hud-val" id="dem-South">0 PCU/h</span></div>
    <div class="hud-row"><span>Approaching:</span><span class="hud-val" id="cnt-South">0 veh</span></div>
    <div class="hud-row"><span>Queued:</span><span class="hud-val" id="que-South">0 veh</span></div>
    <div class="hud-row"><span>Green Budget:</span><span class="hud-val" id="grn-South" style="color:#0F766E;">0s</span></div>
    <button class="hud-btn" onclick="spawnApproachVehicle('South')">+ Add Vehicle</button>
  </div>

  <!-- HUD West -->
  <div class="hud-card west" id="hud-West">
    <div class="hud-title">
      <span>⬅ WEST</span>
      <span class="hud-signal-pill signal-red" id="pill-West">RED 0s</span>
    </div>
    <div class="hud-row"><span>Demand:</span><span class="hud-val" id="dem-West">0 PCU/h</span></div>
    <div class="hud-row"><span>Approaching:</span><span class="hud-val" id="cnt-West">0 veh</span></div>
    <div class="hud-row"><span>Queued:</span><span class="hud-val" id="que-West">0 veh</span></div>
    <div class="hud-row"><span>Green Budget:</span><span class="hud-val" id="grn-West" style="color:#16A34A;">0s</span></div>
    <button class="hud-btn" onclick="spawnApproachVehicle('West')">+ Add Vehicle</button>
  </div>

  <!-- Bottom Floating Control Bar -->
  <div id="control-bar">
    <button id="btn-toggle" class="sim-btn active" onclick="togglePlayPause()">
      <span id="btn-icon">⏸</span> <span id="btn-text">Pause</span>
    </button>
    <button class="sim-btn danger" onclick="resetSimulation()">
      <span>🔄</span> <span>Reset</span>
    </button>
    <button class="sim-btn" onclick="toggleSpeed()">
      <span id="speed-label">⚡ 1x</span>
    </button>
    <div class="status-badge">
      Phase: <span id="phase-display">NORTH GREEN</span>
    </div>
    <div class="status-badge">
      Cycle: <span id="cycle-timer">120s</span>
    </div>
  </div>
</div>

<script>
  const CONFIG = {config_json};

  const canvas = document.getElementById('simCanvas');
  const ctx = canvas.getContext('2d');

  let width = 960;
  let height = 520;

  function resizeCanvas() {{
    const container = document.getElementById('sim-container');
    width = container.clientWidth || 850;
    height = container.clientHeight || 520;
    canvas.width = width;
    canvas.height = height;
  }}
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  // Phase Sequence: North -> East -> South -> West
  const PHASES = ['North', 'East', 'South', 'West'];
  let currentPhaseIndex = 0;
  let phaseSubState = 'GREEN';
  let phaseTimer = CONFIG.timings['North'];
  let phaseTotal = CONFIG.timings['North'];
  let speedMultiplier = 1;
  let isRunning = CONFIG.is_running;

  // Restore simulation phase continuity across Streamlit reruns
  const STATE_KEY = 'trafficiq_sim_v2';
  try {{
    const saved = sessionStorage.getItem(STATE_KEY);
    if (saved) {{
      const parsed = JSON.parse(saved);
      if (typeof parsed.currentPhaseIndex === 'number' && parsed.currentPhaseIndex < PHASES.length) {{
        currentPhaseIndex = parsed.currentPhaseIndex;
        phaseSubState = parsed.phaseSubState || 'GREEN';
        const activeRoad = PHASES[currentPhaseIndex];
        const newTotal = (phaseSubState === 'GREEN') ? CONFIG.timings[activeRoad] :
                         ((phaseSubState === 'YELLOW') ? CONFIG.yellow_time : CONFIG.all_red_time);
        
        // Calculate remaining duration dynamically adapting to new timings
        const elapsed = (parsed.phaseTotal || newTotal) - (parsed.phaseTimer || newTotal);
        phaseTimer = Math.max(1, newTotal - Math.max(0, elapsed));
        phaseTotal = newTotal;
      }}
    }}
  }} catch (e) {{
    console.warn('SessionState restore bypassed:', e);
  }}

  // Signal states for all 4 roads
  let signalStates = {{
    North: 'RED',
    East: 'RED',
    South: 'RED',
    West: 'RED'
  }};

  let signalCountdowns = {{
    North: 0,
    East: 0,
    South: 0,
    West: 0
  }};

  // Simulation Vehicle counts
  let liveVehicles = {{ ...CONFIG.vehicle_counts }};

  // Vehicles on canvas
  const vehicles = [];
  const VEHICLE_COLORS = ['#1E3A8A', '#2563EB', '#3B82F6', '#0284C7', '#0F766E', '#16A34A', '#D97706', '#DC2626'];
  const VEHICLE_TYPES = ['car', 'suv', 'taxi', 'truck'];

  class Vehicle {{
    constructor(approach, lane = 0) {{
      this.approach = approach;
      this.lane = lane;
      this.type = VEHICLE_TYPES[Math.floor(Math.random() * VEHICLE_TYPES.length)];
      this.color = this.type === 'taxi' ? '#F59E0B' : VEHICLE_COLORS[Math.floor(Math.random() * VEHICLE_COLORS.length)];
      this.length = this.type === 'truck' ? 26 : (this.type === 'suv' ? 20 : 16);
      this.width = 10;
      this.speed = 0;
      this.maxSpeed = 2.2 + Math.random() * 0.7;
      this.accel = 0.08;
      this.decel = 0.15;
      this.hasCleared = false;
      this.isStopped = false;

      this.initPosition();
    }}

    initPosition() {{
      const cx = width / 2;
      const cy = height / 2;
      const roadW = 114;
      const laneW = roadW / 4;

      if (this.approach === 'North') {{
        this.x = cx - roadW/2 + laneW * (this.lane === 0 ? 0.6 : 1.6);
        this.y = -30 - Math.random() * 90;
        this.stopLine = cy - roadW/2 - 8;
        this.dirX = 0;
        this.dirY = 1;
      }} else if (this.approach === 'South') {{
        this.x = cx + roadW/2 - laneW * (this.lane === 0 ? 0.6 : 1.6);
        this.y = height + 30 + Math.random() * 90;
        this.stopLine = cy + roadW/2 + 8;
        this.dirX = 0;
        this.dirY = -1;
      }} else if (this.approach === 'East') {{
        this.x = width + 30 + Math.random() * 90;
        this.y = cy - roadW/2 + laneW * (this.lane === 0 ? 0.6 : 1.6);
        this.stopLine = cx + roadW/2 + 8;
        this.dirX = -1;
        this.dirY = 0;
      }} else if (this.approach === 'West') {{
        this.x = -30 - Math.random() * 90;
        this.y = cy + roadW/2 - laneW * (this.lane === 0 ? 0.6 : 1.6);
        this.stopLine = cx - roadW/2 - 8;
        this.dirX = 1;
        this.dirY = 0;
      }}
    }}

    update(leadingVehicle) {{
      const cx = width / 2;
      const cy = height / 2;
      const roadW = 114;

      let distToStop = 9999;
      const currentState = signalStates[this.approach];

      if (this.approach === 'North') {{
        if (this.y < this.stopLine) distToStop = this.stopLine - this.y;
      }} else if (this.approach === 'South') {{
        if (this.y > this.stopLine) distToStop = this.y - this.stopLine;
      }} else if (this.approach === 'East') {{
        if (this.x > this.stopLine) distToStop = this.x - this.stopLine;
      }} else if (this.approach === 'West') {{
        if (this.x < this.stopLine) distToStop = this.stopLine - this.x;
      }}

      let distToLead = 9999;
      if (leadingVehicle) {{
        if (this.approach === 'North') distToLead = leadingVehicle.y - this.y - this.length - 4;
        else if (this.approach === 'South') distToLead = this.y - leadingVehicle.y - this.length - 4;
        else if (this.approach === 'East') distToLead = this.x - leadingVehicle.x - this.length - 4;
        else if (this.approach === 'West') distToLead = leadingVehicle.x - this.x - this.length - 4;
      }}

      let shouldStop = false;
      if (currentState === 'RED') {{
        if (distToStop < 55 && distToStop > 0) shouldStop = true;
      }} else if (currentState === 'YELLOW') {{
        if (distToStop < 60 && distToStop > 25) shouldStop = true;
      }}
      if (distToLead < 16) {{
        shouldStop = true;
      }}

      if (shouldStop) {{
        this.speed = Math.max(0, this.speed - this.decel);
      }} else {{
        if (distToLead < 45) {{
          this.speed = Math.min(this.speed, leadingVehicle.speed);
        }} else {{
          this.speed = Math.min(this.maxSpeed, this.speed + this.accel);
        }}
      }}

      this.isStopped = (this.speed < 0.2 && distToStop < 280);

      this.x += this.dirX * this.speed * speedMultiplier;
      this.y += this.dirY * this.speed * speedMultiplier;

      if (!this.hasCleared) {{
        if (this.approach === 'North' && this.y > cy + roadW/2) this.hasCleared = true;
        if (this.approach === 'South' && this.y < cy - roadW/2) this.hasCleared = true;
        if (this.approach === 'East' && this.x < cx - roadW/2) this.hasCleared = true;
        if (this.approach === 'West' && this.x > cx + roadW/2) this.hasCleared = true;
      }}
    }}

    isOffScreen() {{
      return this.x < -100 || this.x > width + 100 || this.y < -100 || this.y > height + 100;
    }}

    draw(ctx) {{
      ctx.save();
      ctx.translate(this.x, this.y);

      let angle = 0;
      if (this.approach === 'North') angle = Math.PI / 2;
      else if (this.approach === 'South') angle = -Math.PI / 2;
      else if (this.approach === 'East') angle = Math.PI;
      else if (this.approach === 'West') angle = 0;

      ctx.rotate(angle);

      // Subtle vehicle ground shadow
      ctx.fillStyle = 'rgba(0,0,0,0.18)';
      ctx.beginPath();
      ctx.roundRect(-this.length/2 + 2, -this.width/2 + 2.5, this.length, this.width, 3);
      ctx.fill();

      // Vehicle metallic body
      ctx.fillStyle = this.color;
      ctx.beginPath();
      ctx.roundRect(-this.length/2, -this.width/2, this.length, this.width, 3);
      ctx.fill();

      // Cabin / windshield
      ctx.fillStyle = '#0F172A';
      ctx.beginPath();
      ctx.roundRect(-this.length/4, -this.width/2 + 2, this.length/2, this.width - 4, 2);
      ctx.fill();

      // Front headlights
      ctx.fillStyle = '#FEF08A';
      ctx.fillRect(this.length/2 - 2, -this.width/2 + 1, 2, 2);
      ctx.fillRect(this.length/2 - 2, this.width/2 - 3, 2, 2);

      // Rear brake lights
      ctx.fillStyle = (this.speed < 0.2) ? '#EF4444' : '#7F1D1D';
      ctx.fillRect(-this.length/2, -this.width/2 + 1, 2, 2);
      ctx.fillRect(-this.length/2, this.width/2 - 3, 2, 2);

      ctx.restore();
    }}
  }}

  function populateInitialVehicles() {{
    vehicles.length = 0;
    for (const road of PHASES) {{
      const targetCount = Math.min(16, Math.max(3, Math.floor(liveVehicles[road] / 3.2)));
      for (let i = 0; i < targetCount; i++) {{
        const lane = i % 2;
        const v = new Vehicle(road, lane);
        const dist = 70 + (i * 24 + 10);
        if (road === 'North') v.y = (height/2 - 57) - dist;
        else if (road === 'South') v.y = (height/2 + 57) + dist;
        else if (road === 'East') v.x = (width/2 + 57) + dist;
        else if (road === 'West') v.x = (width/2 - 57) - dist;
        vehicles.push(v);
      }}
    }}
  }}
  populateInitialVehicles();

  let spawnTicker = 0;
  function handleVehicleSpawning() {{
    spawnTicker++;
    if (spawnTicker % 35 === 0) {{
      for (const road of PHASES) {{
        const onScreen = vehicles.filter(v => v.approach === road && !v.hasCleared).length;
        const target = Math.min(22, Math.max(3, Math.floor(liveVehicles[road] / 2.8)));

        if (onScreen < target) {{
          const lane = Math.random() > 0.5 ? 1 : 0;
          // Verify entrance is not blocked before spawning
          const entranceClear = !vehicles.some(v => {{
            if (v.approach !== road || v.lane !== lane) return false;
            if (road === 'North') return v.y < 30;
            if (road === 'South') return v.y > height - 30;
            if (road === 'East') return v.x > width - 30;
            if (road === 'West') return v.x < 30;
            return false;
          }});

          if (entranceClear) {{
            vehicles.push(new Vehicle(road, lane));
          }}
        }}
      }}
    }}
  }}

  function spawnApproachVehicle(road) {{
    liveVehicles[road] = Math.min(100, liveVehicles[road] + 4);
    vehicles.push(new Vehicle(road, Math.random() > 0.5 ? 1 : 0));
    updateHUD();
  }}

  let lastTime = performance.now();
  let accumulatedTime = 0;

  function updateSignalController(dt) {{
    if (!isRunning) return;

    accumulatedTime += dt * speedMultiplier;

    if (accumulatedTime >= 1000) {{
      const secondsPassed = Math.floor(accumulatedTime / 1000);
      accumulatedTime %= 1000;
      phaseTimer = Math.max(0, phaseTimer - secondsPassed);

      if (phaseTimer <= 0) {{
        const activeRoad = PHASES[currentPhaseIndex];

        if (phaseSubState === 'GREEN') {{
          phaseSubState = 'YELLOW';
          phaseTimer = CONFIG.yellow_time;
          phaseTotal = CONFIG.yellow_time;
        }} else if (phaseSubState === 'YELLOW') {{
          phaseSubState = 'ALL_RED';
          phaseTimer = CONFIG.all_red_time;
          phaseTotal = CONFIG.all_red_time;
        }} else if (phaseSubState === 'ALL_RED') {{
          currentPhaseIndex = (currentPhaseIndex + 1) % PHASES.length;
          const nextRoad = PHASES[currentPhaseIndex];
          phaseSubState = 'GREEN';
          phaseTimer = CONFIG.timings[nextRoad];
          phaseTotal = CONFIG.timings[nextRoad];
        }}
      }}

      // Persist state to sessionStorage for seamless reloads
      try {{
        sessionStorage.setItem(STATE_KEY, JSON.stringify({{
          currentPhaseIndex: currentPhaseIndex,
          phaseSubState: phaseSubState,
          phaseTimer: phaseTimer,
          phaseTotal: phaseTotal,
          isRunning: isRunning
        }}));
      }} catch (e) {{}}
    }}

    const activeRoad = PHASES[currentPhaseIndex];

    for (let i = 0; i < PHASES.length; i++) {{
      const road = PHASES[i];
      if (road === activeRoad) {{
        signalStates[road] = phaseSubState;
        signalCountdowns[road] = phaseTimer;
      }} else {{
        signalStates[road] = 'RED';
        let wait = phaseTimer;
        if (phaseSubState === 'GREEN') wait += CONFIG.yellow_time + CONFIG.all_red_time;
        else if (phaseSubState === 'YELLOW') wait += CONFIG.all_red_time;

        let p = (currentPhaseIndex + 1) % PHASES.length;
        while (PHASES[p] !== road) {{
          wait += CONFIG.timings[PHASES[p]] + CONFIG.yellow_time + CONFIG.all_red_time;
          p = (p + 1) % PHASES.length;
        }}
        signalCountdowns[road] = wait;
      }}
    }}
  }}

  function drawIntersection() {{
    ctx.clearRect(0, 0, width, height);

    const cx = width / 2;
    const cy = height / 2;
    const roadW = 114;
    const laneW = roadW / 4;

    // Surrounding light pavement ground
    ctx.fillStyle = '#E2E8F0';
    ctx.fillRect(0, 0, width, height);

    // Curbs and sidewalk borders
    ctx.fillStyle = '#CBD5E1';
    ctx.fillRect(0, 0, cx - roadW/2, cy - roadW/2);
    ctx.fillRect(cx + roadW/2, 0, width - (cx + roadW/2), cy - roadW/2);
    ctx.fillRect(0, cy + roadW/2, cx - roadW/2, height - (cy + roadW/2));
    ctx.fillRect(cx + roadW/2, cy + roadW/2, width - (cx + roadW/2), height - (cy + roadW/2));

    // Inner ground pavement tile
    ctx.fillStyle = '#F1F5F9';
    ctx.fillRect(3, 3, cx - roadW/2 - 6, cy - roadW/2 - 6);
    ctx.fillRect(cx + roadW/2 + 3, 3, width - (cx + roadW/2) - 6, cy - roadW/2 - 6);
    ctx.fillRect(3, cy + roadW/2 + 3, cx - roadW/2 - 6, height - (cy + roadW/2) - 6);
    ctx.fillRect(cx + roadW/2 + 3, cy + roadW/2 + 3, width - (cx + roadW/2) - 6, height - (cy + roadW/2) - 6);

    // Dark slate asphalt roads
    ctx.fillStyle = '#334155';
    ctx.fillRect(cx - roadW/2, 0, roadW, height);
    ctx.fillRect(0, cy - roadW/2, width, roadW);

    // Central junction zone
    ctx.fillStyle = '#293548';
    ctx.fillRect(cx - roadW/2, cy - roadW/2, roadW, roadW);

    // Yellow center double dividers
    ctx.strokeStyle = '#F59E0B';
    ctx.lineWidth = 2;
    // North
    ctx.beginPath();
    ctx.moveTo(cx - 2, 0); ctx.lineTo(cx - 2, cy - roadW/2 - 22);
    ctx.moveTo(cx + 2, 0); ctx.lineTo(cx + 2, cy - roadW/2 - 22);
    // South
    ctx.moveTo(cx - 2, cy + roadW/2 + 22); ctx.lineTo(cx - 2, height);
    ctx.moveTo(cx + 2, cy + roadW/2 + 22); ctx.lineTo(cx + 2, height);
    // West
    ctx.moveTo(0, cy - 2); ctx.lineTo(cx - roadW/2 - 22, cy - 2);
    ctx.moveTo(0, cy + 2); ctx.lineTo(cx - roadW/2 - 22, cy + 2);
    // East
    ctx.moveTo(cx + roadW/2 + 22, cy - 2); ctx.lineTo(width, cy - 2);
    ctx.moveTo(cx + roadW/2 + 22, cy + 2); ctx.lineTo(width, cy + 2);
    ctx.stroke();

    // White dashed lane dividers
    ctx.strokeStyle = 'rgba(255,255,255,0.75)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([10, 8]);

    ctx.beginPath();
    ctx.moveTo(cx - laneW, 0); ctx.lineTo(cx - laneW, cy - roadW/2 - 22);
    ctx.moveTo(cx + laneW, 0); ctx.lineTo(cx + laneW, cy - roadW/2 - 22);
    ctx.moveTo(cx - laneW, cy + roadW/2 + 22); ctx.lineTo(cx - laneW, height);
    ctx.moveTo(cx + laneW, cy + roadW/2 + 22); ctx.lineTo(cx + laneW, height);
    ctx.moveTo(0, cy - laneW); ctx.lineTo(cx - roadW/2 - 22, cy - laneW);
    ctx.moveTo(0, cy + laneW); ctx.lineTo(cx - roadW/2 - 22, cy + laneW);
    ctx.moveTo(cx + roadW/2 + 22, cy - laneW); ctx.lineTo(width, cy - laneW);
    ctx.moveTo(cx + roadW/2 + 22, cy + laneW); ctx.lineTo(width, cy + laneW);
    ctx.stroke();
    ctx.setLineDash([]);

    // Stop Lines (Solid White)
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 3.5;
    ctx.beginPath(); ctx.moveTo(cx - roadW/2, cy - roadW/2 - 8); ctx.lineTo(cx, cy - roadW/2 - 8); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx, cy + roadW/2 + 8); ctx.lineTo(cx + roadW/2, cy + roadW/2 + 8); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx - roadW/2 - 8, cy); ctx.lineTo(cx - roadW/2 - 8, cy + roadW/2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx + roadW/2 + 8, cy - roadW/2); ctx.lineTo(cx + roadW/2 + 8, cy); ctx.stroke();

    // Zebra Crossings
    drawZebraCrossing(cx - roadW/2, cy - roadW/2 - 20, roadW, 10, true);
    drawZebraCrossing(cx - roadW/2, cy + roadW/2 + 10, roadW, 10, true);
    drawZebraCrossing(cx - roadW/2 - 20, cy - roadW/2, 10, roadW, false);
    drawZebraCrossing(cx + roadW/2 + 10, cy - roadW/2, 10, roadW, false);

    // Traffic Signal Heads
    drawSignalHead(cx - roadW/2 - 20, cy - roadW/2 - 42, signalStates.North, signalCountdowns.North, 'North');
    drawSignalHead(cx + roadW/2 + 6, cy - roadW/2 - 42, signalStates.East, signalCountdowns.East, 'East');
    drawSignalHead(cx + roadW/2 + 6, cy + roadW/2 + 10, signalStates.South, signalCountdowns.South, 'South');
    drawSignalHead(cx - roadW/2 - 20, cy + roadW/2 + 10, signalStates.West, signalCountdowns.West, 'West');
  }}

  function drawZebraCrossing(x, y, w, h, isHorizontal) {{
    ctx.fillStyle = '#FFFFFF';
    const stripes = 7;
    for (let i = 0; i < stripes; i++) {{
      if (isHorizontal) {{
        const sw = w / (stripes * 2 - 1);
        ctx.fillRect(x + i * sw * 2, y, sw, h);
      }} else {{
        const sh = h / (stripes * 2 - 1);
        ctx.fillRect(x, y + i * sh * 2, w, sh);
      }}
    }}
  }}

  function drawSignalHead(x, y, state, timerSec, road) {{
    // Signal Housing
    ctx.fillStyle = '#1E293B';
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.roundRect(x, y, 16, 40, 3);
    ctx.fill();
    ctx.stroke();

    const cx = x + 8;
    const r = 4;

    // Red Lamp
    const isRed = state === 'RED';
    ctx.fillStyle = isRed ? '#EF4444' : '#450A0A';
    ctx.beginPath(); ctx.arc(cx, y + 7, r, 0, Math.PI * 2); ctx.fill();

    // Yellow Lamp
    const isYellow = state === 'YELLOW';
    ctx.fillStyle = isYellow ? '#F59E0B' : '#451A03';
    ctx.beginPath(); ctx.arc(cx, y + 20, r, 0, Math.PI * 2); ctx.fill();

    // Green Lamp
    const isGreen = state === 'GREEN';
    ctx.fillStyle = isGreen ? '#22C55E' : '#052E16';
    ctx.beginPath(); ctx.arc(cx, y + 33, r, 0, Math.PI * 2); ctx.fill();

    // High-Contrast White Countdown Pill
    ctx.fillStyle = '#FFFFFF';
    ctx.strokeStyle = '#CBD5E1';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(x - 5, y - 16, 26, 13, 3);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = isGreen ? '#16A34A' : (isYellow ? '#D97706' : '#DC2626');
    ctx.font = 'bold 8.5px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(timerSec + 's', x + 8, y - 6);
  }}

  function updateHUD() {{
    for (const road of PHASES) {{
      const pill = document.getElementById('pill-' + road);
      const state = signalStates[road];
      const timer = signalCountdowns[road];

      pill.className = 'hud-signal-pill ' + (state === 'GREEN' ? 'signal-green' : (state === 'YELLOW' ? 'signal-yellow' : 'signal-red'));
      pill.textContent = state + ' ' + timer + 's';

      // Live queued vehicles on canvas
      const queuedCount = vehicles.filter(v => v.approach === road && !v.hasCleared && v.isStopped).length;
      const queueMeters = Math.round(queuedCount * 6.5);

      document.getElementById('cnt-' + road).textContent = liveVehicles[road] + ' veh';
      document.getElementById('que-' + road).textContent = queuedCount + ' veh (' + queueMeters + 'm)';
      document.getElementById('dem-' + road).textContent = Math.round(CONFIG.demands[road]) + ' PCU/h';
      document.getElementById('grn-' + road).textContent = CONFIG.timings[road] + 's';
    }}

    const activeRoad = PHASES[currentPhaseIndex];
    document.getElementById('phase-display').textContent = activeRoad.toUpperCase() + ' ' + phaseSubState;
    document.getElementById('phase-display').style.color = (phaseSubState === 'GREEN' ? '#16A34A' : (phaseSubState === 'YELLOW' ? '#D97706' : '#DC2626'));

    const totalCycle = CONFIG.timings.North + CONFIG.timings.East + CONFIG.timings.South + CONFIG.timings.West + (CONFIG.yellow_time + CONFIG.all_red_time) * 4;
    document.getElementById('cycle-timer').textContent = totalCycle + 's cycle';
  }}

  function animate(now) {{
    const dt = now - lastTime;
    lastTime = now;

    updateSignalController(dt);
    handleVehicleSpawning();

    drawIntersection();

    // Update vehicles independently per approach AND per lane to prevent cross-lane phantom queues
    for (const road of PHASES) {{
      for (let lane = 0; lane < 2; lane++) {{
        const laneVehicles = vehicles.filter(v => v.approach === road && v.lane === lane);
        if (road === 'North') laneVehicles.sort((a, b) => b.y - a.y);
        else if (road === 'South') laneVehicles.sort((a, b) => a.y - b.y);
        else if (road === 'East') laneVehicles.sort((a, b) => a.x - b.x);
        else if (road === 'West') laneVehicles.sort((a, b) => b.x - a.x);

        for (let i = 0; i < laneVehicles.length; i++) {{
          const lead = (i > 0) ? laneVehicles[i - 1] : null;
          laneVehicles[i].update(lead);
        }}
      }}
    }}

    for (let i = vehicles.length - 1; i >= 0; i--) {{
      const v = vehicles[i];
      v.draw(ctx);
      if (v.isOffScreen()) {{
        vehicles.splice(i, 1);
      }}
    }}

    updateHUD();
    requestAnimationFrame(animate);
  }}
  requestAnimationFrame(animate);

  function togglePlayPause() {{
    isRunning = !isRunning;
    const btn = document.getElementById('btn-toggle');
    const icon = document.getElementById('btn-icon');
    const text = document.getElementById('btn-text');

    if (isRunning) {{
      btn.className = 'sim-btn active';
      icon.textContent = '⏸';
      text.textContent = 'Pause';
    }} else {{
      btn.className = 'sim-btn';
      icon.textContent = '▶';
      text.textContent = 'Resume';
    }}
  }}

  function resetSimulation() {{
    try {{
      sessionStorage.removeItem(STATE_KEY);
    }} catch (e) {{}}
    liveVehicles = {{ ...CONFIG.vehicle_counts }};
    currentPhaseIndex = 0;
    phaseSubState = 'GREEN';
    phaseTimer = CONFIG.timings['North'];
    phaseTotal = CONFIG.timings['North'];
    accumulatedTime = 0;
    populateInitialVehicles();
    updateHUD();
  }}

  function toggleSpeed() {{
    if (speedMultiplier === 1) speedMultiplier = 2;
    else if (speedMultiplier === 2) speedMultiplier = 4;
    else speedMultiplier = 1;
    document.getElementById('speed-label').textContent = '⚡ ' + speedMultiplier + 'x';
  }}
</script>

</body>
</html>
    """
    return html_code
