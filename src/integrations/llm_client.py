# integrations/llm_client.py

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI  # now from the correct package

def make_openai_llm(
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.2
):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set in environment.")

    return ChatOpenAI(
        model=model,
        openai_api_key=api_key,
        temperature=temperature
    )
