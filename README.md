<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
<div align="center">

![Stars](https://img.shields.io/github/stars/MihaiStreames/ghlang)
![License](https://img.shields.io/github/license/MihaiStreames/ghlang?label=License)
![Issues](https://img.shields.io/github/issues/MihaiStreames/ghlang?label=Issues)

</div>

<!-- PROJECT LOGO -->
<div align="center">
  <h1>ghlang</h1>

  <h3 align="center">See what languages you've been coding in</h3>

  <p align="center">
    Generate pretty charts from your GitHub repos or local files
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#shell-completion">Shell Completion</a></li>
    <li><a href="#configuration">Configuration</a></li>
    <li><a href="#output">Output</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

Ever wondered what languages you actually use? **ghlang** makes pretty charts to show you:

- **GitHub mode**: Pulls stats from all your repos via the API (counts bytes)
- **Local mode**: Analyzes files on your machine using [cloc](https://github.com/AlDanial/cloc) (counts lines)

### Example Output

<div align="center">
  <img src="assets/example_pie.png" alt="Language Distribution Pie Chart" width="60%">
  <img src="assets/example_bar.png" alt="Top Languages Bar Chart" width="60%">
  <p><em>My personal language statistics</em></p>
</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [Python](https://www.python.org/)
- [Typer](https://typer.tiangolo.com/)
- [Matplotlib](https://matplotlib.org/)
- [Requests](https://requests.readthedocs.io/)
- [Loguru](https://github.com/Delgan/loguru)
- [cloc](https://github.com/AlDanial/cloc) (for local analysis)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Getting this running is pretty straightforward.

### What You'll Need

- Python 3.10+
- For GitHub mode: a GitHub token
- For local mode: [cloc](https://github.com/AlDanial/cloc)

### Installation

```bash
# with pipx (recommended)
pipx install git+https://github.com/MihaiStreames/ghlang.git

# or with pip
pip install git+https://github.com/MihaiStreames/ghlang.git
```

For local mode, you'll also need cloc:

```bash
# Arch
pacman -S cloc

# Ubuntu/Debian
apt install cloc

# macOS
brew install cloc

# Windows
choco install cloc
```

### Setting Up GitHub Mode

1. **Get a token** from [GitHub Settings](https://github.com/settings/tokens)
   - Pick `repo` for private repos, or just `public_repo` for public only

2. **Run it once** to create the config file:

   ```bash
   ghlang github
   ```

   Config lives at `~/.config/ghlang/config.toml` (or `%LOCALAPPDATA%\ghlang\config.toml` on Windows)

3. **Add your token** to the config:

   ```toml
   [github]
   token = "ghp_your_token_here"
   ```

4. **Run it again** and you're good:

   ```bash
   ghlang github
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

### GitHub Mode

```bash
# analyze all your repos
ghlang github
```

### Local Mode

```bash
# analyze current directory
ghlang local

# analyze a specific path
ghlang local ~/projects/my-app
```

### Config Management

```bash
# open config in your editor
ghlang config

# show config as formatted table
ghlang config --show

# print config file path
ghlang config --path

# print raw TOML contents
ghlang config --raw
```

### Other Options

```bash
# more logging
ghlang github -v

# save charts somewhere else
ghlang github -o ~/my-stats

# show top 10 languages instead of 5
ghlang local --top-n 10

# pipe to jq
ghlang local ~/project --stdout | jq '.Python'

# get the top language
ghlang github --stdout | jq -r 'to_entries | sort_by(-.value) | .[0].key'
```

### All the Flags

Both `github` and `local` commands share the same options:

| Flag | Short | What it does |
|------|-------|--------------|
| `--config` | | use a different config file |
| `--output-dir` | | where to save the charts (directory) |
| `--output` | `-o` | custom output filename (creates `_pie` and `_bar` variants) |
| `--title` | `-t` | custom chart title |
| `--top-n` | | how many languages in the bar chart |
| `--json-only` | | output JSON only, skip chart generation |
| `--stdout` | | output stats to stdout (implies `--json-only --quiet`) |
| `--quiet` | `-q` | suppress log output (only show errors) |
| `--verbose` | `-v` | show more details |

The `local` command also takes an optional `[PATH]` argument (defaults to `.`).

The `config` command has its own options:

| Flag | What it does |
|------|--------------|
| `--show` | print config as formatted table |
| `--path` | print config file path |
| `--raw` | print raw TOML contents |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- SHELL COMPLETION -->
## Shell Completion

ghlang has built-in shell completion. To enable it:

```bash
# install completion for your shell
ghlang --install-completion

# or just view the completion script
ghlang --show-completion
```

After installing, restart your shell or source your config file.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- OUTPUT -->
## What You Get

Charts end up in your output directory:

| File | What it is |
|------|------------|
| `language_pie.png` | pie chart with all languages |
| `language_bar.png` | bar chart with top N languages |
| `language_stats.json` | raw stats (if `save_json` is on) |
| `cloc_stats.json` | detailed cloc output (local mode) |
| `repositories.json` | list of repos analyzed (GitHub mode) |
| `github_colors.json` | language colors from GitHub |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONFIGURATION -->
## Config Options

Everything lives in `config.toml`:

### `[github]`

| Option | Default | What it does |
|--------|---------|--------------|
| `token` | - | your GitHub token |
| `affiliation` | `"owner,collaborator,organization_member"` | which repos to include |
| `visibility` | `"all"` | `all`, `public`, or `private` |
| `ignored_repos` | `[]` | repos to skip (e.g. `"org/*"`, `"https://github.com/user/repo"`) |

### `[cloc]`

| Option | Default | What it does |
|--------|---------|--------------|
| `ignored_dirs` | `["node_modules", "vendor", ...]` | directories to skip |

### `[output]`

| Option | Default | What it does |
|--------|---------|--------------|
| `directory` | `"~/Documents/ghlang-stats"` | where to save charts |
| `save_json` | `false` | save raw stats as JSON |
| `save_repos` | `false` | save repo list as JSON |
| `top_n_languages` | `5` | how many in the bar chart |

### `[preferences]`

| Option | Default | What it does |
|--------|---------|--------------|
| `verbose` | `false` | more logging |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

MIT. Do whatever you want with it. See [LICENSE](LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<div align="center">
  <p>Made with ❤️</p>
</div>
