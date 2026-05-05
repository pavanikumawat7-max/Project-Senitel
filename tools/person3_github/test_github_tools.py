from pathlib import Path
from github_tools import clone_repo, run_demo, create_branch, insert_code_snippet

REPO_URL = "https://github.com/octocat/Hello-World.git"
DEST = "temp_repo"

print("\n=== TEST 1: clone_repo ===")
result = clone_repo(REPO_URL, DEST)
print(result)

repo = Path(DEST)

if repo.exists():
    print("\n=== PREP: create a demo.py file manually for run_demo ===")
    demo_file = repo / "demo.py"
    demo_file.write_text(
        'print("demo ran successfully")\n',
        encoding="utf-8"
    )
    print(f"Created {demo_file}")

    print("\n=== TEST 2: run_demo ===")
    result = run_demo(DEST)
    print(result)

    print("\n=== TEST 3: create_branch ===")
    result = create_branch(DEST, "sentinel-integration")
    print(result)

    readme_candidates = [repo / "README.md", repo / "README"]
    target = next((p for p in readme_candidates if p.exists()), None)

    if target:
        relative_target = target.name
        print("\n=== TEST 4: insert_code_snippet ===")
        result = insert_code_snippet(
            DEST,
            relative_target,
            "# Sentinel integration test\n",
            1
        )
        print(result)
    else:
        print("No README file found for insert_code_snippet test.")
else:
    print("Repo was not cloned, so later tests were skipped.")
