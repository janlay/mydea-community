#!/usr/bin/env python3
"""Build all catalogs from the latest main."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KINDS = {"pages": "page", "sections": "section", "lists": "list", "themes": "theme"}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()


def pull_request(path: Path, repository: str) -> int | None:
    try:
        commit = git("log", "-1", "--format=%H", "--", str(path.relative_to(ROOT)))
    except subprocess.CalledProcessError:
        return None
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token and repository:
        url = f"https://api.github.com/repos/{repository}/commits/{commit}/pulls"
        request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                pulls = json.load(response)
            merged = [p for p in pulls if p.get("merged_at")]
            if merged:
                return max(merged, key=lambda p: p["merged_at"])["number"]
        except (OSError, ValueError, KeyError):
            pass
    try:
        message = git("show", "-s", "--format=%B", commit)
        matches = re.findall(r"\(#(\d+)\)", message)
        return int(matches[-1]) if matches else None
    except subprocess.CalledProcessError:
        return None


def localized_value(values: object, category: str, language: str | None, identifier: str) -> dict:
    if not isinstance(values, dict):
        return {}
    category_values = values.get(category, {})
    if language and isinstance(category_values, dict) and language in category_values:
        return category_values[language].get(identifier, {})
    return category_values.get(identifier, {}) if isinstance(category_values, dict) else {}


def is_featured(values: object, category: str, language: str | None, identifier: str, collection: str | None = None) -> bool:
    category_values = values.get(category, []) if isinstance(values, dict) else []
    if language and isinstance(category_values, dict):
        selected = category_values.get(language, [])
        return identifier in selected or (collection and f"{collection}/{identifier}" in selected)
    return identifier in category_values if isinstance(category_values, list) else False


def build_catalog(directory: str, kind: str, language: str | None, featured: object, metadata: object) -> list[dict]:
    paths = ((ROOT / directory).glob(f"*.{kind}.json") if kind == "theme" else
             (ROOT / "collections").glob(f"*/*/*.{kind}.json"))
    items = []
    for path in sorted(paths):
        if kind != "theme" and path.parent.name != language:
            continue
        raw = path.read_bytes()
        data = json.loads(raw)
        identifier = path.name[: -(len(kind) + 6)]
        collection = path.parent.parent.name if kind != "theme" else None
        tags = data.get("tags", [])
        if not isinstance(tags, list):
            tags = []
        extra = localized_value(metadata, directory, language, identifier)
        tags = extra.get("tags", tags)
        item = {"title": data.get("title") or data.get("name") or identifier,
                "description": extra.get("description", data.get("description", "")),
                "digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
                "path": (f"{language}/{path.name}" if kind != "theme" else str(path.relative_to(ROOT)).replace(os.sep, "/"))}
        if collection is not None:
            item["collection"] = collection
        if tags:
            item["tags"] = tags
        if is_featured(featured, directory, language, identifier, collection):
            item["featured"] = True
        pr = pull_request(path, args.repository)
        if pr is not None:
            item["pullRequest"] = pr
        items.append(item)
    return items


def build(args: argparse.Namespace) -> None:
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    featured = json.loads((ROOT / ".community/featured.json").read_text(encoding="utf-8"))
    metadata_path = ROOT / ".community/metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    languages = sorted({path.parent.name for path in (ROOT / "collections").glob("*/*/*.json")})
    catalog_languages: dict[str, list[str]] = {"pages": [], "sections": [], "lists": []}
    for language in languages:
        for directory in ("pages", "sections", "lists"):
            kind = KINDS[directory]
            items = build_catalog(directory, kind, language, featured, metadata)
            if not items:
                continue
            locale_output = output / language
            locale_output.mkdir(parents=True, exist_ok=True)
            (locale_output / f"{directory}.json").write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            catalog_languages[directory].append(language)
    themes = build_catalog("themes", "theme", None, featured, metadata)
    (output / "themes.json").write_text(json.dumps(themes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registry = {"schemaVersion": 1, "repository": args.repository,
                "catalogs": catalog_languages | {"themes": ["."]}}
    (output / "registry.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


parser = argparse.ArgumentParser()
parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "OWNER/mydea-community"))
parser.add_argument("--output", default="registry-output")
args = parser.parse_args()
build(args)
