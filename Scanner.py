import streamlit as st
import pandas as pd
import os
import cv2
import numpy as np

# Streamlit title
st.title("QR Code Scanner with Streamlit")

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
img_file = st.camera_input("Take a picture to scan QR code")

if img_file:
    # Convert image to OpenCV format
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)
    if data:
        clean = data.strip()
        if clean and (clean not in scanned_codes):
            st.success(f"Scanned: {clean}")
            scanned_codes.add(clean)
        else:
            st.info("Code already scanned or not found.")
    else:
        st.warning("No QR code detected. Try taking a clearer picture.")

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
