import io
import re
from openpyxl.styles import Font, PatternFill
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dota 2 Gift Helper", page_icon="🎁", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎁 Paul's Dota 2 Fair Queue & Gift Batcher")

# Quick Golden Rules Banner at the very top
st.success(
    "💡 **HOW THIS WORKS (3 EASY STEPS):** \n1. **Paste your Notepad list** in"
    " Step 1. *(Note: During stream, always add new winners at the VERY BOTTOM"
    " as `Name - 1`, even if they won before!)*\n2. **Use the Roll-Call Timer &"
    " Check who is in chat** in Step 2 (Uncheck `Here?` if they don't reply"
    " before the timer hits 00:00).\n3. **Send Today's 8 Gifts** in Step 3,"
    " then copy the updated Notepad list for tomorrow!"
)

# Default sample from Paul's Notepad
default_text = """Trove of Terror

Joseph Estobo - 1
Julius Durango - 1
Ren Ren- 2
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
Ariel Marquez -1
Carl Villanueva - 1
Paul Panganoron - 1"""

# --- STEP 1: PASTE NOTEPAD ---
with st.expander("📝 STEP 1: Paste Your Notepad List Here", expanded=True):
  c1, c2 = st.columns([2.5, 1.5])
  with c1:
    raw_input = st.text_area(
        "Copy and paste your entire Notepad file here:",
        value=default_text,
        height=170,
    )
  with c2:
    default_treasure = st.text_input(
        "Treasure / Event Name", value="Trove of Terror"
    )
    max_gifts = st.number_input(
        "Steam Daily Gift Limit (Max 8)", min_value=1, max_value=20, value=8
    )
    split_multi_to_bottom = st.checkbox(
        "✅ Fair Queue Mode: Split '- 2' into separate turns",
        value=True,
        help=(
            "If someone has '- 2', they get 1 skin today, and their 2nd skin is"
            " automatically moved to the bottom of the line so everyone gets a"
            " fair turn!"
        ),
    )


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

    win_label = "1st Win" if win_num == 1 else f"🔁 #{win_num} Win (Repeat)"

    rows.append({
        "#": order_idx,
        "Here?": True,
        "Viewer Name": item["Name"],
        "Qty": item["Qty"],
        "Turn / Win #": win_label,
        "Skin Choice": item["Skin"],
    })

  return pd.DataFrame(rows), detected_title


base_df, final_title = parse_fair_queue(
    raw_input, default_treasure, split_multi_to_bottom
)

st.divider()

# --- STEP 2 & STEP 3 WORKSPACE ---
left_col, right_col = st.columns([1.15, 1.35], gap="large")

