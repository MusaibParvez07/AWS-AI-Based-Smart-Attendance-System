import json
import pymysql

# Load AWS configuration
try:
    with open('aws_config.json', 'r') as f:
        config = json.load(f)
except Exception as e:
    print(f"Error loading aws_config.json: {e}")
    exit(1)

print("Connecting to AWS RDS MySQL Database...")
try:
    conn = pymysql.connect(
        host=config['rds_host'],
        user=config['rds_user'],
        password=config['rds_password'],
        port=3306
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # Use database
    db_name = config['rds_db_name']
    cursor.execute(f"USE {db_name}")
    print(f"Connected successfully to database: {db_name}\n")
    
    # 1. Check users count and list
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()['count']
    print(f"--- Registered Users ({user_count} total) ---")
    
    cursor.execute("SELECT id, name, role, email, registered_at FROM users")
    users = cursor.fetchall()
    if users:
        for user in users:
            print(f"ID: {user['id']} | Name: {user['name']} | Role: {user['role']} | Email: {user['email']} | Registered: {user['registered_at']}")
    else:
        print("No users registered yet.")
        
    print("\n" + "="*50 + "\n")
    
    # 2. Check attendance logs count and list latest 5
    cursor.execute("SELECT COUNT(*) as count FROM attendance_logs")
    log_count = cursor.fetchone()['count']
    print(f"--- Attendance Logs ({log_count} total) ---")
    
    cursor.execute("SELECT id, name, role, timestamp FROM attendance_logs ORDER BY timestamp DESC LIMIT 5")
    logs = cursor.fetchall()
    if logs:
        print("Latest 5 Logs:")
        for log in logs:
            print(f"ID: {log['id']} | Name: {log['name']} | Role: {log['role']} | Time: {log['timestamp']}")
    else:
        print("No attendance logs recorded yet.")
        
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Connection Failed: {e}")
