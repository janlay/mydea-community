# Mydea Community

[English](./README.md) | [中文](./README-cn.md)

Mydea Community is the content, collaboration, and review repository for native Mydea resources.

## Contributing Resources

1. Fork this repository.
2. Upload an exported file to the matching directory: `pages/<language>/`, `sections/<language>/`, `lists/<language>/`, or `themes/`.
3. Open a Pull Request.

Keep the original JSON format exported by Mydea. Do not manually maintain the Registry, digest, PR number, or Featured metadata.

CI checks JSON syntax, file location, filenames, resource schemas, and Community List references in Pages and Sections. After a merge into `main`, the publishing workflow validates again and generates the `registry` branch.

## Downloading Resources

Consumers read `registry/registry.json`, then use `repository` and each item's `path` to download the resource from `main`. The Registry is not versioned; it always points at the latest data. Each catalog item's `digest` is a change token: compare it against the copy you already hold to decide what to re-download.

## Local Validation and Build

```sh
python3 .community/scripts/validate.py
python3 .community/scripts/build_registry.py --repository OWNER/mydea-community
```

## Example

`pages/en/cannes.page.json` uses `lists/en/cannes-2026.list.json`. The localized Registry entry point is `registry/en/registry.json`; its catalogs use simple relative names, while the shared theme catalog is `registry/themes.json`.
