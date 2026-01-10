# 🚀 Self-Improving Learning Loop - Deployment Plan

## Phase 1: Validate Components (Today - 1 hour)

### Step 1.1: Test Learning Database

```bash
cd ~/projects/ai-mcp-monorepo/packages/mcp-prompts

python3 << 'EOF'
from pathlib import Path
import sys
sys.path.insert(0, 'scripts')

from self_improving_learning_loop import LearningDatabase

# Test database creation
db = LearningDatabase()
print("✓ Database initialized")

# Test recording interaction
db.record_interaction(
    prompt_id="test-cppcheck-memory",
    query="Analyze ESP32 for memory issues",
    success=True,
    metrics={"findings": 3, "time": 2.1}
)
print("✓ Recorded test interaction")

# Verify it was saved
interactions = db.get_interactions_for_prompt("test-cppcheck-memory")
print(f"✓ Retrieved {len(interactions)} interaction(s)")
print(f"  First interaction: {interactions[0]}")

EOF
```

**Expected Output:**
```
✓ Database initialized
✓ Recorded test interaction
✓ Retrieved 1 interaction(s)
  First interaction: {...}
```

### Step 1.2: Test Analysis Engine

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'scripts')

from self_improving_learning_loop import SelfImprovingLearningLoop

loop = SelfImprovingLearningLoop()

# Record multiple interactions
for i in range(5):
    loop.record_interaction(
        prompt_id="test-analysis",
        query=f"Test query {i}",
        success=(i % 2 == 0),  # 60% success rate
        metrics={"accuracy": 0.7 + (i * 0.05)}
    )

print("✓ Recorded 5 test interactions")

# Analyze
analysis = loop.analyze_prompt("test-analysis")
print(f"✓ Analysis complete:")
print(f"  Success rate: {analysis.success_rate}%")
print(f"  Total interactions: {analysis.total_interactions}")
print(f"  Average accuracy: {analysis.avg_metrics['accuracy']:.2f}")

EOF
```

### Step 1.3: Test Improvement Generation

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'scripts')

from self_improving_learning_loop import PromptRefinementEngine

engine = PromptRefinementEngine()

# Get an improved prompt
improved = engine.generate_improved_prompt(
    original_prompt="Analyze code for security vulnerabilities",
    analysis={
        "success_rate": 0.65,
        "common_failures": ["buffer overflow detection", "SQL injection"],
        "avg_metrics": {"accuracy": 0.72},
        "improvement_suggestions": [
            "Add examples of buffer overflow patterns",
            "Include SQL injection detection rules"
        ]
    }
)

print("✓ Generated improved prompt:")
print(f"  Version: {improved.get('version', 'unknown')}")
print(f"  Added context: {len(improved.get('template', {}).get('context', [])) > 0}")
print(f"  Added examples: {len(improved.get('template', {}).get('examples', [])) > 0}")

EOF
```

---

## Phase 2: Integrate with dev-intelligence-orchestrator (Day 2-3 - 2 hours)

### Step 2.1: Install Integration Module

```bash
cd ~/projects/ai-mcp-monorepo/packages/mcp-prompts

# Copy integration module
cp scripts/learning_loop_integration.py scripts/

# Make it executable
chmod +x scripts/learning_loop_integration.py

# Test it
python3 scripts/learning_loop_integration.py status
```

**Expected Output:**
```
📊 Learning Loop Status
============================================================

📈 Overall Statistics:
  Total Interactions: 5
  Total Prompts: 3
  Average Success Rate: 65.0%

🏆 Top Performing Prompts:
  • test-cppcheck-memory: 100.0% (🟢 High)
  • test-analysis: 60.0% (🟡 Medium)
  
⚠️  Prompts Needing Improvement:
  • test-analysis: 60.0% (only 5 interactions)

============================================================
```

### Step 2.2: Integrate with analyze_cpp.sh

Modify `/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/scripts/analyze_cpp.sh`:

```bash
# Add this at the top (after set -euo pipefail):

# Learning loop integration
LEARNING_INTEGRATION="${SCRIPT_DIR}/learning_loop_integration.py"
INTERACTION_START=$(date +%s%N)

# ... existing script ...

# Add this before outputting results:

# Record interaction with learning loop
END_TIME=$(date +%s%N)
EXECUTION_TIME_MS=$(( ($END_TIME - $INTERACTION_START) / 1000000 ))

if [ -f "$LEARNING_INTEGRATION" ]; then
    python3 "$LEARNING_INTEGRATION" analyze cppcheck "$TARGET" "$FOCUS" "$PROJECT_TYPE" <<< "$RESULT"
    echo "💾 Learning loop recorded interaction" >&2
else
    echo "⚠️  Learning integration not available" >&2
fi

# Output results
echo "$RESULT"
```

### Step 2.3: Integrate with run_tests.sh

