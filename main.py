"""Groq tool-calling starter.  Run:  python main.py

To add your own tool: write a function in section 1 and add it to TOOLS. That's it.
"""
import inspect
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # reads GROQ_API_KEY from .env
client = Groq()

MODEL = "openai/gpt-oss-120b"  # other models: https://console.groq.com/docs/models
# The agent reads context.md before answering. Edit that file to change how it behaves.
SYSTEM_PROMPT = (Path(__file__).parent / "context.md").read_text()


# ---------- 1. TOOLS: plain Python functions ----------
# The docstring tells the AI what the tool does. Type hints tell it what to pass in.

def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%A, %B %d %Y, %I:%M %p")


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"72F and sunny in {city}"  # fake! swap in a real weather API


TOOLS = [get_current_time, multiply, get_weather]


# ---------- 2. PLUMBING: you shouldn't need to touch this ----------

JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean"}


def to_schema(fn):
    """Turn a Python function into the JSON description the API expects."""
    # ponytail: only str/int/float/bool params, write the schema by hand for lists/objects
    params = inspect.signature(fn).parameters
    return {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": fn.__doc__,
            "parameters": {
                "type": "object",
                "properties": {name: {"type": JSON_TYPES[p.annotation]} for name, p in params.items()},
                "required": list(params),
            },
        },
    }


def ask(messages):
    """Send the conversation to the model, run any tools it asks for, return its final answer."""
    functions = {fn.__name__: fn for fn in TOOLS}
    while True:
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=[to_schema(fn) for fn in TOOLS]
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:  # no tool needed -> this is the final answer
            return message.content

        for call in message.tool_calls:
            try:
                result = functions[call.function.name](**json.loads(call.function.arguments))
            except Exception as e:  # tell the model what went wrong so it can retry
                result = f"Error: {e}"
            print(f"  [tool] {call.function.name}({call.function.arguments}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})


# ---------- 3. CHAT LOOP ----------

if __name__ == "__main__":
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Chat with the AI (Ctrl+C to quit). Try: what's 12.5 times 8, and what time is it?")
    while True:
        try:
            user_input = input("\nYou: ")
        except (KeyboardInterrupt, EOFError):
            break
        messages.append({"role": "user", "content": user_input})
        print("AI:", ask(messages))
