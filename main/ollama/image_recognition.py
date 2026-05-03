import base64
import json
import os
from pathlib import Path

import ollama
from django.core.files import images

BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "docs"

def image_recognition(image):
    deepseek_prompt = ""
    llama_prompt = ""
    system_message = ""
    print(file_path)
    with open(f"{file_path}\\deepseek_prompt.txt", "r", encoding="utf-8") as file:
        deepseek_prompt = file.read()
    
    with open(f"{file_path}\\llama_prompt.txt", "r", encoding="utf-8") as file:
        llama_prompt = file.read()
    
    with open(f"{file_path}\\system_prompt.txt", "r", encoding="utf-8") as file:
        system_message = file.read()
    
    ollama_client = ollama.Client("http://localhost:8833/", timeout=None)
    # Call the DeepSeek API to get the image description
    image_encoded = base64.b64encode(image.read()).decode('utf-8')
    deepseek_messages = [{'role': 'user', 'content': deepseek_prompt, 'images': [image_encoded] }]
    deepseek_response = ollama_client.chat(model="deepseek-ocr:latest", messages=deepseek_messages)
    
    with open(f"{file_path}\\deepseek_response.txt", "a", encoding="utf-8") as file:
        file.write(deepseek_response.model_dump_json()+"\n")
    
    llama_prompt_messages = [{'role': 'system', 'content': system_message }, {'role':'user', 'content': llama_prompt }, {'role':'user', 'content': deepseek_response.message.content, 'images': [image_encoded]}]
    llama_response = ollama_client.chat(model='llama3.2-vision:latest', messages=llama_prompt_messages)
    with open(f"{file_path}\\llama_response.txt", "a", encoding="utf-8") as file:
        file.write(llama_response.model_dump_json()+"\n")
    
   
    return llama_response