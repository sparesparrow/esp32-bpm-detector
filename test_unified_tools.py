#!/usr/bin/env python3
"""
Test script for Unified Development Tools MCP Server integration
Run this to verify the installation is working correctly.
"""

import os
import sys
import json
from pathlib import Path

def check_mcp_config():
    """Check if MCP configuration is properly set up."""
    config_path = Path(".claude/mcp.json")
    if not config_path.exists():
        print("❌ MCP configuration not found at .claude/mcp.json")
        return False

    try:
        with open(config_path) as f:
            config = json.load(f)

        if "unified-dev-tools" not in config.get("mcpServers", {}):
            print("❌ unified-dev-tools server not configured in MCP")
            return False

        print("✅ MCP configuration is properly set up")
        return True
    except Exception as e:
        print(f"❌ Error reading MCP configuration: {e}")
        return False

def check_server_installation():
    """Check if the unified development tools server is installed."""
    server_path = Path("/home/sparrow/mcp/servers/python/unified_dev_tools")

    if not server_path.exists():
        print("❌ Unified development tools server not found")
        return False

    # Check if virtual environment exists
    venv_path = server_path / ".venv"
    if not venv_path.exists():
        print("❌ Server virtual environment not found")
        return False

    # Check if server file exists
    server_file = server_path / "unified_dev_tools_mcp_server.py"
    if not server_file.exists():
        print("❌ Server implementation file not found")
        return False

    print("✅ Unified development tools server is properly installed")
    return True

def check_dependencies():
    """Check if required dependencies are available in the unified dev tools environment."""
    import subprocess
    try:
        # Check if uv can run the server (which means dependencies are installed)
        result = subprocess.run([
            "uv", "run", "--project",
            "/home/sparrow/mcp/servers/python/unified_dev_tools",
            "python", "-c", "import mcp, pydantic, asyncio; print('OK')"
        ], capture_output=True, text=True, cwd="/home/sparrow/mcp/servers/python/unified_dev_tools")

        if result.returncode == 0 and "OK" in result.stdout:
            print("✅ All Python dependencies are available in unified dev tools environment")
            return True
        else:
            print(f"❌ Dependencies check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def check_cursor_rules():
    """Check if cursor rules are available."""
    rules_path = Path("/home/sparrow/.cursor/rules/self-improving-prompts-tools.mdc")
    if rules_path.exists():
        print("✅ Cursor rules for self-improving prompts are available")
        return True
    else:
        print("⚠️  Cursor rules not found (optional)")
        return True  # Not critical

def main():
    """Run all checks."""
    print("🔧 Testing Unified Development Tools MCP Server Installation")
    print("=" * 60)

    checks = [
        check_mcp_config,
        check_server_installation,
        check_dependencies,
        check_cursor_rules
    ]

    passed = 0
    total = len(checks)

    for check in checks:
        if check():
            passed += 1
        print()

    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 Installation is complete and ready to use!")
        print()
        print("🚀 To use the unified development tools:")
        print("1. Open Cursor in this project directory")
        print("2. The unified-dev-tools MCP server will be automatically available")
        print("3. Use Claude Skills like 'embedded-audio-analyzer' for ESP32 optimization")
        print("4. Try commands like: 'Analyze ESP32 BPM detector performance'")
        print()
        print("📚 Available tools include:")
        print("  - ESP32 serial monitoring and debugging")
        print("  - Android device management and APK installation")
        print("  - Conan package creation and Cloudsmith integration")
        print("  - Repository cleanup and maintenance")
        print("  - Cross-platform deployment orchestration")
        print("  - Knowledge queries and learning capture")
    else:
        print("❌ Some checks failed. Please resolve the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()