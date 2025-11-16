all: help


install:
	@echo "Configuring bundler for local gem installation.."
	@bundle config set --local path 'vendor/bundle'
	@echo "Installing Ruby gem dependencies.."
	@bundle install

serve:
	@echo "Starting Jekyll development server with live reload (with baseurl).."
	@bundle exec jekyll serve --host 0.0.0.0 --baseurl "/genai-demo"

build:
	@echo "Building Jekyll site.."
	@bundle exec jekyll build

clean:
	@echo "Removing build artifacts and dependencies.."
	@rm -rf vendor/bundle
	@rm -rf .bundle
	@rm -rf _site
	@rm -rf .sass-cache
	@rm -rf .jekyll-cache
	@rm -rf .jekyll-metadata
	@echo "Clean complete"

help:
	@echo "Available make targets:"
	@echo "  make help         - Print this help message"
	@echo "  make install      - Configure bundler and install gem dependencies"
	@echo "  make serve        - Start Jekyll development server (http://localhost:4000/genai-demo)"
	@echo "  make build        - Build the static site"
	@echo "  make clean        - Remove all build artifacts and dependencies"
	@echo ""
