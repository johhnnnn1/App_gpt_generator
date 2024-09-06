import os
from openai import OpenAI
import spacy 
import requests
import random
import re
# Load the GPT-4 API key from the .env file
client = OpenAI(api_key=os.environ.get("GPT4_API_KEY"))

def generate_text(prompt, example_base_text, desired_length, temperature, subgenre):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"{example_base_text}\nNow, write a sci-fi blog post about the following topic:\n\n{prompt}\n\nThe blog post should be a string follow the style and tone of the example provided and should be set in a science-fiction context. It should include a title, an introduction, 2-3 main points,but don't mention the words blog post,main points, point1, point2, just be sure that it includes them and are part of the text in various ways, and an ending.Don't try to use bullet points to mark the main points, I want the text to be continous. Make sure it's engaging, well-structured, and maximum {desired_length} words long.Be sure to have a very intuitive and short title from maximum 5 words and try not to use quotes in the title.Avoid mentioning directly the structure of the post.Want the title to be 4 words long and concise based on the story.This story is set in a {subgenre} universe."},
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=desired_length + 50,
        temperature=temperature,
    )

    generated_text = response.choices[0].message.content
       # Extract and clean the title
    lines = generated_text.split("\n")
    title = lines[0].strip()
    title = re.sub(r'^#+\s*', '', title)  # Remove leading # characters and any spaces after them
    title = " ".join(title.split()[:5])  # Ensure the title is concise (max 4 words)
    title = re.sub(r'^Title:?\s*', '', title.strip(), flags=re.IGNORECASE)
    title = re.sub(r'"', '', title.strip())
    # Remove title from the generated text
    generated_text = "\n".join(lines[1:]).strip()
    
    # Ensure the text ends with proper punctuation
    punctuation_marks = {'.', '?', '!'}
    if generated_text and generated_text[-1] not in punctuation_marks:
        for i in range(len(generated_text) - 1, -1, -1):
            if generated_text[i] in punctuation_marks:
                generated_text = generated_text[:i + 1]
                break

    # Truncate the text to meet the desired length
    words = generated_text.split()
    if len(words) > desired_length:
        generated_text = " ".join(words[:desired_length])
        if generated_text[-1] not in punctuation_marks:
            generated_text += "..."

    return generated_text, title

#def generate_dalle_image(prompt):
   #api_base = os.getenv("AZURE_OAI_ENDPOINT")
   # api_key = os.getenv("AZURE_OAI_KEY")
  #  api_version = '2024-06-15-preview'
  #  url = f"{api_base}openai/deployments/dalle3/images/generations?api-version={api_version}"
 #   headers= { "api-key": api_key, "Content-Type": "application/json" }
 #   body = {"prompt": prompt, "n": 1, "size": "1024x1024"}
 #   response = requests.post(url, headers=headers, json=body)
 #   return response.json()['data'][0]['url']

def generate_dalle_image(prompt):
    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("GPT4_API_KEY"))

    try:
        # Make the API call to DALL-E
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        # Extract and return the image URL
        image_url = response.data[0].url
        return image_url

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def generate_additional_content(prompt, additional_length, temperature):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a prompt creator based on the prompt given and create a continuaton for that prompt, unique and 5 words max length"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=additional_length,
        temperature=temperature,
    )
    return response.choices[0].message.content

def get_concise_prompt(generated_text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(generated_text)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
    concise_prompt = " ".join(keywords)
    return concise_prompt[:250] if len(concise_prompt) > 250 else concise_prompt

def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read().splitlines()

def random_line(lines):
    return random.choice(lines)

def rate_text(generated_text):
    rating_prompt = f"Rate the following text on a scale of 1 to 10 for both creativity and suspense and make sure to be as flexible as possible. Provide the ratings separately in the format: Creativity: X, Suspense: Y\n\nText:\n{generated_text}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a literary critic."},
            {"role": "user", "content": rating_prompt}
        ],
        max_tokens=50,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def generate_continuation(prompt, initial_text, additional_length, temperature):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Continue the text based on the initial text and prompt I will provide you, be sure to not disturb the story."},
            {"role": "user", "content": initial_text},
            {"role": "user", "content": prompt}
        ],
        max_tokens=additional_length,
        temperature=temperature,
    )
    continuation_text = response.choices[0].message.content
    punctuation_marks = {'.', '?', '!'}
    if continuation_text[-1] not in punctuation_marks:
        for i in range(len(continuation_text) - 1, -1, -1):
            if continuation_text[i] in punctuation_marks:
                continuation_text = continuation_text[:i+1]
                break
    return continuation_text
