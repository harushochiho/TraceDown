import base64
import json
from enum import verify
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import ollama
from django.utils import timezone
from httpx import Timeout
from ollama import ChatResponse

BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "docs"

deepseek_prompt = ""
llama_prompt = ""
system_message = ""
with open(f"{file_path}\\deepseek_prompt.txt", "r", encoding="utf-8") as file:
    print("Reading deepseek_prompt.txt")
    deepseek_prompt = file.read()

with open(f"{file_path}\\llama_prompt.txt", "r", encoding="utf-8") as file:
    print("Reading llama_prompt.txt")
    llama_prompt = file.read()

with open(f"{file_path}\\system_prompt.txt", "r", encoding="utf-8") as file:
    print("Reading system_prompt.txt")
    system_message = file.read()


def image_recognition(image):
    timezone.activate(ZoneInfo("America/Toronto"))
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

    llama_prompt_messages = [{'role': 'user', 'content': system_message},
                             {'role': 'assistant', 'content': deepseek_response.message.content,
                              'images': [image_encoded]},
                             {'role': 'user', 'content': f"{llama_prompt}"}]
    llama_response: ChatResponse = llama_client.chat(model='llama3.2-vision:latest', messages=llama_prompt_messages)

    with open(f"{file_path}\\llama_response.txt", "a", encoding="utf-8") as file:
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
    with open(f"{file_path}\\api_calling.txt", "a", encoding="utf-8") as file:
        file.write(
            f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")}-{json.dumps(messages, ensure_ascii=False, indent=4)}\n")

    response = httpx.post("https://localhost:8802/aicalling", json=messages, verify=False,
                          timeout=Timeout(timeout=None))

    with open(f"{file_path}\\deepseek_response.txt", "a", encoding="utf-8") as file:
        print(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")} Logging deepseek_response.txt")
        file.write(f"{timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")}-{json.dumps(response.json())}\n")

    return response
