# Code Review Action Items - Quick Reference

## 🔴 CRITICAL - Fix Immediately

### 1. Memory Leak in FFT (`src/bpm_detector.cpp:217`)
**Fix:** Pre-allocate `fft_real_buffer_` and `fft_imag_buffer_` as member variables
**Time:** 30 minutes
**Impact:** Prevents heap fragmentation and improves performance

### 2. Missing Return Statement (`src/bpm_detector.cpp:179`)
**Fix:** Add `return result;` at end of `detect()` function
**Time:** 1 minute
**Impact:** Prevents undefined behavior

---

## 🟠 HIGH - Fix This Sprint

### 3. Uninitialized Member Variables (`src/bpm_detector.cpp:13-97`)
**Fix:** Initialize all member variables in constructor initializer list
**Time:** 15 minutes
**Impact:** Prevents undefined behavior in BPM detection

### 4. Format String Errors (`src/main.cpp:652, 668, 680`)
**Fix:** Change `%d` to `%.1f` for float BPM values
**Time:** 5 minutes
**Impact:** Prevents undefined behavior in logging

### 5. Raw Pointers (`src/main.cpp:375, 385, 414, 441`)
**Fix:** Use `std::unique_ptr` for all `new` allocations
**Time:** 1 hour
**Impact:** OMS compliance, automatic cleanup, exception safety

---

## 🟡 MEDIUM - Next Sprint

### 6. Global Variables (`src/main.cpp:63-75`)
**Fix:** Encapsulate in `BpmApplication` class
**Time:** 2-3 hours
**Impact:** Better architecture, testability

### 7. Hardcoded WiFi Credentials (`src/config.h:7-8`)
**Fix:** Use WiFiManager or EEPROM storage
**Time:** 1-2 hours
**Impact:** Security, configurability

### 8. Missing Error Handling (`src/audio_input.cpp:180`)
**Fix:** Check `calloc()` return value
**Time:** 10 minutes
**Impact:** Robustness

### 9. Race Condition in Logging (`src/main.cpp:38-59`)
**Fix:** Use `std::atomic` for `logWriteIndex` and `logCount`
**Time:** 30 minutes
**Impact:** Thread safety (if logging from interrupts)

---

## 🟢 LOW - Technical Debt

### 10. OMS Naming Conventions
**Fix:** Rename variables/functions to match OMS style
**Time:** 2-3 hours
**Impact:** Code consistency

### 11. Missing Documentation
**Fix:** Add Doxygen comments to public APIs
**Time:** 4-6 hours
**Impact:** Maintainability

### 12. Magic Numbers
**Fix:** Extract to named constants
**Time:** 1 hour
**Impact:** Code readability

---

## Quick Wins (Do First)

1. ✅ Fix missing return statement (1 min)
2. ✅ Fix format strings (5 min)
3. ✅ Initialize member variables (15 min)
4. ✅ Add error check for calloc (10 min)

**Total Quick Wins Time:** ~30 minutes  
**Impact:** Fixes 4 critical/high priority issues

---

## Estimated Total Effort

- **Critical + High Priority:** ~2 hours
- **Medium Priority:** ~4-6 hours
- **Low Priority:** ~7-10 hours
- **Total:** ~13-18 hours

---

## Priority Order

1. Missing return statement
2. Memory leak in FFT
3. Format string errors
4. Uninitialized variables
5. Error handling for allocations
6. Smart pointers refactor
7. WiFi credentials
8. Global variables refactor
9. Race condition fix
10. Documentation
11. Magic numbers
12. Naming conventions
