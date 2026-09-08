#!/usr/bin/env python3
"""Build the catalogs from the latest main, reusing everything a baseline already describes."""
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
KINDS = {"pages": "page", "lists": "list", "themes": "theme"}


def localized_paths(pattern: str) -> list[Path]:
    """Resources under top-level category directories: <category>/<collection>/<language>/<file>."""
    return sorted(path for category in ROOT.iterdir()
                  if category.is_dir() and not category.name.startswith(".") and category.name != "themes"
                  for path in category.glob(f"*/*/{pattern}"))


def scan() -> dict[tuple[str, str], list[Path]]:
    """Group every localized resource by (kind directory, language) in one filesystem walk."""
    grouped: dict[tuple[str, str], list[Path]] = {}
    for path in localized_paths("*.json"):
        for directory, kind in KINDS.items():
            if kind != "theme" and path.name.endswith(f".{kind}.json"):
                grouped.setdefault((directory, path.parent.name), []).append(path)
    return grouped


def load_baseline(baseline: Path | None) -> dict[tuple[str, str | None, str, str], dict]:
    """Index a previous build's catalog items by (directory, language, collection, path)."""
    index: dict[tuple[str, str | None, str, str], dict] = {}
    if baseline is None:
        return index
    for catalog in baseline.glob("*/*.json") if baseline.is_dir() else []:
        directory = catalog.stem
        if directory not in KINDS or directory == "themes":
            continue
        try:
            items = json.loads(catalog.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for item in items:
            index[(directory, catalog.parent.name, item.get("collection", ""), item.get("path", ""))] = item
    themes = baseline / "themes.json" if baseline else None
    if themes and themes.exists():
        try:
            for item in json.loads(themes.read_text(encoding="utf-8")):
                index[("themes", None, "", item.get("path", ""))] = item
        except ValueError:
            pass
    return index


def write_if_changed(path: Path, text: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


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


def build_catalog(directory: str, kind: str, language: str | None, featured: object, metadata: object,
                  paths: list[Path], baseline: dict, stats: dict) -> list[dict]:
    items = []
    for path in sorted(paths):
        raw = path.read_bytes()
        data = json.loads(raw)
        identifier = path.name[: -(len(kind) + 6)]
        collection = f"{path.parents[2].name}/{path.parents[1].name}" if kind != "theme" else None
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
        previous = baseline.get((directory, language, item.get("collection", ""), item["path"]))
        if previous is not None and previous.get("digest") == item["digest"]:
            # Same bytes as the published catalog: keep its pull request instead of asking Git and GitHub again.
            stats["reused"] += 1
            if previous.get("pullRequest") is not None:
                item["pullRequest"] = previous["pullRequest"]
        else:
            stats["rebuilt"] += 1
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
    baseline_dir = Path(args.baseline) if args.baseline else None
    if baseline_dir is not None and not baseline_dir.is_dir():
        baseline_dir = None
    baseline = load_baseline(baseline_dir)
    stats = {"reused": 0, "rebuilt": 0}
    written: list[Path] = []
    grouped = scan()
    languages = sorted({language for _, language in grouped})
    catalog_languages: dict[str, list[str]] = {"pages": [], "lists": []}
    for language in languages:
        for directory in ("pages", "lists"):
            paths = grouped.get((directory, language), [])
            if not paths:
                continue
            items = build_catalog(directory, KINDS[directory], language, featured, metadata, paths, baseline, stats)
            catalog = output / language / f"{directory}.json"
            if write_if_changed(catalog, json.dumps(items, ensure_ascii=False, indent=2) + "\n"):
                written.append(catalog)
            catalog_languages[directory].append(language)
    themes = build_catalog("themes", "theme", None, featured, metadata,
                           sorted((ROOT / "themes").glob("*.theme.json")), baseline, stats)
    if write_if_changed(output / "themes.json", json.dumps(themes, ensure_ascii=False, indent=2) + "\n"):
        written.append(output / "themes.json")
    registry = {"schemaVersion": 1, "repository": args.repository,
                "catalogs": catalog_languages | {"themes": ["."]}}
    if write_if_changed(output / "registry.json", json.dumps(registry, ensure_ascii=False, indent=2) + "\n"):
        written.append(output / "registry.json")
    # Stale catalogs would otherwise survive a copied baseline: a language that no longer carries
    # a given kind, or a kind dropped from KINDS entirely (e.g. a leftover sections.json).
    for catalog in sorted(output.glob("*/*.json")):
        directory = catalog.stem
        if directory not in KINDS or catalog.parent.name not in catalog_languages.get(directory, []):
            catalog.unlink()
            written.append(catalog)
    print(f"reused {stats['reused']} items, rebuilt {stats['rebuilt']}, "
          f"{len(written)} catalog file(s) changed" + (": " + ", ".join(str(p.relative_to(output)) for p in written) if written else ""))


parser = argparse.ArgumentParser()
parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "janlay/mydea-community"))
parser.add_argument("--output", default="registry-output")
parser.add_argument("--baseline", default=None,
                    help="Directory holding the previously published catalogs; unchanged items keep their pull request "
                         "instead of being looked up again. Ignored when missing.")
args = parser.parse_args()
build(args)
