# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sandbox repository for GenAI examples and demonstrations. The primary focus is on documentation and presentations about DevContainers and Claude Code, hosted as a Jekyll-based GitHub Pages site.

## Development Environment

### Container-Based Development
This project uses VS Code DevContainers with Docker Compose. The environment includes:
- **Python**: 3.12 via pyenv (customizable via `.env`)
- **Node.js**: 22.20.0 via nvm (customizable via `.env`)
- **Ruby**: System Ruby with Bundler for Jekyll
- **AWS CLI v2**: Pre-installed
- **UV Package Manager**: Fast Python package installer
- **Claude Code CLI**: Pre-installed globally via npm

### Environment Configuration
1. Copy `.env.example` to `.env` and customize settings:
   - `HOST_UID` and `HOST_GID`: Match your host user (Linux only)
   - `PYTHON_VERSION` and `NODE_VERSION`: Customize language versions
   - Add GenAI API keys as needed (OpenAI, Anthropic, Google AI, Hugging Face)

2. The devcontainer mounts `~/.aws` as read-only for AWS credentials

## Common Development Commands

### Documentation (Jekyll)

The documentation site is in the `docs/` directory and uses Jekyll with the Minima theme.

**Install dependencies:**
```bash
cd docs
bundle install
```

**Serve documentation locally (port 4000):**
```bash
cd docs
bundle exec jekyll serve --host 0.0.0.0
```

**Build documentation:**
```bash
# From project root
bundle exec jekyll build --source docs --destination _site

# Or from docs directory
cd docs
bundle exec jekyll build
```

### Python Development

**Install packages with uv (recommended):**
```bash
uv pip install package-name
```

**Install packages with pip:**
```bash
pip install package-name
```

**Check Python version:**
```bash
python --version
pyenv versions
```

### Node.js Development

**Check Node version:**
```bash
node --version
nvm list
```

**Install npm packages:**
```bash
npm install package-name
```

## Project Structure

```
genai-demo/
├── .devcontainer/          # DevContainer configuration
│   ├── Dockerfile          # Custom image with Python, Node, Ruby, AWS CLI
│   ├── docker-compose.yml  # Service definitions
│   └── devcontainer.json   # VS Code settings and extensions
├── docs/                   # Jekyll documentation site
│   ├── documentation/      # Documentation pages (devcontainer, claude-code)
│   ├── presentation/       # Reveal.js slide decks
│   ├── website/           # Main site pages
│   ├── _layouts/          # Jekyll layouts
│   ├── _config.yml        # Jekyll configuration
│   └── Gemfile            # Ruby dependencies
├── .github/workflows/     # GitHub Actions
│   └── pages.yml          # Build and deploy Jekyll to GitHub Pages
└── .env.example           # Environment template
```

## Documentation Architecture

### Jekyll Site Structure
- **Automatic layout**: All files under `documentation/` automatically use the default layout
- **Permalinks**: Set to `/:path/` for clean URLs
- **Theme**: Minima (minimal Jekyll theme)
- **Navigation**: Index page at `docs/website/index.md` links to all sections

### Content Organization
- `documentation/devcontainer/`: DevContainer guides and tips
- `documentation/claude-code/`: Claude Code guides and how-tos
- `presentation/devcontainer/`: Reveal.js slides about DevContainers
- `presentation/claude-code/`: Reveal.js slides about Claude Code

## GitHub Actions

The repository uses GitHub Actions to automatically build and deploy the Jekyll site to GitHub Pages on every push to `main` branch.

**Workflow**: `.github/workflows/pages.yml`
- Builds Jekyll from `docs/` directory
- Deploys to GitHub Pages
- Can be manually triggered via `workflow_dispatch`

## Port Forwarding

The devcontainer is configured to forward:
- **Port 4000**: Jekyll documentation server
- **Port 8000**: Reserved for future API/GenAI services

## AWS Configuration

AWS credentials are mounted from `~/.aws` on the host machine (read-only). No additional AWS configuration is needed inside the container.

## Future GenAI Services

The `docker-compose.yml` includes commented examples for:
- **ChromaDB**: Vector database for embeddings
- **Redis**: Caching layer
- **PostgreSQL**: Relational database

Uncomment and customize these services as needed for GenAI projects.
