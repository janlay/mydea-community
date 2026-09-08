# Mydea Community

[English](./README.md) | [中文](./README-cn.md)

Mydea Community is the content, collaboration, and review repository for native Mydea resources.

## Contributing Resources

1. Fork this repository.
2. Upload exported files to the matching collection directory: `<category>/<collection>/<language>/` (Pages, Sections, and Lists) or `themes/`.
3. Open a Pull Request.

Keep the original JSON format exported by Mydea. Do not manually maintain the Registry, digest, PR number, or Featured metadata.

Read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a pull request: it carries the contributor terms, including how authorship is determined and what rights you keep.

CI checks JSON syntax, file location, filenames, resource schemas, and Community List references in Pages and Sections. After a merge into `main`, the publishing workflow validates again and generates the `registry` branch.

## Downloading Resources

Consumers read `registry/registry.json`, then use `repository` and each item's `path` to download the resource from `main`. The Registry is not versioned; it always points at the latest data. Each catalog item's `digest` is a change token: compare it against the copy you already hold to decide what to re-download.

## Local Validation and Build

```sh
python3 .community/scripts/validate.py
python3 .community/scripts/build_registry.py --repository janlay/mydea-community
```

## Example

`awards/cannes/en/cannes-10-years.page.json` uses the same-directory `cannes-2026.list.json`. The Registry entry point is the root `registry.json`; its `catalogs.pages` (and `sections`/`lists`) list every language directory holding a catalog, e.g. `en/pages.json`, while `catalogs.themes` is always `["."]` for the root-level `themes.json`. Catalog item `path` values already carry their own `<language>/<filename>` form.

## License

Code — the scripts under `.community/scripts/` and the workflows under `.github/` — is under the [MIT License](./LICENSE).

Community resources — every Page, Section, List, and Theme document, together with the `.localized.json` files — are under [CC BY-NC-SA 4.0](./LICENSE-CONTENT): credit the source, no commercial use, and share adaptations under the same license. Credit the original contributor along with this repository.

Contributors keep their copyright and keep unrestricted rights to the material they themselves contributed; see [CONTRIBUTING.md](./CONTRIBUTING.md).
