import streamlit as st
import pandas as pd
import os
import requests

st.title("QR Code Scanner and Attendance Tracker")

excel_file = 'scanned_qrcode_attendance.xlsx'

# Add a button to clear all attendance data
if st.button("Clear All Attendance Data 🗑️"):
    if os.path.exists(excel_file):
        os.remove(excel_file)
        st.success("All attendance data cleared!")
    else:
        st.info("No attendance data file found to clear.")
    # Reset session data
    st.stop()  # Stops execution after clearing

# Initialize or load attendance data
if os.path.exists(excel_file):
    try:
        df_existing = pd.read_excel(excel_file, sheet_name=None)
        morning_codes = set(df_existing.get('Morning', pd.DataFrame(columns=['Scanned QR Data']))['Scanned QR Data'].astype(str))
        evening_codes = set(df_existing.get('Evening', pd.DataFrame(columns=['Scanned QR Data']))['Scanned QR Data'].astype(str))
    except Exception as e:
        morning_codes = set()
        evening_codes = set()
else:
    morning_codes = set()
    evening_codes = set()

attendance_slot = st.radio("Select attendance slot:", ['Morning', 'Evening'])

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
        scanned_set = morning_codes if attendance_slot == 'Morning' else evening_codes

        if clean and (clean not in scanned_set):
            scanned_set.add(clean)
            st.success(f"{attendance_slot} Attendance marked for: {clean}")
        elif clean:
            st.info(f"{attendance_slot} attendance already marked for: {clean}")
    else:
        st.warning("No QR code detected or unreadable. Please try again.")

    # Save updated attendance with section titles in Excel sheets with requested changes
    df_morning = pd.DataFrame({'Scanned QR Data': list(morning_codes)})
    df_evening = pd.DataFrame({'Scanned QR Data': list(evening_codes)})

    with pd.ExcelWriter(excel_file) as writer:
        # Write updated section titles with requested casing
        pd.DataFrame({'': ['Morning attendance']}).to_excel(writer, index=False, header=False, sheet_name='Morning')
        df_morning.to_excel(writer, index=False, startrow=1, sheet_name='Morning')

        pd.DataFrame({'': ['Evening attendance']}).to_excel(writer, index=False, header=False, sheet_name='Evening')
        df_evening.to_excel(writer, index=False, startrow=1, sheet_name='Evening')

    st.write(f"Saved {attendance_slot} attendance to '{excel_file}' in respective sheet.")

# Display current attendance records with exact headings
st.subheader("Morning Attendance")
if morning_codes:
    st.dataframe(pd.DataFrame({'Morning Attendance': list(morning_codes)}))
else:
    st.info("No morning attendance recorded yet.")

st.subheader("Evening Attendance")
if evening_codes:
    st.dataframe(pd.DataFrame({'Evening Attendance': list(evening_codes)}))
else:
    st.info("No evening attendance recorded yet.")
