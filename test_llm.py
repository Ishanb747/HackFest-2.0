import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")
print(f"GROQ_API_KEY loaded: {'YES' if key else 'NO'}")
if key:
    print(f"Key starts with: {key[:8]}...")

print("\n--- Testing LiteLLM via CrewAI ---")
try:
    from crewai import LLM
    llm = LLM(
        model="groq/llama-3.1-8b-instant",
        api_key=key,
        temperature=0.0
    )
    res = llm.call(messages=[{"role": "user", "content": "Hello! Reply with exactly 'TEST OK'."}])
    print("Response:", res)
    print("SUCCESS!")
except Exception as e:
    import traceback
    print("FAILED!")
    traceback.print_exc()