with left_col:
  st.subheader("🙋‍♂️ STEP 2: Who is in Chat Right Now?")

  # --- BUILT-IN JAVASCRIPT ROLL-CALL TIMER (NO PAGE RELOADS!) ---
  timer_html = """
    <div style="background: #1e293b; border: 2px solid #334155; border-radius: 10px; padding: 12px 16px; color: white; font-family: sans-serif; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
        <div>
            <div style="font-size: 12px; color: #94a3b8; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">⏱️ Live Chat Call-Out Timer</div>
            <div id="display" style="font-size: 30px; font-weight: 800; color: #4ade80; font-variant-numeric: tabular-nums; margin-top: 2px;">01:00</div>
            <div id="status_text" style="font-size: 12px; color: #cbd5e1;">Click a time button when calling a viewer!</div>
        </div>
        <div style="display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end;">
            <button onclick="startTimer(30)" style="background: #2563eb; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px;">▶ 30s</button>
            <button onclick="startTimer(60)" style="background: #16a34a; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px;">▶ 60s</button>
            <button onclick="startTimer(90)" style="background: #9333ea; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px;">▶ 90s</button>
            <button onclick="resetTimer()" style="background: #475569; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px;">⏹ Reset</button>
        </div>
    </div>

    <script>
    let countdown;
    function playBeep(freq, duration) {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = "sine";
            osc.frequency.value = freq;
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
        document.getElementById('status_text').innerText = "⏳ Waiting for viewer to reply in chat...";

        countdown = setInterval(() => {
            remaining--;
            if (remaining <= 0) {
                clearInterval(countdown);
                const disp = document.getElementById('display');
                disp.innerText = "00:00 - TIME'S UP!";
                disp.style.color = "#ef4444";
                document.getElementById('status_text').innerText = "❌ No reply! Uncheck 'Here?' below & call next.";
                playBeep(440, 200);
                setTimeout(() => playBeep(330, 400), 250);
            } else {
                updateUI(remaining);
                if (remaining <= 5) {
                    playBeep(600, 80);
                }
            }
        }, 1000);
    }

    function resetTimer() {
        clearInterval(countdown);
        const disp = document.getElementById('display');
        disp.innerText = "01:00";
        disp.style.color = "#4ade80";
        document.getElementById('status_text').innerText = "Timer reset. Ready for next viewer!";
    }

    function updateUI(sec) {
        const mins = String(Math.floor(sec / 60)).padStart(2, '0');
        const secs = String(sec % 60).padStart(2, '0');
        const disp = document.getElementById('display');
        disp.innerText = mins + ":" + secs;
        if (sec <= 10) {
            disp.style.color = "#facc15"; // Yellow warning
        } else {
            disp.style.color = "#4ade80"; // Green
        }
    }
    </script>
    """
  components.html(timer_html, height=110)

  st.info(
      "**How to use this table:**\n1. Call out a viewer's name on stream and"
      " click **▶ 60s** (or **30s**) on the timer above.\n2. **If the timer"
      " hits `00:00` (AFK):** Uncheck their **`Here?`** box. *(They won't lose"
      " their prize! They just move to the top of tomorrow's list).* \n3. **If"
      " they reply in chat:** Type the skin they want under **`Skin Choice`**."
  )

  if not base_df.empty:
    rollcall_df = st.data_editor(
        base_df,
        hide_index=True,
        width="stretch",
        height=420,
        disabled=["#", "Viewer Name", "Turn / Win #"],
        column_config={
            "#": st.column_config.NumberColumn("#", width="small"),
            "Here?": st.column_config.CheckboxColumn("Here?", width="small"),
            "Viewer Name": st.column_config.TextColumn("Viewer Name"),
            "Qty": st.column_config.NumberColumn(
                "Qty", min_value=1, max_value=5, width="small"
            ),
            "Turn / Win #": st.column_config.TextColumn("Turn Type"),
            "Skin Choice": st.column_config.TextColumn(
                "Skin Choice (Double-click to type)"
            ),
        },
        key="rollcall_table",
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
    raw_skin = (
        str(row["Skin Choice"]).strip() if pd.notna(row["Skin Choice"]) else ""
    )
    skin_display = raw_skin if raw_skin else treasure_name
    is_here = bool(row["Here?"])

    if is_here and batch1_items + qty <= batch_limit:
      slot_str = (
          f"{batch1_items + 1}"
          if qty == 1
          else f"{batch1_items + 1}-{batch1_items + qty}"
      )
      parsed_rows.append({
          "Batch": "Batch 1 (Today)",
          "Gift #": f"{slot_str} of {batch_limit}",
          "Viewer Name": name,
          "Qty": qty,
          "Turn": win_type,
          "Skin to Send": skin_display,
          "Note": "🟢 Send Now",
          "Done?": False,
      })
      batch1_items += qty
    else:
      reason = (
          "💤 Absent Today (First in line tomorrow!)"
          if not is_here
          else "⏳ Waiting for next batch"
      )
      remaining_queue.append({
          "#": q_num,
          "Name": name,
          "Qty": qty,
          "Turn": win_type,
          "Skin": skin_display,
          "RawSkin": raw_skin,
          "Note": reason,
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

    slot_str = (
        f"{items_in_batch + 1}"
        if qty == 1
        else f"{items_in_batch + 1}-{items_in_batch + qty}"
    )
    parsed_rows.append({
        "Batch": f"Batch {current_batch}",
        "Gift #": f"{slot_str} of {batch_limit}",
        "Viewer Name": name,
        "Qty": qty,
        "Turn": item["Turn"],
        "Skin to Send": item["Skin"],
        "Note": item["Note"],
        "Done?": False,
    })

    items_in_batch += qty
    if items_in_batch >= batch_limit:
      current_batch += 1
      items_in_batch = 0

  rollover_text = (
      f"{treasure_name}\n\n" + "\n".join(rollover_lines)
      if rollover_lines
      else ""
  )
  return pd.DataFrame(parsed_rows), rollover_text


def create_excel(df):
  output = io.BytesIO()
  export_df = df.drop(columns=["Done?"]).copy()

  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    export_df.to_excel(writer, index=False, sheet_name="All_Batches")
    for b_name, group in export_df.groupby("Batch", sort=False):
      clean_sheet = b_name.replace(" (Today)", "")
      group.to_excel(writer, index=False, sheet_name=clean_sheet)

    header_fill = PatternFill(
        start_color="1F2937", end_color="1F2937", fill_type="solid"
    )
    header_font = Font(color="FFFFFF", bold=True)
    for _, ws in writer.sheets.items():
      for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
      for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = (
            max(len(str(c.value or "")) for c in col) + 5
        )
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
        "3️⃣ Full Schedule (All Days)",
    ])

    with tab_today:
      st.info(
          "**What to do right now:**\n1. Open Dota 2 and send skins **ONLY to"
          " these 8 people** below.\n2. Tick the **`Done?`** box after you send"
          " each gift so you don't lose track.\n3. When finished, click tab"
          " **`2️⃣ Save for Tomorrow`** right next to this tab!"
      )
      st.data_editor(
          today_df[[
              "Gift #",
              "Viewer Name",
              "Qty",
              "Turn",
              "Skin to Send",
              "Done?",
          ]],
          hide_index=True,
          width="stretch",
          height=310,
          key="today_checklist",
      )

    with tab_notepad:
      st.warning(
          "**⚠️ IMPORTANT — DO THIS BEFORE CLOSING:**\n1. Hover over the black"
          " box below and click the **Copy icon** (top-right corner of the"
          " black box).\n2. Open your `.txt` Notepad file, **erase"
          " everything**, and **Paste (`Ctrl + V`)** this new list.\n3. **Save"
          " your Notepad!** *(Everyone you already gifted today is removed, and"
          " absent people are waiting at the top for tomorrow)*.\n4. **Rule for"
          " next stream:** When someone wins tomorrow, always add their name at"
          " the **VERY BOTTOM** as `Name - 1` (never change an existing `- 1`"
          " to `- 2`!)."
      )
      if rollover_text:
        st.code(rollover_text, language="text")
      else:
        st.success(
            "🎉 You gifted everyone on the list! Your Notepad is now completely"
            " empty."
        )

    with tab_all:
      st.info(
          "**What is this tab?**\nThis shows the full lineup for **Batch 1,"
          " Batch 2, and Batch 3** so you can show viewers on stream when their"
          " turn is coming up."
      )
      st.dataframe(
          final_df.drop(columns=["Done?"]),
          hide_index=True,
          width="stretch",
          height=310,
      )

    excel_data = create_excel(final_df)
    st.download_button(
        label=f"📥 Optional: Download Excel Backup ({final_title}.xlsx)",
        data=excel_data,
        file_name=f"{final_title.lower().replace(' ', '_')}_batches.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        type="primary",
        width="stretch",
    )
