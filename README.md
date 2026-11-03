# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

Use Node.js 20 or a supported release from Node.js 22 onward, and Yarn 1.22.22.

```bash
yarn
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

As of 2026-11-03, two advisories remain for review:

- [deepmerge GHSA-gcqx-w48m-w2h4](https://github.com/advisories/GHSA-gcqx-w48m-w2h4):
  the latest release, 4.3.1, has no published fix. It is used by the SVG build plugin.
- [minimatch GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249):
  the advisory marks versions below 11.0.1 as affected. `serve-handler` still
  requires the callable API from 3.1.5; overriding it with version 11 would break
  that API. This alert is not suppressed. The upgrade to 3.1.5 fixes the three
  older ReDoS advisories but does not clear this newer version-range alert.

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
