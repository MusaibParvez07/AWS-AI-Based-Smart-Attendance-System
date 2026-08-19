AWS AI-Based Smart Attendance System

An AWS-based, serverless facial recognition attendance system designed to automate attendance check-ins, recognition, database management, and real-time notifications.

📌 Overview

The AWS AI-Based Smart Attendance System replaces manual attendance processes with an automated facial recognition workflow.

The system uses facial recognition to identify registered users, record attendance, store user and attendance information, and send real-time notifications when attendance is marked.

✨ Features

Facial recognition-based attendance

Real-time attendance check-in

User registration

Attendance records and reports

Cloud-based image storage

Automated database management

Real-time attendance notifications

Serverless processing

Secure cloud access and resource management

Monitoring and logging

☁️ AWS Services Used

AWS Service

Purpose

Amazon Rekognition

Facial recognition and face matching

Amazon EC2

Cloud-based application hosting

Amazon S3

Storage of images and application data

Amazon SNS

Real-time attendance notifications

AWS Lambda

Serverless processing and automation

Amazon RDS

Database for user and attendance records

Amazon CloudWatch

Monitoring and logging

AWS IAM

Identity and access management

🛠️ Technologies

Python

Streamlit

OpenCV

InsightFace

MySQL

PyMySQL

AWS Cloud Services

🔄 How It Works

A user registers with their personal information and facial data.

The facial data is processed using the facial recognition system.

Amazon Rekognition identifies registered users during attendance.

Attendance information is stored in Amazon RDS.

Images and required files are stored using Amazon S3.

AWS Lambda handles serverless processing and automation.

Amazon SNS sends real-time attendance notifications.

Amazon CloudWatch provides monitoring and logging.

AWS IAM manages secure access to AWS resources.

📂 Project Structure

AWS-AI-Based-Smart-Attendance-System/
│
├── .streamlit/
├── assets/
├── insightface_model/
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

🏠 Home

Main dashboard and navigation.

📷 Real-Time Prediction

Recognizes registered users and processes attendance.

👤 Registration

Registers users and their facial information.

📊 Reports

Displays attendance records and reports.

📸 Screenshots

Home Page



Attendance Page



Registration Page



Report Page



Application View



Application View



🔐 Security

The project uses authentication and AWS IAM-based access management to protect application and cloud resources.

Sensitive credentials such as AWS access keys, database passwords, and private configuration should never be committed to the repository.

🚀 Setup

Clone the Repository

git clone https://github.com/MusaibParvez07/AWS-AI-Based-Smart-Attendance-System.git
cd AWS-AI-Based-Smart-Attendance-System

Create Virtual Environment

python -m venv venv

Activate Environment

Windows:

venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt

Run the Application

python -m streamlit run Home.py

The application will be available at:

http://localhost:8501

📊 Database

The system uses Amazon RDS with MySQL for storing:

User information

Attendance records

Attendance timestamps

🎯 Project Highlights

Built a cloud-based facial recognition attendance solution

Integrated multiple AWS services into a single application

Implemented serverless processing using AWS Lambda

Used Amazon Rekognition for facial recognition

Used Amazon S3 for cloud storage

Used Amazon RDS for database management

Used Amazon SNS for real-time notifications

Used Amazon CloudWatch for monitoring

Used AWS IAM for secure AWS resource access

