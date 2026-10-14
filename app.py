import io
import re
from openpyxl.styles import Alignment, Font, PatternFill
import pandas as pd
import streamlit as st

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
    "💡 **HOW THIS WORKS (3 EASY STEPS):** \n"
    "1. **Paste your Notepad list** in Step 1. *(Note: During stream, always add new winners at the VERY BOTTOM as `Name - 1`, even if they won before!)*\n"
    "2. **Check who is in chat** in Step 2 (Uncheck anyone who is offline/AFK, and type the hero skin they want).\n"
    "3. **Send Today's 8 Gifts** in Step 3, then copy the updated Notepad list for tomorrow!"
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
        default_treasure = st.text_input("Treasure / Event Name", value="Trove of Terror")
        max_gifts = st.number_input(
            "Steam Daily Gift Limit (Max 8)", min_value=1, max_value=20, value=8
        )
        split_multi_to_bottom = st.checkbox(
            "✅ Fair Queue Mode: Split '- 2' into separate turns",
            value=True,
            help=(
                "If someone has '- 2', they get 1 skin today, and their 2nd skin "
                "is automatically moved to the bottom of the line so everyone gets a fair turn!"
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
    st.info(
        "**How to use this table:**\n"
        "1. Call out the names from top to bottom on stream.\n"
        "2. **If they are NOT in chat (AFK):** Uncheck their **`Here?`** box. *(Don't worry, they won't lose their prize! They just get moved to the top of tomorrow's list).* \n"
        "3. **If they ARE in chat:** Ask what skin they want and type it under **`Skin Choice`**."
    )

    if not base_df.empty:
        rollcall_df = st.data_editor(
            base_df,
            hide_index=True,
            use_container_width=True,
            height=450,
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
            reason = "💤 Absent Today (First in line tomorrow!)" if not is_here else "⏳ Waiting for next batch"
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
                "**What to do right now:**\n"
                "1. Open Dota 2 and send skins **ONLY to these 8 people** below.\n"
                "2. Tick the **`Done?`** box after you send each gift so you don't lose track.\n"
                "3. When finished, click tab **`2️⃣ Save for Tomorrow`** right next to this tab!"
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
                use_container_width=True,
                height=310,
                key="today_checklist",
            )

        with tab_notepad:
            st.warning(
                "**⚠️ IMPORTANT — DO THIS BEFORE CLOSING:**\n"
                "1. Hover over the black box below and click the **Copy icon** (top-right corner of the black box).\n"
                "2. Open your `.txt` Notepad file, **erase everything**, and **Paste (`Ctrl + V`)** this new list.\n"
                "3. **Save your Notepad!** *(Everyone you already gifted today is removed, and absent people are waiting at the top for tomorrow)*.\n"
                "4. **Rule for next stream:** When someone wins tomorrow, always add their name at the **VERY BOTTOM** as `Name - 1` (never change an existing `- 1` to `- 2`!)."
            )
            if rollover_text:
                st.code(rollover_text, language="text")
            else:
                st.success("🎉 You gifted everyone on the list! Your Notepad is now completely empty.")

        with tab_all:
            st.info(
                "**What is this tab?**\n"
                "This shows the full lineup for **Batch 1, Batch 2, and Batch 3** so you can show viewers on stream when their turn is coming up."
            )
            st.dataframe(
                final_df.drop(columns=["Done?"]),
                hide_index=True,
                use_container_width=True,
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
            use_container_width=True,
        )