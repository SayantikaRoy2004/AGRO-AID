import os
import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf
from googletrans import Translator


# Set page configuration
st.set_page_config(page_title='Your Personal Agro-Aid !', layout='wide')

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

# Set up sidebar
st.sidebar.title(translated_navigation)

page = st.sidebar.radio(translated_goto, [translated_home, translated_disease_recognition, translated_treatment, translated_news_updates, translated_about])

if page == translated_home:
    translated_title = translator.translate('🌿 Agro-Aid! 🔍', dest=selected_language.lower()).text
    st.markdown("# " + translated_title)
    
    translated_intro = translator.translate("""
    Our mission is to help in identifying plant diseases efficiently. 
    Upload an image of a plant, and our system will analyze it to detect any signs of diseases. 
    Together, let's protect our crops and ensure a healthier harvest! 🌾🌽
    """, dest=selected_language.lower()).text
    st.markdown(translated_intro)

    translated_how_it_works = translator.translate("🔬 How It Works", dest=selected_language.lower()).text
    with st.expander(translated_how_it_works):
        translated_steps = translator.translate("""
        1. **Upload Image:** Go to the **Disease Recognition** page and upload an image of a plant with suspected diseases. 📸
                                                
        2. **Analysis:** Our system will process the image using advanced algorithms to identify potential diseases. 🧠
                                                
        3. **Results:** View the results and recommendations for further action. 📊
        """, dest=selected_language.lower()).text
        st.markdown(translated_steps)

    translated_why_choose_us = translator.translate("🏆 Why Choose Us?", dest=selected_language.lower()).text
    with st.expander(translated_why_choose_us):
        translated_reasons = translator.translate("""
        - **Accuracy:** Our system utilizes state-of-the-art machine learning techniques for accurate disease detection. 🎯
                                                  
        - **User-Friendly:** Simple and intuitive interface for seamless user experience. 👥
                                                  
        - **Fast and Efficient:** Receive results in seconds, allowing for quick decision-making. ⏱️
        """, dest=selected_language.lower()).text
        st.markdown(translated_reasons)

    translated_get_started = translator.translate("🚀 Get Started", dest=selected_language.lower()).text
    with st.expander(translated_get_started):
        translated_instructions = translator.translate("""
        Click on the **Disease Recognition** page in the sidebar to upload an image and experience the power of our Plant Disease Recognition System! 💪
        """, dest=selected_language.lower()).text
        st.markdown(translated_instructions)



# ... (previous code)

elif page == translated_disease_recognition:
    translated_title = translator.translate('Disease Recognition', dest=selected_language.lower()).text
    st.title(translated_title)
    translated_upload_prompt = translator.translate("Upload your image", dest=selected_language.lower()).text
    uploaded_file = st.file_uploader(translated_upload_prompt, type="jpg")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        translated_caption = translator.translate('Uploaded Image.', dest=selected_language.lower()).text
        st.image(image, caption=translated_caption, use_column_width=True)
        st.write("")
        translated_predict_button = translator.translate('Predict', dest=selected_language.lower()).text
        if st.button(translated_predict_button):
            translated_predicting = translator.translate("Predicting...", dest=selected_language.lower()).text
            st.write(translated_predicting)
            image = read_file_as_image(image)
            img_batch = np.expand_dims(image, 0)
            predictions = MODEL.predict(img_batch)
            predicted_class = CLASS_NAMES[np.argmax(predictions)]
            confidence = np.max(predictions[0])
            translated_result = translator.translate(f"Class: {predicted_class}, Confidence: {confidence*100:.2f}%", dest=selected_language.lower()).text
            st.success(translated_result)
            translated_predict_again_button = translator.translate('Predict Again', dest=selected_language.lower()).text
            if st.button(translated_predict_again_button):
                uploaded_file = None
                translated_upload_next = translator.translate("Please upload the next image.", dest=selected_language.lower()).text
                st.write(translated_upload_next)
            translated_exit_button = translator.translate('Exit', dest=selected_language.lower()).text
            if st.button(translated_exit_button):
                uploaded_file = None
                translated_exited = translator.translate("Exited. Please refresh the page for a new session.", dest=selected_language.lower()).text
                st.write(translated_exited)



elif page == translated_treatment:
    translated_title = translator.translate('Treatment', dest=selected_language.lower()).text
    st.title(translated_title)
    translated_choose_disease = translator.translate("Choose a disease", dest=selected_language.lower()).text
    translated_early_blight = translator.translate('Early Blight', dest=selected_language.lower()).text
    translated_late_blight = translator.translate('Late Blight', dest=selected_language.lower()).text
    treatment_option = st.sidebar.radio(translated_choose_disease, [translated_early_blight, translated_late_blight])
    if treatment_option == translated_early_blight:
        translated_early_blight_treatment = translator.translate("""
        ### Early Blight Treatment
        1. **Fungicides:** Apply fungicides to protect plants, especially during periods of frequent rainfall.
        2. **Proper Spacing:** Space plants properly to improve air circulation and allow foliage to dry quickly.
        3. **Crop Rotation:** Practice crop rotation with non-host crops to reduce the disease inoculum in the soil.
        """, dest=selected_language.lower()).text
        st.write(translated_early_blight_treatment)
        translated_more_info = translator.translate("For more information, visit: https://shasyadhara.com/early-blight-of-potato-cause-symptoms-and-control/", dest=selected_language.lower()).text
        st.write(translated_more_info)
    elif treatment_option == translated_late_blight:
        translated_late_blight_treatment = translator.translate("""
        ### Late Blight Treatment
        1. **Fungicides:** Use fungicides as a preventive measure before the disease appears.
        2. **Destroy Infected Plants:** Remove and destroy all infected plants to prevent the spread of the disease.
        3. **Resistant Varieties:** Plant resistant varieties if they are available.
        """, dest=selected_language.lower()).text
        st.write(translated_late_blight_treatment)
        translated_more_info = translator.translate("For more information, visit: https://krishijagran.com/agripedia/late-blight-of-potato-complete-management-strategy-for-this-deadly-disease/", dest=selected_language.lower()).text
        st.write(translated_more_info)

elif page == translated_news_updates:
    translated_title = translator.translate('News Updates', dest=selected_language.lower()).text
    st.title(translated_title)
    news_data = [
        {"title": "Potato News Today – No-nonsense, no-frills potato news stories from around the world", "link": "https://www.potatonewstoday.com/"},
        {"title": "HyFun Foods to invest Rs 850 crore for three potato processing plants in Gujarat", "link": "https://www.thehindubusinessline.com/companies/hyfun-foods-to-invest-rs-850-crore-for-three-potato-processing-plants-in-gujarat/article37185989.ece"},
        {"title": "\"Pomato\": Farmer's New Technique Of Growing Potatoes And Tomatoes On One Plant", "link": "https://www.ndtv.com/offbeat/pomato-farmers-new-technique-of-growing-potatoes-and-tomatoes-on-one-plant-see-viral-tweet-2617625"},
        {"title": "Big increase in United States potato crop expected", "link": "https://www.freshplaza.com/article/9366388/big-increase-in-united-states-potato-crop-expected/"},
    ]
    for news in news_data:
        st.markdown(f"[{news['title']}]({news['link']})")
elif page == translated_about:
    translated_title = translator.translate('About Us', dest=selected_language.lower()).text
    st.title(translated_title)
    translated_about_text = translator.translate("""
    Learn more about the project, our team, and our goals on this page.
    """, dest=selected_language.lower()).text
    st.write(translated_about_text)
