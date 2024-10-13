from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import OpenAI
import os

class StoryGenerator:
    def __init__(self):
        # Get the OpenAI API key from environment variables
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
        self.template = """
        Generate a short, engaging story for a space survival horror game. The story should include:
        1. A mysterious awakening on a space station
        2. Signs of danger or a threat
        3. A hint at the player's mission or goal

        Story:
        """
        self.prompt = PromptTemplate(template=self.template, input_variables=[])
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def generate_story(self):
        return self.chain.run()
