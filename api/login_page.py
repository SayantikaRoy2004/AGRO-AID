import os
import sqlite3
from datetime import datetime, timedelta
import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf
from googletrans import Translator
from plyer import notification
import hashlib
import schedule
import threading
import time
import winsound

# Set page configuration
st.set_page_config(page_title='Your Personal Agro-Aid!', layout='wide')

saved_model_path = "models/1"

# Check if the directory exists
if not os.path.exists(saved_model_path):
    raise FileNotFoundError(f"SavedModel directory '{saved_model_path}' does not exist.")

# Load the model
MODEL = tf.keras.models.load_model(saved_model_path)

CLASS_NAMES = ["Early Blight", "Late Blight", "Healthy"]

def read_file_as_image(data) -> object:
    image = np.array(data)
    return image

notification_counter = 0  # Initialize notification counter

def send_notification(message):
    global notification_counter  # Access the global notification counter variable
    while notification_counter < 3:  # Limit notifications to 3 times
        winsound.Beep(1000, 1000)  # Beep at 1000 Hz for 1 second (adjust as needed for your sound)
        result = notification.notify(
            title='Plant Care Reminder',
            message=message,
            timeout=10,  # seconds
            app_icon=None,  # optional, use if you want to set an icon for the notification
            ticker=None,  # optional, use if you want to set a ticker text for the notification
            toast=False,  # optional, use if you don't want to display a toast notification on Windows
            # Specify the path to your sound file
            app_name="your_sound_file_path.wav"
        )
        if result == 'clicked':
            break
        time.sleep(1)  # Sleep for 1 second between notifications
        notification_counter += 1  # Increment notification counter

# Function to check and send reminders
def check_reminders():
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M')
    c.execute('SELECT * FROM reminder WHERE date = ? AND time = ?', (current_date, current_time))
    reminders = c.fetchall()
    for reminder in reminders:
        message = f"Time to {reminder[1]} your {reminder[5]} plant"
        send_notification(message)

# Schedule reminder checking every minute
schedule.every().minute.do(check_reminders)

# Start reminder scheduler in a separate thread
def reminder_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep for 1 second to avoid high CPU usage

thread = threading.Thread(target=reminder_scheduler)
thread.start()

# Set up sidebar
st.sidebar.title('Contents')
# Add language selection
languages = ['English', 'Hindi', 'Bengali', 'Telugu', 'Marathi', 'Tamil', 'Gujarati', 'Kannada', 'Malayalam', 'Oriya', 'Punjabi', 'Assamese', 'Maithili', 'Urdu']
selected_language = st.sidebar.selectbox('Choose your language', languages)
translator = Translator()
# Translate text
translated_navigation = translator.translate('Contents', dest=selected_language.lower()).text
translated_goto = translator.translate('Go to', dest=selected_language.lower()).text
translated_home = translator.translate('Home', dest=selected_language.lower()).text
translated_disease_recognition = translator.translate('Disease Recognition', dest=selected_language.lower()).text
translated_treatment = translator.translate('Treatment', dest=selected_language.lower()).text
translated_news_updates = translator.translate('News Updates', dest=selected_language.lower()).text
translated_about = translator.translate('About', dest=selected_language.lower()).text
translated_plant_care_reminder = translator.translate('Plant Care Reminder', dest=selected_language.lower()).text
translated_create_account = translator.translate('Create Account', dest=selected_language.lower()).text
translated_log_in = translator.translate('Log In', dest=selected_language.lower()).text
translated_log_out = translator.translate('Log Out', dest=selected_language.lower()).text
translated_delete_account = translator.translate('Delete Account', dest=selected_language.lower()).text

# Connect to SQLite database
conn = sqlite3.connect('plant_care.db', check_same_thread=False)
c = conn.cursor()

# Create table for reminders if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS reminder (
        username TEXT,
        task TEXT,
        date TEXT,
        time TEXT,  
        frequency TEXT,
        plants TEXT
    )
