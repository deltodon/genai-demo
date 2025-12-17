.PHONY: all clean-python clean-docker clean-all
all: help

.venv:
	@echo "Installing project dependencies.."
	@uv sync

jupyter:
	@echo "Running JupyterLab.."
	@if [ -f .env ]; then \
		uv run --env-file=.env jupyter lab; \
	else \
		uv run jupyter lab; \
	fi

clean-python:
	@echo "Removing Python build output.."
	@rm -rf .venv
	@rm -rf `find -type d -name __pycache__`
	@rm -rf `find -type d -name .pytest_cache`
	@rm -rf `find -type d -name .ipynb_checkpoints`

clean-docker:
	@echo "Removing Docker containers, images, and volumes.."
	@docker compose -p genai-demo_devcontainer \
					-f .devcontainer/docker-compose.yml \
					down --rmi all --volumes

clean-all: clean-python clean-docker
	@echo "All cleanup complete!"

help:
	@echo "Available make targets:"
	@echo " make help          - Print help"
	@echo " make .venv         - Print out project configurations"
	@echo " make jupyter       - Run JupyterLab"
	@echo " make clean-python  - Remove Python build output"
	@echo " make clean-docker  - Remove Docker containers, images, and volumes"
	@echo " make clean-all     - Run both clean-python and clean-docker"
	@echo ""
