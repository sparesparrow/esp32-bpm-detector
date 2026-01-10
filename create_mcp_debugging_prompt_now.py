#!/usr/bin/env python3
"""
Create the mcp-debugging-prompt in mcp-prompts system.
This script creates the prompt file directly in the mcp-prompts directory.
"""

import json
from pathlib import Path

# Prompt data as specified by user
prompt_data = {
    "name": "mcp-debugging-prompt",
    "description": "Generate debugging prompts for troubleshooting and issue resolution using MCP prompts",
    "content": "# Debugging Prompt Generator\n\nGenerate systematic debugging guidance for troubleshooting and issue resolution.\n\n## Issue Information\n\n**Issue Description**: {{issue_description}}\n**Error Message**: {{error_message}}\n**Environment**: {{environment}}\n**Language**: {{language}}\n**Urgency**: {{urgency}}\n\n## Debugging Process\n\n### 1. Problem Analysis\n\nAnalyze the issue systematically:\n\n- **Symptom Identification**: What exactly is happening?\n- **Error Context**: When and where does the error occur?\n- **Reproducibility**: Can the issue be consistently reproduced?\n- **Impact Assessment**: How does this affect the system/users?\n\n### 2. Root Cause Investigation\n\nInvestigate potential causes:\n\n- **Code Analysis**: Review relevant code sections\n- **Dependency Check**: Verify dependencies and versions\n- **Configuration Review**: Check environment-specific settings\n- **Data Validation**: Verify input data and state\n- **Timing Issues**: Check for race conditions or timing problems\n- **Resource Constraints**: Memory, CPU, disk, network issues\n\n{{#if include_logs}}\n### 3. Log Analysis\n\nAnalyze logs and error traces:\n\n- **Error Stack Traces**: Identify the exact failure point\n- **Application Logs**: Review relevant log entries\n- **System Logs**: Check OS/system-level logs\n- **Performance Metrics**: CPU, memory, I/O patterns\n- **Timeline Analysis**: When did the issue start?\n- **Pattern Recognition**: Similar issues in the past?\n{{/if}}\n\n### 4. Diagnostic Steps\n\nProvide step-by-step diagnostic approach:\n\n1. **Reproduce the Issue**: Steps to consistently reproduce\n2. **Isolate the Problem**: Narrow down the scope\n3. **Gather Information**: Collect relevant data and logs\n4. **Hypothesis Formation**: Develop theories about root cause\n5. **Test Hypotheses**: Verify or refute each theory\n6. **Identify Root Cause**: Confirm the actual cause\n\n{{#if include_solutions}}\n### 5. Solution Recommendations\n\nProvide actionable solutions:\n\n- **Immediate Fixes**: Quick workarounds or temporary solutions\n- **Permanent Solutions**: Long-term fixes addressing root cause\n- **Prevention Strategies**: How to prevent similar issues\n- **Code Changes**: Specific code modifications needed\n- **Configuration Updates**: Environment or config changes\n- **Testing Requirements**: How to verify the fix works\n\n### 6. Verification Steps\n\nHow to confirm the issue is resolved:\n\n- **Test Cases**: Specific tests to run\n- **Validation Criteria**: What indicates success?\n- **Monitoring**: What to watch for after fix\n- **Regression Testing**: Ensure no new issues introduced\n{{/if}}\n\n## Debugging Tools and Techniques\n\nFor {{language}} in {{environment}}:\n\n- **Debuggers**: Recommended debugging tools\n- **Profiling**: Performance analysis tools\n- **Logging**: Enhanced logging strategies\n- **Monitoring**: Real-time monitoring approaches\n- **Testing**: Test-driven debugging methods\n\n## Priority Guidelines\n\n**Urgency Level**: {{urgency}}\n\n- **Critical**: Immediate attention required, system down\n- **High**: Significant impact, needs prompt resolution\n- **Medium**: Moderate impact, plan resolution\n- **Low**: Minor issue, schedule for next iteration\n\n## Output Format\n\nProvide:\n1. **Problem Summary**: Clear description of the issue\n2. **Root Cause Analysis**: Detailed investigation findings\n3. **Diagnostic Steps**: Step-by-step debugging process\n{{#if include_logs}}\n4. **Log Analysis**: Key findings from log review\n{{/if}}\n{{#if include_solutions}}\n5. **Solutions**: Recommended fixes with code examples\n6. **Verification**: How to confirm the fix\n{{/if}}\n7. **Prevention**: How to avoid similar issues in future\n\nGenerate comprehensive debugging guidance that helps systematically identify and resolve the issue.\n",
    "arguments": [
        {
            "name": "issue_description",
            "description": "Description of the issue or problem",
            "required": True
        },
        {
            "name": "error_message",
            "description": "Error message or exception details",
            "required": False
        },
        {
            "name": "environment",
            "description": "Environment where the issue occurs (e.g., ESP32, Android, Linux)",
            "required": False
        },
        {
            "name": "language",
            "description": "Programming language (e.g., C++, Python, Kotlin)",
            "required": False
        },
        {
            "name": "urgency",
            "description": "Urgency level (Critical, High, Medium, Low)",
            "required": False
        },
        {
            "name": "include_logs",
            "description": "Whether to include log analysis section",
            "required": False,
            "type": "boolean"
        },
        {
            "name": "include_solutions",
            "description": "Whether to include solution recommendations",
            "required": False,
            "type": "boolean"
        }
    ],
    "tags": [
        "debugging",
        "troubleshooting",
        "issue-resolution",
        "error-handling",
        "diagnostics"
    ],
    "isTemplate": True,
    "metadata": {
        "layer": 4,
        "domain": 1,
        "abstractionLevel": 2
    }
}

# Target directory
target_dir = Path("/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/cognitive/procedural")
target_file = target_dir / "mcp-debugging-prompt.json"

# Create directory if it doesn't exist
target_dir.mkdir(parents=True, exist_ok=True)

# Write the prompt file
with open(target_file, 'w') as f:
    json.dump(prompt_data, f, indent=2)

print(f"✓ Created prompt file: {target_file}")
print(f"  Name: {prompt_data['name']}")
print(f"  Description: {prompt_data['description']}")
print(f"  Tags: {', '.join(prompt_data['tags'])}")
print(f"  Is Template: {prompt_data['isTemplate']}")
print(f"  Arguments: {len(prompt_data['arguments'])} template variables defined")
