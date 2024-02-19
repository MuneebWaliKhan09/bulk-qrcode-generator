import streamlit as st
import pandas as pd
import qrcode
from PIL import Image
import os
import shutil
from io import BytesIO
import re
import zipfile
import tempfile  # Add this import statement

st.title("🚀 [Bulk QR Code Generator By Muneeb Wali Khan] 🚀")
with st.expander("ℹ️ Instructions"):
    st.write("""
        This application allows you to generate QR codes in bulk from a CSV file for free.
        Follow these steps:

        1. **Upload CSV File:**
            - Use the sidebar to upload a CSV file containing data .

        2. **Select Columns:**
            - Choose the columns you want to include in the QR codes for each row.

        3. **Generate QR Codes:**
            - Click the 'Generate QR Codes' button to create QR codes for each rows.

        4. **Download Options:**
            - Download the updated CSV file with QrCode column include in CSV file for each row.
            - Download a zip file containing all QR codes images only.

        Enjoy creating QR codes in bulk By Muneeb wali khan ! 🎉
    """)


# Define your authentication credentials
# users = [
#     {'username': 'admin', 'password': '123'},
#     # Add more users as needed
# ]


# user_input = st.text_input("Username:")
# password_input = st.text_input("Password:", type="password")


# for user in users:
#     if user['username'] == user_input and user['password'] == password_input:





# CREATING QR CODES 
def generate_qr_codes(df, selected_columns, fill_color):
            # Create a directory to save QR codes
            qr_directory = 'qrcodes'
            if not os.path.exists(qr_directory):
                os.makedirs(qr_directory)

            # Create a temporary directory to store individual QR code images
            temp_directory = 'temp_qrcodes'
            if os.path.exists(temp_directory):
                shutil.rmtree(temp_directory)
            os.makedirs(temp_directory)

            # Create a list to store file paths of QR code images
            qr_file_paths = []

            # Create and save QR codes for each student
            for index, row in df.iterrows():
                student_data = "\n".join([f"{col}: {row[col]}" for col in selected_columns])

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=6,
                    border=2,
                )

                qr.add_data(student_data)
                qr.make(fit=True)

                img = qr.make_image(fill_color=fill_color, back_color="white")

                # Save the image in the temporary directory using the student's name
                # student_name = row[selected_columns[0]].replace(" ", "_")  # Use the first selected column as a name
                student_name = re.sub(r'[^a-zA-Z0-9_]', '', str(row[selected_columns[0]]))
                filename = f"{temp_directory}/{student_name}_{index + 1}.JPEG"
                img.save(filename, format="JPEG")

                # Append file path to the list
                qr_file_paths.append(filename)

            # Add QR code file paths to DataFrame
            df['QR Code File'] = qr_file_paths

            return temp_directory




# CREATE A ZIP FILE
def zip_data(temp_directory):
            buffer = BytesIO()
            with zipfile.ZipFile(buffer, 'w') as zip_file:
                for root, dirs, files in os.walk(temp_directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zip_file.write(file_path, os.path.relpath(file_path, temp_directory))
            buffer.seek(0)
            return buffer.read()






# Upload CSV file
st.sidebar.header("Upload CSV file")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
            # Load CSV data into a DataFrame
            df = pd.read_csv(uploaded_file)

            # Display CSV data
            st.sidebar.header("CSV Data")
            st.sidebar.write(df)

            # Prompt the user to select columns
            selected_columns = st.sidebar.multiselect("Select columns for QR code", df.columns)

            if not selected_columns:
                st.warning("Please select columns for QR code generation.")
            else:
                
                fill_color = st.sidebar.color_picker("Select QR Code Fill Color", "#000000")
                # Create a button to generate QR codes
                if st.button("Generate QR Codes"):
                    temp_directory = generate_qr_codes(df, selected_columns,fill_color)

                    # Display the generated QR codes
                    st.success("QR Codes generated successfully!")

                    # Create a new DataFrame with the QR code paths
                    df_with_qr_paths = df.copy()
                    df_with_qr_paths['QR Code File'] = df['QR Code File']

                    # Create a temporary CSV file to store the updated DataFrame
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
                        df_with_qr_paths.to_csv(temp_csv.name, index=False)

                    # Offer the option to download the modified CSV file
                    csv_filename = "updated_data.csv"
                    csv_data = open(temp_csv.name, "rb").read()
                    st.download_button(label="Download Updated CSV File", data=csv_data, file_name=csv_filename)

                    # Create a button to download the zip file
                    download_btn = st.download_button(
                        label="Download QR Codes as Zip",
                        data=zip_data(temp_directory),
                        file_name="qrcodes.zip",
                    )

                    # Clean up temporary directory
                    shutil.rmtree(temp_directory)
                    os.remove(temp_csv.name)  # Remove the temporary CSV file

