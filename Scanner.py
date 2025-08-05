import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
import pytz  # For timezone handling

st.title("QR Code Scanner and Attendance Tracker")

excel_file = 'scanned_qrcode_attendance.xlsx'

slots = [
    'Morning',
    'Evening',
    'Lunch - D1',
    'Dinner - D1',
    'Breakfast - D2'
]

# Helper functions
def load_codes(sheet, df_existing):
    if sheet in df_existing:
        df = df_existing[sheet]
        if 'Scanned QR Data' in df.columns and 'Timestamp' in df.columns:
            return dict(zip(df['Scanned QR Data'].astype(str), df['Timestamp'].astype(str)))
        else:
            # Legacy: only codes, no timestamps
            return {val: "" for val in df['Scanned QR Data'].astype(str)}
    else:
        return {}

# Load or initialize attendance data for all slots
if os.path.exists(excel_file):
    try:
        df_existing = pd.read_excel(excel_file, sheet_name=None)
        slot_codes = {slot: load_codes(slot, df_existing) for slot in slots}
    except Exception as e:
        slot_codes = {slot: {} for slot in slots}
else:
    slot_codes = {slot: {} for slot in slots}

attendance_slot = st.radio("Select attendance slot:", slots)

img_file = st.camera_input(f"Take a picture of the QR code for {attendance_slot} attendance")

if img_file:
    api_url = "https://api.qrserver.com/v1/read-qr-code/"
    files = {"file": img_file.getvalue()}
    with st.spinner("Scanning..."):
        try:
            res = requests.post(api_url, files=files, timeout=20)
            res.raise_for_status()
            out = res.json()
            result = out[0]["symbol"][0]["data"]
        except Exception as e:
            result = None

    if result:
        clean = result.strip()
        scanned_dict = slot_codes[attendance_slot]

        if clean and (clean not in scanned_dict):
            # Set timezone to Indian Standard Time (IST)
            ist = pytz.timezone('Asia/Kolkata')
            timestamp = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
            scanned_dict[clean] = timestamp
            st.success(f"{attendance_slot} Attendance marked for: {clean} at {timestamp}")
        elif clean:
            st.info(f"{attendance_slot} attendance already marked for: {clean} at {scanned_dict[clean]}")
    else:
        st.warning("No QR code detected or unreadable. Please try again.")

    # Save updated attendance with timestamp and custom section titles
    with pd.ExcelWriter(excel_file) as writer:
        for slot in slots:
            section_title = f"{slot} attendance"
            slot_items = list(slot_codes[slot].items())
            df_slot = pd.DataFrame(slot_items, columns=['Scanned QR Data', 'Timestamp'])
            pd.DataFrame({'': [section_title]}).to_excel(writer, index=False, header=False, sheet_name=slot)
            df_slot.to_excel(writer, index=False, startrow=1, sheet_name=slot)

    st.write(f"Saved {attendance_slot} attendance to '{excel_file}' in respective sheet.")

# Display attendance per slot with proper headings and timestamps
for slot in slots:
    st.subheader(f"{slot} Attendance")
    data = slot_codes[slot]
    if data:
        df_display = pd.DataFrame([(k, v) for k, v in data.items()], columns=[f"{slot} Attendance", "Timestamp"])
        st.dataframe(df_display)
    else:
        st.info(f"No {slot.lower()} attendance recorded yet.")

# Data clear button placed at the end
if st.button("Clear All Attendance Data 🗑️"):
    if os.path.exists(excel_file):
        os.remove(excel_file)
        st.success("All attendance data cleared!")
        # Clear the dicts in memory as well
        for slot in slots:
            slot_codes[slot].clear()
    else:
        st.info("No attendance data file found to clear.")
