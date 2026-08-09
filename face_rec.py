import numpy as np
import pandas as pd
import cv2
# from auth import authenticator
import redis

# insight face
from insightface.app import FaceAnalysis
from sklearn.metrics import pairwise
# time
import time
from datetime import datetime

import os
import pickle

class LocalRedisFallback:
    def __init__(self, filepath='local_redis_db.pkl'):
        self.filepath = filepath
        self.db = {'hashes': {}, 'lists': {}}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'rb') as f:
                    self.db = pickle.load(f)
            except Exception as e:
                print(f"Error loading local DB: {e}")
                self.db = {'hashes': {}, 'lists': {}}
        else:
            self.db = {'hashes': {}, 'lists': {}}
            
        # Seed simulated logs if list is empty
        list_name = b'attendance:logs'
        if list_name not in self.db['lists'] or not self.db['lists'][list_name]:
            self.db['lists'][list_name] = []
            if os.path.exists('simulated_logs.txt'):
                try:
                    with open('simulated_logs.txt', 'r', encoding='utf-8') as f:
                        logs_text = f.read()
                    encoded_logs = [line.strip().encode('utf-8') for line in logs_text.split('\n') if line.strip()]
                    self.db['lists'][list_name] = encoded_logs
                    self.save()
                    print("Seeded local DB with simulated logs.")
                except Exception as e:
                    print(f"Error seeding simulated logs: {e}")

    def save(self):
        try:
            with open(self.filepath, 'wb') as f:
                pickle.dump(self.db, f)
        except Exception as e:
            print(f"Error saving local DB: {e}")

    def hset(self, name, key, value):
        if isinstance(name, str):
            name = name.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(value, str):
            value = value.encode('utf-8')
        
        if name not in self.db['hashes']:
            self.db['hashes'][name] = {}
        self.db['hashes'][name][key] = value
        self.save()
        return 1

    def hgetall(self, name):
        if isinstance(name, str):
            name = name.encode('utf-8')
        return self.db['hashes'].get(name, {})

    def lpush(self, name, *values):
        if isinstance(name, str):
            name = name.encode('utf-8')
        if name not in self.db['lists']:
            self.db['lists'][name] = []
        for val in values:
            if isinstance(val, str):
                val = val.encode('utf-8')
            self.db['lists'][name].insert(0, val)
        self.save()
        return len(self.db['lists'][name])

    def lrange(self, name, start, end):
        if isinstance(name, str):
            name = name.encode('utf-8')
        lst = self.db['lists'].get(name, [])
        if end == -1:
            return lst[start:]
        else:
            return lst[start:end+1]
            
    def ping(self):
        return True

# Initialize database client
r = None
# 1. Try local Redis (e.g. if running in docker or local windows redis)

try:
    r_local = redis.StrictRedis(
        host='localhost',
        port=6379,
        socket_timeout=1.0,
        socket_connect_timeout=1.0
    )
    r_local.ping()
    r = r_local
    print("Connected to LOCAL Redis database.")
