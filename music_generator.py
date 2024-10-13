import requests
import os

class MusicGenerator:
    def __init__(self):
        self.api_key = "your-suno-api-key-here"
        self.api_url = "https://api.suno.ai/v1/generate"

    def generate_music(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "duration": 60  # Generate 60 seconds of music
        }
        response = requests.post(self.api_url, json=data, headers=headers)
        if response.status_code == 200:
            audio_url = response.json()["audio_url"]
            self.download_audio(audio_url, "generated_music.mp3")
            return "generated_music.mp3"
        else:
            print(f"Error generating music: {response.text}")
            return None

    def download_audio(self, url, filename):
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
        else:
            print(f"Error downloading audio: {response.text}")
