from django.utils import timezone
from zoneinfo import ZoneInfo

from google import genai
from pathlib import Path

from google.genai import types

from main.utils import FilesProcessing


class GeminiAI:
    def __init__(self):
        self.gemini_client = genai.Client()
        self.file_path = Path(__file__).resolve().parent.parent / "docs"
    
    def get_json_data(self, image_encoded: bytes, config: types.GenerateContentConfig):
        file_readings = FilesProcessing()

        file_readings.read_files(
            [f"{self.file_path}/llama_prompt.txt", f"{self.file_path}/system_prompt.txt"])
        
        [llama_prompt, system_prompt] = file_readings.get_contents()
        
        prep_image = types.Part.from_bytes(data=image_encoded, mime_type="image/png")
        
        ai_response = self.gemini_client.models.generate_content(model="gemini-3.1-flash-lite", contents=[system_prompt, prep_image, llama_prompt], config=config)

        timezone.activate(ZoneInfo("America/Toronto"))
        
        FilesProcessing.write_files(
            path=f"{self.file_path}/gemini_response.txt", content=ai_response.model_dump_json(),
            time=timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"), line_end="\n")
        
        return ai_response