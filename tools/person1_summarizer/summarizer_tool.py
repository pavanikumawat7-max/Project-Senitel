# tools/person1_summarizer/summarizer_tool.py

from __future__ import annotations

import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------- OpenClaw fallback (allows the decorator even if openclaw is missing) ----------
try:
    from openclaw import tool
except ImportError:
    def tool(*args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

# If you need approval functions (not needed here, but safe to include)
try:
    from openclaw import request_approval
except ImportError:
    def request_approval(*args, **kwargs):
        raise RuntimeError("OpenClaw approval API not available.")


# ---------- Text extractors ----------
def extract_text_from_pdf(pdf_path: str, max_chars: int = 8000) -> str:
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
        if len(text) >= max_chars:
            break
    return text[:max_chars].strip()


def extract_text_from_github(repo_url: str, max_chars: int = 8000) -> str:
    url = repo_url.strip().rstrip("/")
    path = url.replace("https://github.com/", "", 1)
    parts = path.split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")
    owner, repo = parts[0], parts[1]
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
    resp = requests.get(raw_url, timeout=10)
    if resp.status_code == 404:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
        resp = requests.get(raw_url, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Could not fetch README (status {resp.status_code})")
    return resp.text[:max_chars].strip()


# ---------- LLM caller ----------
def call_llm(text: str) -> dict:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set. Add it to your .env file.")

    client = OpenAI(api_key=api_key)
    model = "gpt-4o-mini"

    system_prompt = (
        "You are an assistant that reads academic paper or GitHub repo content. "
        "Output a JSON object with exactly these keys: "
        "summary (3 sentences), relevance_decision ('yes' or 'no'), "
        "relevance_reason (string), dependencies (list of strings), key_datasets (list of strings). "
        "No extra text."
    )
    user_prompt = (
        f"Content:\n{text}\n\n"
        f"Analyze its relevance for a project that does real-time speech enhancement on edge devices. "
        f"Provide the JSON."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError("Could not parse LLM output as JSON")

    for key in ["summary", "relevance_decision", "relevance_reason", "dependencies", "key_datasets"]:
        if key not in data:
            if key in ["dependencies", "key_datasets"]:
                data[key] = []
            elif key == "relevance_decision":
                data[key] = "no"
            else:
                data[key] = ""
    return data


# ---------- Main tool (decorated with @tool) ----------
@tool
def analyze_research_input(source: str) -> dict:
    """
    Analyze a research paper PDF or GitHub repo.
    Returns JSON with summary, relevance, dependencies, and datasets.
    """
    if source.lower().endswith(".pdf"):
        text = extract_text_from_pdf(source)
    elif "github.com" in source.lower():
        text = extract_text_from_github(source)
    else:
        raise ValueError("source must be a .pdf file path or a GitHub URL")

    if not text or len(text) < 50:
        raise ValueError("Extracted text too short or empty")

    return call_llm(text)
