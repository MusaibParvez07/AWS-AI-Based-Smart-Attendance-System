import json
import os
import pymysql
import boto3

CONFIG_PATH = 'aws_config.json'

def test_aws():
    print("==================================================")
    print("         AWS INTEGRATION TEST SCRIPT             ")
    print("==================================================")
    
    if not os.path.exists(CONFIG_PATH):
        print(f"[-] Error: {CONFIG_PATH} file not found!")
        return

    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"[-] Error parsing {CONFIG_PATH}: {e}")
        return

    # Check config values
    if config.get('aws_access_key_id') == 'YOUR_AWS_ACCESS_KEY_ID' or config.get('rds_host') == 'YOUR_RDS_ENDPOINT_HOST':
        print("[!] Warning: Please update aws_config.json with your actual credentials first!")
        return

    # Initialize Session
    session = boto3.Session(
        aws_access_key_id=config['aws_access_key_id'],
        aws_secret_access_key=config['aws_secret_access_key'],
        region_name=config['aws_region']
    )

    # 1. Test S3
    print("\n[1/4] Testing Amazon S3 Connection...")
    try:
        s3 = session.client('s3', region_name=config['s3_region'])
        bucket_name = config['s3_bucket_name']
        s3.head_bucket(Bucket=bucket_name)
        print(f"[+] SUCCESS: Connected to S3 bucket '{bucket_name}' successfully.")
    except Exception as e:
        print(f"[-] FAILED: S3 Connection failed. Error: {e}")

    # 2. Test Rekognition
    print("\n[2/4] Testing Amazon Rekognition...")
    try:
        rekognition = session.client('rekognition', region_name=config['rekognition_region'])
        collection_id = config['rekognition_collection_id']
        try:
            rekognition.describe_collection(CollectionId=collection_id)
            print(f"[+] SUCCESS: Rekognition collection '{collection_id}' exists and is accessible.")
        except rekognition.exceptions.ResourceNotFoundException:
            rekognition.create_collection(CollectionId=collection_id)
            print(f"[+] SUCCESS: Created Rekognition collection '{collection_id}' successfully.")
    except Exception as e:
        print(f"[-] FAILED: Rekognition Connection failed. Error: {e}")

    # 3. Test RDS MySQL
    print("\n[3/4] Testing Amazon RDS MySQL Connection...")
    try:
        conn = pymysql.connect(
            host=config['rds_host'],
            user=config['rds_user'],
            password=config['rds_password'],
            port=3306,
            autocommit=True,
            connect_timeout=5
        )
        print("[+] SUCCESS: Connected to RDS MySQL Database server.")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['rds_db_name']}")
        cursor.execute(f"USE {config['rds_db_name']}")
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"[+] SUCCESS: Running MySQL Version: {version[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[-] FAILED: RDS MySQL Connection failed. Error: {e}")
        print("    (Make sure your RDS instance has 'Public access' enabled and its security group allows inbound TCP port 3306 traffic from your IP.)")

    # 4. Test SNS
    print("\n[4/4] Testing Amazon SNS Alert...")
    try:
        sns = session.client('sns', region_name=config['sns_region'])
        topic_arn = config['sns_topic_arn']
        response = sns.publish(
            TopicArn=topic_arn,
            Subject="AWS Integration Test",
            Message="This is a test notification from your local Face Recognition Attendance System script."
        )
        print(f"[+] SUCCESS: Message published to SNS Topic. MessageId: {response['MessageId']}")
    except Exception as e:
        print(f"[-] FAILED: SNS publish failed. Error: {e}")

    print("\n==================================================")
    print("                 TEST COMPLETED                   ")
    print("==================================================")

if __name__ == '__main__':
    test_aws()
