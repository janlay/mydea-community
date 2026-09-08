# Contributing to Mydea Community

## What Goes Where

Upload resources exported by Mydea into the matching directory: `<category>/<collection>/<language>/` for Pages and Lists, or `themes/` for shared Themes. Section is not a resource kind of its own — export it as part of the Page that uses it; standalone `.section.json` files are rejected. Keep the original JSON format; do not edit Registry, digest, pull request, or Featured metadata by hand. CI validates every pull request.

## Licensing

This repository holds two kinds of material under two different licenses.

- **Code** — the scripts under `.community/scripts/` and the workflows under `.github/` — is under the MIT License; see [LICENSE](./LICENSE).
- **Community resources** — every Page, List, and Theme document, together with the collection and category `.localized.json` files — is under [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/) (CC BY-NC-SA 4.0); the full text is in [LICENSE-CONTENT](./LICENSE-CONTENT).

CC BY-NC-SA 4.0 means anyone may copy, redistribute, and adapt the resources, provided they credit the source, do not use the material commercially, and release any adapted material under the same license.

Award results, film titles, and person names are facts, and facts are not protected by copyright in most jurisdictions. What the license covers is the selection, arrangement, translation, and descriptive text that make up a resource document, and the collection as a whole.

## Contributor Terms

By opening a pull request you confirm that you have the right to contribute the material, and you agree to the following.

1. **You keep your copyright.** Contributing grants licenses; it transfers nothing. You remain the copyright holder of the material you contribute.

2. **You grant the public a license.** A resource contribution is published under CC BY-NC-SA 4.0; a code contribution is published under the MIT License.

3. **You grant the maintainers a broader license.** You grant the project maintainers a perpetual, worldwide, irrevocable, royalty-free license to use, reproduce, modify, publish, distribute, and sublicense your contribution, including commercially and including within the Mydea application, without the NonCommercial and ShareAlike restrictions.

4. **You keep unrestricted rights to your own contribution.** Nothing in this repository's licenses restricts you in any way with respect to material you yourself contributed. You may use, modify, relicense, and publish it elsewhere, commercially or otherwise, on any terms you choose. The NonCommercial and ShareAlike terms bind those who receive the material through this repository, never you as its author.

   This reservation covers the material you actually contributed, as recorded in this repository's Git history — not every file that happens to carry your name. Where several people have contributed to one file, each keeps unrestricted rights to their own part, and the file as a whole remains available to everyone under CC BY-NC-SA 4.0.

## Attribution and the `author` Field

A resource's `author` field is free-form display text. It is what a credit line shows, and it is not verified by CI.

Authorship for the purposes of the terms above is determined by this repository's Git history — the GitHub account that opened the pull request — not by the `author` field. Set `author` to your own name or handle, or to the project or organization you contribute on behalf of, so the display credit matches who stands behind the resource. Do not set it to someone else's name, and do not set it to the name of a tool that generated the content; if a tool helped you produce a resource, you are still the contributor and you are responsible for the result.

The resources seeded by the maintainers carry `"author": "Mydea"`, since the project itself publishes them.

## Attributing This Repository

When redistributing a resource, credit the original contributor together with this repository, and link back to it. For example:

> Cannes Film Festival 2026 — by <contributor>, from Mydea Community (https://github.com/janlay/mydea-community), licensed under CC BY-NC-SA 4.0.
