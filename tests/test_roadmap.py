import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.person2_roadmap.roadmap_tool import generate_roadmap, roadmap_to_markdown


def run_test():
    analysis = {
        "summary": "This paper proposes a deep learning model for image classification using convolutional neural networks.",
        "keywords": ["deep learning", "cnn", "image"]
    }

    roadmap = generate_roadmap(analysis)

    print("\n=== JSON OUTPUT ===\n")
    print(roadmap)

    print("\n=== MARKDOWN OUTPUT ===\n")
    print(roadmap_to_markdown(roadmap))


if __name__ == "__main__":
    run_test()