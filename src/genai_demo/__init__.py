import importlib.metadata

# Retrieve the version from package metadata (pyproject.toml)
try:
    __version__ = importlib.metadata.version("genai-demo")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


def main() -> None:
    print("Hello from genai-demo!")
