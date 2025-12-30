<a id="changelog-top"></a>

<div align="center">
  <h1>Changelog</h1>

  <h3>All notable changes to ghlang</h3>

</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#v210--themes--svg-export">v2.1.0</a></li>
    <li><a href="#v205--reliability--symlinks">v2.0.5</a></li>
    <li><a href="#v204--config-command">v2.0.4</a></li>
    <li><a href="#v203--pipeline-friendly">v2.0.3</a></li>
    <li><a href="#v202--custom-titles--output">v2.0.2</a></li>
    <li><a href="#v201--typer-swap">v2.0.1</a></li>
    <li><a href="#v200--local-mode--big-refactor">v2.0.0</a></li>
    <li><a href="#v100--initial-release">v1.0.0</a></li>
  </ol>
</details>

## v2.1.0 — Themes & SVG export

Theme support and SVG output for better customization.

**New stuff:**

- `--theme` flag to choose chart color schemes
  - Built-in themes: `light` (default), `dark`
  - Configurable via `preferences.theme` in config
- `--format` / `-f` flag for output format
  - Support for PNG (default) and SVG
  - Priority: `--format` > `--output` extension > default png
- Rounded corners on PNG charts
- Theme-aware fallback colors for languages without GitHub linguist equivalents

**Changed:**

- Pillow used for adding rounded corners to PNGs
- Refactored static data: `lang_mapping.py` now uses Python dicts instead of JSON
- All chart styling constants moved to top of `visualizers.py` for easy customization
- Language normalization: languages without linguist mapping now use original name with fallback color instead of being excluded

**Improved:**

- Cleaner constant organization for maintainability
- User-friendly warnings for invalid themes and unsupported formats

<p align="right">(<a href="#changelog-top">back to top</a>)</p>

## v2.0.5 — Reliability & symlinks

Better rate limit handling and symlink support for local mode.

**New stuff:**

- `--follow-links` flag for local mode to follow symlinks (unix only)
- Rate limit info shown in verbose mode (`Rate limit: X/Y remaining`)
- Dev dependencies for type checking (`types-requests`, `types-PyYAML`)

**Improved:**

- GitHub API rate limiting now uses exponential backoff for 429/5xx errors
- Retries up to 5 times with increasing delays before failing
- Internal code cleanup: private attributes/methods where appropriate

**Fixed:**

- Various mypy type errors resolved

<p align="right">(<a href="#changelog-top">back to top</a>)</p>

## v2.0.4 — Config command

New `ghlang config` command for managing your config file.

**New stuff:**

- `ghlang config` opens config in your default editor
- `ghlang config --show` prints config as a formatted table
- `ghlang config --path` prints the config file path
- `ghlang config --raw` prints raw TOML contents

**Changed:**

- CLI refactored into `ghlang/cli/` package for better organization

<p align="right">(<a href="#changelog-top">back to top</a>)</p>

## v2.0.3 — Pipeline friendly

New flags for scripting and CI/CD workflows.

**New stuff:**

- `--json-only` flag to skip chart generation and just output JSON
- `--stdout` flag to output stats to stdout (perfect for piping to jq)
- `--quiet` / `-q` flag to suppress log output

**Notes:**

- `--stdout` implies both `--json-only` and `--quiet`
- Great for CI pipelines, scripts, and custom visualizations

<p align="right">(<a href="#changelog-top">back to top</a>)</p>

## v2.0.2 — Custom titles & output

New CLI flags for more control over your charts.

**New stuff:**

- `--title` / `-t` flag to set a custom chart title
- `--output` / `-o` flag to specify custom output filename (creates `_pie` and `_bar` variants)
- Dynamic chart titles: GitHub mode shows "GitHub Language Stats", local mode shows "Local: {folder}"

**Changed:**

- `--output-dir` no longer has `-o` shorthand (now used by `--output`)

<p align="right">(<a href="#changelog-top">back to top</a>)</p>

## v2.0.1 — Typer swap

Swapped Click for [Typer](https://typer.tiangolo.com/). Same functionality, but now with:

- Built-in shell completion (`ghlang --install-completion`)
- Nicer help output with colors and tables

**New stuff:**

- GitHub Actions workflow for automatic releases

**Changed:**

- Dropped `click` as a direct dependency (Typer uses it internally anyway)

<p align="right">(<a href="#changelog-top">back to top</a>)</p>

## v2.0.0 — Local mode & big refactor

Big update. You can now analyze local files, not just GitHub repos.

**New stuff:**

- `ghlang local` command using [cloc](https://github.com/AlDanial/cloc)
- Ignore repos with patterns (`org/*`, full URLs)
- Ignore directories in local mode
- Default config bundled in the package

**Changed:**

- CLI now uses Click groups (`github`, `local` subcommands)
- Config system overhauled: `Config` dataclass, platform-specific paths
- Visualizers cleaned up: better legends, layout fixes
- README completely rewritten

**Fixed:**

- Console script entry point works with pipx now

<p align="right">(<a href="#changelog-top">back to top</a>)</p>

## v1.0.0 — Initial release

First version. GitHub-only.

- `GitHubClient` to fetch repos and aggregate language stats
- Pie and bar charts with GitHub's linguist colors
- Config via `config.toml`
- Filter by repo affiliation and visibility
- MIT License

<p align="right">(<a href="#changelog-top">back to top</a>)</p>

---

<div align="center">
  <p>Back to <a href="README.md">README</a>?</p>
</div>
