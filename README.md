# ☁️ AWS AI-Based Smart Attendance System

> A cloud-enabled facial recognition attendance system that automates attendance registration using **Amazon Rekognition, Amazon S3, Amazon RDS MySQL, Amazon SNS, Python, and Streamlit**.

**Status:** ✅ Completed | Locally Tested | AWS Integration Implemented

---

## 📌 Overview

The **AWS AI-Based Smart Attendance System** is a facial-recognition-powered attendance application designed to automate the process of registering users, identifying faces, recording attendance, and notifying users when attendance is marked.

The application provides a **Streamlit-based web interface** and supports an AWS-backed workflow using:

* **Amazon Rekognition** for facial recognition
* **Amazon S3** for storing registered face images
* **Amazon RDS MySQL** for user and attendance records
* **Amazon SNS** for attendance notifications

For development and testing, the project also includes local fallback mechanisms so the basic application can run without an active AWS environment.

---

## ✨ Key Features

### 👤 Facial Recognition

* Face registration workflow
* Face detection and recognition using InsightFace for local processing
* AWS Rekognition-based face indexing and searching
* Real-time recognition workflow
* Configurable face-match threshold
* Automated attendance identification

### 📝 Attendance Management

* Automatic attendance recording
* Timestamped attendance logs
* User registration
* Attendance reports
* Registered-user management
* Simulated attendance data for testing

### ☁️ AWS Integration

* Amazon Rekognition face collections
* Amazon S3 image storage
* Amazon RDS MySQL database
* Amazon SNS attendance notifications
* AWS configuration through external configuration
* Local fallback support when AWS services are unavailable

### 🌐 Web Application

Built with Streamlit and organized into:

* Home / Dashboard
* Real-Time Prediction
* Registration
* Reports

### 🔐 Authentication & Security

* Username/password authentication
* Password hashing
* Protected application functionality
* AWS credentials kept outside the repository
* Configuration separated from application code

---

## 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │     Streamlit UI     │
                         │  Dashboard / Pages   │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   │                                 │
                   ▼                                 ▼
          ┌─────────────────┐               ┌─────────────────┐
          │   Registration  │               │   Recognition   │
          │     Workflow    │               │    Workflow     │
          └────────┬────────┘               └────────┬────────┘
                   │                                 │
                   ▼                                 ▼
          ┌─────────────────┐               ┌─────────────────┐
          │   Amazon S3     │               │ Amazon           │
          │ Face Image      │──────────────►│ Rekognition      │
          │ Storage         │               │ Collection       │
          └─────────────────┘               └────────┬────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Amazon RDS      │
                                            │ MySQL           │
                                            │ Users + Logs    │
                                            └────────┬────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Amazon SNS      │
                                            │ Notifications   │
                                            └─────────────────┘
```

---

## 🔄 Attendance Workflow

### 1. User Registration

```text
User Details + Face Image
          ↓
       Streamlit
          ↓
      Amazon RDS
     User Record
          +
      Amazon S3
     Face Image
          ↓
   Amazon Rekognition
    Index Face
```

The application stores user information in RDS, uploads the face image to S3, and indexes the face in an Amazon Rekognition collection.

### 2. Attendance Recognition

```text
Camera / Image
      ↓
Face Recognition
      ↓
Amazon Rekognition
      ↓
Matched User
      ↓
Amazon RDS
Attendance Log
      ↓
