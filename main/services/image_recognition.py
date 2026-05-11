import base64
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from django.conf import settings
from django.utils import timezone
from httpx import Timeout
from ollama import ChatResponse, Client

BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "docs"

deepseek_prompt = ""
llama_prompt = ""
system_message = ""
with open(f"{file_path}/deepseek_prompt.txt", "r", encoding="utf-8") as file:
    print("Reading deepseek_prompt.txt")
    deepseek_prompt = file.read()

with open(f"{file_path}/llama_prompt.txt", "r", encoding="utf-8") as file:
    print("Reading llama_prompt.txt")
    llama_prompt = file.read()

with open(f"{file_path}/system_prompt.txt", "r", encoding="utf-8") as file:
    print("Reading system_prompt.txt")
    system_message = file.read()


def image_recognition(image_encoded):
    docker_running = os.getenv("docker_running", "False").lower() == "true"

    ollama_host = os.getenv("OLLAMA_IN") if docker_running else os.getenv("OLLAMA_OUT")

    if not ollama_host:
        ollama_host = getattr(settings, "OLLAMA_IN") if docker_running else getattr(settings, "OLLAMA_OUT")

    print(f"docker_running: {docker_running}, ollama_host: {ollama_host}")
    timezone.activate(ZoneInfo("America/Toronto"))
    ollama_client = Client(ollama_host, timeout=httpx.Timeout(900.0))
    print(f"Ollama host: {ollama_host}")
    # Call the DeepSeek API to get the image description
    deepseek_messages = [{'role': 'user', 'content': deepseek_prompt, 'images': [image_encoded]}]
    deepseek_response: ChatResponse = ollama_client.chat(model="deepseek-ocr:latest", messages=deepseek_messages)

    with open(f"{file_path}/deepseek_response.txt", "a", encoding="utf-8") as file:
        print(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")} Logging deepseek_response.txt")
        file.write(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")}-{deepseek_response.model_dump_json()}\n")

    ollama_client.close()

    llama_client = Client(ollama_host, timeout=httpx.Timeout(900.0))

    llama_prompt_messages = [{'role': 'user', 'content': system_message},
                             {'role': 'assistant', 'content': deepseek_response.message.content,
                              'images': [image_encoded]},
                             {'role': 'user', 'content': f"{llama_prompt}"}]
    llama_response: ChatResponse = llama_client.chat(model='llama3.2-vision:latest', messages=llama_prompt_messages)

    with open(f"{file_path}/llama_response.txt", "a", encoding="utf-8") as file:
        print(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")} Logging llama_response.txt")
        file.write(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")}-{llama_response.model_dump_json()}\n")

    llama_client.close()

    return llama_response


def call_api_localhost(image):
    timezone.activate(ZoneInfo("America/Toronto"))
    image_data = base64.b64encode(image.read()).decode('utf-8')
    media_type = getattr(image, 'content_type', 'image/png')
    messages = {
        "ModelName": "deepseek-ocr:latest",
        "Prompts": [
            {
                "Role": "User",
                "DefaultPrompt": deepseek_prompt,
                "Contents": [],
                "Images": [
                    {
                        "ImageData": image_data,
                        "MediaType": media_type
                    }
                ]
            }
        ]
    }
    with open(f"{file_path}/api_calling.txt", "a", encoding="utf-8") as file:
        file.write(
            f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")}-{json.dumps(messages, ensure_ascii=False, indent=4)}\n")

    response = httpx.post("https://localhost:8802/aicalling", json=messages, verify=False,
                          timeout=Timeout(timeout=None))

    with open(f"{file_path}/deepseek_response.txt", "a", encoding="utf-8") as file:
        print(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")} Logging deepseek_response.txt")
        file.write(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")}-{json.dumps(response.json())}\n")

    return response
