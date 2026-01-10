Analyze the build errors using the dev-intelligence-orchestrator skill. 

1. Use `parse_build_errors.py` to intelligently parse and diagnose compilation/linking errors
2. Query mcp-prompts for learned error patterns and solutions
3. Provide specific fixes with explanations
4. Capture successful solutions for future reference

Run: `.claude/skills/dev-intelligence-orchestrator/scripts/parse_build_errors.py <log_file> esp32 platformio`

