# tools/person1_summarizer/summarizer_tool.py

import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------- Text extractors ----------
def extract_text_from_pdf(pdf_path: str, max_chars: int = 2000) -> str:
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


def extract_text_from_github(repo_url: str, max_chars: int = 2000) -> str:
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


# ---------- LLM caller (Ollama via OpenAI client) ----------
def call_llm(text: str) -> dict:
    from openai import OpenAI

    # Connect to local Ollama server (no API key needed)
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required by client but ignored by Ollama
    )
    model = "llama3.2"   # you can also use "llama3.1", "mistral", etc.

    system_prompt = (
        "You are an assistant that reads academic paper or GitHub repo content. "
        "Output a JSON object with exactly these keys: "
        "summary (3 sentences), relevance_decision ('yes' or 'no'), "
        "relevance_reason (string), dependencies (list of strings), key_datasets (list of strings). "
        "No extra text, no markdown formatting."
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
        # Ollama ignores response_format, but we handle parsing below
    )
    raw = response.choices[0].message.content.strip()

    # Strip possible markdown fences (```json ... ```)
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    # Parse JSON robustly
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
    for key in ["summary", "relevance_decision", "relevance_reason", "dependencies", "key_datasets"]:
        if key not in data:
            if key in ["dependencies", "key_datasets"]:
                data[key] = []
            elif key == "relevance_decision":
                data[key] = "no"
            else:
                data[key] = ""
    return data


# ---------- Plain function (no decorator, returns dict) ----------
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
