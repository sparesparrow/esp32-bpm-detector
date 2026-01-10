Run tests using the dev-intelligence-orchestrator skill with framework detection.

1. Detect test framework (pytest, PlatformIO, gtest)
2. Query mcp-prompts for learned test configurations
3. Execute tests with appropriate framework
4. Generate coverage reports if requested
5. Capture successful test patterns for future use

Run: `.claude/skills/dev-intelligence-orchestrator/scripts/run_tests.sh . <test_path> <coverage>`

For Docker-based tests: Use `unified-deployment.run_docker_tests` MCP tool.

