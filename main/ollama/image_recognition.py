import base64
from pathlib import Path

import httpx
import ollama
from django.utils import timezone
from ollama import ChatResponse

BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "docs"


def image_recognition(image):
    deepseek_prompt = ""
    llama_prompt = ""
    system_message = ""

    with open(f"{file_path}\\deepseek_prompt.txt", "r", encoding="utf-8") as file:
        deepseek_prompt = file.read()

    with open(f"{file_path}\\llama_prompt.txt", "r", encoding="utf-8") as file:
        llama_prompt = file.read()

    with open(f"{file_path}\\system_prompt.txt", "r", encoding="utf-8") as file:
        system_message = file.read()

    ollama_client = ollama.Client("http://localhost:8833/", timeout=httpx.Timeout(900.0))

    # Call the DeepSeek API to get the image description
    image_encoded = base64.b64encode(image.read()).decode('utf-8')
    deepseek_messages = [{'role': 'user', 'content': deepseek_prompt, 'images': [image_encoded]}]
    deepseek_response: ChatResponse = ollama_client.chat(model="deepseek-ocr:latest", messages=deepseek_messages)

    with open(f"{file_path}\\deepseek_response.txt", "a", encoding="utf-8") as file:
        print(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")} Logging deepseek_response.txt")
        file.write(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")}-{deepseek_response.model_dump_json()}\n")

    ollama_client.close()

    llama_client = ollama.Client("http://localhost:8833/", timeout=httpx.Timeout(900.0))

    llama_prompt_messages = [{'role': 'system', 'content': system_message}, {'role': 'user', 'content': llama_prompt},
                             {'role': 'assistant', 'content': deepseek_response.message.content,
                              'images': [image_encoded]}]
    llama_response: ChatResponse = llama_client.chat(model='llama3.2-vision:latest', messages=llama_prompt_messages)

    with open(f"{file_path}\\llama_response.txt", "a", encoding="utf-8") as file:
        print(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")} Logging llama_response.txt")
        file.write(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")}-{llama_response.model_dump_json()}\n")

    llama_client.close()

    return llama_response