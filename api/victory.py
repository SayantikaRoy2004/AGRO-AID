import os
import sqlite3
from datetime import datetime
import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf
from googletrans import Translator
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

@st.cache_data(show_spinner=False)
def translate_text(text, dest_language):
    if not text:
        print("Empty text received for translation.")
        return ""
    print(f"Translating: {text}")
    try:
        translator = Translator()
        translated_text = translator.translate(text, dest=dest_language).text
        return translated_text if translated_text else text
    except Exception as e:
        print(f"Error during translation: {str(e)}")
        return text



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

    # Input fields for alarm time
    alarm_time_str = st.text_input('Set Alarm Time (HH:MM:SS)', value=datetime.now().strftime('%H:%M:%S'))

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

            message = f"It's time to {task} your {plant_name} plant!"
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
languages = ['en', 'hi', 'mr']  # English, Hindi, Marathi
selected_language = st.sidebar.selectbox('Choose your language', languages)

# Translate page titles
translated_titles = translate_text(['Home', 'Disease Recognition', 'Treatment', 'News Updates', 'About',
                                    'Plant Care Reminder', 'Create Account', 'Log In', 'Log Out', 'Delete Account'],
                                   dest_language=selected_language)

# Define page variable with a default value
page = st.sidebar.radio('Go to', translated_titles)

# Function to check if user is logged in
def is_user_logged_in():
    return 'username' in st.session_state

# Function to get the username of the logged-in user
def get_logged_in_username():
    return st.session_state.username if is_user_logged_in() else None

# Homepage
if page == 'Home':
    st.markdown("# " + translate_text('🌿 Agro-Aid! 🔍', selected_language))
    st.markdown(translate_text("""
    Our mission is to help in identifying plant diseases efficiently. 
    Upload an image of a plant, and our system will analyze it to detect any signs of diseases. 
    Together, let's protect our crops and ensure a healthier harvest! 🌾🌽
    """, selected_language))

    with st.expander(translate_text("🔬 How It Works", selected_language)):
        st.markdown(translate_text("""
        1. **Upload Image:** Go to the **Disease Recognition** page and upload an image of a plant with suspected diseases. 📸
                                                
        2. **Analysis:** Our system will process the image using advanced algorithms to identify potential diseases. 🧠
                                                
        3. **Results:** View the results and recommendations for further action. 📊
        """, selected_language))

    with st.expander(translate_text("🏆 Why Choose Us?", selected_language)):
        st.markdown(translate_text("""
        - **Accuracy:** Our system utilizes state-of-the-art machine learning techniques for accurate disease detection. 🎯
                                                  
        - **User-Friendly:** Simple and intuitive interface for seamless user experience. 👥
                                                  
        - **Fast and Efficient:** Receive results in seconds, allowing for quick decision-making. ⏱️
        """, selected_language))

    with st.expander(translate_text("🚀 Get Started", selected_language)):
        st.markdown(translate_text("""
        Click on the **Disease Recognition** page in the sidebar to upload an image and experience the power of our Plant Disease Recognition System! 💪
        """, selected_language))

elif page == 'Disease Recognition':
    st.title('Disease Recognition')
    uploaded_file = st.file_uploader(translate_text("Upload your image", selected_language), type="jpg")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption=translate_text('Uploaded Image.', selected_language), use_column_width=True)
        if st.button(translate_text('Predict', selected_language)):
            st.write(translate_text("Predicting...", selected_language))
            image_np = np.array(image)
            img_batch = np.expand_dims(image_np, 0)
            predictions = MODEL.predict(img_batch)
            predicted_class = CLASS_NAMES[np.argmax(predictions)]
            confidence = np.max(predictions[0])
            st.success(
                translate_text(f"Class: {predicted_class}, Confidence: {confidence * 100:.2f}%", selected_language))
            if st.button(translate_text('Predict Again', selected_language)):
                uploaded_file = None
                st.write(translate_text("Please upload the next image.", selected_language))
            if st.button(translate_text('Exit', selected_language)):
                uploaded_file = None
                st.write(translate_text("Exited. Please refresh the page for a new session.", selected_language))

# Treatment Page
elif page == 'Treatment':
    st.title('Treatment')
    st.sidebar.title('Treatment')
    st.sidebar.write(translate_text("Choose a disease", selected_language))
    translated_early_blight = translate_text('Early Blight', selected_language)
    translated_late_blight = translate_text('Late Blight', selected_language)
    treatment_option = st.sidebar.radio('', [translated_early_blight, translated_late_blight])
    if treatment_option == translated_early_blight:
        st.markdown(f"""
        ### {translated_early_blight} {translate_text("Treatment", selected_language)}
        1. **{translate_text("Fungicides", selected_language)}:** {translate_text("Apply fungicides to protect plants, especially during periods of frequent rainfall.", selected_language)}
        2. **{translate_text("Proper Spacing", selected_language)}:** {translate_text("Space plants properly to improve air circulation and allow foliage to dry quickly.", selected_language)}
        3. **{translate_text("Crop Rotation", selected_language)}:** {translate_text("Practice crop rotation with non-host crops to reduce the disease inoculum in the soil.", selected_language)}
        """)
        st.markdown(translate_text("For more information, visit: https://shasyadhara.com/early-blight-of-potato-cause-symptoms-and-control/", selected_language))
    elif treatment_option == translated_late_blight:
        st.markdown(f"""
        ### {translated_late_blight} {translate_text("Treatment", selected_language)}
        1. **{translate_text("Fungicides", selected_language)}:** {translate_text("Use fungicides as a preventive measure before the disease appears.", selected_language)}
        2. **{translate_text("Destroy Infected Plants", selected_language)}:** {translate_text("Remove and destroy all infected plants to prevent the spread of the disease.", selected_language)}
        3. **{translate_text("Resistant Varieties", selected_language)}:** {translate_text("Plant resistant varieties if they are available.", selected_language)}
        """)
        st.markdown(translate_text("For more information, visit: https://krishijagran.com/agripedia/late-blight-of-potato-complete-management-strategy-for-this-deadly-disease/", selected_language))

