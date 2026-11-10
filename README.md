# rCore Study Blog

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

Rebuilt from the official `create-docusaurus@3.10.2` classic TypeScript
template. Articles, source assets, custom components, syntax definitions, tools,
and deployment routes are retained. JavaScript direct dependencies are pinned to
the stable releases checked on 2026-11-10; Python dependencies are unchanged.

## Installation

Use Node.js 20 or a supported release from Node.js 22 onward, and Yarn 1.22.22.

```bash
yarn install --frozen-lockfile
```

## Dependency security checks

```bash
yarn test:security-dependencies
yarn typecheck
yarn build
yarn audit
```

The `tinypool`, `serialize-javascript`, and `sockjs/uuid` resolutions select
patched releases while the upstream packages still request older major versions.
The regression checks cover the APIs used by Docusaurus, Terser, and SockJS. Keep
these checks when updating or removing the resolutions.

The existing resolutions are unchanged. `patches/gray-matter+4.0.3.patch` is
retained and applied with `patch-package --error-on-fail` when that package is
installed. Docusaurus 3.10 uses `@11ty/gray-matter`, which already has the YAML
API fix; postinstall verifies its YAML round trip and rejection of JavaScript
tags instead. Unexpected additional patches fail explicitly.

On 2026-11-10, Yarn 1.22.22 audited both the original and rebuilt lockfiles:

| Lockfile           | Independent advisories | Affected package entries | Critical / high / moderate / low |
| ------------------ | ---------------------- | ------------------------ | -------------------------------- |
| Original `cd4c950` | 1                      | 1 (`deepmerge@4.3.1`)    | 0 / 0 / 0 / 1                    |
| Rebuilt            | 1                      | 1 (`deepmerge@4.3.1`)    | 0 / 0 / 0 / 1                    |

No new advisory was introduced. One advisory remains for review:

- [deepmerge GHSA-gcqx-w48m-w2h4](https://github.com/advisories/GHSA-gcqx-w48m-w2h4):
  the latest release, 4.3.1, has no published fix. It is used by the SVG build plugin.

[minimatch GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249)
was updated on 2026-11-04 to cover `>=7.0.0 <11.0.1`. The callable minimatch
3.1.5 used by `serve-handler` is outside that range. The previous statement
that all versions below 11.0.1 were affected is obsolete. No alert is suppressed.

## Local Development

```bash
yarn start
```

This command starts a local development server without opening a browser window.
Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build

# Vercel root route, using Webpack instead of Rspack
VERCEL=1 yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

The default build uses Rspack and the GitHub Pages `/rcore/` base path. Vercel
uses `/`. Both retain the existing link and image checks. The nine existing
broken-anchor warnings in the two RISC-V blog posts remain visible.

## Project tools

The original `scripts/`, `pyproject.toml`, and `uv.lock` are retained, including
the locked Pillow 13.0.0 security update. Use the existing `yarn setup-python`
and image, diagram, ANSI, and Markdown table commands as needed. The migration
does not upgrade or recreate the Python environment.

## Deployment

Pushing `main` triggers `.github/workflows/deploy.yml` to build and deploy
GitHub Pages. Validate the frozen install, security tests, types, and both builds
before pushing. The commands below are the existing manual deployment options.

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
