# agent-skills

set shell := ["bash", "-cu"]

# Show available commands
default:
    @just --list

# Generate plugins/ and marketplace.json from skills/
generate:
    python3 scripts/generate_plugins.py

# Validate skill structure
validate:
    python3 scripts/validate.py

# Run pre-commit on all files
check:
    pre-commit run --all-files

# Bump patch version for changed skills
version-bump:
    python3 scripts/version_bump.py

# Run tests
test:
    python3 -m unittest tests/test_scripts.py -v
