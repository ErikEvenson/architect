#!/bin/bash
# Check that all knowledge/*.md files are listed in mkdocs.yml nav
# Run as part of CI or pre-commit to prevent missing sidebar entries

set -e

MISSING=0

# Find all .md files in knowledge/ (excluding stylesheets/javascripts)
for f in $(find knowledge -name "*.md" -not -path "*/stylesheets/*" -not -path "*/javascripts/*" | sort); do
    # Get path relative to knowledge/ (which is docs_dir)
    rel="${f#knowledge/}"
    # Check if this path appears in mkdocs.yml
    if ! grep -qF "$rel" mkdocs.yml; then
        echo "MISSING from mkdocs.yml nav: $rel"
        MISSING=$((MISSING + 1))
    fi
done

if [ "$MISSING" -gt 0 ]; then
    echo ""
    echo "ERROR: $MISSING knowledge file(s) not in mkdocs.yml sidebar."
    echo "Add them to the nav: section in mkdocs.yml."
    exit 1
else
    echo "All knowledge files are in the mkdocs.yml nav."
fi
