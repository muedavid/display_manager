#!/usr/bin/env bash
# ===============================================================
# sync_to_pi.sh
# Sync local project to Raspberry Pi using rsync via "ssh feg"
# ===============================================================

# Exit immediately if a command fails
set -e

# Where to copy the project on the Pi
REMOTE_DIR="~/code"

# Optional: list of files/folders to exclude from sync
EXCLUDES=(
    ".git"
    "__pycache__"
    "venv"
    ".venv"
    "*.pyc"
    "*.pyo"
    "*.log"
)

# Build the exclude arguments for rsync
EXCLUDE_ARGS=()
for EX in "${EXCLUDES[@]}"; do
    EXCLUDE_ARGS+=("--exclude=$EX")
done

echo "Syncing project to Raspberry Pi ($REMOTE_DIR)..."
rsync -avz \
    "${EXCLUDE_ARGS[@]}" \
    ./ \
    feg:"$REMOTE_DIR"

echo "✅ Sync complete!"

# Optional: run a remote command after syncing (e.g. install/update)
# Uncomment if you want to automatically install/update the package:
# ssh feg "cd $REMOTE_DIR && pip install -e ."

