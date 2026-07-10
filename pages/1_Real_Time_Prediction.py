import streamlit as st
from Home import face_rec
if hasattr(face_rec, 'apply_custom_css'):
    face_rec.apply_custom_css()
from streamlit_webrtc import webrtc_streamer
import av
import time
from aws_helper import aws

st.subheader('Real-Time Attendance System')

# Retrieve the data
with st.spinner('Retrieving Data...'):
    redis_face_db = face_rec.retrive_data(name='academy:register')
    st.dataframe(redis_face_db)

# Check if AWS is active
is_aws = aws.is_configured()
if is_aws:
    st.info("AWS Mode Active: Using S3, RDS and AWS Rekognition (Throttled for high performance).")
else:
    st.info("Local Mode Active: Using local database and InsightFace.")

if 'realtimepred' not in st.session_state:
    st.session_state.realtimepred = face_rec.RealTimePred()
realtimepred = st.session_state.realtimepred

waitTime = 10 # 10 seconds interval

# Reset the log timer on start
realtimepred.setTime = time.time()

# Real Time Prediction callback function (runs in background thread, smooth & throttled)
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24") # 3 dimension numpy array
    pred_img = realtimepred.face_prediction(img, redis_face_db,
                                        'facial_features', ['Name','Role'], thresh=0.5)

    timenow = time.time()
    difftime = timenow - realtimepred.setTime
    if difftime >= waitTime:
        realtimepred.saveLogs_redis()
        realtimepred.setTime = time.time() # reset time
        print('Save Data to database')

    return av.VideoFrame.from_ndarray(pred_img, format="bgr24")

# Start Streamlit WebRTC component
webrtc_streamer(key="realtimePrediction", video_frame_callback=video_frame_callback,
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }
)