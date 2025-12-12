import os
from dotenv import load_dotenv
load_dotenv()

try:
    # Attempt the 1.1.3 compatible import
    from langchain.llms import OpenAI
except ImportError:
    # fallback: older LangChain path
    from langchain import OpenAI

def make_openai_llm(model="gpt-3.5-turbo", temperature=0.2):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set in environment.")
    return OpenAI(model_name=model, openai_api_key=api_key, temperature=temperature)
