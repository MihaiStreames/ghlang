<a id="changelog-top"></a>

<div align="center">
  <h1>Changelog</h1>

  <h3>All notable changes to ghlang</h3>

</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#v203--pipeline-friendly">v2.0.3</a></li>
    <li><a href="#v202--custom-titles--output">v2.0.2</a></li>
    <li><a href="#v201--typer-swap">v2.0.1</a></li>
    <li><a href="#v200--local-mode--big-refactor">v2.0.0</a></li>
    <li><a href="#v100--initial-release">v1.0.0</a></li>
  </ol>
</details>

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
