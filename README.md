# 🎯 AWS AI-Based Smart Attendance System

**A facial-recognition-powered attendance platform combining computer vision with a serverless, cloud-ready AWS architecture.**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![AWS](https://img.shields.io/badge/AWS-Rekognition%20%7C%20S3%20%7C%20Lambda%20%7C%20SNS-FF9900?logo=amazonaws&logoColor=white)](https://aws.amazon.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()

---

## 📖 Overview

Manual roll-call attendance is slow, error-prone, and easy to game. This project replaces it with an **automated, facial-recognition-driven attendance system**, built with a cloud-native architecture in mind and a fully working local implementation for fast iteration and demoing.

The system detects and recognizes registered faces in real time, logs attendance instantly, and surfaces the results through a clean Streamlit dashboard — with **AWS Rekognition, S3, Lambda, SNS, RDS, and CloudWatch** integrated as the intended production backbone for a serverless, scalable deployment.

> 💡 **Two ways to run it:** a zero-dependency **local mode** (InsightFace + OpenCV, no AWS account needed) for quick setup and demos, and a **cloud-ready mode** designed around AWS managed services for production-scale deployment.

---

## ✨ Key Features

### 🖥️ Face Detection & Recognition
- Real-time face detection and recognition powered by **InsightFace**
- **OpenCV**-based image and video pipeline
- Automated, instant attendance logging on recognition
- Local fallback storage when a live data store isn't available

### 📝 Registration & Reporting
- Guided face-registration workflow for onboarding new users
- Attendance record management and historical reports
- Simulated data mode for testing and demos

### 🌐 Streamlit Web Interface
- **Home / Dashboard** — system overview and navigation
- **Real-Time Prediction** — live recognition and check-in
- **Registration Form** — enroll new faces
- **Reports** — view and export attendance history

### 🔐 Authentication & Security
- Username/password application authentication
- Password hashing for credential storage
- Environment-variable-based configuration — no hard-coded secrets
- `.gitignore`-protected local configuration files

### ☁️ Cloud-Ready Architecture (AWS)
- **Amazon Rekognition** for scalable facial recognition
- **AWS Lambda** for a serverless processing pipeline
- **Amazon S3** for image/data storage
- **Amazon SNS** for real-time attendance notifications
- **Amazon RDS** for durable, queryable attendance records
- **Amazon CloudWatch** for monitoring and logging
- **IAM** for least-privilege access control

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Web Interface | Streamlit |
| Face Recognition | InsightFace |
| Image/Video Processing | OpenCV |
| Data Processing | NumPy, Pandas |
| Caching / Data Store | Redis (optional), Pickle (local fallback) |
| Cloud Services | AWS Rekognition, S3, Lambda, SNS, RDS, CloudWatch, IAM |

---

## 📸 Screenshots

| Dashboard | Real-Time Recognition |
|---|---|
| ![Home Dashboard](Screenshots/home-dashboard.png) | ![Real-Time Prediction](Screenshots/real-time-prediction.png) |
| Model and database health checks on load | Live face-embedding table pulled from Redis, ready for recognition |

| Registration | Attendance Logs |
|---|---|
| ![Registration Form](Screenshots/registration-form.png) | ![Attendance Logs](Screenshots/attendance-logs.png) |
| Face-sample enrollment with role, course, and contact details | Raw check-in event log with per-user timestamps |

| Attendance Report | Filter Report |
|---|---|
| ![Attendance Report](Screenshots/attendance-report.png) | ![Filter Report](Screenshots/filter-report.png) |
| Consolidated in/out times, duration, and status per user | Query attendance by date, name, role, and duration threshold |

> Screenshots are stored in the [`Screenshots/`](./Screenshots) directory.

---

## 🚀 Getting Started (Local Setup — Windows)

### Requirements
- Windows 10 or Windows 11
- Python 3.x
- Git
- A modern web browser

### 1. Clone the repository
```bash
git clone https://github.com/MusaibParvez07/AWS-AI-Based-Smart-Attendance-System.git
cd AWS-AI-Based-Smart-Attendance-System
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Run the app
```bash
python -m streamlit run Home.py
```

Then open **http://localhost:8501** in your browser.

> No AWS account or paid cloud service is required to run the local version — Redis and AWS are optional enhancements, not prerequisites.

---

## ☁️ Cloud Deployment Notes

This repository ships with AWS helper/config scaffolding (`aws_helper.py`, `aws_config.example.json`, `configure.sh`) reflecting the system's intended production design:

- **Rekognition** replaces local InsightFace inference for managed, scalable face matching
- **Lambda** orchestrates the recognition-to-logging pipeline in a serverless flow
- **S3** stores registered face images and captured frames
- **RDS** persists attendance records for reporting and analytics
- **SNS** pushes real-time check-in notifications
- **CloudWatch** and **IAM** handle observability and access control

AWS credentials are never committed to the repo — configuration is handled entirely through environment variables and `.gitignore`-excluded local files.

---

## 📁 Project Structure

```
AWS-AI-Based-Smart-Attendance-System/
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── style.css
│   └── tech_bg.png
├── insightface_model/
│   └── models/buffalo_sc/
├── pages/
│   ├── 1_Real_Time_Prediction.py
│   ├── 2_Registration_form.py
│   └── 3_Report.py
├── Screenshots/
├── Home.py
├── auth.py
├── aws_config.example.json
├── aws_helper.py
├── aws_test.py
├── check_rds.py
├── config.yaml
├── configure.sh
├── face_rec.py
├── main.sh
├── requirements.txt
└── README.md
```

---

## 🔭 Roadmap

- [ ] Improved face recognition accuracy under varied lighting/angles
- [ ] Real-time camera pipeline optimization
- [ ] Enhanced attendance analytics dashboard
- [ ] Exportable attendance reports (CSV/PDF)
- [ ] Multi-user / role-based administration
- [ ] Full managed-database (RDS) integration
- [ ] End-to-end AWS deployment guide

---

---

⭐ If you find this project useful, consider giving it a star!
