Generate or update FlatBuffers schemas following OMS patterns.

1. Review existing schemas in `schemas/` directory
2. Use oms-cpp-style skill to ensure schema follows OMS FlatBuffers patterns
3. Check `references/flatbuffers_patterns.md` for OMS conventions
4. Generate headers using: `python scripts/generate_flatbuffers.py`
5. Verify generated headers in `include/` or `conan-headers/`

Ensure schema design follows OMS naming conventions and versioning strategies.