''')

# Create table for user profiles if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')

# Define page variable with a default value
page = st.sidebar.radio('Go to', [translated_home, translated_disease_recognition, translated_treatment, translated_news_updates, translated_about, translated_plant_care_reminder, translated_create_account, translated_log_in, translated_log_out, translated_delete_account])

# Homepage
if page == translated_home:
    translated_title = translator.translate('🌿 Agro-Aid! 🔍', dest=selected_language.lower()).text
    st.markdown("# " + translated_title)
    
    st.markdown("""
    Our mission is to help in identifying plant diseases efficiently. 
    Upload an image of a plant, and our system will analyze it to detect any signs of diseases. 
    Together, let's protect our crops and ensure a healthier harvest! 🌾🌽
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

    with st.expander("🚀 Get Started"):
        st.markdown("""
        Click on the **Disease Recognition** page in the sidebar to upload an image and experience the power of our Plant Disease Recognition System! 💪
        """)

elif page == translated_disease_recognition:
    st.title(translated_disease_recognition)
    uploaded_file = st.file_uploader(translator.translate("Upload your image", dest=selected_language).text, type="jpg")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption=translator.translate('Uploaded Image.', dest=selected_language).text, use_column_width=True)
        if st.button(translator.translate('Predict', dest=selected_language).text):
            st.write(translator.translate("Predicting...", dest=selected_language).text)
            image = read_file_as_image(image)
            img_batch = np.expand_dims(image, 0)
            predictions = MODEL.predict(img_batch)
            predicted_class = CLASS_NAMES[np.argmax(predictions)]
            confidence = np.max(predictions[0])
            st.success(translator.translate(f"Class: {predicted_class}, Confidence: {confidence*100:.2f}%", dest=selected_language).text)
            if st.button(translator.translate('Predict Again', dest=selected_language).text):
                uploaded_file = None
                st.write(translator.translate("Please upload the next image.", dest=selected_language).text)
            if st.button(translator.translate('Exit', dest=selected_language).text):
                uploaded_file = None
                st.write(translator.translate("Exited. Please refresh the page for a new session.", dest=selected_language).text)

# Treatment Page
elif page == translated_treatment:
    st.title(translated_treatment)
    st.sidebar.title(translated_treatment)
    st.sidebar.write(translator.translate("Choose a disease", dest=selected_language).text)
    treatment_option = st.sidebar.radio('', [translator.translate('Early Blight', dest=selected_language).text, 
                                             translator.translate('Late Blight', dest=selected_language).text])
    if treatment_option == translator.translate('Early Blight', dest=selected_language).text:
        st.markdown("""
        ### Early Blight Treatment
        1. **Fungicides:** Apply fungicides to protect plants, especially during periods of frequent rainfall.
        2. **Proper Spacing:** Space plants properly to improve air circulation and allow foliage to dry quickly.
        3. **Crop Rotation:** Practice crop rotation with non-host crops to reduce the disease inoculum in the soil.
        """)
        st.markdown(translator.translate("For more information, visit: https://shasyadhara.com/early-blight-of-potato-cause-symptoms-and-control/", dest=selected_language).text)
    elif treatment_option == translator.translate('Late Blight', dest=selected_language).text:
        st.markdown("""
        ### Late Blight Treatment
        1. **Fungicides:** Use fungicides as a preventive measure before the disease appears.
        2. **Destroy Infected Plants:** Remove and destroy all infected plants to prevent the spread of the disease.
        3. **Resistant Varieties:** Plant resistant varieties if they are available.
        """)
        st.markdown(translator.translate("For more information, visit: https://krishijagran.com/agripedia/late-blight-of-potato-complete-management-strategy-for-this-deadly-disease/", dest=selected_language).text)

# News Updates
elif page == translated_news_updates:
    st.title(translated_news_updates)
    news_data = [
        {"title": "Potato News Today – No-nonsense, no-frills potato news stories from around the world", "link": "https://www.potatonewstoday.com/"},
        {"title": "HyFun Foods to invest Rs 850 crore for three potato processing plants in Gujarat", "link": "https://www.thehindubusinessline.com/companies/hyfun-foods-to-invest-rs-850-crore-for-three-potato-processing-plants-in-gujarat/article37185989.ece"},
        {"title": "\"Pomato\": Farmer's New Technique Of Growing Potatoes And Tomatoes On One Plant", "link": "https://www.ndtv.com/offbeat/pomato-farmers-new-technique-of-growing-potatoes-and-tomatoes-on-one-plant-see-viral-tweet-2617625"},
        {"title": "Big increase in United States potato crop expected", "link": "https://www.freshplaza.com/article/9366388/big-increase-in-united-states-potato-crop-expected/"},
    ]
    for news in news_data:
        st.markdown(f"[{news['title']}]({news['link']})")

# About
elif page == translated_about:
    st.title(translated_about)
    st.write(translator.translate("""
    Learn more about the project, our team, and our goals on this page.
    """, dest=selected_language).text)

# Create Account
elif page == translated_create_account:
    st.title(translated_create_account)
    new_username = st.text_input(translator.translate("New Username", dest=selected_language).text)
    new_password = st.text_input(translator.translate("New Password", dest=selected_language).text, type="password")
    
    if st.button(translator.translate("Create Account", dest=selected_language).text):
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        c.execute('SELECT * FROM profiles WHERE username = ?', (new_username,))
        existing_user = c.fetchone()
        if existing_user:
            st.error(translator.translate("Username already exists. Please choose another one.", dest=selected_language).text)
        else:
            c.execute('INSERT INTO profiles VALUES (?, ?)', (new_username, hashed_password))
            conn.commit()
            st.success(translator.translate("Account created successfully! Please login.", dest=selected_language).text)

# Log In
elif page == translated_log_in:
    st.title(translated_log_in)
    username = st.text_input(translator.translate("Username", dest=selected_language).text)
    password = st.text_input(translator.translate("Password", dest=selected_language).text, type="password")

    if st.button(translator.translate("Login", dest=selected_language).text):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        c.execute('SELECT * FROM profiles WHERE username = ? AND password = ?', (username, hashed_password))
        data = c.fetchone()
        if data is None:
            st.error(translator.translate("Invalid username or password", dest=selected_language).text)
        else:
            st.success(translator.translate("Login successful!", dest=selected_language).text)

elif page == translated_plant_care_reminder:
    st.title(translated_plant_care_reminder)
    username = st.text_input(translator.translate("Username", dest=selected_language).text)
    task = st.text_input(translator.translate("Task", dest=selected_language).text)
    reminder_date = st.date_input(translator.translate("Date", dest=selected_language).text, min_value=datetime.now())
    reminder_time_hour = st.number_input(translator.translate("Hour", dest=selected_language).text, min_value=0, max_value=23)
    reminder_time_minute = st.number_input(translator.translate("Minute", dest=selected_language).text, min_value=0, max_value=59)
    frequency = st.selectbox(translator.translate("Frequency", dest=selected_language).text, ['Once', 'Daily', 'Weekly', 'Monthly'])
    plants = st.text_input(translator.translate("Plants", dest=selected_language).text)
    
    if st.button(translator.translate("Set Reminder", dest=selected_language).text):
        try:
            # Create a timedelta object for the time
            reminder_time = timedelta(hours=reminder_time_hour, minutes=reminder_time_minute)
            reminder_datetime = datetime.combine(reminder_date, datetime.min.time()) + reminder_time
            reminder_time_str = "{:02}:{:02}".format(reminder_time.seconds // 3600, (reminder_time.seconds // 60) % 60)
            c.execute('INSERT INTO reminder (username, task, date, time, frequency, plants) VALUES (?, ?, ?, ?, ?, ?)', (username, task, reminder_date, reminder_time_str, frequency, plants))

            conn.commit()
            st.success(translator.translate("Reminder set successfully!", dest=selected_language).text)
        except ValueError:
            st.error(translator.translate("Invalid time input. Please enter a valid time.", dest=selected_language).text)

# Log Out
elif page == translated_log_out:
    # Add log out functionality
    st.write(translator.translate("You are logged out.", dest=selected_language).text)

# Delete Account
elif page == translated_delete_account:
    st.title(translated_delete_account)
    username = st.text_input(translator.translate("Username", dest=selected_language).text)
    password = st.text_input(translator.translate("Password", dest=selected_language).text, type="password")
    
    if st.button(translator.translate("Delete Account", dest=selected_language).text):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        c.execute('DELETE FROM profiles WHERE username = ? AND password = ?', (username, hashed_password))
        conn.commit()
        st.success(translator.translate("Account deleted successfully!", dest=selected_language).text)
