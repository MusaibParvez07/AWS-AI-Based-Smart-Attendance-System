import streamlit as st
from Home import face_rec
if hasattr(face_rec, 'apply_custom_css'):
    face_rec.apply_custom_css()
import cv2
import numpy as np
from aws_helper import aws

st.subheader('Registration Form')

is_aws = aws.is_configured()

with st.container(border=True):
    name = st.text_input(label='Name', placeholder='Enter First name and Last name')
    role = st.selectbox(label='Role', placeholder='Select Role', options=('--select--',
                                                                          'Student', 'Teacher'))
    course = st.selectbox(label='Select Course', placeholder='Select Course',
                          options=('--select--','Computer Science',
                                   'Electrical','Electronics'))
    year_level = st.selectbox(label='Year Level', placeholder='Year Level',
                              options=('--select--', 'I - First Year',
                                       'II - Second Year',
                                       'III - Third Year','IV - Fourth Year'))
    address = st.text_area(label='Address', placeholder='Enter your address')
    contact = st.text_input(label='Contact Number', placeholder='Enter your contact number')
    email = st.text_input(label='Email', placeholder='Enter Email Address')

    st.write("### Capture Photo")
    if is_aws:
        st.info("AWS Integration Mode Active: A single clear photo is required for face registration.")
    else:
        st.info("Local Mode Active: Extracting face embedding using local ML models.")
        
    img_file = st.camera_input("Take a photo of your face")

# step-3: save the data
if st.button('Submit'):
    if img_file is None:
        st.error('Please capture a face photo first using the camera component above.')
    elif name is None or name.strip() == '':
        st.error('Please enter a name.')
    elif role == '--select--':
        st.error('Please select a role.')
    else:
        # Get image bytes from st.camera_input
        image_bytes = img_file.getvalue()
        
        if is_aws:
            try:
                # Register user in AWS S3, RDS MySQL and Rekognition Collection
                aws.register_user(name, role, course, year_level, address, contact, email, image_bytes)
                st.success(f"{name} registered successfully in AWS database!")
            except Exception as e:
                st.error(f"AWS Registration Error: {e}")
        else:
            # Local fallback mode
            # Convert image bytes to opencv frame
            file_bytes = np.asarray(bytearray(image_bytes), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, 1)
            
            # Save local embedding
            try:
                from face_rec import faceapp
                if faceapp is not None:
                    results = faceapp.get(frame, max_num=1)
                    if results:
                        embedding = results[0]['embedding']
                        key = f'{name}@{role}'
                        # Save embedding bytes to local database (r)
                        face_rec.r.hset(name='academy:register', key=key, value=embedding.tobytes())
                        st.success(f"{name} registered successfully locally!")
                    else:
                        st.error("No face detected in the photo. Please make sure your face is clearly visible and try again.")
                else:
                    st.error("Local ML model not loaded.")
            except Exception as e:
                st.error(f"Local Registration Error: {e}")
        
