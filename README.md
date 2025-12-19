# ghlang - GitHub Language Stats

Get a breakdown of programming languages across all your GitHub repositories with beautiful visualizations.

## Installation

Install globally with pipx (recommended):

```bash
pipx install git+https://github.com/Mihaistreames/ghlang.git
```

Or with pip:

```bash
pip install git+https://github.com/Mihaistreames/ghlang.git
```

## Setup

### 1. Create a GitHub Token

- Go to <https://github.com/settings/tokens>
- Click "Generate new token" (classic) or "Fine-grained token"
- For classic token, select scopes:
  - `repo` (for private repos access)
  - OR `public_repo` (for public repos only)
- Copy the token

### 2. Run for the First Time

```bash
ghlang
```

This will create a config file at:

- **Linux/macOS**: `~/.config/ghlang/config.toml`
- **Windows**: `%LOCALAPPDATA%\ghlang\config.toml`

### 3. Add Your Token

Edit the config file and replace `YOUR_TOKEN_HERE` with your actual GitHub token:

```toml
[github]
token = "ghp_your_actual_token_here"
affiliation = "owner,collaborator,organization_member"
visibility = "all"  # Options: all, public, private

[output]
directory = "~/Documents/ghlang-stats"
save_json = true
save_repos = true
top_n_languages = 5

[preferences]
verbose = false
```

### 4. Run Again

```bash
ghlang
```

## Usage

Basic usage (uses config file):

```bash
ghlang
```

Override output directory:

```bash
ghlang -o ~/my-stats
```

Show more languages in bar chart:

```bash
ghlang --top-n 10
```

Enable verbose logging:

```bash
ghlang -v
```

Use custom config file:

```bash
ghlang --config ~/my-custom-config.toml
```

## Output

The tool generates:

- **language_pie.png** - Pie chart showing language distribution
- **language_bar.png** - Horizontal bar chart of top N languages
- **language_stats.json** - Raw language statistics (if `save_json = true`)
- **repositories.json** - List of repositories analyzed (if `save_repos = true`)
- **github_colors.json** - GitHub's official language colors (if `save_json = true`)

## Configuration

All options can be set in the config file:

### GitHub Settings

- `token` - Your GitHub personal access token (required)
- `affiliation` - Which repos to include (default: `owner,collaborator,organization_member`)
- `visibility` - Filter by visibility (options: `all`, `public`, `private`)

### Output Settings

- `directory` - Where to save output files
- `save_json` - Save JSON data files (default: `false`)
- `save_repos` - Save repository list (default: `false`)
- `top_n_languages` - Number of languages in bar chart (default: `5`)

### Preferences

- `verbose` - Enable detailed logging (default: `false`)

## License

MIT
