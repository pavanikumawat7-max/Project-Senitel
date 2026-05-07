from tools.person1_summarizer.summarizer_tool import analyze_research_input
from tools.person2_roadmap.roadmap_tool import generate_roadmap
from tools.person3_github.github_tools import suggest_actions
import traceback

source = "https://github.com/fastapi/fastapi"
try:
    print("Running step 1...")
    a = analyze_research_input(source)
    print("Step 1 done. Data:", a)
    print("Running step 2...")
    r = generate_roadmap(a)
    print("Step 2 done. Data:", r)
    print("Running step 3...")
    act = suggest_actions(source)
    print("Step 3 done.")
except Exception as e:
    traceback.print_exc()