Amazon SNS
Notification
```

When a face is matched, the system retrieves the associated user information from RDS, records the attendance event, and publishes an attendance notification through SNS.

---

## ☁️ AWS Services

| AWS Service            | Role                                            |
| ---------------------- | ----------------------------------------------- |
| **Amazon Rekognition** | Face collection, face indexing, and face search |
| **Amazon S3**          | Storage of registered face images               |
| **Amazon RDS MySQL**   | User and attendance data                        |
| **Amazon SNS**         | Attendance notification publishing              |

The repository contains AWS helper functionality for initializing these services and performing the corresponding operations.

---

## 🧠 Face Recognition

The project supports two complementary recognition paths:

### Local Processing

The local application uses **InsightFace** together with OpenCV for face detection and recognition.

### AWS Processing

The AWS-backed workflow uses **Amazon Rekognition** collections for registering and searching faces.

This allows the project to operate as a local demonstration while also supporting a cloud-backed deployment architecture.

---

## 🛠️ Technology Stack

### Application

* Python
* Streamlit
* OpenCV
* InsightFace
* NumPy
* Pandas

### Cloud

* Amazon Rekognition
* Amazon S3
* Amazon RDS
* Amazon SNS

### Database

* MySQL
* PyMySQL

### Configuration

* YAML configuration
* JSON configuration
* Environment/local configuration
* Shell scripts for setup

---

## 📂 Project Structure

```text
AWS-AI-Based-Smart-Attendance-System/
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   ├── style.css
│   └── tech_bg.png
│
├── insightface_model/
│   └── models/
│       └── buffalo_sc/
│
├── pages/
│   ├── 1_Real_Time_Prediction.py
│   ├── 2_Registration_form.py
│   └── 3_Report.py
│
├── Screenshots/
│
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
├── simulated_logs.txt
└── README.md
```

---

## 🖥️ Application Pages

### 🏠 Home / Dashboard

Provides the main application interface and navigation.

### 📷 Real-Time Prediction

Uses the face-recognition workflow to identify registered users and record attendance.

### 👤 Registration

Allows users to register their information and facial data.

### 📊 Reports

Displays attendance records and reporting information.

---

## 🔐 Security

The project includes:

* Password hashing
* Protected application functionality
* External AWS configuration
* `.gitignore` protection for local configuration
* Separation of sensitive configuration from source code

### Important

Never commit:

```text
AWS access keys
AWS secret keys
RDS passwords
Database credentials
SNS topic secrets
Private configuration
```

The repository provides an example AWS configuration file instead of requiring credentials to be committed.

---

## 🧪 Testing & Development

The repository includes:

* AWS connectivity/testing utilities
* RDS checking functionality
* Simulated attendance logs
* Local fallback storage
* Manual recognition testing
* Application screenshots

The project has been tested locally on Windows with:

* Face recognition
* User registration
* Attendance processing
* Streamlit interface
* Reports
* Local fallback storage

---

## 💻 Local Setup

### Requirements

* Windows 10 / 11
* Python 3.x
* Git
* Modern web browser

### 1. Clone

```bash
git clone https://github.com/MusaibParvez07/AWS-AI-Based-Smart-Attendance-System.git

cd AWS-AI-Based-Smart-Attendance-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate it

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Start the application

```bash
python -m streamlit run Home.py
```

Open:

```text
http://localhost:8501
```

---

## ☁️ AWS Configuration

The repository contains:

```text
aws_config.example.json
```

The AWS-backed workflow requires appropriate configuration for:

* AWS credentials
* AWS region
* S3 bucket
* Rekognition collection
* RDS MySQL instance
* SNS topic

The application checks whether the AWS configuration is available before using the cloud-backed workflow.

Without AWS configuration, the local development/fallback workflow can still be used.

---

## 📸 Screenshots

Application screenshots are available in:

```text
Screenshots/
```

Recommended screenshots to showcase:

1. Home Dashboard
2. Registration
3. Real-Time Face Recognition
4. Attendance Result
5. Attendance Report

---

## 📊 Database Design

The AWS-backed database contains two primary logical entities:

### Users

Stores registered user information including:

* Name
* Role
* Course
* Year
* Address
* Contact
* Email
* Registration timestamp

### Attendance Logs

Stores:

* User name
* Role
* Attendance timestamp

The repository creates these MySQL tables through the AWS helper when the configured RDS environment is initialized.

---

## 🚀 Project Status

**Completed and locally tested.**

The current version provides a functional local Streamlit application and contains an AWS-backed integration layer for:

**Rekognition + S3 + RDS MySQL + SNS**

The project can be extended toward a fully cloud-hosted deployment.

---

## 🗺️ Future Improvements

* [ ] Full production AWS deployment
* [ ] EC2-based application hosting
* [ ] Serverless processing using AWS Lambda
* [ ] CloudWatch monitoring and logging
* [ ] IAM role-based access instead of long-lived credentials
* [ ] Improved face-recognition accuracy
* [ ] Real-time camera optimization
* [ ] Advanced attendance analytics
* [ ] Exportable attendance reports
* [ ] Multi-user administration
* [ ] Managed cloud deployment pipeline
* [ ] Improved API architecture
* [ ] CI/CD integration

---

## 🎯 Key Learning Areas

This project provided hands-on experience with:

**Computer Vision • Facial Recognition • AWS Cloud Services • Cloud Databases • Object Storage • Event Notifications • Python • Streamlit • MySQL • Authentication • Cloud Integration**
---

⭐ If you find this project useful or interesting, feel free to explore the repository.