# News Updates
elif page == 'News Updates':
    st.title('News Updates')
    news_data = [
        {"title": "Potato News Today – No-nonsense, no-frills potato news stories from around the world", "link": "https://www.potatonewstoday.com/"},
        {"title": "HyFun Foods to invest Rs 850 crore for three potato processing plants in Gujarat", "link": "https://www.thehindubusinessline.com/companies/hyfun-foods-to-invest-rs-850-crore-for-three-potato-processing-plants-in-gujarat/article37185989.ece"},
        {"title": "\"Pomato\": Farmer's New Technique Of Growing Potatoes And Tomatoes On One Plant", "link": "https://www.ndtv.com/offbeat/pomato-farmers-new-technique-of-growing-potatoes-and-tomatoes-on-one-plant-see-viral-tweet-2617625"},
        {"title": "Big increase in United States potato crop expected", "link": "https://www.freshplaza.com/article/9366388/big-increase-in-united-states-potato-crop-expected/"},
    ]
    for news in news_data:
        st.markdown(f"[{news['title']}]({news['link']})")

elif page == 'About':
    st.title('About')
    st.write(translate_text("""
    Learn more about the project, our team, and our goals on this page.
    """, selected_language))

    # Feedback Section
    feedback_expander = st.expander(translate_text("Feedback", selected_language))
    with feedback_expander:
        feedback_username = st.text_input(translate_text("Username", selected_language))
        feedback_message = st.text_area(translate_text("Feedback Message", selected_language))
        feedback_rating = st.slider(translate_text("Rating", selected_language), min_value=1, max_value=5)
        feedback_type = st.selectbox(translate_text("Feedback Type", selected_language), ['General Feedback', 'Bug/Error', 'Critical Feedback'])

        feedback_submit_button = st.button(translate_text("Submit Feedback", selected_language))
        
        if feedback_submit_button:
            try:
                # Save feedback to the database
                c.execute('INSERT INTO feedbacks (username, message, rating, type) VALUES (?, ?, ?, ?)', (feedback_username, feedback_message, feedback_rating, feedback_type))
                conn.commit()
                st.success(translate_text("Feedback submitted successfully!", selected_language))
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Create Account
elif page == 'Create Account':
    st.title('Create Account')
    new_username = st.text_input(translate_text("New Username", selected_language))
    new_password = st.text_input(translate_text("New Password", selected_language), type="password")
    
    if st.button(translate_text("Create Account", selected_language)):
        try:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            c.execute('SELECT * FROM profiles WHERE username = ?', (new_username,))
            existing_user = c.fetchone()
            if existing_user:
                st.error(translate_text("Username already exists. Please choose another one.", selected_language))
            else:
                c.execute('INSERT INTO profiles VALUES (?, ?)', (new_username, hashed_password))
                conn.commit()
                st.success(translate_text("Account created successfully! Please login.", selected_language))
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Log In
elif page == 'Log In':
    st.title('Log In')
    username = st.text_input(translate_text("Username", selected_language))
    password = st.text_input(translate_text("Password", selected_language), type="password")
    
    if st.button(translate_text("Log In", selected_language)):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            c.execute('SELECT * FROM profiles WHERE username = ? AND password = ?', (username, hashed_password))
            user = c.fetchone()
            if user:
                st.session_state.username = username
                st.success(translate_text("Logged in successfully!", selected_language))
            else:
                st.error(translate_text("Invalid username or password. Please try again.", selected_language))
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Log Out
elif page == 'Log Out':
    st.title('Log Out')
    if is_user_logged_in():
        st.session_state.pop('username')
        st.success(translate_text("Logged out successfully!", selected_language))
    else:
        st.warning(translate_text("You are not logged in.", selected_language))

# Delete Account
elif page == 'Delete Account':
    st.title('Delete Account')
    if is_user_logged_in():
        st.write(translate_text("Are you sure you want to delete your account? This action cannot be undone.", selected_language))
        confirm_delete = st.checkbox(translate_text("Yes, I want to delete my account.", selected_language))
        if confirm_delete:
            try:
                username = get_logged_in_username()
                c.execute('DELETE FROM profiles WHERE username = ?', (username,))
                conn.commit()
                st.success(translate_text("Account deleted successfully!", selected_language))
                st.session_state.pop('username')
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning(translate_text("You are not logged in.", selected_language))

# Alarm Page
elif page == translate_text('Plant Care Reminder', selected_language):
    if is_user_logged_in():
        display_alarm()
    else:
        st.error(translate_text('Please log in to access the Alarm page.', selected_language))

# Ensure connection is closed
conn.close()
