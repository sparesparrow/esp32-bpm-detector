#!/bin/bash
# Script to commit and push Android project setup changes

echo "Staging all changes..."
git add -A

echo "Committing changes..."
git commit -m "Configure Android project structure and APK build setup

- Move build.gradle to android-app/app/
- Create root build.gradle with project-level config
- Set up Gradle wrapper (gradlew, gradlew.bat, wrapper properties)
- Add gradle.properties with project-wide settings
- Configure debug and release build types
- Create ProGuard rules file
- Add build scripts (build-debug.sh/bat, build-release.sh/bat)
- Create missing Android resources (data_extraction_rules.xml, backup_rules.xml)
- Update .gitignore to allow build/sparetools/
- Add comprehensive documentation (README updates, setup guides)
- Create sparetools integration guides and review scripts
- Add implementation summary documentation"

echo "Pushing to remote..."
git push

echo "Done!"
