"""Discover and validate the installable skills in this collection."""

from pathlib import Path
import re

try:
    import yaml
except ModuleNotFoundError:
    raise SystemExit("Install the authoring dependencies: python3 -m pip install -r requirements-codex.txt")


ROOT = Path(__file__).resolve().parents[1]


def catalog(root=ROOT):
    paths = sorted(set(root.glob("*/SKILL.md"))
                   | set(root.glob("superpowers/*/SKILL.md"))
                   | set(root.glob("doc/00_reference/*/SKILL.md")))
    entries = {}
    for path in paths:
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
        if not match:
            raise ValueError(f"Missing YAML frontmatter: {path}")
        try:
            fields = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML frontmatter in {path}: {exc}") from exc
        if not isinstance(fields, dict):
            raise ValueError(f"Frontmatter must be a mapping: {path}")
        name, description = fields.get("name"), fields.get("description")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            raise ValueError(f"Invalid skill name in {path}: {name!r}")
        if name != path.parent.name:
            raise ValueError(f"Name must match directory: {path}")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            raise ValueError(f"Invalid/overlong description: {path}")
        if any(c in description for c in "<>"):
            raise ValueError(f"Angle brackets in description: {path}")
        if name in entries:
            raise ValueError(f"Duplicate skill name {name}: {path} and {entries[name]}")
        entries[name] = path.parent
    if not entries:
        raise ValueError("No installable skills found")
    return entries
