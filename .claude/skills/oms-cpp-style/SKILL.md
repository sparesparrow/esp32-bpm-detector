---
name: oms-cpp-style
description: "C++ coding standards and best practices analyzer for OMS projects. Use when writing C++ code, creating flatbuffers schemas, adding unit tests, reviewing code, or refactoring to match OMS conventions. Analyzes actual OMS code in ~/projects/oms/ to extract and document naming conventions, code style, testing patterns, flatbuffers usage, smart pointers, RAII, polymorphism, and other design patterns. Applies learned patterns to new code in any project (e.g., esp32-bpm-detector). Self-improving: updates documentation as new patterns are discovered."
---

# OMS C++ Style

## Overview

This skill learns and applies C++ coding conventions from the OMS projects located in `~/projects/oms/`. It analyzes existing code to extract patterns, documents them in reference files, and applies those patterns when writing new code in any project.

## Workflow

### 1. First-Time Use: Learning Phase

When using this skill for the first time, or when significant OMS code changes are detected:

1. **Analyze OMS Projects**: Examine C++ source files in `~/projects/oms/` to identify:
   - Variable and function naming conventions
   - Class structure and organization
   - Code formatting and style preferences
   - Unit test patterns and frameworks
   - Python integration testing approaches
   - Flatbuffers schema design patterns
   - Smart pointer usage (unique_ptr, shared_ptr, weak_ptr)
   - RAII implementations
   - Interface/abstraction patterns
   - Polymorphism usage

2. **Document Findings**: Create or update reference files:
   - `references/naming_conventions.md` - Variables, functions, classes, files
   - `references/code_style.md` - Formatting, organization, comments
   - `references/testing_patterns.md` - Unit tests, integration tests, mocking
   - `references/flatbuffers_patterns.md` - Schema design, usage patterns
   - `references/design_patterns.md` - Smart pointers, RAII, polymorphism, abstractions

3. **Extract Examples**: Include concrete code snippets from OMS projects to illustrate patterns

### 2. Application Phase

When writing new code or reviewing existing code:

1. **Load Relevant References**: Read the appropriate reference files based on the task
2. **Apply Patterns**: Follow the documented conventions from OMS
3. **Maintain Consistency**: Ensure new code matches the established style
4. **Cross-Reference**: When in doubt, examine similar OMS code for guidance

### 3. Continuous Improvement

As you work with the codebase:

1. **Discover New Patterns**: Notice conventions not yet documented
2. **Update References**: Add newly discovered patterns to the appropriate reference files
3. **Refine Documentation**: Improve clarity and add more examples
4. **Track Evolution**: Note when OMS conventions change over time

## Usage Scenarios

**Writing New C++ Code**
- "Create a new C++ class for BPM detection following OMS conventions"
- "Implement a message handler using OMS patterns"

**Flatbuffers Integration**
- "Design a flatbuffers schema for sensor data following OMS style"
- "Add flatbuffers serialization to this class"

**Testing**
- "Write unit tests for this class using OMS testing patterns"
- "Create Python integration tests following OMS conventions"

**Code Review & Refactoring**
- "Review this code and suggest changes to match OMS style"
- "Refactor this to use proper smart pointers like OMS does"
- "Make this RAII-compliant following OMS patterns"

## Initial Analysis Guide

When first analyzing OMS code, examine:

**Files to prioritize:**
- Core library headers (.h, .hpp)
- Implementation files (.cpp, .cc)
- Test files (test_*.cpp, *_test.cpp)
- Flatbuffers schemas (.fbs)
- Python test files (test_*.py)
- CMakeLists.txt (build patterns)

**What to look for:**
- Consistent naming patterns across files
- Common code structures (constructors, destructors, move semantics)
- Error handling approaches
- Logging conventions
- Documentation style (Doxygen, inline comments)
- Include guard patterns
- Namespace organization
- Template usage patterns

## References

This skill maintains self-documenting references that evolve over time:

### references/naming_conventions.md
Naming patterns for variables, functions, classes, namespaces, files, and constants. Created by analyzing OMS code.

### references/code_style.md
Formatting preferences, file organization, include ordering, comment style, and code structure conventions.

### references/testing_patterns.md
Unit testing frameworks, test organization, mocking strategies, assertion patterns, and Python integration testing.

### references/flatbuffers_patterns.md
Schema design principles, naming in .fbs files, versioning strategies, and C++ integration patterns.

### references/design_patterns.md
Smart pointer usage, RAII implementations, interface design, polymorphism patterns, and abstraction strategies.

**Note:** These reference files start empty or minimal and are populated through code analysis. Always check if references exist and are up-to-date before relying on them.
