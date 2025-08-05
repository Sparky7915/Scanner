import streamlit as st
import pandas as pd
import os
import requests
from datetime import date

st.title("QR Code Scanner and Attendance Tracker")

# File to store scanned QR codes (attendance)
excel_file = 'scanned_qrcode_attendance.xlsx'

# Initialize or load attendance data
if os.path.exists(excel_file):
    try:
        df_existing = pd.read_excel(excel_file, sheet_name=None)
        morning_codes = set(df_existing.get('Morning', pd.DataFrame(columns=['Scanned QR Data']))['Scanned QR Data'].astype(str))
        evening_codes = set(df_existing.get('Evening', pd.DataFrame(columns=['Scanned QR Data']))['Scanned QR Data'].astype(str))
    except Exception:
        morning_codes = set()
        evening_codes = set()
else:
    morning_codes = set()
    evening_codes = set()

# User selects attendance slot
attendance_slot = st.radio("Select attendance slot:", ['Morning', 'Evening'])

# Camera input for QR scanning
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
        except:
            result = None

    if result:
        clean = result.strip()
        if attendance_slot == 'Morning':
            scanned_set = morning_codes
        else:
            scanned_set = evening_codes

        if clean and (clean not in scanned_set):
            scanned_set.add(clean)
            st.success(f"{attendance_slot} Attendance marked for: {clean}")
        elif clean:
            st.info(f"{attendance_slot} attendance already marked for: {clean}")
    else:
        st.warning("No QR code detected or unreadable. Please try again.")

    # Save attendance data to Excel whenever new codes are added
    df_morning = pd.DataFrame({'Scanned QR Data': list(morning_codes)})
    df_evening = pd.DataFrame({'Scanned QR Data': list(evening_codes)})

    with pd.ExcelWriter(excel_file) as writer:
        df_morning.to_excel(writer, sheet_name='Morning', index=False)
        df_evening.to_excel(writer, sheet_name='Evening', index=False)

    st.write("Attendance records saved.")

# Show current attendance records
st.subheader("Morning Attendance")
if morning_codes:
    st.dataframe(pd.DataFrame({'Scanned QR Data': list(morning_codes)}))
else:
    st.info("No morning attendance recorded yet.")

st.subheader("Evening Attendance")
if evening_codes:
    st.dataframe(pd.DataFrame({'Scanned QR Data': list(evening_codes)}))
else:
    st.info("No evening attendance recorded yet.")
