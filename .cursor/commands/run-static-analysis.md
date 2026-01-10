Run static code analysis using the dev-intelligence-orchestrator skill with learning capabilities.

For C++ code:
- Use `analyze_cpp.sh` with focus: security|performance|memory|general
- Query mcp-prompts for learned cppcheck configurations
- Capture successful configurations for future use

For Python code:
- Use `analyze_python.sh` with focus: security|performance|style|general
- Query mcp-prompts for learned pylint configurations

Example: `.claude/skills/dev-intelligence-orchestrator/scripts/analyze_cpp.sh src/main.cpp memory .`

