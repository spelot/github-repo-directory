#!/usr/bin/env bash
# Search the AI resources directory. Example: ./search.sh newsletter
exec python3 "$(dirname "$0")/search.py" "$@"
