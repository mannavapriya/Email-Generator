# integrations/llm_client.py
import os
import openai
from dotenv import load_dotenv

load_dotenv()

def make_openai_llm(model="gpt-3.5-turbo", temperature=0.2):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set in environment.")
    
    class OpenAIWrapper:
        def __init__(self, model, temperature, api_key):
            self.model = model
            self.temperature = temperature
            self.api_key = api_key

        def generate(self, prompt):
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                api_key=self.api_key
            )
            return response.choices[0].message.content

    return OpenAIWrapper(model=model, temperature=temperature, api_key=api_key)
