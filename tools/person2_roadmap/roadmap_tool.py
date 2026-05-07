import json
import re
from openai import OpenAI

def call_llm_roadmap(analysis_data: dict) -> dict:
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required by client but ignored by Ollama
    )
    model = "llama3.2"

    system_prompt = (
        "You are an expert technical project manager and software architect. "
        "Based on the provided analysis data, create a technical roadmap. "
        "Output a JSON object with exactly these keys: "
        "'simplified_idea' (string, a concise idea of what we are building based on the analysis), "
        "'milestones' (object mapping timeframe strings like '2_weeks', '1_month', '1_semester' to lists of task strings), "
        "and 'safe_integration_plan' (string, detailing how to safely integrate this technology). "
        "No extra text, no markdown formatting."
    )
    user_prompt = f"Analysis Data:\n{json.dumps(analysis_data, indent=2)}\n\nGenerate the roadmap JSON."

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
    )
    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

    # Ensure required keys exist
    for key in ["simplified_idea", "milestones", "safe_integration_plan"]:
        if key not in data:
            if key == "milestones":
                data[key] = {
                    "2_weeks": ["Initial setup"],
                    "1_month": ["Integration"],
                    "1_semester": ["Production ready"]
                }
            else:
                data[key] = "Not provided."
    return data

def generate_roadmap(analysis_data: dict) -> dict:
    """
    Generate a roadmap based on the input analysis data.
    """
    return call_llm_roadmap(analysis_data)
