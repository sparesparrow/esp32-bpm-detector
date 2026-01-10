#!/usr/bin/env python3
"""
Create the mcp-debugging-prompt in mcp-prompts system.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_prompts_integration import create_prompt_mcp, get_prompt_mcp

# Define the debugging prompt template
prompt_content = """# Debugging Prompt Generator

Systematic debugging guide for troubleshooting and issue resolution.

## Issue Information

**Description**: {{issue_description}}
**Error Message**: {{error_message}}
**Environment**: {{environment}}
**Language**: {{language}}
**Urgency**: {{urgency}}

## Debugging Process

### 1. Problem Analysis

#### Issue Summary
- **What**: {{issue_description}}
- **When**: When does this occur?
- **Where**: {{environment}} environment
- **Impact**: {{urgency}} priority

#### Error Details
```
{{error_message}}
```

### 2. Root Cause Investigation

#### Initial Checks
1. **Reproducibility**: Can the issue be consistently reproduced?
2. **Environment**: Is this environment-specific ({{environment}})?
3. **Recent Changes**: What changed before this issue appeared?
4. **Dependencies**: Are all dependencies up to date?

#### Code Analysis
- Check {{language}}}-specific patterns
- Review error stack traces
- Examine related code paths
- Check for common pitfalls in {{language}}

{{#if include_logs}}
### 3. Log Analysis

#### Log Review Checklist
- [ ] Error logs from application
- [ ] System logs (if applicable)
- [ ] Network logs (if applicable)
- [ ] Database logs (if applicable)
- [ ] Performance metrics

#### Key Log Patterns to Look For
- Error patterns matching: `{{error_message}}`
- Timing issues
- Resource exhaustion
- Connection failures
- Authentication/authorization issues

#### Log Analysis Steps
1. Filter logs by timestamp around issue occurrence
2. Search for error patterns
3. Identify correlation with other events
4. Check for patterns across multiple occurrences
{{/if}}

### 4. Diagnostic Steps

#### Systematic Debugging Approach

**Step 1: Isolate the Problem**
- Identify the minimal reproduction case
- Determine if issue is in specific component
- Check if issue affects all users or subset

**Step 2: Gather Information**
- Collect all relevant error messages
- Document steps to reproduce
- Note environment details ({{environment}})
- Capture system state at time of issue

**Step 3: Hypothesis Formation**
- Based on error: `{{error_message}}`
- Consider {{language}}-specific causes
- Review common issues for {{environment}} environment
- Check for known bugs in dependencies

**Step 4: Verification**
- Test hypothesis with targeted debugging
- Add logging/breakpoints as needed
- Verify fix addresses root cause

{{#if include_solutions}}
### 5. Solution Recommendations

#### Immediate Actions
Based on the error and environment, consider:

1. **Quick Fixes** (if safe for {{environment}})
   - Restart services if appropriate
   - Clear caches if relevant
   - Check resource availability

2. **Code Fixes**
   - Address root cause in {{language}} code
   - Add proper error handling
   - Improve logging for future debugging

3. **Prevention**
   - Add monitoring/alerting
   - Improve error messages
   - Add defensive programming
   - Document edge cases

#### Solution Priority
- **{{urgency}}** urgency requires immediate attention
- Balance fix quality with speed
- Consider impact on {{environment}} environment

#### Testing the Fix
- Verify fix resolves: `{{error_message}}`
- Test in {{environment}}}-like environment
- Ensure no regressions
- Monitor after deployment
{{/if}}

### 6. Documentation

#### What to Document
- Root cause analysis
- Solution implemented
- Prevention measures
- Related issues or patterns
- Lessons learned

## Next Steps

1. **Immediate**: Address {{urgency}} priority issue
2. **Short-term**: Implement fix and verify
3. **Long-term**: Prevent recurrence

## Debugging Checklist

- [ ] Issue clearly described
- [ ] Error message captured
- [ ] Environment identified ({{environment}})
- [ ] Reproduction steps documented
{{#if include_logs}}
- [ ] Logs reviewed and analyzed
{{/if}}
- [ ] Root cause identified
{{#if include_solutions}}
- [ ] Solution implemented and tested
{{/if}}
- [ ] Issue resolved and documented

Use this systematic approach to resolve: **{{issue_description}}**
"""

def main():
    """Create the mcp-debugging-prompt."""
    print("Creating mcp-debugging-prompt in mcp-prompts system...")
    
    try:
        success = create_prompt_mcp(
            name="mcp-debugging-prompt",
            description="Generate debugging prompts for troubleshooting and issue resolution using MCP prompts",
            content=prompt_content,
            tags=["debugging", "troubleshooting", "issue-resolution", "error-handling", "diagnostics"],
            category="debugging",
            is_template=True
        )
        
        if success:
            print("✅ Successfully created mcp-debugging-prompt")
            
            # Test retrieval with template variables
            print("\nTesting template substitution...")
            
            test_args = {
                "issue_description": "API returning 500 errors",
                "error_message": "Internal Server Error: Database connection failed",
                "environment": "production",
                "language": "Python",
                "urgency": "critical",
                "include_logs": "true",
                "include_solutions": "true"
            }
            
            prompt = get_prompt_mcp("mcp-debugging-prompt", arguments=test_args)
            
            if prompt:
                print("✅ Prompt retrieved successfully")
                
                # Check if template variables were substituted
                if "{{" in prompt:
                    print("⚠️  Warning: Some template variables may not have been substituted")
                    import re
                    remaining = re.findall(r'\{\{[^}]+\}\}', prompt)
                    print(f"   Remaining: {remaining}")
                else:
                    print("✅ All template variables substituted")
                
                # Check if values are present
                if "API returning 500 errors" in prompt and "Database connection failed" in prompt:
                    print("✅ Template values found in output")
                else:
                    print("⚠️  Template values may not be in output")
                
                print(f"\nPrompt preview (first 500 chars):\n{prompt[:500]}...")
            else:
                print("⚠️  Failed to retrieve prompt (may be MCP connection issue)")
                print("   Prompt was created, but retrieval test failed")
                print("   This is okay - the prompt exists in the system")
        else:
            print("❌ Failed to create mcp-debugging-prompt")
            print("   This may be due to MCP connection issues")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nThis may be due to MCP connection issues.")
        print("The prompt creation script will work once MCP connection is restored.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
