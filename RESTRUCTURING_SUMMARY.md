# Repository Restructuring - Quick Summary

## Recommended Structure (Option C - Hybrid)

### Three New Repositories:

1. **`sparetools-bpm-schemas`** (NEW)
   - FlatBuffers schema: `bpm_protocol.fbs`
   - Conan package providing C++, Java/Kotlin, Python bindings
   - Versioned independently
   - Published to Conan registry

2. **`esp32-bpm-provider`** (NEW - from current repo)
   - ESP32 firmware (src/, include/, platformio.ini)
   - Consumes `sparetools-bpm-schemas` via Conan
   - Independent CI/CD

3. **`android-bpm-consumer`** (NEW - from current repo)
   - Android app (android-app/)
   - Consumes `sparetools-bpm-schemas` via Conan
   - Independent CI/CD

### SpareTools Integration:

- **Move to `sparetools/`:**
  - `scripts/generate_flatbuffers.py` → `sparetools/scripts/bpm/`
  - `scripts/run_bpm_tests.py` → `sparetools/test/bpm/`
  - `tests/` → `sparetools/test/bpm/`

- **Enhance Templates:**
  - `sparetools/templates/esp32/` - Add Conan integration examples
  - `sparetools/templates/android/` - Add Conan integration examples

## Migration Order

1. **Week 1:** Create `sparetools-bpm-schemas`, set up Conan package
2. **Week 2:** Create `esp32-bpm-provider`, migrate firmware
3. **Week 2-3:** Create `android-bpm-consumer`, migrate Android app
4. **Week 3:** Move scripts/tests to SpareTools, update templates
5. **Week 4:** Cleanup, documentation, deprecation notices

## Key Decisions Needed

1. **MIA Schemas:** Keep separate (`sparetools-mia-schemas`) or merge?
2. **Android Apps:** Keep separate or merge into `android-mia-consumer` monorepo?
3. **Conan Remote:** GitHub Packages, Artifactory, or other?
4. **Schema Repository:** Standalone or part of SpareTools packages?

## Benefits

✅ **Modularity:** Each repository has single responsibility  
✅ **Versioning:** Independent versioning per component  
✅ **Dependency Management:** Conan handles schema distribution  
✅ **Reusability:** Schemas can be consumed by other projects  
✅ **Maintainability:** Clear separation of concerns  
✅ **CI/CD:** Independent build/test/deploy pipelines

## See Full Plan

For detailed migration steps, alternatives, and risk assessment, see:
**[RESTRUCTURING_PLAN.md](./RESTRUCTURING_PLAN.md)**
