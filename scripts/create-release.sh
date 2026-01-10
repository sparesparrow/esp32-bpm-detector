#!/bin/bash
# Create release for esp32-bpm-detector
# Usage: ./scripts/create-release.sh [version] [patch|minor|major]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Get current version from conanfile.py
CURRENT_VERSION=$(grep -E '^\s*version\s*=' conanfile.py | sed "s/.*version\s*=\s*[\"']\(.*\)[\"'].*/\1/" || echo "0.1.0")
echo "Current version: $CURRENT_VERSION"

# Determine new version
if [ -n "${1:-}" ]; then
    NEW_VERSION="$1"
elif [ -n "${2:-}" ]; then
    # Parse version and bump
    IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
    MAJOR="${VERSION_PARTS[0]}"
    MINOR="${VERSION_PARTS[1]}"
    PATCH="${VERSION_PARTS[2]}"
    
    case "$2" in
        patch) PATCH=$((PATCH + 1)) ;;
        minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
        major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
        *) echo "Invalid bump type: $2"; exit 1 ;;
    esac
    
    NEW_VERSION="$MAJOR.$MINOR.$PATCH"
else
    echo "Usage: $0 [version] [patch|minor|major]"
    echo "Example: $0 0.1.1"
    echo "Example: $0 '' patch"
    exit 1
fi

echo "New version: $NEW_VERSION"

# Update conanfile.py
sed -i "s/version = \"[^\"]*\"/version = \"$NEW_VERSION\"/" conanfile.py

# Commit changes
git add conanfile.py
git commit -m "chore: Bump version to $NEW_VERSION"

# Create tag
TAG="v$NEW_VERSION"
git tag -a "$TAG" -m "Release $TAG

- Version: $NEW_VERSION
- Firmware: ESP32 BPM Detector
- Packages: Conan package available"

echo ""
echo "✅ Release prepared:"
echo "   Version: $NEW_VERSION"
echo "   Tag: $TAG"
echo ""
echo "Next steps:"
echo "  1. Review changes: git log HEAD~1..HEAD"
echo "  2. Push tag: git push origin $TAG"
echo "  3. Push commits: git push origin main"
echo ""
echo "To build and upload firmware:"
echo "  pio run --environment esp32-s3-release"
echo "  # Then use sparetools upload script to upload artifacts"