Similar modifications to `scripts/run_tests.sh`:

```bash
# Add learning recording before final output:

if [ -f "$LEARNING_INTEGRATION" ]; then
    python3 "$LEARNING_INTEGRATION" test "$FRAMEWORK" "$PROJECT_ROOT" <<< "$RESULT"
    echo "💾 Learning loop recorded test execution" >&2
fi

# Output final result
echo "$RESULT"
```

---

## Phase 3: Set Up Automatic Analysis (Day 3 - 1 hour)

### Step 3.1: Create Analysis Trigger Script

```bash
cat > ~/projects/ai-mcp-monorepo/packages/mcp-prompts/scripts/trigger_learning_analysis.sh << 'TRIGGER_EOF'
#!/bin/bash
# Trigger learning loop analysis

cd "$(dirname "$0")/.."

INTERACTION_COUNT=$(python3 << 'PYTHON_EOF'
import sys
sys.path.insert(0, 'scripts')
from self_improving_learning_loop import SelfImprovingLearningLoop
loop = SelfImprovingLearningLoop()
stats = loop.db.get_statistics()
print(stats.get('total_interactions', 0))
PYTHON_EOF
)

echo "Current interaction count: $INTERACTION_COUNT"

# Trigger if we've had 10+ new interactions
if [ "$INTERACTION_COUNT" -ge 10 ]; then
    echo "🔍 Triggering learning analysis..."
    python3 scripts/self_improving_learning_loop.py --analyze-all
    echo "✓ Analysis complete"
else
    echo "ℹ️  Waiting for more interactions (need $((10 - INTERACTION_COUNT)) more)"
fi
TRIGGER_EOF

chmod +x ~/projects/ai-mcp-monorepo/packages/mcp-prompts/scripts/trigger_learning_analysis.sh
```

### Step 3.2: Set Up Cron Job (Optional)

```bash
# For automated analysis every 4 hours
(crontab -l 2>/dev/null; echo "0 */4 * * * cd ~/projects/ai-mcp-monorepo/packages/mcp-prompts && ./scripts/trigger_learning_analysis.sh >> /tmp/learning-loop.log 2>&1") | crontab -

# Verify cron job was added
crontab -l | grep trigger_learning
```

---

## Phase 4: Validation Test (Day 4 - 1 hour)

### Step 4.1: Run Real-World Analysis with Learning

```bash
# Test 1: Analyze with learning
cd ~/projects/embedded-systems/esp32-bpm-detector

echo "Running first analysis..."
./scripts/analyze_cpp.sh src/bpm_detector.cpp memory .

echo ""
echo "Checking learning loop status..."
python3 ~/projects/ai-mcp-monorepo/packages/mcp-prompts/scripts/learning_loop_integration.py status
```

### Step 4.2: Run Multiple Times to Trigger Improvement

```bash
# Run 10+ times to trigger analysis
for i in {1..12}; do
    echo "Run $i/12..."
    ./scripts/analyze_cpp.sh src/bpm_detector.cpp memory . > /dev/null 2>&1
    sleep 1
done

echo "Status after 12 runs:"
python3 ~/projects/ai-mcp-monorepo/packages/mcp-prompts/scripts/learning_loop_integration.py status
```

**Expected Output:**
```
📊 Learning Loop Status
============================================================

📈 Overall Statistics:
  Total Interactions: 12
  Total Prompts: 1
  Average Success Rate: 100.0%

🏆 Top Performing Prompts:
  • cppcheck-memory-esp32: 100.0% (🟢 High)
  - Used 12 times
  - Execution time: avg 2.3ms

⚠️  Prompts Needing Improvement:
  (none - all prompts performing well)

============================================================
```

### Step 4.3: Verify Improvements Were Generated

```bash
# Check if new improved prompts were created
ls -lah ~/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/tool-config/ | tail -10

# Check if they were versioned
python3 << 'EOF'
import json
from pathlib import Path

prompts_dir = Path("~/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/tool-config").expanduser()

for f in sorted(prompts_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
    with open(f) as fp:
        p = json.load(fp)
        version = p.get('metadata', {}).get('improvement_version')
        if version:
            print(f"✓ {f.name}: version {version}")
        else:
            print(f"  {f.name}: (no version)")
EOF
```

---

## Phase 5: Integration Verification Checklist

- [ ] **Database Tests Pass**
  ```bash
  python3 -m pytest scripts/tests/test_learning_database.py -v
  ```

- [ ] **Analysis Engine Works**
  ```bash
  python3 scripts/learning_loop_integration.py status
  # Should show statistics
  ```

- [ ] **Tool Scripts Record Interactions**
  - Run `analyze_cpp.sh` and verify "💾 Learning loop recorded" message
  - Run `run_tests.sh` and verify message
  
- [ ] **Improvements Generated**
  - Run tool 12+ times
  - Check that new versioned prompts created
  
