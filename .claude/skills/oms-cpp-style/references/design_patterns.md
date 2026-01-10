# Design Patterns

*This document is populated by analyzing OMS code in ~/projects/oms/*

## Smart Pointers

### unique_ptr Usage
- When to use:
- Typical patterns:
- Factory functions:
- Examples:
```cpp
// unique_ptr patterns:
```

### shared_ptr Usage
- When to use:
- Typical patterns:
- Avoiding overuse:
- Examples:
```cpp
// shared_ptr patterns:
```

### weak_ptr Usage
- When to use:
- Breaking cycles:
- Examples:
```cpp
// weak_ptr patterns:
```

### Raw Pointer Usage
- When acceptable:
- Non-owning pointers:
- Guidelines:

### Custom Deleters
- When used:
- Patterns:
- Examples:

## RAII (Resource Acquisition Is Initialization)

### Resource Management
- File handles:
- Network connections:
- Locks:
- Memory:
- Examples:

### RAII Wrappers
```cpp
// Standard RAII wrapper pattern:
```

### Lock Guards
- mutex usage:
- lock_guard vs unique_lock:
- Examples:

### Scope Guards
- If used:
- Pattern:
- Examples:

## Object Lifetime

### Constructor Patterns
- Member initialization:
- Delegating constructors:
- Examples:

### Destructor Patterns
- Virtual destructors:
- Exception safety:
- Examples:

### Move Semantics
- Move constructors:
- Move assignment:
- std::move usage:
- Examples:

### Copy Semantics
- Copy constructors:
- Copy assignment:
- When to delete:
- Examples:

### Rule of Five/Zero
- Application:
- Examples:

## Interfaces and Abstractions

### Abstract Base Classes
- Pure virtual interfaces:
- Naming convention:
- Examples:
```cpp
// Interface pattern:
```

### Virtual Functions
- When to use virtual:
- Virtual destructors:
- Override keyword:
- Final keyword:

### Interface Segregation
- Single-purpose interfaces:
- Avoiding fat interfaces:
- Examples:

## Polymorphism

### Runtime Polymorphism
- Virtual function usage:
- Dynamic dispatch:
- Examples:

### Compile-Time Polymorphism
- Templates:
- CRTP (Curiously Recurring Template Pattern):
- If/when used:

### Type Erasure
- If used:
- Patterns:
- Examples:

## Design Principles

### Dependency Injection
- Constructor injection:
- Setter injection:
- Examples:

### Inversion of Control
- Pattern usage:
- Examples:

### Single Responsibility
- Class design:
- Function design:

### Open/Closed Principle
- Extensibility:
- Examples:

## Factory Patterns

### Factory Functions
```cpp
// Factory pattern:
```

### Factory Classes
- If used:
- Pattern:
- Examples:

### Builder Pattern
- If used:
- Pattern:
- Examples:

## Observer Pattern

### Implementation
- If used:
- Callback patterns:
- Signal/slot mechanisms:
- Examples:

### Event Handling
- Event dispatch:
- Listener registration:
- Examples:

## Template Patterns

### Template Classes
- When used:
- Patterns:
- Examples:

### Template Functions
- When used:
- Type deduction:
- SFINAE usage:

### Template Specialization
- Full specialization:
- Partial specialization:
- Examples:

### Concepts (C++20)
- If used:
- Patterns:

## Error Handling Patterns

### Exception Hierarchy
```cpp
// Custom exception classes:
```

### Exception Safety
- Strong guarantee:
- Basic guarantee:
- No-throw guarantee:
- Examples:

### Error Codes
- If/when used instead of exceptions:
- Return patterns:
- Examples:

### Result/Optional Types
- std::optional usage:
- std::expected usage (C++23):
- Custom result types:

## Concurrency Patterns

### Thread Management
- std::thread usage:
- Thread pools:
- Examples:

### Synchronization
- Mutex patterns:
- Condition variables:
- Atomics:
- Examples:

### Lock-Free Patterns
- If used:
- Atomic operations:
- Memory ordering:

## Compile-Time Patterns

### constexpr Usage
- constexpr functions:
- constexpr variables:
- Examples:

### Type Traits
- std::enable_if:
- Custom traits:
- Examples:

### Tag Dispatch
- If used:
- Pattern:

## Composition Patterns

### Composition over Inheritance
- When applied:
- Examples:

### Mixin Pattern
- If used:
- Examples:

### Pimpl (Pointer to Implementation)
- If used:
- Pattern:
- Examples:

## Memory Patterns

### Memory Pools
- If used:
- Pattern:
- Examples:

### Object Pools
- If used:
- Pattern:
- Examples:

### Custom Allocators
- If used:
- Pattern:
- Examples:
