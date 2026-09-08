#!/usr/bin/env python3
"""Validate Community resources and their local List references."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("Install the validation dependency first: python3 -m pip install jsonschema", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[2]
KINDS = {"pages": "page", "sections": "section", "lists": "list", "themes": "theme"}
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*\.(page|section|list|theme)\.json$")
# Language tag: a language subtag plus an optional script subtag, such as zh, zh-Hans or
# zh-Hant. Region subtags are rejected on purpose: Chinese is separated by script, never
# by region, so zh-CN, zh-HK and zh-TW are not accepted.
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9-]*$")
LANGUAGE = re.compile(r"^[a-z]{2,3}(?:-[A-Z][a-z]{3})?$")


def localized_paths(pattern: str) -> list[Path]:
    """Resources under top-level category directories: <category>/<collection>/<language>/<file>."""
    return sorted(path for category in ROOT.iterdir()
                  if category.is_dir() and not category.name.startswith(".") and category.name != "themes"
                  for path in category.glob(f"*/*/{pattern}"))


def fail(path: Path, message: str) -> None:
    print(f"✗ {path.relative_to(ROOT)}: {message}", file=sys.stderr)


def schema_validator(kind: str):
    path = ROOT / ".community" / "schemas" / f"{kind}.schema.json"
    if not path.exists():
        return None
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def local_list(value: object) -> str | None:
    if not isinstance(value, str) or not value or urlparse(value).scheme in {"http", "https"}:
        return None
    value = value.removesuffix(".list.json")
    if "/" in value or not value:
        return None
    return f"{value}.list.json"


def check_list_refs(value: object, lists: set[str]) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"url", "list", "listUrl", "listURL", "source"}:
                candidate = local_list(child)
                if candidate:
                    found.append(candidate)
            found.extend(check_list_refs(child, lists))
    elif isinstance(value, list):
        for child in value:
            found.extend(check_list_refs(child, lists))
    return sorted(set(found))


def main() -> int:
    validators = {kind: schema_validator(kind) for kind in KINDS.values()}
    errors = 0
    for directory, kind in KINDS.items():
        paths = (sorted((ROOT / directory).glob("**/*")) if kind == "theme"
                 else localized_paths(f"*.{kind}.json"))
        for path in paths:
            if not path.is_file():
                continue
            language = None
            if kind != "theme":
                language = path.parent.name
                if (not LANGUAGE.fullmatch(language) or not all(IDENTIFIER.fullmatch(p.name) for p in path.parents[1:3])):
                    fail(path, "localized resources must be stored as <category>/<collection>/<language>/<file>")
                    errors += 1
            elif path.parent != ROOT / directory:
                fail(path, "themes must remain flat")
                errors += 1
            if not NAME.fullmatch(path.name) or not path.name.endswith(f".{kind}.json"):
                fail(path, f"filename must be <id>.{kind}.json and use only lowercase letters, digits, and hyphens")
                errors += 1
                continue
            try:
                raw = path.read_bytes()
                text = raw.decode("utf-8")
                value = json.loads(text)
            except UnicodeDecodeError:
                fail(path, "must use UTF-8 encoding")
                errors += 1
                continue
            except json.JSONDecodeError as exc:
                fail(path, f"invalid JSON (line {exc.lineno}, column {exc.colno})")
                errors += 1
                continue
            if validators[kind] is None:
                fail(path, f"no upstream OpenAPI schema is available for {kind}")
                errors += 1
                continue
            messages = sorted(validators[kind].iter_errors(value), key=lambda e: tuple(map(str, e.path)))
            for error in messages:
                location = ".".join(map(str, error.path)) or "root object"
                fail(path, f"field {location}: {error.message}; re-export the resource from Mydea")
                errors += 1
            if kind in {"page", "section"} and language:
                local_lists = {p.name for p in path.parent.glob("*.list.json")}
                for ref in check_list_refs(value, local_lists):
                    if ref not in local_lists:
                        fail(path, f"referenced Community List does not exist in the same collection: {ref}")
                        errors += 1
        print(f"✓ {directory} validation complete")
    featured = ROOT / ".community" / "featured.json"
    try:
        data = json.loads(featured.read_text(encoding="utf-8"))
        for category in KINDS:
            entries = data.get(category, {}) if category != "themes" else data.get(category, [])
            if isinstance(entries, dict):
                entries = [identifier for language_entries in entries.values() for identifier in language_entries]
            for identifier in entries:
                available = ({identifier for p in localized_paths(f"*.{KINDS[category]}.json")
                             for identifier in (p.stem.rsplit(".", 1)[0], f"{p.parents[2].name}/{p.parents[1].name}/{p.stem.rsplit('.', 1)[0]}")}
                             if category != "themes" else
                             {p.stem.rsplit(".", 1)[0] for p in (ROOT / category).glob(f"*.{KINDS[category]}.json")})
                if not isinstance(identifier, str) or identifier not in available:
                    fail(featured, f"Featured resource does not exist in {category}: {identifier}")
                    errors += 1
    except (OSError, json.JSONDecodeError) as exc:
        fail(featured, f"cannot read: {exc}")
        errors += 1
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
