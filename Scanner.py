import streamlit as st
import pandas as pd
import os
import requests

st.title("QR Code Scanner and Attendance Tracker")

excel_file = 'scanned_qrcode_attendance.xlsx'

# Extended attendance slots
slots = [
    'Morning',
    'Evening',
    'Lunch - D1',
    'Dinner - D1',
    'Breakfast - D2'
]

# Helper to initialize or read data for each slot
def load_codes(sheet, df_existing):
    return set(df_existing.get(sheet, pd.DataFrame(columns=['Scanned QR Data']))['Scanned QR Data'].astype(str))

# Load or initialize attendance data for all slots
if os.path.exists(excel_file):
    try:
        df_existing = pd.read_excel(excel_file, sheet_name=None)
        slot_codes = {slot: load_codes(slot, df_existing) for slot in slots}
    except Exception as e:
        slot_codes = {slot: set() for slot in slots}
else:
    slot_codes = {slot: set() for slot in slots}

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
        scanned_set = slot_codes[attendance_slot]

        if clean and (clean not in scanned_set):
            scanned_set.add(clean)
            st.success(f"{attendance_slot} Attendance marked for: {clean}")
        elif clean:
            st.info(f"{attendance_slot} attendance already marked for: {clean}")
    else:
        st.warning("No QR code detected or unreadable. Please try again.")

    # Save updated attendance with section titles in Excel sheets (using casing as requested)
    with pd.ExcelWriter(excel_file) as writer:
        for slot in slots:
            section_title = f"{slot} attendance"
            df_slot = pd.DataFrame({'Scanned QR Data': list(slot_codes[slot])})
            pd.DataFrame({'': [section_title]}).to_excel(writer, index=False, header=False, sheet_name=slot)
            df_slot.to_excel(writer, index=False, startrow=1, sheet_name=slot)

    st.write(f"Saved {attendance_slot} attendance to '{excel_file}' in respective sheet.")

# Display attendance per slot with proper headings
for slot in slots:
    st.subheader(f"{slot} Attendance")
    if slot_codes[slot]:
        st.dataframe(pd.DataFrame({f"{slot} Attendance": list(slot_codes[slot])}))
    else:
        st.info(f"No {slot.lower()} attendance recorded yet.")

# Data clear button placed at the end
if st.button("Clear All Attendance Data 🗑️"):
    if os.path.exists(excel_file):
        os.remove(excel_file)
        st.success("All attendance data cleared!")
        # Clear the sets in memory as well
        for slot in slots:
            slot_codes[slot].clear()
    else:
        st.info("No attendance data file found to clear.")
