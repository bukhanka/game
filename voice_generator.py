from elevenlabs.client import ElevenLabs
import os

class VoiceGenerator:
    def __init__(self):
        self.api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
        self.client = ElevenLabs(api_key=self.api_key)

    def generate_voice(self, text, filename):
        audio = self.client.generate(
            text=text,
            voice="Josh",
            model="eleven_monolingual_v1"
        )
        
        with open(filename, "wb") as f:
            f.write(audio)
        
        return filename
