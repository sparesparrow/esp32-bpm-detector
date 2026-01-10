# Debugging Prompt Generator

Systematic debugging guide for troubleshooting and issue resolution.

## Issue Information

**Description**: Tests failing locally
**Error Message**: AssertionError: Expected 5, got 3
**Environment**: development
**Language**: Python
**Urgency**: medium

## Debugging Process

### 1. Problem Analysis

#### Issue Summary
- **What**: Tests failing locally
- **When**: When does this occur?
- **Where**: development environment
- **Impact**: medium priority

#### Error Details
```
AssertionError: Expected 5, got 3
```

### 2. Root Cause Investigation

#### Initial Checks
1. **Reproducibility**: Can the issue be consistently reproduced?
2. **Environment**: Is this environment-specific (development)?
3. **Recent Changes**: What changed before this issue appeared?
4. **Dependencies**: Are all dependencies up to date?

#### Code Analysis
- Check Python-specific patterns
- Review error stack traces
- Examine related code paths
- Check for common pitfalls in Python

### 3. Diagnostic Steps

#### Systematic Debugging Approach

**Step 1: Isolate the Problem**
- Identify the minimal reproduction case
- Determine if issue is in specific component
- Check if issue affects all users or subset

**Step 2: Gather Information**
- Collect all relevant error messages
- Document steps to reproduce
- Note environment details (development)
- Capture system state at time of issue

**Step 3: Hypothesis Formation**
- Based on error: `AssertionError: Expected 5, got 3`
- Consider Python-specific causes
- Review common issues for development environment
- Check for known bugs in dependencies

**Step 4: Verification**
- Test hypothesis with targeted debugging
- Add logging/breakpoints as needed
- Verify fix addresses root cause

### 4. Solution Recommendations

#### Immediate Actions
Based on the error and environment, consider:

1. **Quick Fixes** (if safe for development)
   - Restart services if appropriate
   - Clear caches if relevant
   - Check resource availability

2. **Code Fixes**
   - Address root cause in Python code
   - Add proper error handling
   - Improve logging for future debugging

3. **Prevention**
   - Add monitoring/alerting
   - Improve error messages
   - Add defensive programming
   - Document edge cases

#### Solution Priority
- **medium** urgency requires immediate attention
- Balance fix quality with speed
- Consider impact on development environment

#### Testing the Fix
- Verify fix resolves: `AssertionError: Expected 5, got 3`
- Test in development-like environment
- Ensure no regressions
- Monitor after deployment

### 5. Documentation

#### What to Document
- Root cause analysis
- Solution implemented
- Prevention measures
- Related issues or patterns
- Lessons learned

## Next Steps

1. **Immediate**: Address medium priority issue
2. **Short-term**: Implement fix and verify
3. **Long-term**: Prevent recurrence

## Debugging Checklist

- [ ] Issue clearly described
- [ ] Error message captured
- [ ] Environment identified (development)
- [ ] Reproduction steps documented
- [ ] Root cause identified
- [ ] Solution implemented and tested
- [ ] Issue resolved and documented

Use this systematic approach to resolve: **Tests failing locally**
