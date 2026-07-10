import os
import json
import pymysql
import boto3
import pandas as pd
from datetime import datetime

# Path to AWS Configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'aws_config.json')

class AWSHelper:
    def __init__(self):
        self.config = {}
        self.load_config()
        self._setup_verified = False
        
        # Initialize AWS Sessions and Clients if config is provided
        if self.is_configured():
            self.session = boto3.Session(
                aws_access_key_id=self.config['aws_access_key_id'],
                aws_secret_access_key=self.config['aws_secret_access_key'],
                region_name=self.config['aws_region']
            )
            self.s3 = self.session.client('s3', region_name=self.config['s3_region'])
            self.rekognition = self.session.client('rekognition', region_name=self.config['rekognition_region'])
            self.sns = self.session.client('sns', region_name=self.config['sns_region'])
        else:
            print("WARNING: AWS credentials/configuration are not yet filled in aws_config.json.")

    def verify_setup(self):
        """
        Lazily verifies and creates the Rekognition Collection and RDS SQL tables.
        """
        if not self.is_configured() or self._setup_verified:
            return
            
        try:
            self.create_rekognition_collection()
            self.create_tables()
            self._setup_verified = True
        except Exception as e:
            print(f"Error during lazy AWS setup verification: {e}")

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error reading aws_config.json: {e}")
                self.config = {}

    def is_configured(self):
        return (self.config and 
                self.config.get('aws_access_key_id') != 'YOUR_AWS_ACCESS_KEY_ID' and
                self.config.get('rds_host') != 'YOUR_RDS_ENDPOINT_HOST')

    def get_db_connection(self):
        if not self.is_configured():
            raise ValueError("AWS RDS configuration is missing in aws_config.json.")
        
        # Connect to MySQL (initially without database to create it if it doesn't exist)
        conn = pymysql.connect(
            host=self.config['rds_host'],
            user=self.config['rds_user'],
            password=self.config['rds_password'],
            port=3306,
            autocommit=True
        )
        return conn

    def create_tables(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Create database
        db_name = self.config['rds_db_name']
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                role VARCHAR(100) NOT NULL,
                course VARCHAR(100),
                year_level VARCHAR(100),
                address TEXT,
                contact VARCHAR(50),
                email VARCHAR(255),
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create attendance_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                role VARCHAR(100) NOT NULL,
                timestamp DATETIME NOT NULL
            )
        """)
        
        # Seed simulated logs if database is empty
        cursor.execute("SELECT COUNT(*) FROM attendance_logs")
        count = cursor.fetchone()[0]
        if count == 0:
            if os.path.exists('simulated_logs.txt'):
                try:
                    with open('simulated_logs.txt', 'r', encoding='utf-8') as f:
                        logs_text = f.read()
                    
                    lines = [line.strip() for line in logs_text.split('\n') if line.strip()]
                    batch_data = []
                    for line in lines:
                        parts = line.split('@')
                        if len(parts) == 3:
                            name, role, time_str = parts
                            # Parse timestamp
                            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                            batch_data.append((name, role, dt))
                    
                    if batch_data:
                        cursor.executemany("""
                            INSERT INTO attendance_logs (name, role, timestamp)
                            VALUES (%s, %s, %s)
                        """, batch_data)
                        print(f"Seeded RDS MySQL database with {len(batch_data)} simulated logs.")
                except Exception as e:
                    print(f"Error seeding RDS MySQL logs: {e}")
        
        cursor.close()
        conn.close()
        print("RDS MySQL Database & Tables verified/created successfully.")

    def create_rekognition_collection(self):
        collection_id = self.config['rekognition_collection_id']
        try:
            # Check if collection exists
            self.rekognition.describe_collection(CollectionId=collection_id)
            print(f"Rekognition Collection '{collection_id}' already exists.")
        except self.rekognition.exceptions.ResourceNotFoundException:
            # Create collection
            self.rekognition.create_collection(CollectionId=collection_id)
            print(f"Created Rekognition Collection '{collection_id}' successfully.")

    def register_user(self, name, role, course, year_level, address, contact, email, image_bytes):
        """
        Registers user details in RDS, uploads face image to S3, and indexes it in AWS Rekognition.
        """
        self.verify_setup()
        if not self.is_configured():
            raise ValueError("AWS configuration is missing.")
            
        # 1. Save user details to RDS MySQL
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"USE {self.config['rds_db_name']}")
        
        cursor.execute("""
            INSERT INTO users (name, role, course, year_level, address, contact, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, role, course, year_level, address, contact, email))
        
        # Get generated user ID
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        # 2. Upload photo to S3
        file_name = f"user_{user_id}.jpg"
        bucket_name = self.config['s3_bucket_name']
        self.s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=image_bytes,
            ContentType='image/jpeg'
        )
        print(f"Uploaded photo to S3: {bucket_name}/{file_name}")
        
        # 3. Index face in AWS Rekognition Collection
        collection_id = self.config['rekognition_collection_id']
        response = self.rekognition.index_faces(
            CollectionId=collection_id,
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_name
                }
            },
            ExternalImageId=f"user_{user_id}",
            MaxFaces=1,
            DetectionAttributes=['ALL']
        )
        
        if not response.get('FaceRecords'):
            # Rollback DB insert if no face detected in image
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {self.config['rds_db_name']}")
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            cursor.close()
            conn.close()
            
            # Delete S3 object
            self.s3.delete_object(Bucket=bucket_name, Key=file_name)
            raise ValueError("No face detected in the captured image. Please try again with a clear photo.")
            
        print(f"Indexed face in Rekognition for User ID: {user_id}")
        return True

    def search_face(self, image_bytes):
        """
        Searches AWS Rekognition collection using input image bytes.
        Returns (name, role, user_id) if matched, otherwise ("Unknown", "Unknown", None).
        """
        self.verify_setup()
        if not self.is_configured():
            return "Unknown", "Unknown", None
            
        collection_id = self.config['rekognition_collection_id']
        try:
            response = self.rekognition.search_faces_by_image(
                CollectionId=collection_id,
                Image={'Bytes': image_bytes},
                MaxFaces=1,
                FaceMatchThreshold=80.0
            )
            
            face_matches = response.get('FaceMatches')
            if face_matches:
                match = face_matches[0]
                external_image_id = match['Face']['ExternalImageId'] # e.g. "user_12"
                user_id_str = external_image_id.split('_')[1]
                user_id = int(user_id_str)
                
                # Fetch user details from RDS MySQL
                conn = self.get_db_connection()
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(f"USE {self.config['rds_db_name']}")
                cursor.execute("SELECT name, role FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if user:
                    return user['name'], user['role'], user_id
                    
        except Exception as e:
            print(f"Error searching face in Rekognition: {e}")
            
        return "Unknown", "Unknown", None

    def log_attendance(self, name, role):
        """
        Logs attendance in RDS MySQL and publishes alert to Amazon SNS.
        """
        self.verify_setup()
        if not self.is_configured():
            return
            
        now = datetime.now()
        timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. Insert Log in RDS MySQL
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"USE {self.config['rds_db_name']}")
        cursor.execute("""
            INSERT INTO attendance_logs (name, role, timestamp)
            VALUES (%s, %s, %s)
        """, (name, role, now))
        cursor.close()
        conn.close()
        print(f"Logged attendance in MySQL for: {name}")
        
        # 2. Publish email alert to Amazon SNS
        topic_arn = self.config['sns_topic_arn']
        message = f"Attendance Marked!\n\nName: {name}\nRole: {role}\nTime: {timestamp_str}\n\nThis is an automated alert from your Face Recognition Attendance System."
        try:
            self.sns.publish(
                TopicArn=topic_arn,
                Subject="Attendance Notification Alert",
                Message=message
            )
            print(f"Sent email alert via SNS to topic: {topic_arn}")
        except Exception as e:
            print(f"Error publishing to SNS topic: {e}")

    def delete_user(self, name):
        """
        Deletes user record from RDS MySQL database, deletes their face image from S3, 
        and deletes their indexed face from the AWS Rekognition collection.
        """
        self.verify_setup()
        if not self.is_configured():
            return False
            
        conn = self.get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"USE {self.config['rds_db_name']}")
        
        # 1. Fetch user ID to locate S3 photo and Rekognition face
        cursor.execute("SELECT id FROM users WHERE name = %s", (name,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return False
            
        user_id = user['id']
        
        # 2. Delete from AWS Rekognition Collection
        collection_id = self.config['rekognition_collection_id']
        external_image_id = f"user_{user_id}"
        try:
            response = self.rekognition.list_faces(CollectionId=collection_id)
            face_id_to_delete = None
            for face in response.get('Faces', []):
                if face.get('ExternalImageId') == external_image_id:
                    face_id_to_delete = face.get('FaceId')
                    break
                    
            if face_id_to_delete:
                self.rekognition.delete_faces(
                    CollectionId=collection_id,
                    FaceIds=[face_id_to_delete]
                )
                print(f"Deleted face {face_id_to_delete} from Rekognition collection.")
        except Exception as e:
            print(f"Error deleting from Rekognition: {e}")
            
        # 3. Delete from S3 Bucket
        file_name = f"user_{user_id}.jpg"
        bucket_name = self.config['s3_bucket_name']
        try:
            self.s3.delete_object(
                Bucket=bucket_name,
                Key=file_name
            )
            print(f"Deleted {file_name} from S3 bucket '{bucket_name}'.")
        except Exception as e:
            print(f"Error deleting S3 object: {e}")
            
        # 4. Delete from RDS MySQL Database
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        return True

    def get_registered_users(self):
        """
        Retrieves all registered users from RDS MySQL.
        """
        self.verify_setup()
        if not self.is_configured():
            return pd.DataFrame(columns=['Name', 'Role'])
            
        conn = self.get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"USE {self.config['rds_db_name']}")
        cursor.execute("SELECT name AS Name, role AS Role FROM users")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return pd.DataFrame(rows)

    def get_attendance_logs(self):
        """
        Retrieves all attendance logs from RDS MySQL.
        """
        self.verify_setup()
        if not self.is_configured():
            return []
            
        conn = self.get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"USE {self.config['rds_db_name']}")
        cursor.execute("SELECT name, role, timestamp FROM attendance_logs ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format logs as bytes to match original face_rec/redis format (Name@Role@Timestamp)
        encoded_logs = []
        for row in rows:
            time_str = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            log_str = f"{row['name']}@{row['role']}@{time_str}"
            encoded_logs.append(log_str.encode('utf-8'))
            
        return encoded_logs

# Single instance of AWSHelper
aws = AWSHelper()
