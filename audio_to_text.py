
import whisper
import os
from typing import Optional


class AudioToText:
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = whisper.load_model(model_size)
    
    def transcribe(self, audio_path: str, language: Optional[str] = "zh") -&gt; dict:
        result = self.model.transcribe(audio_path, language=language)
        return {
            "text": result["text"],
            "segments": result["segments"],
            "language": result["language"]
        }


if __name__ == "__main__":
    converter = AudioToText()
    print("AudioToText class loaded successfully")
