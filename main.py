from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import tools
from tools.person1_summarizer.summarizer_tool import analyze_research_input
from tools.person2_roadmap.roadmap_tool import generate_roadmap
from tools.person3_github.github_tools import suggest_actions

app = FastAPI(title="Project Sentinel API")

# Add CORS middleware to allow requests from the frontend (index.html)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class AnalyzeRequest(BaseModel):
    source: str

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if not req.source:
        raise HTTPException(status_code=400, detail="Source is required")
        
    try:
        # Step 1: Person 1 (Summarizer)
        analysis_data = analyze_research_input(req.source)
        
        # Step 2: Person 2 (Roadmap)
        roadmap_data = generate_roadmap(analysis_data)
        
        # Step 3: Person 3 (Actions)
        actions = suggest_actions(req.source)
        
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
