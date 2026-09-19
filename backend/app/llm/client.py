from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv(
    Path(__file__).resolve().parents[2] / ".env"
)


def get_llm():
    """Create and return the CodePilot LLM client."""

    return ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0,
    )