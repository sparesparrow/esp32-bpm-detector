# Testing Patterns

*This document is populated by analyzing OMS code in ~/projects/oms/*

## Unit Testing Framework

### Framework Used
- Name (gtest, catch2, etc.):
- Version:

### Test File Organization
- Naming convention:
- Directory structure:
- One test file per class vs combined:

### Test Naming
- Test case naming:
- Test function naming:
- Examples:

## Unit Test Structure

### Basic Test Pattern
```cpp
// Standard test structure:
```

### Setup and Teardown
- Test fixtures:
- SetUp/TearDown usage:
- Resource management:

### Assertions
- Preferred assertion macros:
- ASSERT vs EXPECT:
- Custom assertions:
- Examples:

## Test Coverage

### What to Test
- Public interfaces:
- Edge cases:
- Error conditions:
- Examples:

### What Not to Test
- Private methods:
- Trivial getters/setters:
- Third-party code:

## Mocking and Stubbing

### Mocking Framework
- Framework used (gmock, etc.):
- When to use mocks:

### Mock Objects
- Creation pattern:
- Examples:

### Stub Implementation
- When to use:
- Examples:

## Python Integration Testing

### Framework
- pytest, unittest, or other:
- Directory structure:

### Test Organization
- File naming:
- Test class structure:
- Examples:

### C++ Integration
- Binding approach (pybind11, ctypes, etc.):
- Calling C++ from Python:
- Data exchange patterns:
- Examples:

### Test Patterns
```python
# Standard Python test structure:
```

### Fixtures and Setup
```python
# Setup/teardown in Python tests:
```

## Continuous Integration

### Build Integration
- CMake test targets:
- Test execution:

### Test Running
- Command-line invocation:
- Filtering tests:
- Parallel execution:

## Performance Testing

### Benchmarking
- Framework/approach:
- Patterns:
- Examples:

### Profiling
- Tools used:
- Integration in tests:

## Test Data Management

### Input Data
- Location:
- Format:
- Loading pattern:

### Expected Output
- Storage:
- Comparison approach:

### Temporary Files
- Creation:
- Cleanup:
- Examples:

## Special Testing Scenarios

### Multi-threading Tests
- Synchronization:
- Race condition testing:
- Examples:

### Memory Leak Detection
- Tools (valgrind, sanitizers):
- Integration:

### Flatbuffers in Tests
- Creating test messages:
- Validation:
- Examples:
