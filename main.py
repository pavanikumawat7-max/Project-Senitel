from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import base64
import os
import tempfile
from pathlib import Path
from typing import Optional

# Import tools
from tools.person1_summarizer.summarizer_tool import analyze_research_input
from tools.person2_roadmap.roadmap_tool import generate_roadmap
from tools.person3_github.github_tools import suggest_actions

class AnalyzeRequest(BaseModel):
    source: Optional[str] = None
    pdf_name: Optional[str] = None
    pdf_data: Optional[str] = None


def _save_uploaded_pdf(pdf_name: str, pdf_data: str) -> str:
    try:
        raw_data = base64.b64decode(pdf_data)
    except Exception as e:
        raise ValueError(f"Invalid PDF data: {e}")

    suffix = Path(pdf_name).suffix if pdf_name else ".pdf"
    if suffix.lower() != ".pdf":
        suffix = ".pdf"

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(raw_data)
    temp_file.flush()
    temp_file.close()
    return temp_file.name

app = FastAPI(title="Project Sentinel API")

# Add CORS middleware to allow requests from the frontend (index.html)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if (req.source and req.pdf_data) or (not req.source and not req.pdf_data):
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one input: either a GitHub URL or an uploaded PDF file."
        )

    temp_pdf_path = None
    try:
        if req.pdf_data:
            temp_pdf_path = _save_uploaded_pdf(req.pdf_name or "upload.pdf", req.pdf_data)
            source = temp_pdf_path
        else:
            source = req.source

        # Step 1: Person 1 (Summarizer)
        analysis_data = analyze_research_input(source)

        # Step 2: Person 2 (Roadmap)
        roadmap_data = generate_roadmap(analysis_data)

        # Step 3: Person 3 (Actions)
        actions = suggest_actions(source)

        # Combine the results to match frontend expectations
        response = {
            "analysis": analysis_data,
            "roadmap": roadmap_data,
            "actions": actions
        }

        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
            except OSError:
                pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


