from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

try:
    from openclaw import tool, request_approval
except ImportError:
    try:
        from openclaw import tool, interrupt as request_approval
    except ImportError:
        def tool(*args, **kwargs):
            def decorator(fn):
                return fn
            return decorator

        def request_approval(message: str):
            raise RuntimeError(
                "OpenClaw approval API not available. Install/import OpenClaw's request_approval or interrupt function."
            )


def _ask_approval(message: str) -> None:
    result = request_approval(message)
    if result is False:
        raise PermissionError("Action not approved by human.")
    if isinstance(result, str) and result.strip().lower() not in {"y", "yes", "approved", "true"}:
        raise PermissionError("Action not approved by human.")


def _run_command(command: list[str], cwd: Optional[Path] = None) -> str:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=True,
    )
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return output or "command completed successfully"


@tool

def clone_repo(repo_url: str, dest_path: str = "temp_repo") -> str:
    """Clone a Git repository locally after human approval."""
    try:
        _ask_approval(f"Will clone {repo_url} into {dest_path}. Approve?")
        dest = Path(dest_path).expanduser().resolve()
        if dest.exists():
            return f"error: destination already exists: {dest}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        output = _run_command(["git", "clone", repo_url, str(dest)])
        return f"cloned into {dest}\n{output}"
    except PermissionError:
        return "cancelled: clone not approved"
    except subprocess.CalledProcessError as e:
        detail = "\n".join(part for part in [e.stdout.strip(), e.stderr.strip()] if part)
        return f"error cloning repo: {detail or str(e)}"
    except Exception as e:
        return f"error cloning repo: {e}"


@tool

def run_demo(repo_path: str) -> str:
    """Run a local demo script after human approval."""
    try:
        repo = Path(repo_path).expanduser().resolve()
        if not repo.exists() or not repo.is_dir():
            return f"error: repo path not found: {repo}"

        candidates = ["demo.py", "example.py", "run.sh"]
        script = next((repo / name for name in candidates if (repo / name).exists()), None)
        if script is None:
            return "no demo found"

        _ask_approval(f"Will run {script.name}. Approve?")

        if script.suffix == ".py":
            output = _run_command(["python", script.name], cwd=repo)
        elif script.suffix == ".sh":
            output = _run_command(["bash", script.name], cwd=repo)
        else:
            return f"error: unsupported demo script: {script.name}"

        return f"ran {script.name}\n{output}"
    except PermissionError:
        return "cancelled: demo run not approved"
    except subprocess.CalledProcessError as e:
        detail = "\n".join(part for part in [e.stdout.strip(), e.stderr.strip()] if part)
        return f"error running demo: {detail or str(e)}"
    except Exception as e:
        return f"error running demo: {e}"


@tool

def create_branch(repo_path: str, branch_name: str = "sentinel-integration") -> str:
    """Create a local git branch after human approval."""
    try:
        repo = Path(repo_path).expanduser().resolve()
        if not repo.exists() or not repo.is_dir():
            return f"error: repo path not found: {repo}"

        _ask_approval(f"Will create branch {branch_name}. Approve?")
        output = _run_command(["git", "checkout", "-b", branch_name], cwd=repo)
        return f"created branch {branch_name}\n{output}"
    except PermissionError:
        return "cancelled: branch creation not approved"
    except subprocess.CalledProcessError as e:
        detail = "\n".join(part for part in [e.stdout.strip(), e.stderr.strip()] if part)
        return f"error creating branch: {detail or str(e)}"
    except Exception as e:
        return f"error creating branch: {e}"


@tool

def insert_code_snippet(
    repo_path: str,
    file_path: str,
    code_snippet: str,
    line_number: Optional[int] = None,
) -> str:
    """Insert code into a file in the local repo after human approval."""
    try:
        repo = Path(repo_path).expanduser().resolve()
        target = (repo / file_path).resolve()

        if not repo.exists() or not repo.is_dir():
            return f"error: repo path not found: {repo}"
        if not str(target).startswith(str(repo)):
            return "error: file_path must stay within repo_path"
        if not target.exists():
            return f"error: target file not found: {target}"

        _ask_approval(f"Will insert code into {file_path}. Approve?")

        original = target.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        snippet = code_snippet if code_snippet.endswith("\n") else code_snippet + "\n"

        if line_number is None:
            insert_at = 0
        else:
            if line_number < 1:
                return "error: line_number must be 1 or greater"
            insert_at = min(line_number - 1, len(lines))

        lines.insert(insert_at, snippet)
        target.write_text("".join(lines), encoding="utf-8")
        human_line = insert_at + 1
        return f"inserted code into {target} at line {human_line}"
    except PermissionError:
        return "cancelled: code insertion not approved"
    except Exception as e:
        return f"error inserting code: {e}"

def suggest_actions(source_url: str) -> list[dict]:
    """Suggest actions based on the source repository URL."""
    actions = []
    source_lower = source_url.lower() if source_url else ""

    # Heuristic for GitHub URL
    if "github.com" in source_lower:
        repo_name = source_url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
            
        actions.append({
            "name": "Clone repository",
            "cmd": f"git clone {source_url}"
        })
        actions.append({
            "name": "Create integration branch",
            "cmd": f"cd {repo_name} && git checkout -b sentinel-integration"
        })
        actions.append({
            "name": "Install dependencies",
            "cmd": f"cd {repo_name} && pip install -r requirements.txt"
        })
    elif source_lower.endswith('.pdf') or source_lower.startswith(('file:', '/', '\\')):
        # No repo actions for uploaded/local PDFs
        return []
    else:
        # Default actions if not a recognizable GitHub URL
        actions.append({
            "name": "Create integration branch",
            "cmd": "git checkout -b sentinel-integration"
        })

    return actions
