import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../../.env",override=False)

llm = ChatOpenAI(
    model=os.getenv("EVAL_LLM_MODEL", "deepseek-chat"),
    # model=os.getenv("EVAL_LLM_MODEL", "deepseek-reasoner"),
    api_key=os.getenv("EVAL_LLM_BINDING_API_KEY"),
    base_url=os.getenv("EVAL_LLM_BINDING_HOST"),
)

try:
    response = llm.invoke("Hello, test message")
    print(f"Success: {response.content}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
