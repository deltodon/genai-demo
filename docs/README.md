# Documentation & Presentations

This directory contains the Jekyll-based documentation site and Reveal.js slide presentations for the genai-demo project.

## Quick Start

### Prerequisites
- Ruby with Bundler installed (included in the devcontainer)
- Jekyll and dependencies (install with `bundle install`)

### Local Development

#### Using Make (Recommended)

The easiest way to work with the documentation site is using the provided Makefile:

```bash
cd docs

# Install dependencies (first time only)
make install

# Start development server with live reload
make serve

# Build the static site
make build

# Remove all build artifacts and dependencies
make clean

# See all available commands
make help
```

The site will be available at **http://localhost:4000**

#### Using Bundle Directly

Alternatively, you can use bundle commands directly:

**Install dependencies (first time only):**

```bash
cd docs
bundle config set --local path 'vendor/bundle'
bundle install
```

> **Note**: The `bundle config` command configures bundler to install gems locally in the `vendor/bundle` directory instead of system-wide. This avoids permission issues and keeps gems isolated to this project.

**Serve locally with live reload:**
```bash
cd docs
bundle exec jekyll serve --host 0.0.0.0
```

**Build without serving:**
```bash
# From project root
bundle exec jekyll build --source docs --destination _site

# Or from docs directory
cd docs
bundle exec jekyll build
```

## Site Structure

```
docs/
├── documentation/      # Documentation pages
│   ├── claude-code/   # Claude Code guides
│   └── devcontainer/  # DevContainer guides
├── presentations/     # Reveal.js slide decks
│   ├── claude-code/   # Claude Code slides
│   └── devcontainer/  # DevContainer slides
├── website/           # Main site pages
│   └── index.md       # Homepage
├── _layouts/          # Jekyll layouts
├── _config.yml        # Jekyll configuration
├── Gemfile            # Ruby dependencies
└── README.md          # This file
```

## Viewing Presentations

The Reveal.js presentations use CDN-hosted libraries (no npm install required) and are integrated into the Jekyll site.

**Start Jekyll server first:**
```bash
cd docs
bundle exec jekyll serve --host 0.0.0.0
```

**Then access presentations at:**
- DevContainer slides: http://localhost:4000/presentations/devcontainer/
- Claude Code slides: http://localhost:4000/presentations/claude-code/

## Editing Presentations

Each presentation directory contains:
- `index.html` - Loads Reveal.js from CDN and configures the presentation
- `slides.md` - Markdown content for the slides

**Slide Separators:**
- `---` - Creates a new horizontal slide
- `|||` - Creates a new vertical slide (sub-slide)
- `Note:` - Adds speaker notes

**Workflow:**
1. Start Jekyll server with `bundle exec jekyll serve --host 0.0.0.0`
2. Edit the `slides.md` file in your presentation directory
3. Refresh your browser - Jekyll automatically rebuilds the site

**Example slide structure:**
```markdown
# First Slide
Note: These are speaker notes.

---

## Second Slide
- Bullet point 1
- Bullet point 2

|||

### Sub-slide
Additional content below the second slide

---

## Third Slide
Content here
```

## Jekyll Configuration

- **Theme**: Minima
- **Permalinks**: `/:path/` (clean URLs)
- **Auto-layout**: All files under `documentation/` automatically use the default layout
- **Source**: `docs/` directory
- **Port**: 4000 (forwarded in devcontainer)

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions (`.github/workflows/pages.yml`) when changes are pushed to the `main` branch.

## Tips

- Jekyll has live reload enabled - changes to markdown files will automatically rebuild and refresh
- To see detailed build output, use `--verbose` flag: `bundle exec jekyll serve --verbose`
- To clear cached files, use: `bundle exec jekyll clean`
- The devcontainer forwards port 4000, so the site is accessible from your host machine at http://localhost:4000
