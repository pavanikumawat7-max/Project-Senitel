# tests/test_summarizer.py
import sys
sys.path.append(".")
from tools.person1_summarizer.summarizer_tool import analyze_research_input

def test_github():
    result = analyze_research_input("https://github.com/facebookresearch/segment-anything")
    print("GitHub result:")
    print(result)
    assert "summary" in result and "relevance_decision" in result

if __name__ == "__main__":
    test_github()
