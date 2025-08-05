import streamlit as st
import pandas as pd
import os
from pyzbar.pyzbar import decode
from PIL import Image

st.title("QR Code Scanner with Streamlit (No OpenCV!)")

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

# Camera input widget for user to capture an image
img_file = st.camera_input("Take a picture of the QR code")

if img_file:
    img = Image.open(img_file)
    results = decode(img)

    found_codes = set()
    for barcode in results:
        data = barcode.data.decode('utf-8').strip()
        if data and (data not in scanned_codes):
            found_codes.add(data)
            scanned_codes.add(data)
            st.success(f"Scanned: {data}")
        elif data:
            st.info(f"Already scanned: {data}")

    if not found_codes:
        st.warning("No new QR code detected. Try retaking the picture.")

    # Save to Excel on every new scan
    df = pd.DataFrame({'Scanned QR Data': list(scanned_codes)})
    df.to_excel(excel_file, index=False)
    st.write("All scanned codes saved.")

# Display list of all scanned codes
if scanned_codes:
    st.subheader("Scanned QR Codes")
    st.dataframe(pd.DataFrame({'Scanned QR Data': list(scanned_codes)}))
else:
    st.info("No QR codes detected/scanned yet.")