except Exception:
    # 2. Try remote Redis
    try:
        r_remote = redis.StrictRedis(
            host=os.getenv('REDIS_HOST', '13.233.200.165'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            password=os.getenv('REDIS_PASSWORD'),
            socket_timeout=2.0,
            socket_connect_timeout=2.0
        )
        r_remote.ping()
        r = r_remote
        print("Connected to REMOTE Redis database.")
    except Exception:
        # 3. Fallback to Local Pickled Database
        print("Could not connect to any Redis database. Falling back to local pickle database.")
        r = LocalRedisFallback()


# Retrive Data from database
def retrive_data(name):
    from aws_helper import aws
    if aws.is_configured():
        try:
            df = aws.get_registered_users()
            # Ensure it has facial_features column so code doesn't break
            if 'facial_features' not in df.columns:
                df['facial_features'] = None
            return df
        except Exception as e:
            print(f"Error retrieving AWS registered users: {e}")
            
    retrive_dict = r.hgetall(name)
    if not retrive_dict:
        return pd.DataFrame(columns=['Name','Role','facial_features'])
    retrive_series = pd.Series(retrive_dict)
    retrive_series = retrive_series.apply(lambda x: np.frombuffer(x,dtype=np.float32))
    index = retrive_series.index
    index = list(map(lambda x: x.decode(), index))
    retrive_series.index = index
    retrive_df =  retrive_series.to_frame().reset_index()
    retrive_df.columns = ['name_role','facial_features']
    retrive_df[['Name','Role']] = retrive_df['name_role'].apply(lambda x: x.split('@')).apply(pd.Series)
    return retrive_df[['Name','Role','facial_features']]


# Delete Data from database
def delete_user_data(name_to_delete, role_to_delete=None):
    from aws_helper import aws
    if aws.is_configured():
        try:
            return aws.delete_user(name_to_delete)
        except Exception as e:
            print(f"Error deleting AWS user: {e}")
            return False
    else:
        try:
            # Delete in local Redis mode
            key = f"{name_to_delete}@{role_to_delete}"
            if r.hexists(name='academy:register', key=key):
                r.hdel('academy:register', key)
                return True
            # Fallback (search by name only)
            for k in r.hkeys(name='academy:register'):
                k_str = k.decode('utf-8') if isinstance(k, bytes) else k
                if k_str.split('@')[0] == name_to_delete:
                    r.hdel('academy:register', k)
                    return True
            return False
        except Exception as e:
            print(f"Error deleting local user: {e}")
            return False


# configure face analysis
faceapp = None
from aws_helper import aws
if not aws.is_configured():
    print("AWS is not configured. Initializing local InsightFace model...")
    from insightface.app import FaceAnalysis
    faceapp = FaceAnalysis(name='buffalo_sc',root='insightface_model', providers = ['CPUExecutionProvider'])
    faceapp.prepare(ctx_id = 0, det_size=(640,640), det_thresh = 0.5)

# ML Search Algorithm
def ml_search_algorithm(dataframe,feature_column,test_vector,
                        name_role=['Name','Role'],thresh=0.5):
    """
    cosine similarity base search algorithm
    """
    # If dataframe is empty, return Unknown immediately
    if dataframe.empty:
        return 'Unknown', 'Unknown'
        
    # step-1: take the dataframe (collection of data)
    dataframe = dataframe.copy()
    # step-2: Index face embeding from the dataframe and convert into array
    X_list = dataframe[feature_column].tolist()
    x = np.asarray(X_list)
    
    # step-3: Cal. cosine similarity
    similar = pairwise.cosine_similarity(x,test_vector.reshape(1,-1))
    similar_arr = np.array(similar).flatten()
    dataframe['cosine'] = similar_arr

    # step-4: filter the data
    data_filter = dataframe.query(f'cosine >= {thresh}')
    if len(data_filter) > 0:
        # step-5: get the person name
        data_filter.reset_index(drop=True,inplace=True)
        argmax = data_filter['cosine'].argmax()
        person_name, person_role = data_filter.loc[argmax][name_role]
        
    else:
        person_name = 'Unknown'
        person_role = 'Unknown'
        
    return person_name, person_role


### Real Time Prediction
# we need to save logs for every 1 mins
class RealTimePred:
    def __init__(self):
        self.logs = dict(name=[],role=[],current_time=[])
        self.frame_count = 0
        self.last_box = None
        self.last_name = "Unknown"
        self.last_role = "Unknown"
        self.setTime = time.time()
        self.user_cache = {}
        self.load_user_cache()
        
    def load_user_cache(self):
        from aws_helper import aws
        if aws.is_configured():
            try:
                import pymysql
                conn = aws.get_db_connection()
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(f"USE {aws.config['rds_db_name']}")
                cursor.execute("SELECT id, name, role FROM users")
                rows = cursor.fetchall()
                for row in rows:
                    self.user_cache[row['id']] = {
                        'name': row['name'],
                        'role': row['role']
                    }
                cursor.close()
                conn.close()
                print(f"Loaded {len(self.user_cache)} users into local cache.")
            except Exception as e:
                print(f"Error loading user cache: {e}")
        
    def reset_dict(self):
        self.logs = dict(name=[],role=[],current_time=[])
        
    def saveLogs_redis(self):
        from aws_helper import aws
        if aws.is_configured():
            dataframe = pd.DataFrame(self.logs)        
            dataframe.drop_duplicates('name', inplace=True) 
            name_list = dataframe['name'].tolist()
            role_list = dataframe['role'].tolist()
            
            for name, role in zip(name_list, role_list):
                if name != 'Unknown':
                    # Log attendance in RDS MySQL and notify via SNS
                    aws.log_attendance(name, role)
            self.reset_dict()
        else:
            # step-1: create a logs dataframe
            dataframe = pd.DataFrame(self.logs)        
            # step-2: drop the duplicate information (distinct name)
            dataframe.drop_duplicates('name',inplace=True) 
            # step-3: push data to redis database (list)
            # encode the data
            name_list = dataframe['name'].tolist()
            role_list = dataframe['role'].tolist()
            ctime_list = dataframe['current_time'].tolist()
            encoded_data = []
            for name, role, ctime in zip(name_list, role_list, ctime_list):
                if name != 'Unknown':
                    concat_string = f"{name}@{role}@{ctime}"
                    encoded_data.append(concat_string)
                    
            if len(encoded_data) >0:
                r.lpush('attendance:logs',*encoded_data)
            
                        
            self.reset_dict()     
        
        
    def face_prediction(self,test_image, dataframe,feature_column,
                            name_role=['Name','Role'],thresh=0.5):
        from aws_helper import aws
        if aws.is_configured():
            current_time = str(datetime.now())
            self.frame_count += 1
            
            # Throttle: Strictly call Rekognition only once every 10 frames
            if self.frame_count % 10 == 0:
                success, encoded_image = cv2.imencode('.jpg', test_image)
                if success:
                    image_bytes = encoded_image.tobytes()
                    try:
                        response = aws.rekognition.search_faces_by_image(
                            CollectionId=aws.config['rekognition_collection_id'],
                            Image={'Bytes': image_bytes},
                            MaxFaces=1,
                            FaceMatchThreshold=80.0
                        )
                        
                        box = response.get('SearchedFaceBoundingBox')
                        if box:
                            self.last_box = box
                            face_matches = response.get('FaceMatches')
                            person_name, person_role = "Unknown", "Unknown"
                            if face_matches:
                                match = face_matches[0]
                                external_image_id = match['Face']['ExternalImageId']
                                user_id = int(external_image_id.split('_')[1])
                                
                                # Resolve name and role using local cache (0ms)
                                if user_id in self.user_cache:
                                    person_name = self.user_cache[user_id]['name']
                                    person_role = self.user_cache[user_id]['role']
                                else:
                                    # Fallback: Query RDS MySQL once for new user
                                    try:
                                        import pymysql
                                        conn = aws.get_db_connection()
                                        cursor = conn.cursor(pymysql.cursors.DictCursor)
                                        cursor.execute(f"USE {aws.config['rds_db_name']}")
                                        cursor.execute("SELECT name, role FROM users WHERE id = %s", (user_id,))
                                        user = cursor.fetchone()
                                        cursor.close()
                                        conn.close()
                                        if user:
                                            person_name = user['name']
                                            person_role = user['role']
                                            # Cache it
                                            self.user_cache[user_id] = {
                                                'name': person_name,
                                                'role': person_role
                                            }
                                    except Exception as e:
                                        print(f"Error querying user ID {user_id}: {e}")
                            
                            self.last_name = person_name
                            self.last_role = person_role
                        else:
                            self.last_box = None
                            self.last_name = "Unknown"
                            self.last_role = "Unknown"
                    except Exception as e:
                        # Reset tracking if no face is detected or error occurs
                        print(f"AWS Rekognition Error: {e}")
                        self.last_box = None
                        self.last_name = "Unknown"
                        self.last_role = "Unknown"
            
            # Draw tracking box and label using cached/last-detected parameters
            test_copy = test_image.copy()
            h, w, _ = test_image.shape
            
            if self.last_box:
                x1 = int(self.last_box['Left'] * w)
                y1 = int(self.last_box['Top'] * h)
                x2 = int((self.last_box['Left'] + self.last_box['Width']) * w)
                y2 = int((self.last_box['Top'] + self.last_box['Height']) * h)
                
                color = (0, 255, 0) if self.last_name != "Unknown" else (0, 0, 255)
                cv2.rectangle(test_copy, (x1, y1), (x2, y2), color, 2)
                
                cv2.putText(test_copy, self.last_name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2)
                cv2.putText(test_copy, current_time, (x1, y2 + 20), cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2)
                
                self.logs['name'].append(self.last_name)
                self.logs['role'].append(self.last_role)
                self.logs['current_time'].append(current_time)
                
            return test_copy
        else:
            # step-1: find the time
            current_time = str(datetime.now())
            
            # step-1: take the test image and apply to insight face
            test_copy = test_image.copy()
            if faceapp is not None:
                results = faceapp.get(test_image)
                # step-2: use for loop and extract each embedding and pass to ml_search_algorithm
                for res in results:
                    x1, y1, x2, y2 = res['bbox'].astype(int)
                    embeddings = res['embedding']
                    person_name, person_role = ml_search_algorithm(dataframe,
                                                                feature_column,
                                                                test_vector=embeddings,
                                                                name_role=name_role,
                                                                thresh=thresh)
                    if person_name == 'Unknown':
                        color =(0,0,255) # bgr
                    else:
                        color = (0,255,0)

                    cv2.rectangle(test_copy,(x1,y1),(x2,y2),color)

                    text_gen = person_name
                    cv2.putText(test_copy,text_gen,(x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.7,color,2)
                    cv2.putText(test_copy,current_time,(x1,y2+10),cv2.FONT_HERSHEY_DUPLEX,0.7,color,2)
                    # save info in logs dict
                    self.logs['name'].append(person_name)
                    self.logs['role'].append(person_role)
                    self.logs['current_time'].append(current_time)
                
            return test_copy


#### Registration Form
class RegistrationForm:
    def __init__(self):
        self.sample = 0
        self.latest_frame = None
    def reset(self):
        self.sample = 0
        self.latest_frame = None
        
    def get_embedding(self,frame):
        from aws_helper import aws
        if aws.is_configured():
            # In AWS Mode, we save the current frame temporarily in memory
            self.latest_frame = frame.copy()
            
            # Draw a nice green rectangle in the center for user framing/feedback
            h, w, _ = frame.shape
            cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (0, 255, 0), 2)
            cv2.putText(frame, "Align Face Here", (w//4, h//4 - 10), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)
            self.sample = 1
            return frame, None
            
        # Local fallback mode using preloaded faceapp
        if faceapp is not None:
            try:
                results = faceapp.get(frame,max_num=1)
                embeddings = None
                for res in results:
                    self.sample += 1
                    x1, y1, x2, y2 = res['bbox'].astype(int)
                    cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0),1)
                    text = f"samples = {self.sample}"
                    cv2.putText(frame,text,(x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.6,(255,255,0),2)
                    embeddings = res['embedding']
                return frame, embeddings
            except Exception as e:
                print(f"InsightFace error: {e}")
                
        # Draw fallback box if local InsightFace is not initialized/working
        h, w, _ = frame.shape
        cv2.rectangle(frame, (w//4, h//4), (3*w//4, 3*h//4), (255, 255, 0), 1)
        cv2.putText(frame, "Align Face", (w//4, h//4 - 10), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 0), 1)
        self.sample = 1
        return frame, None
    
    def save_data_in_redis_db(self,name,role,course='',year_level='',address='',contact='',email=''):
        from aws_helper import aws
        if aws.is_configured():
            if name is None or name.strip() == '':
                return 'name_false'
            
            if self.latest_frame is None:
                return 'file_false'
                
            try:
                # Convert the in-memory frame to JPEG bytes
                success, encoded_image = cv2.imencode('.jpg', self.latest_frame)
                if not success:
                    return 'file_false'
                image_bytes = encoded_image.tobytes()
                    
                # Register user in AWS S3, RDS MySQL and Rekognition Collection
                aws.register_user(name, role, course, year_level, address, contact, email, image_bytes)
                
                self.reset()
                return True
            except Exception as e:
                print(f"AWS registration failed: {e}")
                return str(e)
        else:
            # Validation name
            if name is not None:
                if name.strip() != '':
                    key = f'{name}@{role}'
                else:
                    return 'name_false'
            else:
                return 'name_false'
            
            # If face_embedding.txt exists
            if 'face_embedding.txt' not in os.listdir():
                return 'file_false'
            
            # Step-1: load "face_embedding.txt"
            x_array = np.loadtxt('face_embedding.txt',dtype=np.float32) # flatten array            
            
            # Step-2: convert into array (proper shape)
            received_samples = int(x_array.size/512)
            x_array = x_array.reshape(received_samples,512)
            x_array = np.asarray(x_array)       
            
            # Step-3: cal. mean embeddings
            x_mean = x_array.mean(axis=0)
            x_mean = x_mean.astype(np.float32)
            x_mean_bytes = x_mean.tobytes()
            
            # Step-4: save this into redis database
            r.hset(name='academy:register',key=key,value=x_mean_bytes)
            
            # Cleanup
            os.remove('face_embedding.txt')
            self.reset()
            
            return True


def apply_custom_css():
    import streamlit as st
    import os
    import base64
    
    # Initialize theme mode in session state
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'dark'
        
    # Render the native toggle switch inside the sidebar globally
    with st.sidebar:
        st.write("---")
        st.write("⚙️ **Preferences**")
        is_light = st.toggle(
            "White Screen Mode", 
            value=(st.session_state.theme_mode == 'light'),
            key="theme_toggle_switch"
        )
        new_mode = 'light' if is_light else 'dark'
        if new_mode != st.session_state.theme_mode:
            st.session_state.theme_mode = new_mode
            st.rerun()
        
    bg_base64 = ""
    bg_path = os.path.join(os.path.dirname(__file__), 'assets', 'tech_bg.png')
    if os.path.exists(bg_path):
        with open(bg_path, 'rb') as f:
            bg_data = f.read()
        bg_base64 = base64.b64encode(bg_data).decode('utf-8')
        
    css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()
            
        if bg_base64:
            # Replace target background styling in CSS
            target = "background-image: radial-gradient(circle at 10% 20%, rgba(0, 242, 254, 0.03) 0%, transparent 40%),\n                      radial-gradient(circle at 90% 80%, rgba(79, 172, 254, 0.03) 0%, transparent 40%) !important;"
            replacement = f"background-image: linear-gradient(rgba(7, 8, 13, 0.94), rgba(7, 8, 13, 0.94)), url('data:image/png;base64,{bg_base64}') !important;\n    background-size: cover !important;\n    background-position: center !important;\n    background-attachment: fixed !important;"
            css = css.replace(target, replacement)
            
        # Append readable light mode overrides if enabled
        if st.session_state.get('theme_mode', 'dark') == 'light':
            light_overrides = """
            /* Readable Light Theme Overrides */
            html, body, [data-testid="stAppViewContainer"] {
                background-color: #F8F9FA !important;
                background-image: none !important;
                color: #212529 !important;
            }
            [data-testid="stSidebar"] {
                background: #E9ECEF !important;
                border-right: 1px solid #DEE2E6 !important;
                box-shadow: none !important;
            }
            /* Ensure sidebar navigation labels are completely visible */
            [data-testid="stSidebar"] * {
                color: #212529 !important;
            }
            h1, h2, h3, h4, h5, h6 {
                background: none !important;
                -webkit-background-clip: unset !important;
                -webkit-text-fill-color: #212529 !important;
                color: #212529 !important;
            }
            div.stAlert, 
            div[data-testid="stMetric"], 
            div[data-testid="stVerticalBlock"] > div > div[data-testid="element-container"] > div.stMarkdownBlock {
                background: #FFFFFF !important;
                border: 1px solid #CED4DA !important;
                color: #212529 !important;
                box-shadow: none !important;
            }
            .stTextInput > div > div > input, 
            .stSelectbox > div > div, 
            .stTextArea > div > div > textarea {
                background-color: #FFFFFF !important;
                border: 1px solid #CED4DA !important;
                color: #212529 !important;
            }
            button[data-baseweb="tab"] {
                color: #495057 !important;
            }
            button[data-baseweb="tab"][aria-selected="true"] {
                color: #007BFF !important;
                border-bottom: 2px solid #007BFF !important;
                text-shadow: none !important;
            }
            div[data-testid="stDataFrame"] {
                background: #FFFFFF !important;
                border: 1px solid #CED4DA !important;
            }
            div.stSuccess {
                background-color: #D4EDDA !important;
                border-color: #C3E6CB !important;
                color: #155724 !important;
            }
            div.stInfo {
                background-color: #D1ECF1 !important;
                border-color: #BEE5EB !important;
                color: #0C5460 !important;
            }
            div.stError {
                background-color: #F8D7DA !important;
                border-color: #F5C6CB !important;
                color: #721C24 !important;
            }
            """
            css += light_overrides
            
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)