# GitHub Language Stats

Get a breakdown of programming languages across all your GitHub repositories.

## Setup

1. **Install dependencies:**
   ```bash
   pip install requests matplotlib python-dotenv
   ```

2. **Create a GitHub token:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token" (classic) or "Fine-grained token"
   - For classic token, select scopes:
     - `repo` (for private repos access)
     - OR `public_repo` (for public repos only)
   - Copy the token

3. **Create `.env` file:**
   - Copy `.env.example` to `.env`
   - Replace `ghp_your_token_here` with your actual token

4. **Run the script:**
   ```bash
   python main.py
   ```

## Output

The script will:
- Print a language breakdown to the console
- Show an ASCII bar chart
- Generate `github_language_pie.png` with a pie chart visualization

## Configuration

Optional environment variables in `.env`:
- `GH_AFFILIATION`: Which repos to include (default: `owner,collaborator,organization_member`)
- `GH_VISIBILITY`: Repo visibility (default: `all`, options: `all`, `public`, `private`)
