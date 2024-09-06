from flask import request, render_template, send_file, session
import re
from flask import send_file
import requests
from io import BytesIO
import requests
from base64 import b64encode
import joblib
from app import app
from utils import (
    generate_text, generate_dalle_image, generate_additional_content, 
    get_concise_prompt, rate_text, generate_continuation, read_file, random_line
)
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import os
from flask import jsonify, request
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("GPT4_API_KEY"))
model_filename = 'sci_fi_theme_classifier.pkl'
best_model = joblib.load(model_filename)

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

# Function to predict the theme of a new text
app.jinja_env.filters['b64encode'] = lambda u: b64encode(u).decode('utf-8') if u else ''


@app.route('/')
def login():
    return render_template('index1.html')

@app.route('/index')
def main_page():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/saved')
def saved():
    return render_template('saved_content.html')

def analyze_sentiment_azure(text):
   preprocessed_text = preprocess_text(text)
   predicted_theme = best_model.predict([preprocessed_text])[0]
   return predicted_theme


@app.route('/download_image', methods=['GET'])
def download_image():
    generated_image_url = session.get('generated_image_url')
    response = requests.get(generated_image_url)
    if response.status_code == 200:
        with open('generated_image.jpg', 'wb') as f:
            f.write(response.content)
        return send_file('generated_image.jpg', as_attachment=True)
    else:
        return "Failed to download the image."

@app.route('/download_text', methods=['GET'])
def download_text():
    generated_text = session.get('edited_text', session.get('generated_text'))
    generated_title = session.get('generated_title')
    text_with_title = f"{generated_title}\n\n{generated_text}"
    with open('generated_text.txt', 'w') as f:
        f.write(text_with_title)
    return send_file('generated_text.txt', as_attachment=True)

@app.route('/save_text', methods=['POST'])
def save_text():
    edited_text = request.form.get('edited_text')
    session['edited_text'] = edited_text
    return "Text saved successfully!"

@app.route('/generate_prompt', methods=['POST'])
def generate_prompt():
    user_description = request.json['description']
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a prompt creator."},
            {"role": "user", "content": f"Based on this user description: '{user_description}', generate a sci-fi writing prompt with less than 15 words."}
        ],
        max_tokens=50,
        temperature=0.8,
    )
    
    generated_prompt = response.choices[0].message.content.strip()
    return jsonify({'prompt': generated_prompt})


@app.route('/generate_avatar', methods=['POST'])
def generate_avatar():
    client = OpenAI(api_key=os.getenv("GPT4_API_KEY"))
    user_description = request.json['description']
    user_gender = request.json['gender']
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Generate a sci-fi avatar based on this description: {user_description}. The image should be a close-up portrait of {user_gender} in a futuristic style.",
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        
        # Fetch the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        # Send the image directly to the client
        return send_file(
            BytesIO(image_response.content),
            mimetype='image/png',
            as_attachment=True,
            download_name='avatar.png'
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    prompts = read_file("prom.txt")
    base_texts = read_file("base_text.txt")
    custom_prompt = request.form.get("custom_prompt")
    predefined_prompt = request.form.get("predefined_prompt")
    subgenre = request.form.get("subgenre")
    desired_length = int(request.form.get("length"))
    temperature = request.form.get("temperature")
    temperature = float(temperature) if temperature is not None else 0.7
    random_base_text = random_line(base_texts)
    prompt = custom_prompt if custom_prompt else (predefined_prompt if predefined_prompt else random_line(prompts))
    generated_text, generated_title = generate_text(prompt, random_base_text, desired_length, temperature, subgenre)
    concise_prompt = get_concise_prompt(generated_text)
    generated_image_url = generate_dalle_image(concise_prompt)
    prompt1 = generate_additional_content(concise_prompt, 15, temperature)
    prompt2 = generate_additional_content(prompt1, 15, temperature)
    rating = rate_text(generated_text)
    sentiment=analyze_sentiment_azure(generated_text)


    image_response = requests.get(generated_image_url)
    image_data = image_response.content if image_response.status_code == 200 else None
    sentiment_music_map = {
        'adventure': 'adventure.mp3',
        'crime': 'crime.mp3',
        'dystopia':'dystopia.mp3',
        'mystery':'mystery.mp3',
        'science fiction':'science_fiction.mp3'
    }
    background_music = sentiment_music_map.get(sentiment, 'crime.mp3')



    session['prompts'] = {'prompt1': prompt1, 'prompt2': prompt2}
    session['initial_parameters'] = {'prompt': prompt, 'desired_length': desired_length, 'temperature': temperature}
    session['generated_title'] = generated_title
    session['generated_text'] = generated_text
    return render_template('generated.html', generated_text=generated_text, generated_title=generated_title, generated_image_data=image_data, prompt1=prompt1, prompt2=prompt2, rating=rating, sentiment=sentiment, background_music=background_music)

@app.route('/continue', methods=['POST'])
def continue_generating():
    initial_text = request.form.get('initial_text')
    initial_text=str(initial_text)
    initial_parameters = session.get('initial_parameters')
    desired_length = 150
    temperature = initial_parameters['temperature']
    selected_prompt = request.form.get("selected_prompt")
    prompt = request.form.get("prompt1") if selected_prompt == "1" else request.form.get("prompt2")
    prompt=str(prompt)
    additional_text = generate_continuation(prompt, initial_text, desired_length, temperature)
    final_text = initial_text + "\n" + additional_text
    rating = rate_text(final_text)
    sentiment=analyze_sentiment_azure(final_text)
    sentiment_music_map = {
        'adventure': 'adventure.mp3',
        'crime': 'crime.mp3',
        'dystopia':'dystopia.mp3',
        'mystery':'mystery.mp3',
        'science fiction':'science_fiction.mp3'
    }
    background_music = sentiment_music_map.get(sentiment, 'crime.mp3')

    new_image_url = generate_dalle_image(get_concise_prompt(final_text))
    generated_title = session.get('generated_title')
    session['generated_image_url'] = new_image_url 
    session['generated_title'] = generated_title
    session['generated_text'] = final_text
    session['edited_text'] = final_text
    return render_template('final.html', generated_text=final_text, generated_image_url=new_image_url, generated_title=generated_title, rating=rating, sentiment=sentiment, background_music=background_music)