- [ ] **Learning Visible to User**
  - Output shows "✓ Using learned configuration" when available
  - Shows success rate and confidence level
  
- [ ] **Automatic Analysis Triggers**
  - Run trigger script manually
  - Verify it detects interaction count correctly

---

## Quick Validation Script

Run this to verify everything is working:

```bash
#!/bin/bash
# validate_learning_loop.sh

cd ~/projects/ai-mcp-monorepo/packages/mcp-prompts

echo "🔍 Validating Learning Loop..."
echo ""

# Test 1: Database
echo "1️⃣  Testing database..."
python3 scripts/learning_loop_integration.py status > /dev/null 2>&1 && echo "   ✓ Database working" || echo "   ✗ Database failed"

# Test 2: Integration module
echo "2️⃣  Testing integration module..."
python3 -c "from scripts.learning_loop_integration import ToolExecutionRecorder; print('   ✓ Integration module loaded')" 2>/dev/null || echo "   ✗ Integration module failed"

# Test 3: Recording
echo "3️⃣  Testing interaction recording..."
python3 << 'EOF' && echo "   ✓ Recording works" || echo "   ✗ Recording failed"
import sys; sys.path.insert(0, 'scripts')
from self_improving_learning_loop import SelfImprovingLearningLoop
loop = SelfImprovingLearningLoop()
loop.record_interaction("test", "test", True, {})
EOF

# Test 4: Analysis
echo "4️⃣  Testing analysis engine..."
python3 << 'EOF' && echo "   ✓ Analysis works" || echo "   ✗ Analysis failed"
import sys; sys.path.insert(0, 'scripts')
from self_improving_learning_loop import SelfImprovingLearningLoop
loop = SelfImprovingLearningLoop()
analysis = loop.analyze_prompt("test")
print(f"   Analysis: {analysis.success_rate}% success")
EOF

echo ""
echo "✅ Learning loop validation complete!"
```

---

## Success Metrics (After 1 Week)

Track these to measure success:

```bash
python3 << 'METRICS'
import sys
sys.path.insert(0, 'scripts')
from self_improving_learning_loop import SelfImprovingLearningLoop
from datetime import datetime, timedelta

loop = SelfImprovingLearningLoop()

# Get statistics
stats = loop.db.get_statistics()

print("📊 Learning Loop Metrics (After 1 Week)")
print("=" * 60)
print(f"Total Interactions: {stats.get('total_interactions', 0)}")
print(f"Total Prompts Tracked: {stats.get('total_prompts', 0)}")
print(f"Average Success Rate: {stats.get('avg_success_rate', 0):.1f}%")
print(f"Prompts Improved: {len(loop.db.get_improved_prompts())}")
print(f"Average Improvement: +{stats.get('avg_improvement', 0):.1f}%")
print("=" * 60)

# Goal: 100+ interactions, 5+ prompts, 70%+ success
success = (
    stats.get('total_interactions', 0) >= 100 and
    stats.get('total_prompts', 0) >= 5 and
    stats.get('avg_success_rate', 0) >= 70
)

if success:
    print("✅ Learning loop performing well!")
else:
    print("⏳ Keep running the learning loop for better results")

METRICS
```

---

## Troubleshooting

### Problem: "Database file not found"
```bash
# Verify database location
ls -la ~/projects/ai-mcp-monorepo/packages/mcp-prompts/data/learning.db

# Reinitialize if needed
rm ~/projects/ai-mcp-monorepo/packages/mcp-prompts/data/learning.db
python3 scripts/self_improving_learning_loop.py --init
```

### Problem: No interactions being recorded
```bash
# Check if learning_loop_integration.py is being called
analyze_cpp.sh src/test.cpp memory . 2>&1 | grep -i "learning\|💾"

# If not in output, verify it's integrated correctly
grep -n "learning_loop_integration" scripts/analyze_cpp.sh
```

### Problem: Improvements not being generated
```bash
# Check analysis threshold
python3 << 'EOF'
import sys
sys.path.insert(0, 'scripts')
from self_improving_learning_loop import SelfImprovingLearningLoop
loop = SelfImprovingLearningLoop()

# Manually trigger analysis
loop.analyze_all_prompts()
print("Analysis triggered manually")
EOF
```

---

## Next Steps

Once validation is complete:

1. **Monitor Learning** (Week 1-2)
   - Track metrics daily
   - Adjust analysis triggers if needed
   - Collect feedback from actual usage

2. **Cross-Project Transfer** (Week 2-3)
   - Apply learned configs from esp32 to other projects
   - Create meta-prompts combining multiple domains

3. **Continuous Improvement** (Week 4+)
   - Let system run automatically
   - Periodically review most-improved prompts
   - Share best patterns across projects

Your learning loop is ready to deploy! 🚀
