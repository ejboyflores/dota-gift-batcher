import io
import json
import re
from openpyxl.styles import Font, PatternFill
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dota 2 Gift Studio", page_icon="🎁", layout="wide")

# --- EXPERT UI/UX STYLING OVERHAUL ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1450px; }
    
    /* Global Typography & Polish */
    h1, h2, h3 { font-family: system-ui, -apple-system, sans-serif; letter-spacing: -0.3px; }
    
    /* Custom Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #0b0f19; padding: 6px; border-radius: 12px; border: 1px solid #1e293b; }
    .stTabs [data-baseweb="tab"] {
        height: 46px;
        padding: 0px 22px;
        border-radius: 8px;
        font-weight: 700;
        color: #94a3b8;
        background-color: transparent;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    /* Modern Card Containers */
    .studio-card {
        background: linear-gradient(145deg, #0f172a, #162032);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        margin-bottom: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎁 Paul's Dota 2 Giveaway & Gifting Studio")

default_text = """Trove of Terror

Joseph Estobo - 1
Julius Durango - 1
Ren Ren - 2
Mark louie - 1
Adrian Libres - 1
Eijie Agodera - 1
Mardion Lloyd - 1
Jayson Eunchica - 1
Prince May - 2
Xyr john - 1
Ejboy flores - 1
Edgardo Jr - 1
Chito Dagreat - 2
Ariel Marquez - 1
Carl Villanueva - 1
Paul Panganoron - 1"""

if "notepad_queue" not in st.session_state:
    st.session_state.notepad_queue = default_text

default_wheel_names = """Adrian Libres
Joseph Estobo
Julius Durango
Ren Ren
Mark louie
Eijie Agodera
Mardion Lloyd
Jayson Eunchica
Prince May
Xyr john
Ejboy flores
Edgardo Jr
Chito Dagreat
Ariel Marquez
Carl Villanueva
Paul Panganoron"""

main_tab_batcher, main_tab_wheel, main_tab_lms = st.tabs([
    "📦 1. Post-Stream Gift Batcher",
    "🎡 2. Normal Spin the Wheel",
    "👑 3. Last Man Standing (Main Event)"
])

# ==============================================================================
# TAB 3: LAST MAN STANDING
# ==============================================================================
with main_tab_lms:
    lms_left, lms_right = st.columns([1, 1.65], gap="large")

    with lms_left:
        st.subheader("👑 Main Event Setup")
        arcana_prize = st.text_input("Grand Prize Name (Shown on Banner):", value="Item Name", key="lms_arcana_input")
        lms_raw = st.text_area("Paste Finalists / Participants (1 per line):", value=default_wheel_names, height=320, key="lms_names_input")
        lms_participants = [p.strip() for p in lms_raw.split("\n") if p.strip()]
        st.caption(f"⚔️ Total Fighters Entering Arena: **{len(lms_participants)}** *(Every spin ELIMINATES 1 person until only 1 Champion remains!)*")

    with lms_right:
        lms_json = json.dumps(lms_participants if len(lms_participants) >= 2 else ["Player 1", "Player 2"])
        
        lms_html = f"""
        <div id="lmsFullscreenContainer" style="background: linear-gradient(145deg, #1a0b0e, #2a1215); padding: 18px; border-radius: 16px; border: 2px solid #b91c1c; color: white; font-family: system-ui, -apple-system, sans-serif; box-shadow: 0 12px 30px rgba(185,28,28,0.25);">
            
            <div style="display: flex; justify-content: space-between; align-items: center; background: #0f0507; padding: 10px 16px; border-radius: 10px; border: 1px solid #7f1d1d; margin-bottom: 12px;">
                <div>
                    <div style="font-size: 11px; color: #fca5a5; text-transform: uppercase; font-weight: 800; letter-spacing: 1px;">🔥 LAST MAN STANDING — GRAND PRIZE:</div>
                    <div style="font-size: 18px; font-weight: 900; color: #fde047;">🏆 {arcana_prize}</div>
                </div>
                <div style="display: flex; gap: 12px; align-items: center;">
                    <div style="text-align: right;">
                        <div style="font-size: 10px; color: #94a3b8; font-weight: bold;">ALIVE</div>
                        <div id="alive_counter" style="font-size: 20px; font-weight: 900; color: #4ade80;">{len(lms_participants)}</div>
                    </div>
                    <button onclick="toggleFullscreen('lmsFullscreenContainer')" style="background: #334155; color: white; border: 1px solid #64748b; padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer;" title="Toggle Fullscreen">⛶ Fullscreen</button>
                </div>
            </div>

            <div id="lms_banner" style="width: 100%; text-align: center; background: #450a0a; padding: 10px; border-radius: 8px; font-size: 18px; font-weight: 900; color: #fef08a; margin-bottom: 14px; border: 1px solid #dc2626; box-sizing: border-box;">
                💀 Whoever the arrow lands on is ELIMINATED!
            </div>

            <div style="display: flex; gap: 18px; align-items: center; justify-content: center; flex-wrap: wrap;">
                <div style="position: relative; width: 320px; height: 320px;">
                    <div style="position: absolute; right: -16px; top: 50%; transform: translateY(-50%); width: 0; height: 0; border-top: 15px solid transparent; border-bottom: 15px solid transparent; border-right: 28px solid #fde047; z-index: 10; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.8));"></div>
                    <canvas id="lmsCanvas" width="320" height="320"></canvas>
                </div>

                <div style="flex: 1; min-width: 210px; height: 310px; background: #0f0507; border: 1px solid #451a1c; border-radius: 10px; padding: 10px 12px; display: flex; flex-direction: column;">
                    <div style="font-size: 12px; font-weight: 800; color: #f87171; text-transform: uppercase; border-bottom: 1px solid #3f1517; padding-bottom: 6px; margin-bottom: 8px;">
                        🪦 Eliminated Graveyard
                    </div>
                    <div id="graveyard_list" style="flex: 1; overflow-y: auto; font-size: 13px; color: #cbd5e1; display: flex; flex-direction: column; gap: 5px;">
                        <div style="color: #64748b; font-style: italic; font-size: 12px;">No eliminations yet...</div>
                    </div>
                </div>
            </div>

            <div style="font-size: 11px; color: #fca5a5; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 700; text-align: center; margin-top: 14px; margin-bottom: 8px;">
                Spin to Eliminate 1 Player (Or Run Auto-Battle Royale!):
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;">
                <button onclick="spinEliminate(3)" style="background: #dc2626; color: white; border: none; padding: 10px 14px; border-radius: 8px; font-size: 13px; font-weight: 800; cursor: pointer;">💀 3s Fast KO</button>
                <button onclick="spinEliminate(8)" style="background: #ea580c; color: white; border: none; padding: 10px 14px; border-radius: 8px; font-size: 13px; font-weight: 800; cursor: pointer;">🔥 8s KO Spin</button>
                <button onclick="spinEliminate(20)" style="background: #eab308; color: #0f172a; border: none; padding: 10px 16px; border-radius: 8px; font-size: 13px; font-weight: 900; cursor: pointer;">⏱️ 20s Suspense KO</button>
                <button onclick="toggleAutoRoyale()" id="autoBtn" style="background: linear-gradient(90deg, #9333ea, #db2777); color: white; border: 1px solid #f472b6; padding: 10px 16px; border-radius: 8px; font-size: 13px; font-weight: 900; cursor: pointer; box-shadow: 0 4px 12px rgba(219,39,119,0.4);">⚡ AUTO-BATTLE ROYALE (3s/KO)</button>
                <button onclick="resetArena()" style="background: #334155; color: white; border: none; padding: 10px 12px; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer;">🔄 Reset All</button>
            </div>
        </div>

        <script>
        const initialPlayers = {lms_json};
        let alive = [...initialPlayers];
        let graveyard = [];
        const lmsColors = ["#dc2626", "#2563eb", "#16a34a", "#d97706", "#7c3aed", "#db2777", "#0891b2", "#4d7c0f"];
        
        const canvas = document.getElementById("lmsCanvas");
        const ctx = canvas.getContext("2d");
        let currentAngle = 0;
        let isSpinning = false;
        let autoMode = false;
        let animId = null;
        let autoTimeout = null;
        let audioCtx = null;

        function toggleFullscreen(elementId) {{
            const elem = document.getElementById(elementId);
            if (!document.fullscreenElement) {{
                if (elem.requestFullscreen) {{ elem.requestFullscreen(); }}
                else if (elem.webkitRequestFullscreen) {{ elem.webkitRequestFullscreen(); }}
            }} else {{
                if (document.exitFullscreen) {{ document.exitFullscreen(); }}
            }}
        }}

        function getAudio() {{
            if (!audioCtx) {{
                const AC = window.AudioContext || window.webkitAudioContext;
                audioCtx = new AC();
            }}
            if (audioCtx.state === 'suspended') audioCtx.resume();
            return audioCtx;
        }}

        function playSound(freq, dur, type="sine", vol=0.1) {{
            try {{
                const ac = getAudio();
                const osc = ac.createOscillator();
                const gain = ac.createGain();
                osc.type = type;
                osc.frequency.value = freq;
                gain.gain.value = vol;
                osc.connect(gain);
                gain.connect(ac.destination);
                osc.start();
                osc.stop(ac.currentTime + dur / 1000);
            }} catch(e) {{}}
        }}

        function drawLmsWheel() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const num = alive.length;
            const center = canvas.width / 2;
            const radius = center - 6;

            if (num === 1) {{
                ctx.beginPath();
                ctx.fillStyle = "#eab308";
                ctx.arc(center, center, radius, 0, 2 * Math.PI);
                ctx.fill();
                ctx.strokeStyle = "#fef08a";
                ctx.lineWidth = 5;
                ctx.stroke();

                ctx.fillStyle = "#0f172a";
                ctx.font = "900 22px sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("👑 CHAMPION 👑", center, center - 12);
                ctx.font = "900 26px sans-serif";
                ctx.fillText(alive[0], center, center + 24);
                return;
            }}

            const arc = (2 * Math.PI) / num;
            for (let i = 0; i < num; i++) {{
                const angle = currentAngle + i * arc;
                ctx.beginPath();
                ctx.fillStyle = lmsColors[i % lmsColors.length];
                ctx.moveTo(center, center);
                ctx.arc(center, center, radius, angle, angle + arc);
                ctx.lineTo(center, center);
                ctx.fill();
                ctx.strokeStyle = "#1a0b0e";
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.save();
                ctx.translate(center, center);
                ctx.rotate(angle + arc / 2);
                ctx.textAlign = "right";
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 13px sans-serif";
                let label = alive[i].length > 16 ? alive[i].substring(0, 14) + ".." : alive[i];
                ctx.fillText(label, radius - 14, 5);
                ctx.restore();
            }}

            ctx.beginPath();
            ctx.fillStyle = "#0f0507";
            ctx.arc(center, center, 22, 0, 2 * Math.PI);
            ctx.fill();
            ctx.strokeStyle = "#fde047";
            ctx.lineWidth = 3;
            ctx.stroke();
        }}

        function updateGraveyardUI() {{
            document.getElementById("alive_counter").innerText = alive.length;
            const listEl = document.getElementById("graveyard_list");
            if (graveyard.length === 0) {{
                listEl.innerHTML = '<div style="color: #64748b; font-style: italic; font-size: 12px;">No eliminations yet...</div>';
                return;
            }}
            listEl.innerHTML = graveyard.map(item => 
                `<div style="background: #1f090d; padding: 5px 8px; border-radius: 5px; border-left: 3px solid #ef4444; display: flex; justify-content: space-between;">
                    <span style="text-decoration: line-through; color: #fca5a5;">💀 ${{item.name}}</span>
                    <span style="color: #94a3b8; font-size: 11px; font-weight: bold;">#${{item.rank}}</span>
                </div>`
            ).join("");
        }}

        function spinEliminate(seconds) {{
            if (isSpinning || alive.length <= 1) return;
            isSpinning = true;

            const actualSec = (alive.length === 2 && seconds < 8) ? 6 : seconds;
            const duration = actualSec * 1000;
            const baseRotations = actualSec * 2.3 + Math.random() * 4;
            const spinRotations = baseRotations * 2 * Math.PI;
            const startAngle = currentAngle;
            const startTime = performance.now();
            let lastSlice = -1;

            const banner = document.getElementById("lms_banner");
            banner.style.color = "#fef08a";

            function animate(now) {{
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeOut = 1 - Math.pow(1 - progress, 4);
                currentAngle = startAngle + spinRotations * easeOut;
                drawLmsWheel();

                const arc = (2 * Math.PI) / alive.length;
                const normAngle = (2 * Math.PI - (currentAngle % (2 * Math.PI))) % (2 * Math.PI);
                const currentSlice = Math.floor(normAngle / arc) % alive.length;

                banner.innerText = "🎯 In Danger: " + alive[currentSlice] + "...";

                if (currentSlice !== lastSlice && progress < 0.995) {{
                    playSound(480, 20, "triangle", 0.08);
                    lastSlice = currentSlice;
                }}

                if (progress < 1) {{
                    animId = requestAnimationFrame(animate);
                }} else {{
                    isSpinning = false;
                    const eliminatedName = alive[currentSlice];
                    const finishRank = alive.length;

                    alive.splice(currentSlice, 1);
                    graveyard.unshift({{ name: eliminatedName, rank: finishRank }});
                    updateGraveyardUI();
                    drawLmsWheel();

                    if (alive.length === 1) {{
                        autoMode = false;
                        document.getElementById("autoBtn").innerText = "⚡ AUTO-BATTLE ROYALE (3s/KO)";
                        banner.style.background = "#14532d";
                        banner.style.borderColor = "#4ade80";
                        banner.style.color = "#fde047";
                        banner.innerText = "👑 LAST MAN STANDING: " + alive[0] + " WINS THE ARCANA! 🎉";
                        playSound(523, 150, "sine", 0.15);
                        setTimeout(() => playSound(659, 150, "sine", 0.15), 160);
                        setTimeout(() => playSound(784, 150, "sine", 0.15), 320);
                        setTimeout(() => playSound(1046, 450, "sine", 0.2), 480);
                    }} else {{
                        banner.style.color = "#f87171";
                        banner.innerText = "💀 ELIMINATED: " + eliminatedName + " (#" + finishRank + " Place) — " + alive.length + " Left!";
                        playSound(190, 300, "sawtooth", 0.12);

                        if (autoMode && alive.length > 1) {{
                            autoTimeout = setTimeout(() => {{
                                if (autoMode) spinEliminate(3);
                            }}, 2200);
                        }}
                    }}
                }}
            }}
            animId = requestAnimationFrame(animate);
        }}

        function toggleAutoRoyale() {{
            if (alive.length <= 1) return;
            autoMode = !autoMode;
            const btn = document.getElementById("autoBtn");
            if (autoMode) {{
                btn.innerText = "⏸ PAUSE AUTO-ROYALE";
                btn.style.background = "#dc2626";
                if (!isSpinning) spinEliminate(3);
            }} else {{
                btn.innerText = "⚡ AUTO-BATTLE ROYALE (3s/KO)";
                btn.style.background = "linear-gradient(90deg, #9333ea, #db2777)";
                if (autoTimeout) clearTimeout(autoTimeout);
            }}
        }}

        function resetArena() {{
            if (animId) cancelAnimationFrame(animId);
            if (autoTimeout) clearTimeout(autoTimeout);
            isSpinning = false;
            autoMode = false;
            alive = [...initialPlayers];
            graveyard = [];
            document.getElementById("autoBtn").innerText = "⚡ AUTO-BATTLE ROYALE (3s/KO)";
            document.getElementById("autoBtn").style.background = "linear-gradient(90deg, #9333ea, #db2777)";
            const banner = document.getElementById("lms_banner");
            banner.style.background = "#450a0a";
            banner.style.borderColor = "#dc2626";
            banner.style.color = "#fef08a";
            banner.innerText = "💀 Arena Reset! Whoever the arrow lands on is ELIMINATED!";
            updateGraveyardUI();
            drawLmsWheel();
        }}

        drawLmsWheel();
        </script>
        """
        components.html(lms_html, height=555)

# ==============================================================================
# TAB 2: NORMAL LIVE STREAM SPIN THE WHEEL
# ==============================================================================
with main_tab_wheel:
    w_left, w_right = st.columns([1, 1.55], gap="large")

    with w_left:
        st.subheader("👥 Wheel Participants")
        wheel_raw = st.text_area("Paste viewer names here (1 name per line):", value=default_wheel_names, height=360, key="normal_wheel_input")
        participants = [p.strip() for p in wheel_raw.split("\n") if p.strip()]
        st.caption(f"🎯 Total viewers on wheel: **{len(participants)}**")

    with w_right:
        names_json = json.dumps(participants if participants else ["Add Names"])
        wheel_html = f"""
        <div id="normalFullscreenContainer" style="background: linear-gradient(145deg, #0f172a, #1e293b); padding: 20px; border-radius: 16px; border: 1px solid #334155; color: white; font-family: system-ui, -apple-system, sans-serif; display: flex; flex-direction: column; align-items: center; box-shadow: 0 10px 25px rgba(0,0,0,0.4);">
            
            <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; background: #090d16; padding: 10px 18px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 14px; box-sizing: border-box;">
                <div id="winner_banner" style="font-size: 18px; font-weight: 800; color: #facc15;">
                    🎰 Select spin duration below!
                </div>
                <div style="display: flex; gap: 12px; align-items: center;">
                    <div id="spin_timer" style="font-size: 18px; font-weight: 900; color: #38bdf8; font-variant-numeric: tabular-nums; background: #1e293b; padding: 4px 10px; border-radius: 6px;">
                        00:00
                    </div>
                    <button onclick="toggleFullscreen('normalFullscreenContainer')" style="background: #334155; color: white; border: 1px solid #64748b; padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer;" title="Toggle Fullscreen">⛶ Fullscreen</button>
                </div>
            </div>

            <div style="position: relative; width: 350px; height: 350px; margin: 4px 0;">
                <div style="position: absolute; right: -16px; top: 50%; transform: translateY(-50%); width: 0; height: 0; border-top: 16px solid transparent; border-bottom: 16px solid transparent; border-right: 30px solid #ef4444; z-index: 10; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.6));"></div>
                <canvas id="wheelCanvas" width="350" height="350"></canvas>
            </div>

            <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 700; margin-top: 12px; margin-bottom: 8px;">
                Choose Spin Duration:
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;">
                <button onclick="spinWheel(5)" style="background: #3b82f6; color: white; border: none; padding: 10px 16px; border-radius: 8px; font-size: 14px; font-weight: 800; cursor: pointer;">⚡ 5s Quick</button>
                <button onclick="spinWheel(15)" style="background: #10b981; color: white; border: none; padding: 10px 16px; border-radius: 8px; font-size: 14px; font-weight: 800; cursor: pointer;">🔥 15s Spin</button>
                <button onclick="spinWheel(30)" style="background: #f59e0b; color: #0f172a; border: none; padding: 10px 18px; border-radius: 8px; font-size: 14px; font-weight: 900; cursor: pointer; box-shadow: 0 4px 10px rgba(245,158,11,0.3);">⏱️ 30 Sec Spin</button>
                <button onclick="spinWheel(60)" style="background: #ef4444; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-size: 14px; font-weight: 900; cursor: pointer; box-shadow: 0 4px 10px rgba(239,68,68,0.3);">🚨 1 Min Spin (60s)</button>
                <button onclick="stopAndReset()" style="background: #475569; color: white; border: none; padding: 10px 12px; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer;">⏹ Stop</button>
            </div>

            <div style="margin-top: 10px; min-height: 36px; display: flex; gap: 10px; align-items: center;">
                <button onclick="removeLastWinner()" id="removeBtn" style="background: #334155; color: #f8fafc; border: 1px solid #64748b; padding: 7px 14px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer; display: none;">
                    ❌ Remove Winner from Wheel
                </button>
            </div>
        </div>

        <script>
        let names = {names_json};
        const colors = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"];
        const canvas = document.getElementById("wheelCanvas");
        const ctx = canvas.getContext("2d");
        let currentAngle = 0;
        let isSpinning = false;
        let animId = null;
        let lastWinnerIndex = -1;
        let sharedAudioCtx = null;

        function toggleFullscreen(elementId) {{
            const elem = document.getElementById(elementId);
            if (!document.fullscreenElement) {{
                if (elem.requestFullscreen) {{ elem.requestFullscreen(); }}
                else if (elem.webkitRequestFullscreen) {{ elem.webkitRequestFullscreen(); }}
            }} else {{
                if (document.exitFullscreen) {{ document.exitFullscreen(); }}
            }}
        }}

        function getAudioCtx() {{
            if (!sharedAudioCtx) {{
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                sharedAudioCtx = new AudioContext();
            }}
            if (sharedAudioCtx.state === 'suspended') {{
                sharedAudioCtx.resume();
            }}
            return sharedAudioCtx;
        }}

        function playTick(freq, dur) {{
            try {{
                const audioCtx = getAudioCtx();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.frequency.value = freq;
                gain.gain.value = 0.08;
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + dur / 1000);
            }} catch(e) {{}}
        }}

        function drawWheel() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const num = names.length;
            const arc = (2 * Math.PI) / num;
            const center = canvas.width / 2;
            const radius = center - 8;

            for (let i = 0; i < num; i++) {{
                const angle = currentAngle + i * arc;
                ctx.beginPath();
                ctx.fillStyle = colors[i % colors.length];
                ctx.moveTo(center, center);
                ctx.arc(center, center, radius, angle, angle + arc);
                ctx.lineTo(center, center);
                ctx.fill();
                ctx.strokeStyle = "#0f172a";
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.save();
                ctx.translate(center, center);
                ctx.rotate(angle + arc / 2);
                ctx.textAlign = "right";
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 13px sans-serif";
                let label = names[i].length > 17 ? names[i].substring(0, 15) + ".." : names[i];
                ctx.fillText(label, radius - 14, 5);
                ctx.restore();
            }}

            ctx.beginPath();
            ctx.fillStyle = "#0f172a";
            ctx.arc(center, center, 24, 0, 2 * Math.PI);
            ctx.fill();
            ctx.strokeStyle = "#f8fafc";
            ctx.lineWidth = 3;
            ctx.stroke();
        }}

        function formatTime(sec) {{
            const m = String(Math.floor(sec / 60)).padStart(2, '0');
            const s = String(Math.ceil(sec % 60)).padStart(2, '0');
            return m + ":" + s;
        }}

        function spinWheel(seconds) {{
            if (isSpinning || names.length === 0) return;
            isSpinning = true;
            document.getElementById("removeBtn").style.display = "none";
            document.getElementById("winner_banner").style.color = "#38bdf8";

            const duration = seconds * 1000;
            const baseRotations = seconds * 2.2 + Math.random() * 4;
            const spinRotations = baseRotations * 2 * Math.PI;
            const startAngle = currentAngle;
            const startTime = performance.now();
            let lastSlice = -1;

            function animate(now) {{
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const remainingSec = Math.max(0, (duration - elapsed) / 1000);

                document.getElementById("spin_timer").innerText = formatTime(remainingSec);

                const easeOut = 1 - Math.pow(1 - progress, 4);
                currentAngle = startAngle + spinRotations * easeOut;
                drawWheel();

                const arc = (2 * Math.PI) / names.length;
                const normalizedAngle = (2 * Math.PI - (currentAngle % (2 * Math.PI))) % (2 * Math.PI);
                const currentSlice = Math.floor(normalizedAngle / arc) % names.length;

                document.getElementById("winner_banner").innerText = "👉 " + names[currentSlice];

                if (currentSlice !== lastSlice && progress < 0.995) {{
                    playTick(540, 20);
                    lastSlice = currentSlice;
                }}

                if (progress < 1) {{
                    animId = requestAnimationFrame(animate);
                }} else {{
                    isSpinning = false;
                    document.getElementById("spin_timer").innerText = "00:00";
                    lastWinnerIndex = currentSlice;
                    const winner = names[lastWinnerIndex];
                    document.getElementById("winner_banner").style.color = "#4ade80";
                    document.getElementById("winner_banner").innerText = "🎉 WINNER: " + winner + "!";
                    if (names.length > 1) {{
                        document.getElementById("removeBtn").style.display = "inline-block";
                    }}
                    playTick(587, 120);
                    setTimeout(() => playTick(880, 350), 150);
                }}
            }}
            animId = requestAnimationFrame(animate);
        }}

        function stopAndReset() {{
            if (animId) cancelAnimationFrame(animId);
            isSpinning = false;
            document.getElementById("spin_timer").innerText = "00:00";
            document.getElementById("winner_banner").style.color = "#facc15";
            document.getElementById("winner_banner").innerText = "⏹ Spin stopped. Ready!";
        }}

        function removeLastWinner() {{
            if (lastWinnerIndex > -1 && names.length > 1) {{
                names.splice(lastWinnerIndex, 1);
                lastWinnerIndex = -1;
                document.getElementById("removeBtn").style.display = "none";
                document.getElementById("winner_banner").innerText = "✅ Winner removed from wheel!";
                drawWheel();
            }}
        }}

        drawWheel();
        </script>
        """
        components.html(wheel_html, height=540)

# ==============================================================================
# TAB 1: POST-STREAM GIFT BATCHER
# ==============================================================================
with main_tab_batcher:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border-left: 4px solid #3b82f6; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px; color: #e2e8f0; font-size: 14px;">
            <b>💡 QUICK STREAM GUIDE:</b> 
            &nbsp;1️⃣ Paste Notepad List &nbsp;→&nbsp; 
            2️⃣ Run Call-Out Timer & Check Attendance &nbsp;→&nbsp; 
            3️⃣ Gift Batch 1 & Save Tomorrow's Backup!
        </div>
    """, unsafe_allow_html=True)

    with st.expander("📝 STEP 1: Paste Your Notepad List & Settings", expanded=True):
        c1, c2 = st.columns([2.5, 1.5])
        with c1:
            raw_input = st.text_area("Copy and paste your entire Notepad file here (`Name - 1`):", key="notepad_queue", height=160)
        with c2:
            default_treasure = st.text_input("Treasure / Event Name", value="Trove of Terror")
            max_gifts = st.number_input("Steam Daily Gift Limit (Max 8)", min_value=1, max_value=20, value=8)
            split_multi_to_bottom = st.checkbox("✅ Fair Queue Mode: Split '- 2' into separate turns", value=True, help="Gives 1 skin now and moves extra wins to the bottom of the line so nobody cuts the queue.")

    def parse_fair_queue(text, fallback_title, split_extras_to_bottom):
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        detected_title = fallback_title
        first_pass = []
        extra_wins_bottom = []

        for idx, line in enumerate(lines):
            match = re.match(r"^(.*?)\s*-\s*(\d+)(?:\s*-\s*(.+))?$", line)
            if match:
                name = match.group(1).strip()
                qty = int(match.group(2))
                skin = match.group(3).strip() if match.group(3) else ""

                if split_extras_to_bottom and qty > 1:
                    first_pass.append({"Name": name, "Qty": 1, "Skin": skin})
                    for _ in range(qty - 1):
                        extra_wins_bottom.append({"Name": name, "Qty": 1, "Skin": skin})
                else:
                    first_pass.append({"Name": name, "Qty": qty, "Skin": skin})
            elif idx == 0 and not re.search(r"\d", line):
                detected_title = line

        all_entries = first_pass + extra_wins_bottom
        rows = []
        win_counts = {}
        for order_idx, item in enumerate(all_entries, 1):
            name_key = item["Name"].lower()
            win_counts[name_key] = win_counts.get(name_key, 0) + 1
            win_num = win_counts[name_key]
            win_label = "1st Win" if win_num == 1 else f"🔁 #{win_num} Win"

            rows.append({
                "#": order_idx,
                "Here?": True,
                "Viewer Name": item["Name"],
                "Qty": item["Qty"],
                "Turn / Win #": win_label,
                "Skin Choice": item["Skin"]
            })

        return pd.DataFrame(rows), detected_title

    base_df, final_title = parse_fair_queue(raw_input, default_treasure, split_multi_to_bottom)

    left_col, right_col = st.columns([1.15, 1.35], gap="large")

    with left_col:
        st.subheader("🙋‍♂️ STEP 2: Chat Roll-Call")

        timer_html = """
        <div style="background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 12px 18px; color: white; font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">⏱️ Call-Out Timer</div>
                <div id="display" style="font-size: 26px; font-weight: 900; color: #4ade80; font-variant-numeric: tabular-nums;">01:00</div>
                <div id="status_text" style="font-size: 11px; color: #cbd5e1;">Ready for next viewer call-out</div>
            </div>
            <div style="display: flex; gap: 6px;">
                <button onclick="startTimer(30)" style="background: #2563eb; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 12px;">▶ 30s</button>
                <button onclick="startTimer(60)" style="background: #16a34a; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 12px;">▶ 1 Min</button>
                <button onclick="resetTimer()" style="background: #475569; color: white; border: none; padding: 8px 10px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 12px;">⏹</button>
            </div>
        </div>
        <script>
        let countdown;
        function playBeep(freq, duration) {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.frequency.value = freq;
                gain.gain.value = 0.1;
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                setTimeout(() => { osc.stop(); ctx.close(); }, duration);
            } catch(e) {}
        }
        function startTimer(seconds) {
            clearInterval(countdown);
            let remaining = seconds;
            updateUI(remaining);
            document.getElementById('status_text').innerText = "⏳ Waiting for chat reply...";
            countdown = setInterval(() => {
                remaining--;
                if (remaining <= 0) {
                    clearInterval(countdown);
                    const disp = document.getElementById('display');
                    disp.innerText = "00:00 - AFK!";
                    disp.style.color = "#ef4444";
                    document.getElementById('status_text').innerText = "❌ Uncheck 'Here?' below!";
                    playBeep(440, 200);
                    setTimeout(() => playBeep(330, 350), 220);
                } else {
                    updateUI(remaining);
                    if (remaining <= 5) playBeep(600, 70);
                }
            }, 1000);
        }
        function resetTimer() {
            clearInterval(countdown);
            const disp = document.getElementById('display');
            disp.innerText = "01:00";
            disp.style.color = "#4ade80";
            document.getElementById('status_text').innerText = "Ready for next viewer!";
        }
        function updateUI(sec) {
            const mins = String(Math.floor(sec / 60)).padStart(2, '0');
            const secs = String(sec % 60).padStart(2, '0');
            const disp = document.getElementById('display');
            disp.innerText = mins + ":" + secs;
            disp.style.color = sec <= 10 ? "#facc15" : "#4ade80";
        }
        </script>
        """
        components.html(timer_html, height=95)

        st.markdown("<p style='font-size: 13px; color: #94a3b8; margin-top: 8px;'>Uncheck <b>Here?</b> if they are absent (they move to #1 tomorrow). Double-click <b>Skin Choice</b> to type their custom hero skin!</p>", unsafe_allow_html=True)

        if not base_df.empty:
            rollcall_df = st.data_editor(
                base_df,
                hide_index=True,
                use_container_width=True,
                height=420,
                disabled=["#", "Viewer Name", "Turn / Win #"],
                column_config={
                    "#": st.column_config.NumberColumn("#", width="small"),
                    "Here?": st.column_config.CheckboxColumn("Here?", width="small"),
                    "Viewer Name": st.column_config.TextColumn("Viewer Name"),
                    "Qty": st.column_config.NumberColumn("Qty", min_value=1, max_value=5, width="small"),
                    "Turn / Win #": st.column_config.TextColumn("Turn"),
                    "Skin Choice": st.column_config.TextColumn("Skin Choice (Type Here)")
                },
                key="rollcall_table"
            )
        else:
            rollcall_df = pd.DataFrame()

    def build_batches(df, batch_limit, treasure_name):
        if df.empty:
            return pd.DataFrame(), ""

        df = df.sort_values("#").copy()
        parsed_rows = []
        rollover_lines = []
        batch1_items = 0
        remaining_queue = []

        for _, row in df.iterrows():
            q_num = row["#"]
            name = row["Viewer Name"]
            qty = int(row["Qty"])
            win_type = row["Turn / Win #"]
            raw_skin = str(row["Skin Choice"]).strip() if pd.notna(row["Skin Choice"]) else ""
            skin_display = raw_skin if raw_skin else treasure_name
            is_here = bool(row["Here?"])

            if is_here and batch1_items + qty <= batch_limit:
                slot_str = f"{batch1_items + 1}" if qty == 1 else f"{batch1_items + 1}-{batch1_items + qty}"
                parsed_rows.append({
                    "Batch": "Batch 1 (Today)",
                    "Gift #": f"{slot_str} of {batch_limit}",
                    "Viewer Name": name,
                    "Qty": qty,
                    "Turn": win_type,
                    "Skin to Send": skin_display,
                    "Note": "🟢 Send Now",
                    "Done?": False
                })
                batch1_items += qty
            else:
                reason = "💤 Absent (First tomorrow!)" if not is_here else "⏳ Next Batch"
                remaining_queue.append({
                    "#": q_num,
                    "Name": name,
                    "Qty": qty,
                    "Turn": win_type,
                    "Skin": skin_display,
                    "RawSkin": raw_skin,
                    "Note": reason
                })

        current_batch = 2
        items_in_batch = 0

        for item in remaining_queue:
            name = item["Name"]
            qty = item["Qty"]

            if item["RawSkin"]:
                rollover_lines.append(f"{name} - {qty} - {item['RawSkin']}")
            else:
                rollover_lines.append(f"{name} - {qty}")

            slot_str = f"{items_in_batch + 1}" if qty == 1 else f"{items_in_batch + 1}-{items_in_batch + qty}"
            parsed_rows.append({
                "Batch": f"Batch {current_batch}",
                "Gift #": f"{slot_str} of {batch_limit}",
                "Viewer Name": name,
                "Qty": qty,
                "Turn": item["Turn"],
                "Skin to Send": item["Skin"],
                "Note": item["Note"],
                "Done?": False
            })

            items_in_batch += qty
            if items_in_batch >= batch_limit:
                current_batch += 1
                items_in_batch = 0

        rollover_text = f"{treasure_name}\n\n" + "\n".join(rollover_lines) if rollover_lines else ""
        return pd.DataFrame(parsed_rows), rollover_text

    def create_excel(df):
        output = io.BytesIO()
        export_df = df.drop(columns=["Done?"]).copy()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="All_Batches")
            for b_name, group in export_df.groupby("Batch", sort=False):
                clean_sheet = b_name.replace(" (Today)", "")
                group.to_excel(writer, index=False, sheet_name=clean_sheet)

            header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            for _, ws in writer.sheets.items():
                for cell in ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                for col in ws.columns:
                    ws.column_dimensions[col[0].column_letter].width = max(len(str(c.value or "")) for c in col) + 5
        return output.getvalue()

    with right_col:
        st.subheader("🎁 STEP 3: Send Gifts & Save Tomorrow's List")
        final_df, rollover_text = build_batches(rollcall_df, max_gifts, final_title)

        if not final_df.empty:
            today_df = final_df[final_df["Batch"] == "Batch 1 (Today)"]
            next_df = final_df[final_df["Batch"] != "Batch 1 (Today)"]

            today_count = today_df["Qty"].sum() if not today_df.empty else 0
            leftover_count = next_df["Qty"].sum() if not next_df.empty else 0

            tab_today, tab_notepad, tab_all = st.tabs([
                f"1️⃣ Gift Today ({today_count}/{max_gifts})",
                f"2️⃣ Save for Tomorrow ({leftover_count} left)",
                "3️⃣ Full Schedule"
            ])

            with tab_today:
                st.markdown("""
                    <div style="background: #1e293b; padding: 12px 16px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 12px; font-size: 13px; color: #cbd5e1;">
                        <b>Instructions:</b><br>
                        1. Gift <b>ONLY these 8 people</b> in Dota 2 right now.<br>
                        2. Check <b>Done?</b> as you send each skin.<br>
                        3. Click <b>2️⃣ Save for Tomorrow</b> when finished!
                    </div>
                """, unsafe_allow_html=True)
                
                st.data_editor(
                    today_df[["Gift #", "Viewer Name", "Qty", "Turn", "Skin to Send", "Done?"]],
                    hide_index=True,
                    use_container_width=True,
                    height=330,
                    key="today_checklist"
                )

            with tab_notepad:
                st.markdown("""
                    <div style="background: #451a03; padding: 12px 16px; border-radius: 8px; border: 1px solid #78350f; margin-bottom: 12px; font-size: 13px; color: #fef3c7;">
                        <b>⚠️ BEFORE CLOSING:</b><br>
                        1. Click the Copy icon in the top-right corner of the code box below.<br>
                        2. Paste it into your <code>.txt</code> Notepad file and Save.<br>
                        3. Tomorrow, add new winners at the very bottom as <code>Name - 1</code>!
                    </div>
                """, unsafe_allow_html=True)
                
                if rollover_text:
                    st.code(rollover_text, language="text")
                else:
                    st.success("🎉 Everyone on the list has been gifted!")

            with tab_all:
                st.caption("Full queue overview across all upcoming days:")
                st.dataframe(
                    final_df.drop(columns=["Done?"]),
                    hide_index=True,
                    use_container_width=True,
                    height=330
                )

            excel_data = create_excel(final_df)
            st.download_button(
                label=f"📥 Download Excel Backup ({final_title}.xlsx)",
                data=excel_data,
                file_name=f"{final_title.lower().replace(' ', '_')}_batches.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )
