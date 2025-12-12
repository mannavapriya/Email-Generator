import os
from dotenv import load_dotenv
from langchain.llms import OpenAI

load_dotenv()

def make_openai_llm(
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.2
):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set in environment.")

    return OpenAI(
        model_name=model,
        openai_api_key=api_key,
        temperature=temperature
    )
