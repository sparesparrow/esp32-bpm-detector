# Flatbuffers Patterns

*This document is populated by analyzing OMS code in ~/projects/oms/*

## Schema Design

### File Organization
- Schema file naming:
- Directory structure:
- Multiple schemas vs single schema:

### Schema Structure
```fbs
// Standard schema layout:
```

### Naming Conventions
- Table names:
- Struct names:
- Enum names:
- Field names:
- Namespace usage:

### Type Usage
- When to use tables vs structs:
- When to use strings vs byte vectors:
- When to use unions:
- Enum usage patterns:

## Versioning

### Schema Evolution
- Adding new fields:
- Deprecating fields:
- Version tracking approach:

### Backwards Compatibility
- Required fields:
- Optional fields:
- Default values:

## C++ Integration

### Code Generation
- flatc compiler flags:
- Build system integration:
- Generated file locations:

### Builder Pattern
```cpp
// Standard builder usage:
```

### Serialization
```cpp
// Creating and serializing messages:
```

### Deserialization
```cpp
// Reading and validating messages:
```

### Verification
- Buffer verification:
- Error handling:
- Examples:

## Memory Management

### Buffer Ownership
- Who allocates:
- Who frees:
- Lifetime management:

### Zero-Copy Access
- When used:
- Patterns:
- Examples:

### Buffer Pooling
- If used:
- Pattern:

## Message Patterns

### Request/Response
- Schema structure:
- Correlation IDs:
- Examples:

### Events/Notifications
- Schema structure:
- Timestamp handling:
- Examples:

### Nested Messages
- When to use:
- Patterns:
- Examples:

## Testing

### Test Message Creation
```cpp
// Creating test flatbuffers:
```

### Validation in Tests
```cpp
// Verifying flatbuffer content:
```

### Test Data
- Binary test data:
- JSON representation:
- Generation:

## Performance Considerations

### Size Optimization
- Field ordering:
- Alignment:
- Padding avoidance:

### Access Patterns
- Random vs sequential:
- Caching:

### Benchmarking
- Serialization speed:
- Deserialization speed:
- Size measurements:

## Python Integration

### Python Bindings
- Flatbuffers in Python:
- Schema compilation for Python:

### Serialization/Deserialization
```python
# Python flatbuffers usage:
```

### Testing with Python
```python
# Creating test messages in Python:
```

## Common Patterns

### Configuration Messages
- Schema approach:
- Examples:

### Telemetry/Metrics
- Schema approach:
- Examples:

### Command Messages
- Schema approach:
- Examples:

## Error Handling

### Schema Validation
- Compile-time checks:
- Runtime checks:

### Malformed Messages
- Detection:
- Recovery:
- Logging:

## Documentation

### Schema Comments
```fbs
// Documentation style:
```

### Field Documentation
- Required information:
- Units specification:
- Value ranges:
