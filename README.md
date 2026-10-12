# Copilot Build Night — Groq Tool Calling Template

A one-file starter for giving an AI tools it can call. Free API key, no credit card.

## Setup (2 minutes)

1. Get a free key at https://console.groq.com/keys
2. Run:

```bash
git clone https://github.com/Agentic-AI-UIUC/copilot-buildnight-code-template
cd copilot-buildnight-code-template
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # Windows: copy .env.example .env
```

3. Open `.env` and paste your key.
4. `python main.py`

## Add your own tool

Open `main.py`, write a function, add it to `TOOLS`:

```python
def roll_dice(sides: int) -> int:
    """Roll a dice with the given number of sides."""
    return random.randint(1, sides)

TOOLS = [get_current_time, multiply, get_weather, roll_dice]
```

- The **docstring** is how the AI knows when to use your tool — make it clear.
- **Type hints** (`str`, `int`, `float`, `bool`) are required on every parameter.

## Give the agent context

The agent reads `context.md` before every conversation (it's the system prompt).
Edit it in plain English: who the agent is, what it knows, what rules it follows.

## How tool calling works

1. You send the model your message plus a list of tools it may use.
2. The model replies either with an answer, or with "call `multiply` with `a=12.5, b=8`".
3. Your code runs the function and sends the result back.
4. Repeat until the model answers. That loop is the `ask()` function.

## Things to try

- Make `get_weather` real (https://open-meteo.com needs no key)
- Edit `context.md` to give the AI a personality, a job, or facts to know
- Add a tool that reads/writes a file, searches the web, or calls another API

Never commit your `.env` — it's already in `.gitignore`.
