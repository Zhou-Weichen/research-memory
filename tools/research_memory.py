#!/usr/bin/env python3
"""Portable checks and explicit file handoff; no model, network, or execution."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

CORE = (
    "RESEARCH_STATE.md", "DECISIONS.md", "IDEA_POOL.md",
    "HYPOTHESES.md", "LITERATURE.md", "OPEN_QUESTIONS.md",
)
RECORD_DIRS = (
    "updates", "literature", "experiments", "results",
    "analyses", "agent_tasks", "reports",
)
STATE_SECTIONS = (
    "Direction", "Established Facts", "Active Hypotheses",
    "Current Experiments", "Decisions and Constraints", "Open Questions",
    "Next Actions",
)
TASK_SECTIONS = (
    "Context", "Objective", "Research Motivation", "Implementation",
    "Constraints", "Expected Behavior", "Acceptance Criteria",
    "Functional", "Scientific", "Regression", "Tests", "Experiment",
    "Deliverables", "Handoff",
)
EXP_SECTIONS = (
    "Experiment Question", "Hypothesis", "Manipulation", "Control",
    "Data and Sampling", "Metric", "Expected", "Falsification",
    "Inconclusive", "Alternative Explanation", "Validity Checks",
    "Ablation Plan", "Execution", "Analysis Plan", "Freeze and Revision History",
)
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\n]+)\)")
PLACEHOLDER = re.compile(r"\b(?:TODO|TBD|UNKNOWN)\b|待填写|待确定", re.I)


class MemoryError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local_path(root, name):
    """All manifest paths and explicitly included files stay within this root."""
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise MemoryError(f"Path escapes workspace: {name}")
    return path


def read(root, name):
    return local_path(root, name).read_text(encoding="utf-8")


def field(text, key):
    values = re.findall(rf"^{re.escape(key)}:[ \t]*([^\n]+)$", text, re.M)
    if len(values) != 1 or not values[0].strip():
        raise MemoryError(f"Expected exactly one metadata field: {key}")
    return values[0].strip()


def section(text, name):
    match = re.search(rf"^(#{{2,3}}) {re.escape(name)}\s*$", text, re.M)
    if not match:
        raise MemoryError(f"Missing section: {name}")
    tail = text[match.end():]
    end = re.search(rf"^#{{1,{len(match[1])}}} ", tail, re.M)
    body = tail[:end.start()] if end else tail
    if not body.strip():
        raise MemoryError(f"Empty section: {name}")
    return body.strip()


def state_info(root):
    data = local_path(root, "RESEARCH_STATE.md").read_bytes()
    version = field(data.decode("utf-8"), "State-Version")
    if not re.fullmatch(r"[1-9]\d*", version):
        raise MemoryError("State-Version must be a positive integer")
    return {"state_version": int(version), "state_sha256": digest(data)}


def inventory(root):
    paths = [local_path(root, name) for name in CORE]
    for folder in RECORD_DIRS:
        paths.extend((root / folder).rglob("*.md"))
    result = {}
    for path in sorted(set(paths)):
        name = path.relative_to(root).as_posix()
        result[name] = digest(local_path(root, name).read_bytes())
    return result


def linked_markdown(root, source, text):
    for raw in LINK.findall(text):
        target = raw.strip().split(" ", 1)[0].strip("<>")
        if not target or target.startswith("#") or re.match(r"[a-zA-Z][\w+.-]*:", target):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        candidate = local_path(root, str(Path(source).parent / target))
        yield candidate


def validate_ready(root, name):
    path = local_path(root, name)
    text = path.read_text(encoding="utf-8")
    if PLACEHOLDER.search(text):
        raise MemoryError(f"{name}: unresolved placeholder")
    if not re.fullmatch(r"[1-9]\d*", field(text, "Revision")):
        raise MemoryError(f"{name}: Revision must be a positive integer")
    if path.parent == root / "agent_tasks":
        if field(text, "Status") not in {"Ready", "InProgress"}:
            raise MemoryError(f"{name}: task is not Ready or InProgress")
        task_id = field(text, "Task-ID")
        if not re.fullmatch(r"TASK-\d{3,}", task_id) or path.stem != task_id:
            raise MemoryError(f"{name}: Task-ID must match its filename")
        for heading in TASK_SECTIONS:
            section(text, heading)
        info = state_info(root)
        if field(text, "State-Version") != str(info["state_version"]):
            raise MemoryError(f"{name}: stale State-Version")
        if field(text, "State-SHA256") != info["state_sha256"]:
            raise MemoryError(f"{name}: stale State-SHA256")
        if "RESEARCH_STATE.md" not in section(text, "Context"):
            raise MemoryError(f"{name}: Context must reference RESEARCH_STATE.md")
        exp_id = field(text, "Experiment-ID")
        if exp_id == "None":
            if any(field(text, key) != "None" for key in (
                "Experiment-Revision", "Experiment-SHA256"
            )):
                raise MemoryError(f"{name}: non-experimental task must use None for experiment binding")
            for heading in ("Scientific", "Experiment"):
                if not re.search(r"N/A|不适用", section(text, heading)):
                    raise MemoryError(f"{name}: explain why {heading} is not applicable")
        else:
            if not re.fullmatch(r"EXP-\d{3,}", exp_id):
                raise MemoryError(f"{name}: invalid Experiment-ID")
            exp_name = f"experiments/{exp_id}.md"
            validate_ready(root, exp_name)
            exp_data = local_path(root, exp_name).read_bytes()
            if field(text, "Experiment-Revision") != field(exp_data.decode("utf-8"), "Revision"):
                raise MemoryError(f"{name}: stale Experiment-Revision")
            if field(text, "Experiment-SHA256") != digest(exp_data):
                raise MemoryError(f"{name}: stale Experiment-SHA256")
            if exp_name not in section(text, "Context"):
                raise MemoryError(f"{name}: Context must reference {exp_name}")
    elif path.parent == root / "experiments":
        if field(text, "Status") not in {"Ready", "Running", "Completed"}:
            raise MemoryError(f"{name}: experiment design is not ready")
        exp_id = field(text, "Experiment-ID")
        if not re.fullmatch(r"EXP-\d{3,}", exp_id) or path.stem != exp_id:
            raise MemoryError(f"{name}: Experiment-ID must match its filename")
        for heading in EXP_SECTIONS:
            section(text, heading)
        hyp = field(text, "Hypothesis-ID")
        hypotheses = read(root, "HYPOTHESES.md")
        if not re.fullmatch(r"HYP-\d{3,}", hyp) or not re.search(
            rf"^#{{1,6}} {re.escape(hyp)}\s*$", hypotheses, re.M
        ):
            raise MemoryError(f"{name}: hypothesis record not found")
    else:
        raise MemoryError("--ready requires a file directly in agent_tasks/ or experiments/")


def validate(root, ready=None):
    errors = []
    try:
        for name in CORE + ("RESEARCH_AGENT_PROTOCOL.md", "AGENTS.md"):
            read(root, name)
        state_info(root)
        text = read(root, "RESEARCH_STATE.md")
        for heading in STATE_SECTIONS:
            section(text, heading)
        count = len(re.sub(r"\s", "", text))
        if count > 6000 or len(text.splitlines()) > 180:
            errors.append("RESEARCH_STATE.md exceeds 6000 non-whitespace characters or 180 lines")
        hypotheses = set(re.findall(r"\bHYP-\d{3,}\b", section(text, "Active Hypotheses")))
        if len(hypotheses) > 3:
            errors.append("RESEARCH_STATE.md has more than 3 active hypotheses")
        last = field(text, "Last-Update")
        if not re.fullmatch(r"UPD-\d{8}-\d{3,}", last):
            errors.append("Invalid Last-Update ID")
        elif not local_path(root, f"updates/{last}.md").is_file():
            errors.append(f"Last-Update record not found: {last}")
    except (MemoryError, OSError, UnicodeError) as exc:
        errors.append(str(exc))
    doc_paths = {root / name for name in CORE + ("README.md", "AGENTS.md", "RESEARCH_AGENT_PROTOCOL.md")}
    for folder in RECORD_DIRS + ("prompts", "templates", "examples"):
        doc_paths.update((root / folder).rglob("*.md"))
    for path in sorted(doc_paths):
        relative = path.relative_to(root)
        if set(relative.parts) & {".git", "exports", "artifacts", "__pycache__"}:
            continue
        name = relative.as_posix()
        try:
            text = read(root, name)
            for linked in linked_markdown(root, name, text):
                if not linked.is_file():
                    errors.append(f"{name}: missing linked file {linked.relative_to(root)}")
            if path.parent in (root / "agent_tasks", root / "experiments"):
                status = field(text, "Status")
                if status in {"Ready", "InProgress", "Running"}:
                    validate_ready(root, name)
        except (MemoryError, OSError, UnicodeError) as exc:
            errors.append(f"{name}: {exc}")
    if ready:
        try:
            validate_ready(root, ready)
        except (MemoryError, OSError, UnicodeError) as exc:
            errors.append(str(exc))
    return list(dict.fromkeys(errors))


def verify_manifest(root, manifest):
    if not isinstance(manifest, dict) or manifest.get("schema") != 1:
        raise MemoryError("Unsupported manifest schema")
    info = state_info(root)
    for key, value in info.items():
        if manifest.get(key) != value:
            raise MemoryError(f"Stale context: {key} differs")
    expected = manifest.get("files")
    expected_inventory = manifest.get("inventory")
    if not isinstance(expected, dict) or not expected or not isinstance(expected_inventory, dict):
        raise MemoryError("Manifest requires non-empty files and an inventory")
    if expected.get("RESEARCH_STATE.md") != info["state_sha256"]:
        raise MemoryError("Manifest must bind RESEARCH_STATE.md")
    for name, sha in expected.items():
        if not isinstance(name, str) or not isinstance(sha, str):
            raise MemoryError("Invalid manifest entry")
        if digest(local_path(root, name).read_bytes()) != sha:
            raise MemoryError(f"Stale context: {name} differs")
    if inventory(root) != expected_inventory:
        raise MemoryError("Stale context: research records added, removed, or changed")


def export_context(root, includes=()):
    errors = validate(root)
    if errors:
        raise MemoryError("\n".join(errors))
    names = set(CORE) | {"RESEARCH_AGENT_PROTOCOL.md"}
    for folder in ("prompts", "templates"):
        names.update(p.relative_to(root).as_posix() for p in (root / folder).glob("*.md"))
    for name in includes:
        path = local_path(root, name)
        if path.suffix != ".md" or not path.is_file():
            raise MemoryError(f"--include requires an existing Markdown file: {name}")
        names.add(path.relative_to(root).as_posix())
    content = {}
    pending = sorted(names)
    while pending:
        name = pending.pop()
        if name in content:
            continue
        content[name] = local_path(root, name).read_bytes()
        for path in linked_markdown(root, name, content[name].decode("utf-8")):
            relative = path.relative_to(root)
            if path.suffix == ".md" and relative.parts[0] in RECORD_DIRS:
                pending.append(relative.as_posix())
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_id = f"{stamp}-{uuid.uuid4().hex[:8]}"
    manifest = {
        "schema": 1, "bundle_id": bundle_id, "exported_at_utc": stamp,
        **state_info(root),
        "files": {name: digest(data) for name, data in sorted(content.items())},
        "inventory": inventory(root),
    }
    verify_manifest(root, manifest)
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    chunks = [
        "# Research Context Snapshot\n\n",
        "这是文件快照，不是新的研究结论。以本清单识别基线；未提供内容不能从聊天记忆补造。\n\n",
        "## Manifest\n\n~~~json\n", manifest_text, "~~~\n\n",
    ]
    for name in ["RESEARCH_STATE.md"] + sorted(set(content) - {"RESEARCH_STATE.md"}):
        chunks += [
            f"\n<!-- BEGIN FILE: {name} -->\n\n",
            f"## Source file: {name}\n\n",
            content[name].decode("utf-8"),
            f"\n\n<!-- END FILE: {name} -->\n",
        ]
    output = local_path(root, "exports")
    output.mkdir(exist_ok=True)
    bundle = output / f"context-{bundle_id}.md"
    manifest_path = output / f"manifest-{bundle_id}.json"
    # Unique filenames: exports never silently overwrite a previous snapshot.
    with bundle.open("x", encoding="utf-8") as handle:
        handle.write("".join(chunks))
    with manifest_path.open("x", encoding="utf-8") as handle:
        handle.write(manifest_text)
    return bundle, manifest_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="Check memory and optionally execution readiness")
    check.add_argument("--ready", help="Task or experiment path relative to workspace")
    commands.add_parser("fingerprint", help="Print current version and research file hashes")
    export = commands.add_parser("export", help="Export a discussion snapshot and manifest")
    export.add_argument("--include", action="append", default=[])
    verify = commands.add_parser("verify-base", help="Reject stale discussion context")
    verify.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "check":
            errors = validate(root, args.ready)
            if errors:
                raise MemoryError("\n".join(errors))
            info = state_info(root)
            print(f"OK: State v{info['state_version']}; structural checks passed.")
            print("Scientific validity and evidence still require review.")
        elif args.command == "fingerprint":
            print(json.dumps({**state_info(root), "inventory": inventory(root)}, indent=2, ensure_ascii=False))
        elif args.command == "export":
            bundle, manifest = export_context(root, args.include)
            print(f"Context: {bundle}\nManifest: {manifest}")
        else:
            # Relative manifest paths are workspace-relative, even with --root.
            manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            verify_manifest(root, manifest)
            print("OK: discussion baseline matches current files.")
        return 0
    except (MemoryError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
