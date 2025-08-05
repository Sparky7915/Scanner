import streamlit as st
import pandas as pd
import os
import requests

st.title("QR Code Scanner with Streamlit (API-Based, Cloud-Friendly)")

# File to store scanned QR codes
excel_file = 'scanned_qrcode_camera.xlsx'

# Load existing scanned codes
if os.path.exists(excel_file):
    try:
        df_existing = pd.read_excel(excel_file)
        scanned_codes = set(df_existing['Scanned QR Data'].astype(str))
    except Exception:
        scanned_codes = set()
else:
    scanned_codes = set()

img_file = st.camera_input("Take a picture of the QR code")

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

    found_codes = set()
    if result:
        clean = result.strip()
        if clean and (clean not in scanned_codes):
            found_codes.add(clean)
            scanned_codes.add(clean)
            st.success(f"Scanned: {clean}")
        elif clean:
            st.info(f"Already scanned: {clean}")
    else:
        st.warning("No QR code detected or this code is unreadable.")

    # Save to Excel on every new scan
    if found_codes:
        df = pd.DataFrame({'Scanned QR Data': list(scanned_codes)})
        df.to_excel(excel_file, index=False)
        st.write("All scanned codes saved.")

# Display list of all scanned codes
if scanned_codes:
    st.subheader("Scanned QR Codes")
    st.dataframe(pd.DataFrame({'Scanned QR Data': list(scanned_codes)}))
else:
    st.info("No QR codes detected/scanned yet.")
