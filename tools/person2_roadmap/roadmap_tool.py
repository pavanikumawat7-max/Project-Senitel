def tool(func):
    return func


@tool
def generate_roadmap(analysis: dict) -> dict:
    summary = analysis.get("summary", "")
    keywords = analysis.get("keywords", [])

    simplified_idea = f"This project is about {summary[:150]}..."

    required_datasets = []
    if "image" in summary.lower():
        required_datasets.append("MNIST / CIFAR-10")
    if "text" in summary.lower():
        required_datasets.append("Wikipedia / custom text dataset")

    required_dependencies = [
        "Python",
        "NumPy",
        "Pandas",
        "Scikit-learn"
    ]

    if "deep learning" in summary.lower() or "neural" in summary.lower():
        required_dependencies.append("TensorFlow / PyTorch")

    milestones = ["Setup", "Prototype", "Integrate", "Test", "Deploy"]

    def scale_timeline(total_days):
        weights = {
            "Setup": 0.2,
            "Prototype": 0.3,
            "Integrate": 0.2,
            "Test": 0.2,
            "Deploy": 0.1
        }
        return {
            "milestone_days": {
                m: max(1, int(total_days * w)) for m, w in weights.items()
            }
        }

    timelines = {
        "2_weeks": scale_timeline(10),
        "1_month": scale_timeline(20),
        "1_semester": scale_timeline(90)
    }

    safe_integration_plan = (
        "Use a separate Git branch. Run in virtualenv or Docker. "
        "Avoid modifying core files directly."
    )

    return {
        "simplified_idea": simplified_idea,
        "required_datasets": required_datasets,
        "required_dependencies": required_dependencies,
        "milestones": milestones,
        "timelines": timelines,
        "safe_integration_plan": safe_integration_plan
    }


def roadmap_to_markdown(roadmap: dict) -> str:
    md = ""

    md += "## 📌 Simplified Idea\n"
    md += f"{roadmap['simplified_idea']}\n\n"

    md += "## 📊 Required Datasets\n"
    for ds in roadmap["required_datasets"]:
        md += f"- {ds}\n"
    md += "\n"

    md += "## ⚙️ Dependencies\n"
    for dep in roadmap["required_dependencies"]:
        md += f"- {dep}\n"
    md += "\n"

    md += "## 🚀 Milestones\n"
    for i, m in enumerate(roadmap["milestones"], 1):
        md += f"{i}. {m}\n"
    md += "\n"

    md += "## ⏳ Timelines\n"
    for k, v in roadmap["timelines"].items():
        md += f"\n### {k.replace('_', ' ').title()}\n"
        for m, d in v["milestone_days"].items():
            md += f"- {m}: {d} days\n"

    md += "\n## 🔒 Safe Integration Plan\n"
    md += roadmap["safe_integration_plan"]

    return md