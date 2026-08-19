☁️ AWS AI-Based Smart Attendance System

Cloud-based, serverless facial recognition attendance system built with AWS to automate attendance check-ins, recognition, database management, and real-time notifications.







📌 Overview

The AWS AI-Based Smart Attendance System automates attendance tracking using facial recognition and cloud services.

The system uses Amazon Rekognition for facial recognition and integrates AWS services for application deployment, cloud storage, database management, serverless processing, notifications, monitoring, and secure access management.

The application provides a Streamlit-based interface for registration, real-time prediction, attendance processing, and reporting.

✨ Key Features

👤 Facial Recognition

Facial recognition using Amazon Rekognition

Face registration and identification

Real-time attendance check-in

Automated attendance recording

Computer vision-based processing

☁️ Cloud-Based Architecture

Cloud deployment using Amazon EC2

Image and object storage using Amazon S3

Attendance and user data management using Amazon RDS

Serverless processing using AWS Lambda

Real-time notifications using Amazon SNS

Application monitoring using Amazon CloudWatch

Secure access management using AWS IAM

📊 Attendance Management

Automated attendance check-ins

User registration

Attendance record management

Attendance reports

Real-time notification after attendance

Centralized cloud-based data management

🌐 Streamlit Web Interface

The application provides separate pages for:

🏠 Home / Dashboard

📷 Real-Time Prediction

👤 Registration Form

📊 Reports

🔐 Security

AWS IAM-based access management

Authentication

Username/password-based access

Password hashing

Secure handling of cloud resources and credentials

☁️ AWS Services

AWS Service

Purpose

Amazon Rekognition

Facial recognition and face matching

Amazon EC2

Cloud application deployment and compute

Amazon S3

Cloud storage for application and facial data

Amazon SNS

Real-time attendance notifications

Amazon RDS

User and attendance data management

AWS Lambda

Serverless processing pipeline

Amazon CloudWatch

Monitoring and logging

AWS IAM

Identity and access management

🔄 System Workflow

                 User / Camera
                       │
                       ▼
              Facial Recognition
                       │
                       ▼
              Amazon Rekognition
                       │
                       ▼
                 AWS Lambda
              Serverless Pipeline
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
       Amazon S3   Amazon RDS   Amazon SNS
        Storage     Database   Notification
                                  │
                                  ▼
                         Real-Time Attendance
                            Notification

              EC2 → Application Deployment
              IAM → Access Management
              CloudWatch → Monitoring

Attendance Flow

User registers facial information.

Facial data is processed for recognition.

Amazon Rekognition identifies the registered user.

AWS Lambda supports the serverless processing workflow.

Attendance information is stored in Amazon RDS.

Required files and facial data are stored using Amazon S3.

Amazon SNS sends a real-time attendance notification.

Amazon CloudWatch provides monitoring and logging.

AWS IAM manages secure access to AWS resources.

🛠️ Technology Stack

Technology

Purpose

Python

Core application development and backend logic

Streamlit

Interactive web application interface

Amazon Rekognition

Facial recognition and face matching

Amazon EC2

Cloud deployment and compute

Amazon S3

Cloud object storage

Amazon SNS

Real-time notifications

Amazon RDS

Database management

AWS Lambda

Serverless processing

Amazon CloudWatch

Monitoring and logging

AWS IAM

Access and permissions management

OpenCV

Image and video processing

InsightFace

Face detection and recognition support

MySQL

Relational database

PyMySQL

Python-MySQL connectivity

NumPy

Numerical and image-data processing

Pandas

Attendance data processing and reporting

🧠 Concepts Demonstrated

Computer Vision

Computer vision techniques are used to process images and video frames for facial recognition and attendance automation.

Facial Recognition

Facial recognition identifies registered users using facial information and enables automated attendance check-ins.

Serverless Computing

AWS Lambda is used as part of the serverless processing pipeline, reducing the need to manage application servers for processing tasks.

Cloud Computing

AWS services provide the infrastructure required for deployment, storage, database management, processing, notifications, monitoring, and access control.

Cloud Storage

Amazon S3 provides scalable object storage for application and facial data.

Cloud Database

Amazon RDS provides managed relational database capabilities for user and attendance information.

Event Notifications

Amazon SNS enables real-time attendance notifications.

Monitoring

Amazon CloudWatch provides monitoring and logging capabilities for the cloud environment.

Identity and Access Management

AWS IAM controls access and permissions for AWS resources.

📂 Project Structure

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
│   ├── image-1.png
│   ├── image-2.png
│   ├── image-3.png
│   ├── image-4.png
│   ├── image-5.png
│   └── image-6.png
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

🖥️ Application Pages

🏠 Home / Dashboard

Provides the main application interface and navigation.

📷 Real-Time Prediction

Uses the facial recognition workflow to identify registered users and process attendance.

👤 Registration Form

Allows users to register their facial information for attendance recognition.

📊 Report

Displays attendance information and reporting data.

🔐 Security

AWS IAM-based identity and access management

Application authentication

Username/password-based access

Password hashing

Secure cloud resource access

Sensitive credentials excluded from source code

Configuration separated from application code

Never commit AWS access keys, secret keys, database passwords, or other sensitive credentials to the repository.

🚀 Setup

Requirements

Windows 10 / Windows 11

Python 3.x

Git

Modern web browser

1. Clone the Repository

git clone https://github.com/MusaibParvez07/AWS-AI-Based-Smart-Attendance-System.git
cd AWS-AI-Based-Smart-Attendance-System

2. Create a Virtual Environment

python -m venv venv

3. Activate the Virtual Environment

venv\Scripts\activate

4. Install Dependencies

python -m pip install -r requirements.txt

5. Start the Application

python -m streamlit run Home.py

Open the application:

http://localhost:8501

📸 Screenshots

🏠 Home Page



📋 Attendance Page



👤 Registration Page



📊 Report Page



🖥️ Application View



🖥️ Application View



🎯 Project Highlights

Built a cloud-based facial recognition attendance system

Integrated Amazon Rekognition for facial recognition

Used Amazon EC2 for cloud deployment

Used Amazon S3 for cloud storage

Used Amazon RDS for data management

Implemented AWS Lambda for serverless processing

Used Amazon SNS for real-time attendance notifications

Used Amazon CloudWatch for monitoring and logging

Used AWS IAM for secure access management

Developed an interactive Streamlit application

Automated attendance check-ins using facial recognition

📈 Future Improvements

Improved facial recognition accuracy

Real-time camera optimization

Enhanced attendance analytics

Exportable attendance reports

Multi-user administration

Advanced cloud automation

Improved API and documentation
