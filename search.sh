#!/usr/bin/env bash
# Search Sage's GitHub repo directory. Example: ./search.sh seo audit
exec python3 "$(dirname "$0")/search.py" "$@"
