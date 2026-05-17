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

from main.utils import FilesProcessing

BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "docs"


def image_recognition(image_encoded) -> str:
    file_readings = FilesProcessing()

    file_readings.read_files(
        [f"{file_path}/deepseek_prompt.txt", f"{file_path}/llama_prompt.txt", f"{file_path}/system_prompt.txt"])

    [deepseek_prompt, llama_prompt, system_message] = file_readings.get_contents()

    docker_running = os.getenv("DOCKER_RUNNING", "False").lower() == "true"

    ollama_host = os.getenv("AI_CALLING_IN") if docker_running else os.getenv("AI_CALLING_OUT")

    if not ollama_host:
        ollama_host = getattr(settings, "AI_CALLING_IN") if docker_running else getattr(settings, "AI_CALLING_OUT")

    print(f"DOCKER_RUNNING: {docker_running}, ollama_host: {ollama_host}")
    timezone.activate(ZoneInfo("America/Toronto"))
    ollama_client = Client(ollama_host, timeout=httpx.Timeout(900.0))

    # Call the DeepSeek API to get the image description
    deepseek_messages = [{'role': 'user', 'content': deepseek_prompt, 'images': [image_encoded]}]
    deepseek_response: ChatResponse = ollama_client.chat(model="deepseek-ocr:latest", messages=deepseek_messages, options={"temperature": 0})

    FilesProcessing.write_files(
        path=f"{file_path}/deepseek_response.txt", content=deepseek_response.model_dump_json(),
        time=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"), line_end="\n")

    ollama_client.close()

    llama_client = Client(ollama_host, timeout=httpx.Timeout(900.0))
    proceed_markdown = deepseek_response.message.content.replace("\n\n", " ").replace("\n", " ")
    FilesProcessing.write_files(path=f"{file_path}/processed_markdown.txt",
                                content=proceed_markdown,
                                time=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"), line_end="\n")

    llama_prompt_messages = [{'role': 'assistant', 'content': system_message},
                             {'role': 'assistant', 'content': proceed_markdown
                              },
                             {'role': 'user', 'content': f"{llama_prompt}",
                              'images': [image_encoded]}]

    llama_response: ChatResponse = llama_client.chat(model='llama3.2-vision:latest', messages=llama_prompt_messages, think=False, options={"temperature": 0})

    FilesProcessing.write_files(
        path=f"{file_path}/llama_response.txt", content=llama_response.model_dump_json(),
        time=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"), line_end="\n")

    llama_client.close()

    if not llama_response.message.content:
        raise ValueError("AI response is empty.")

    prefix_index = llama_response.message.content.find("{")
    suffix_index = llama_response.message.content.rfind("}")

    result = llama_response.message.content[
        prefix_index:suffix_index + 1] if prefix_index != -1 and suffix_index != -1 else llama_response.message.content

    return result


def call_api_localhost(image):
    timezone.activate(ZoneInfo("America/Toronto"))
    image_data = base64.b64encode(image.read()).decode('utf-8')
    media_type = getattr(image, 'content_type', 'image/png')

    file_readings = FilesProcessing()

    file_readings.read_files([f"{file_path}/deepseek_prompt.txt"])

    [deepseek_prompt] = file_readings.get_contents()

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
