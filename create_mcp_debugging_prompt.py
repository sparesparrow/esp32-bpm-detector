#!/usr/bin/env python3
"""Create mcp-debugging-prompt.json in mcp-prompts directory."""

import json
from pathlib import Path
from datetime import datetime

prompt_data = {
    "id": "mcp-debugging-prompt",
    "name": "mcp-debugging-prompt",
    "description": "Generate debugging prompts for troubleshooting and issue resolution using MCP prompts",
    "content": "# Debugging Prompt Generator\n\nSystematic debugging and troubleshooting guide for resolving issues in {{language}} code.\n\n## Issue Overview\n\n**Description**: {{issue_description}}\n**Error Message**: {{error_message}}\n**Environment**: {{environment}}\n**Language**: {{language}}\n**Urgency**: {{urgency}}\n\n## Debugging Process\n\n### 1. Problem Analysis\n\n**Issue Description**:\n{{issue_description}}\n\n**Error/Symptoms**:\n{{error_message}}\n\n**Environment Context**:\n- Environment: {{environment}}\n- Language: {{language}}\n- Urgency Level: {{urgency}}\n\n### 2. Root Cause Investigation\n\n#### Step 1: Reproduce the Issue\n- Identify steps to reproduce\n- Determine if issue is consistent or intermittent\n- Check if issue occurs in all environments or specific ones\n\n#### Step 2: Error Analysis\n- Examine the error message: `{{error_message}}`\n- Identify error type (syntax, runtime, logic, etc.)\n- Check error stack trace for clues\n- Look for patterns in error occurrence\n\n#### Step 3: Code Review\n- Review relevant code sections\n- Check recent changes that might have introduced the issue\n- Look for common bug patterns:\n  - Null/undefined references\n  - Type mismatches\n  - Off-by-one errors\n  - Race conditions\n  - Memory leaks\n  - Resource cleanup issues\n\n{{#if include_logs}}\n### 3. Log Analysis\n\n**Log Review Checklist**:\n- Review application logs around the time of the error\n- Check for related errors or warnings\n- Look for patterns in log entries\n- Identify correlation with system events\n- Check log levels and verbosity settings\n\n**Key Log Areas to Examine**:\n- Error logs\n- Application logs\n- System logs\n- Network logs (if applicable)\n- Database logs (if applicable)\n{{/if}}\n\n### 4. Diagnostic Steps\n\n#### Immediate Actions\n1. **Verify Environment**: Confirm {{environment}} environment configuration\n2. **Check Dependencies**: Verify all required packages/libraries are installed\n3. **Validate Input**: Check if input data is valid and in expected format\n4. **Resource Check**: Verify system resources (memory, disk, network)\n\n#### Code-Level Diagnostics\n1. Add debug logging at critical points\n2. Use breakpoints/debugger to step through code\n3. Check variable values at key execution points\n4. Verify function return values\n5. Validate data structures and types\n\n#### System-Level Diagnostics\n1. Check system resources and limits\n2. Verify network connectivity (if applicable)\n3. Check file permissions and access\n4. Validate configuration files\n5. Review system logs\n\n{{#if include_solutions}}\n### 5. Solution Recommendations\n\nBased on the issue analysis, consider the following solutions:\n\n#### Quick Fixes\n- Verify and fix syntax errors\n- Add null/undefined checks\n- Fix type mismatches\n- Correct logic errors\n- Add proper error handling\n\n#### Long-term Solutions\n- Improve error handling and validation\n- Add comprehensive logging\n- Implement proper resource cleanup\n- Add unit tests for edge cases\n- Improve code documentation\n- Set up monitoring and alerting\n\n#### Prevention Strategies\n- Code review processes\n- Automated testing\n- Static code analysis\n- Performance monitoring\n- Regular dependency updates\n{{/if}}\n\n## Debugging Checklist\n\n- [ ] Issue reproduced and documented\n- [ ] Error message analyzed\n- [ ] Code reviewed for obvious issues\n{{#if include_logs}}\n- [ ] Logs reviewed and analyzed\n{{/if}}\n- [ ] Root cause identified\n{{#if include_solutions}}\n- [ ] Solution implemented\n- [ ] Fix tested and verified\n- [ ] Prevention measures considered\n{{/if}}\n\n## Expected Output\n\nProvide:\n1. **Root Cause**: Clear identification of the underlying issue\n2. **Impact Assessment**: How the issue affects the system\n3. **Solution Steps**: Detailed steps to resolve the issue\n{{#if include_solutions}}\n4. **Code Fixes**: Specific code changes needed\n5. **Testing Plan**: How to verify the fix works\n6. **Prevention**: Steps to prevent similar issues\n{{/if}}\n\n## Priority Guidelines\n\n**{{urgency}} Priority**: \n- Requires immediate attention\n- May impact system stability or user experience\n- Should be resolved as soon as possible\n\nGenerate a comprehensive debugging guide that systematically identifies and resolves the issue with {{issue_description}}.\n",
    "isTemplate": True,
    "tags": [
        "debugging",
        "troubleshooting",
        "issue-resolution",
        "error-handling",
        "diagnostics"
    ],
    "category": "debugging",
    "createdAt": datetime.now().isoformat() + "Z",
    "updatedAt": datetime.now().isoformat() + "Z",
    "version": 1
}

# Path to mcp-prompts prompts directory
prompts_dir = Path("/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts")
output_file = prompts_dir / "mcp-debugging-prompt.json"

# Ensure directory exists
prompts_dir.mkdir(parents=True, exist_ok=True)

# Write the prompt file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(prompt_data, f, indent=2, ensure_ascii=False)

print(f"✅ Successfully created prompt: {output_file}")
print(f"   Name: {prompt_data['name']}")
print(f"   Description: {prompt_data['description']}")
print(f"   Tags: {', '.join(prompt_data['tags'])}")
print(f"   Category: {prompt_data['category']}")
print(f"   Is Template: {prompt_data['isTemplate']}")
