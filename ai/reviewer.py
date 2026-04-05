# ai/reviewer.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash-lite"




def _call_ai(prompt: str) -> str:
    
    """Send a prompt to OpenRouter and return the response text."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter API error {response.status_code}: {response.text[:300]}"
        )

    data = response.json()

    try:
        #print(f"       Model used: {data.get('model', 'unknown')}")
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected response shape: {data}")


def full_review(code: str, lang: str, problem_title: str) -> dict:
    """
    Send the latest submission for a detailed review.
    Returns a dict with keys: time, space, optimization, best_solution_text,
    best_solution_code, takeaways.
    """
    prompt = f"""
You are a competitive programming mentor and LeetCode interviewer.

I will give you a LeetCode problem name and my code solution.
Problem: {problem_title}

Analyze my solution and return your response in EXACTLY this format with these exact headers:

### Time Complexity
[State Big-O and explain step by step why]

### Space Complexity
[State Big-O and clearly distinguish auxiliary space vs input/output space]

### Optimization Review
[Is this solution optimal? If not, explain what makes it suboptimal]

### Best Possible Solution
[Explain the best known solution — intuition first, then approach. Do NOT include code here.]

### Best Solution Code
[Provide ONLY the clean well-commented code in {lang} with no extra explanation outside the code]

### Learning Takeaways
[Key patterns and techniques used. How to recognize this pattern in future problems.]

Here is my code:
{lang}
{code}

Important: Use exactly the headers above. Be concise but thorough. Explain like you are teaching someone preparing for technical interviews.
"""
    raw = _call_ai(prompt)
    return _parse_full_review(raw, lang)


def _parse_full_review(raw: str, lang: str) -> dict:
    """
    Parse the structured AI response into a dict.
    Each key maps to the content under that section header.
    """
    sections = {
        "time": "",
        "space": "",
        "optimization": "",
        "best_solution_text": "",
        "best_solution_code": "",
        "takeaways": "",
    }

    markers = {
        "### Time Complexity": "time",
        "### Space Complexity": "space",
        "### Optimization Review": "optimization",
        "### Best Possible Solution": "best_solution_text",
        "### Best Solution Code": "best_solution_code",
        "### Learning Takeaways": "takeaways",
    }

    current_key = None
    buffer = []

    for line in raw.splitlines():
        stripped = line.strip()
        if stripped in markers:
            if current_key:
                sections[current_key] = "\n".join(buffer).strip()
            current_key = markers[stripped]
            buffer = []
        else:
            if current_key:
                buffer.append(line)

    if current_key:
        sections[current_key] = "\n".join(buffer).strip()

    # Clean code block markers from best_solution_code if AI wrapped it
    code = sections["best_solution_code"]
    lines = code.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    sections["best_solution_code"] = "\n".join(lines).strip()

    return sections
def light_review(code: str, lang: str, status: str) -> str:
    prompt = f"""
You are an expert software engineer doing a brief code review.

This submission has status: {status}.
{"This means the code produced incorrect output — focus on what went wrong logically." if status == "Wrong Answer" else ""}
{"This means the code timed out — focus on the time complexity issue." if status == "Time Limit Exceeded" else ""}

In exactly 2-3 sentences:
1. What approach does this code use?
2. Why did it fail or what is its main limitation?

Here is the code:
{code}
"""
    return _call_ai(prompt)