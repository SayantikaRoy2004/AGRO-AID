import os
import sqlite3
from datetime import datetime
import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf
from plyer import notification
import hashlib
import threading
import time
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
from pygame import mixer
import subprocess  
import tempfile
from tabulate import tabulate
from termcolor import colored

# Set page configuration
st.set_page_config(page_title='Your Personal Agro-Aid!', layout='wide')

# Load the model
saved_model_path = "models/1"
MODEL = tf.keras.models.load_model(saved_model_path)
CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

# Connect to SQLite database
conn = sqlite3.connect('plant_care.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS feedbacks (
        username TEXT,
        message TEXT,
        rating INTEGER,
        type TEXT
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS plant_tasks (
        username TEXT,
        task TEXT,
        plant_name TEXT,
        date TEXT,
        time TEXT
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS tasks_completed (
        username TEXT PRIMARY KEY,
        tasks_completed INTEGER
    )
''')

def display_alarm():
    st.title('Alarm')

    # Input field for username
    username = st.text_input('Username', help='Enter your username')

    # Input field for task
    task = st.text_input('Task', help='Enter the task related to plants')

    # Input field for plant name
    plant_name = st.text_input('Plant Name', help='Enter the name of the plant')

    # Input field for date using calendar picker
    date = st.date_input('Set Alarm Date', value=datetime.today())

    # Input field for alarm time
    alarm_time_str = st.text_input('Set Alarm Time (HH:MM:SS)', value='08:00:00')
    # Note: The default value is '08:00:00', users can replace it with their desired time in HH:MM:SS format

    # Convert input time string to datetime object
    try:
        alarm_time = datetime.strptime(alarm_time_str, '%H:%M:%S').time()
    except ValueError:
        st.error('Invalid time format. Please enter time in HH:MM:SS format.')
        return

    if st.button('Set Alarm'):
        set_alarm(username, task, plant_name, date, alarm_time)


def set_alarm(username, task, plant_name, date, alarm_time):
    audio_path = os.path.join(tempfile.mkdtemp(), "alarm.mp3")

    def alarm_thread():
        try:
            current_time = datetime.now()
            alarm_datetime = datetime.combine(date, alarm_time)
            while current_time < alarm_datetime:
                time_difference = alarm_datetime - current_time
                time.sleep(time_difference.total_seconds() + 1)
                current_time = datetime.now()

            message = f"Hi, {username}, it's time to {task} your {plant_name} plants!"
            tts = gTTS(text=message, lang='en')
            tts.save(audio_path)

            # Play the audio
            mixer.init()
            mixer.music.load(audio_path)
            mixer.music.play()
            while mixer.music.get_busy():
                time.sleep(1)

            # Save task to database
            conn = sqlite3.connect('plant_care.db', check_same_thread=False)
            save_task_to_database(conn, username, task, plant_name, date, alarm_time)
            conn.close()
            
            print('Alarm set successfully!')
        except Exception as e:
            print(f"Error setting alarm: {e}")

    threading.Thread(target=alarm_thread).start()

def save_task_to_database(conn, username, task, plant_name, date, time_input):
    try:
        c = conn.cursor()
        c.execute('INSERT INTO plant_tasks (username, task, plant_name, date, time) VALUES (?, ?, ?, ?, ?)',
                  (username, task, plant_name, date.strftime('%Y-%m-%d'), time_input.strftime('%H:%M:%S')))
        c.execute('INSERT OR IGNORE INTO tasks_completed (username, tasks_completed) VALUES (?, 0)', (username,))
        c.execute('UPDATE tasks_completed SET tasks_completed = tasks_completed + 1 WHERE username = ?', (username,))
        conn.commit()
        print("Task saved to database successfully:", username, task, plant_name, date, time_input)  # Print success message
    except Exception as e:
        print("Error saving task to database:", e)
        raise  # Raising the exception for better error reporting

directory_path = tempfile.mkdtemp()
print(f"Temporary directory created: {directory_path}")

# Set alarm audio file path within the temporary directory
audio_path = os.path.join(directory_path, "music/alarm.mp3")

# Set up sidebar
st.sidebar.title('Contents')
selected_language = 'en'  # Assuming English language by default

# Define page variable with a default value
page = st.sidebar.radio('Go to', ['Home', 'Disease Recognition', 'Treatment', 'News Updates', 
                                  'Plant Care Reminder','Leaderboard','Create Account', 'Log In','About', 'Log Out', 'Delete Account'])

# Function to check if user is logged in
def is_user_logged_in():
    return 'username' in st.session_state

# Function to get the username of the logged-in user
def get_logged_in_username():
    return st.session_state.username if is_user_logged_in() else None

# Homepage
if page == 'Home':
    st.title('🌿 Agro-Aid! 🔍')
    st.markdown("""
    Our mission is to help in identifying plant diseases efficiently. 
    Upload an image of a plant, and our system will analyze it to detect any signs of diseases. 
    Together, let's protect our crops and ensure a healthier harvest!
    """)

    with st.expander("🔬 How It Works"):
        st.markdown("""
        1. **Upload Image:** Go to the **Disease Recognition** page and upload an image of a plant with suspected diseases. 📸
                                                
        2. **Analysis:** Our system will process the image using advanced algorithms to identify potential diseases. 🧠
                                                
        3. **Results:** View the results and recommendations for further action. 📊
        """)

    with st.expander("🏆 Why Choose Us?"):
        st.markdown("""
        - **Accuracy:** Our system utilizes state-of-the-art machine learning techniques for accurate disease detection. 🎯
                                                  
        - **User-Friendly:** Simple and intuitive interface for seamless user experience. 👥
                                                  
        - **Fast and Efficient:** Receive results in seconds, allowing for quick decision-making. ⏱️
        """)

    with st.expander("Get Started 🚀 "):
        st.markdown("""
        Click on the **Disease Recognition** page in the sidebar to upload an image and experience the power of our Plant Disease Recognition System! 💪
        """)


elif page == 'Disease Recognition':
    st.title('Disease Recognition')
    uploaded_files = st.file_uploader("Upload your images", type="jpg", accept_multiple_files=True)
    if uploaded_files:
        for idx, uploaded_file in enumerate(uploaded_files):
            image = Image.open(uploaded_file)
            st.image(image, caption=f'Uploaded Image {idx + 1}.', use_column_width=True)
            if st.button(f'Predict Image {idx + 1}'):
                st.write(f"Predicting for Image {idx + 1}...")
                image_np = np.array(image)
                img_batch = np.expand_dims(image_np, 0)
                predictions = MODEL.predict(img_batch)
                predicted_class = CLASS_NAMES[np.argmax(predictions)]
                confidence = np.max(predictions[0])
                st.success(f"Class: {predicted_class}, Confidence: {confidence * 100:.2f}%")
                if st.button(f'Predict Again {idx + 1}'):
                    st.write("Please upload the next image.")
                if st.button(f'Exit {idx + 1}'):
                    uploaded_files = None
                    st.write("Exited. Please refresh the page for a new session.")


# Treatment Page
elif page == 'Treatment':
    st.title('Treatment')
    st.sidebar.title('Treatment')
    st.sidebar.write("Choose a disease")
    treatment_option = st.sidebar.radio('', ['Early Blight', 'Late Blight'])
    if treatment_option == 'Early Blight':
        st.markdown("""
        ### Early Blight Treatment
        1. **Fungicides:** Apply fungicides to protect plants, especially during periods of frequent rainfall.
        2. **Proper Spacing:** Space plants properly to improve air circulation and allow foliage to dry quickly.
        3. **Crop Rotation:** Practice crop rotation with non-host crops to reduce the disease inoculum in the soil.
        """)
        st.markdown("For more information, visit: https://shasyadhara.com/early-blight-of-potato-cause-symptoms-and-control/")
    elif treatment_option == 'Late Blight':
        st.markdown("""
        ### Late Blight Treatment
        1. **Fungicides:** Use fungicides as a preventive measure before the disease appears.
        2. **Destroy Infected Plants:** Remove and destroy all infected plants to prevent the spread of the disease.
        3. **Resistant Varieties:** Plant resistant varieties if they are available.
        """)
        st.markdown("For more information, visit: https://krishijagran.com/agripedia/late-blight-of-potato-complete-management-strategy-for-this-deadly-disease/")

# News Updates
elif page == 'News Updates':
    st.title('News Updates')
    news_data = [
        {"title": "Potato News Today – No-nonsense, no-frills potato news stories from around the world", "link": "https://www.potatonewstoday.com/"},
        {"title": "Potato Disease Identification", "link": "https://potatoes.ahdb.org.uk/knowledge-library/potato-disease-identification"},
        {"title": "Plantura Magazine", "link": "https://plantura.garden/uk/vegetables/potatoes/potato-diseases"},
        {"title": "Cornell Vegetables", "link": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/detection-of-potato-tuber-diseases-defects/"},
    ]
    for news in news_data:
        st.markdown(f"[{news['title']}]({news['link']})")

elif page == 'About':
    st.title('About')
    st.write("Learn more about the project, our team, and our goals on this page.")

    # Feedback Section
    feedback_expander = st.expander("Feedback")
    if is_user_logged_in():
        with feedback_expander:
            feedback_username = get_logged_in_username()
            feedback_message = st.text_area("Feedback Message")
            feedback_rating = st.slider("Rating", min_value=1, max_value=5)
            feedback_type = st.selectbox("Feedback Type", ['General Feedback', 'Bug/Error', 'Critical Feedback'])

            feedback_submit_button = st.button("Submit Feedback")
            
            if feedback_submit_button:
                try:
                    # Save feedback to the database
                    c.execute('INSERT INTO feedbacks (username, message, rating, type) VALUES (?, ?, ?, ?)', (feedback_username, feedback_message, feedback_rating, feedback_type))
                    conn.commit()
                    st.success("Feedback submitted successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        feedback_expander.error('Please log in to submit feedback.')

    

# Create Account
elif page == 'Create Account':
    st.title('Create Account')
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    
    if st.button("Create Account"):
        try:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            c.execute('SELECT * FROM profiles WHERE username = ?', (new_username,))
            existing_user = c.fetchone()
            if existing_user:
                st.error("Username already exists. Please choose another one.")
            else:
                c.execute('INSERT INTO profiles VALUES (?, ?)', (new_username, hashed_password))
                c.execute('INSERT INTO tasks_completed (username, tasks_completed) VALUES (?, 0)', (new_username,))
                conn.commit()
                st.success("Account created successfully! Please login.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Log In
elif page == 'Log In':
    st.title('Log In')
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Log In"):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            c.execute('SELECT * FROM profiles WHERE username = ? AND password = ?', (username, hashed_password))
            user = c.fetchone()
            if user:
                st.session_state.username = username
                st.success(f"Welcome, {username}! Logged in successfully!")
            else:
                st.error("Invalid username or password. Please try again.")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# Log Out
elif page == 'Log Out':
    st.title('Log Out')
    if is_user_logged_in():
        st.session_state.pop('username')
        st.success("Logged out successfully!")
    else:
        st.warning("You are not logged in.")

# Delete Account
elif page == 'Delete Account':
    st.title('Delete Account')
    if is_user_logged_in():
        st.write("Are you sure you want to delete your account? This action cannot be undone.")
        confirm_delete = st.checkbox("Yes, I want to delete my account.")
        if confirm_delete:
            try:
                username = get_logged_in_username()
                c.execute('DELETE FROM profiles WHERE username = ?', (username,))
                c.execute('DELETE FROM tasks_completed WHERE username = ?', (username,))
                conn.commit()
                st.success("Account deleted successfully!")
                st.session_state.pop('username')
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("You are not logged in.")


# Leaderboard

elif page == 'Leaderboard':
    st.title('Leaderboard')
    c.execute('SELECT username, tasks_completed FROM tasks_completed ORDER BY tasks_completed DESC')
    leaderboard_data = c.fetchall()
    if leaderboard_data:
        st.markdown("## Top Performers 🏆")
        st.write("")
        st.write("Here are the top performers based on tasks completed:")
        st.write("")

        # Convert data to tabular format using tabulate
        table_data = [(i+1, username, tasks_completed) for i, (username, tasks_completed) in enumerate(leaderboard_data[:20])]
        headers = ["Rank", "Username", "Tasks Completed"]
        leaderboard_table = tabulate(table_data, headers=headers, tablefmt="plain")

        # Add color to the table
        colored_leaderboard_table = ""
        for line in leaderboard_table.split("\n"):
            if line.startswith("|"):
                colored_line = colored(line, attrs=["bold"])
                colored_leaderboard_table += colored_line + "\n"
            else:
                colored_leaderboard_table += line + "\n"

        st.code(colored_leaderboard_table, language="")

        st.write("")
        st.write("")
    else:
        st.write("Leaderboard is empty. No tasks completed yet.")


# Alarm Page
elif page == 'Plant Care Reminder':
    if is_user_logged_in():
        display_alarm()
    else:
 
       st.error('Please log in to access the Alarm page.')


# Ensure connection is closed
conn.close()
