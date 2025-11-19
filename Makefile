.PHONY: all
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

clean:
	@echo "Removing .venv"
	@rm -rf .venv
	@rm -rf `find -type d -name __pycache__`
	@rm -rf `find -type d -name .pytest_cache`
	@rm -rf `find -type d -name .ipynb_checkpoints`

help:
	@echo "Available make targets:"
	@echo " make help         - Print help"
	@echo " make .venv        - Print out project configurations"
	@echo " make clean        - Remove all build output"
	@echo ""
