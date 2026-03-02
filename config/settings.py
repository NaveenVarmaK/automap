from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "lm_studio")

    if provider == "lm_studio":
        return ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="not-needed"
        )
    elif provider == "comet":
        return ChatOpenAI(
            api_key=os.getenv("COMET_API_KEY"),
            base_url="https://api.cometapi.com/v1",
            model=os.getenv("COMET_MODEL")
        )