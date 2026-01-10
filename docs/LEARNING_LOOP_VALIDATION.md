# Self-Improving Learning Loop - Validation & Integration Guide

## ✅ What You've Built

### Components Implemented

1. **LearningDatabase** (SQLite)
   - Tracks every prompt interaction
   - Stores success/failure metrics
   - Records user feedback and improvement suggestions
   - Indexed for fast analysis

2. **PromptAnalyzer**
   - Calculates success rates
   - Identifies failure patterns
   - Detects improvement opportunities
   - Generates performance reports

3. **PromptRefinementEngine**
   - Automatically improves low-performing prompts
   - Adds context from failure patterns
   - Generates versioned improvements
   - Maintains history for rollback

4. **SelfImprovingLearningLoop**
   - Orchestrates the entire cycle
   - Triggers analysis every 10 interactions
   - Applies improvements automatically
   - Runs continuously

---

## 🔍 Validation Checklist

### Phase 1: Verify Components Work Independently

```bash
# Test 1: Database creation and interaction recording
python3 << 'TESTDB'
from scripts.self_improving_learning_loop import LearningDatabase
db = LearningDatabase()
db.record_interaction(
    prompt_id="test-prompt",
    query="test query",
    success=True,
    metrics={"accuracy": 0.95, "time": 1.2}
)
print("✓ Database recording works")
TESTDB

# Test 2: Analysis engine
python3 << 'TESTANALYZE'
from scripts.self_improving_learning_loop import SelfImprovingLearningLoop
loop = SelfImprovingLearningLoop()
analysis = loop.analyze_prompt("test-prompt")
print(f"✓ Analysis works: {analysis.success_rate}% success rate")
TESTANALYZE

# Test 3: Refinement engine
python3 << 'TESTREFINE'
from scripts.self_improving_learning_loop import PromptRefinementEngine
engine = PromptRefinementEngine()
improved = engine.generate_improved_prompt(
    original_prompt="Analyze code for security issues",
    analysis={
        "success_rate": 0.70,
        "common_failures": ["buffer overflow detection"],
        "avg_metrics": {"accuracy": 0.78}
    }
)
print(f"✓ Refinement works: Generated improved version")
TESTREFINE
```

### Phase 2: Verify Integration with MCP Server

```bash
# Check if learning system can read/write prompts from mcp-prompts storage
python3 << 'TESTMCP'
from scripts.self_improving_learning_loop import SelfImprovingLearningLoop
import json
from pathlib import Path

loop = SelfImprovingLearningLoop()

# Find a real prompt in your mcp-prompts
prompt_file = Path("/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/tool-config/cppcheck-config-embedded-esp32-memory-default.json")

if prompt_file.exists():
    with open(prompt_file) as f:
        prompt = json.load(f)
    
    # Record an interaction
    loop.record_interaction(
        prompt_id=prompt.get("id") or prompt.get("name"),
        query="cppcheck memory analysis",
        success=True,
        metrics={"findings": 3, "false_positives": 0}
    )
    print("✓ Can record interactions with real prompts")
    
    # Analyze it
    analysis = loop.analyze_prompt(prompt.get("id") or prompt.get("name"))
    print(f"✓ Can analyze real prompts: {analysis}")
TESTMCP
```

### Phase 3: Verify Automatic Improvement Triggers

```bash
# Run a prompt through 15 interactions (should trigger improvements at 10)
python3 scripts/demo_learning_loop.py --interactions 15

# Check generated improvements
ls -lah /home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/tool-config/*.json | tail -5

# Verify versions were created
python3 << 'TESTVERSIONS'
import json
from pathlib import Path

prompts_dir = Path("/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/tool-config")
for f in prompts_dir.glob("*.json"):
    with open(f) as fp:
        p = json.load(fp)
        if "version" in p or "improvement_version" in p:
            print(f"✓ Versioned prompt found: {f.name}")
TESTVERSIONS
```

---

## 🚀 Next: Integration with dev-intelligence-orchestrator

### Step 1: Connect Learning Loop to Tool Scripts

Modify `scripts/analyze_cpp.sh` to record interactions:

```bash
#!/bin/bash
# analyze_cpp.sh - WITH LEARNING LOOP INTEGRATION

set -euo pipefail

TARGET="${1:-}"
FOCUS="${2:-general}"
PROJECT_ROOT="${3:-.}"

# ═══════════════════════════════════════════════════════════
# LEARNING LOOP: Record interaction
# ═══════════════════════════════════════════════════════════

INTERACTION_ID=$(uuidgen)
START_TIME=$(date +%s%N)

cd "$PROJECT_ROOT"

# ... existing analysis code ...

RESULT=$(cppcheck "${CPPCHECK_OPTS[@]}" "$TARGET" 2>&1 || true)

# ═══════════════════════════════════════════════════════════
# LEARNING LOOP: Record outcome
# ═══════════════════════════════════════════════════════════

END_TIME=$(date +%s%N)
EXECUTION_TIME=$((($END_TIME - $START_TIME) / 1000000)) # ms

FINDINGS_COUNT=$(echo "$RESULT" | grep -c "error:" || true)
SUCCESS=$([ $FINDINGS_COUNT -gt 0 ] && echo "true" || echo "false")

python3 - << "RECORD_INTERACTION" "$INTERACTION_ID" "$TARGET" "$FOCUS" "$FINDINGS_COUNT" "$EXECUTION_TIME"
import sys
sys.path.insert(0, '/path/to/scripts')

from self_improving_learning_loop import SelfImprovingLearningLoop

loop = SelfImprovingLearningLoop()
loop.record_interaction(
    prompt_id=f"cppcheck-{sys.argv[3]}-default",  # focus
    query=sys.argv[2],  # target
    success=True,
    metrics={
        "findings": int(sys.argv[4]),
        "execution_time_ms": int(sys.argv[5]),
        "interaction_id": sys.argv[1]
    }
)
print(f"✓ Recorded interaction {sys.argv[1]}", file=sys.stderr)
RECORD_INTERACTION

# Output results
echo "$RESULT"
```

### Step 2: Trigger Analysis Automatically

Add a cron job to analyze prompts every 100 interactions:

```bash
# /etc/cron.d/mcp-learning-loop

# Every hour, check if analysis should run
0 * * * * cd /home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts && python3 scripts/self_improving_learning_loop.py --analyze-all >> /var/log/mcp-learning.log 2>&1

# Every 6 hours, improve all prompts
0 */6 * * * cd /home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts && python3 scripts/self_improving_learning_loop.py --improve-all >> /var/log/mcp-learning.log 2>&1
```

### Step 3: Display Learning Status to User

Enhance output to show when knowledge is being captured:

```bash
#!/bin/bash
# Show learning loop status

python3 << 'SHOW_STATUS'
from scripts.self_improving_learning_loop import SelfImprovingLearningLoop
import json

loop = SelfImprovingLearningLoop()

# Get stats for all prompts
prompts = ["cppcheck-memory-default", "pylint-security-default", "pytest-default"]

print("📊 Learning Loop Status")
print("=" * 60)

for prompt_id in prompts:
    try:
        analysis = loop.analyze_prompt(prompt_id)
        print(f"\n📚 {prompt_id}")
        print(f"  Interactions: {analysis.total_interactions}")
        print(f"  Success Rate: {analysis.success_rate:.1f}%")
        print(f"  Confidence: {'🟢 High' if analysis.success_rate > 80 else '🟡 Medium' if analysis.success_rate > 60 else '🔴 Low'}")
        
        if analysis.improvement_needed:
            print(f"  ⚠️  Needs improvement (low success rate)")
    except Exception as e:
        print(f"\n📚 {prompt_id}: Not yet trained")

print("\n" + "=" * 60)
SHOW_STATUS
```

---

## 📊 Real-World Integration Example

### Scenario: Analyzing ESP32 Code

**User Input:**
```
Analyze my ESP32 BPM detector for memory issues
```

**Claude's Actions (with learning loop):**

```
🔍 Checking accumulated knowledge...
  ✓ Found learned configuration: cppcheck-embedded-esp32-memory
  ✓ Success rate: 85% (12 successful uses)
  ✓ Confidence: High

🔧 Running analysis with learned configuration...
  [cppcheck runs with optimized flags]

📊 Analysis Complete:
  • 3 memory leaks detected
  • 1 buffer overflow risk
  • 0 false positives (based on historical accuracy)

💾 Recording interaction...
  ✓ Interaction recorded (ID: abc123def456)
  ✓ Stored metrics: 3 findings, accuracy 0.98, time 2.3s

📈 Learning Loop Status:
  • This configuration has now been validated 13 times
  • Success rate: 85% → 86% (trending up)
  • Next analysis trigger: 10 interactions remain
```

---

## 🎯 Validation Metrics to Track

Create a dashboard to monitor learning loop effectiveness:

```python
# scripts/learning_loop_dashboard.py

from self_improving_learning_loop import SelfImprovingLearningLoop
import json
from datetime import datetime

loop = SelfImprovingLearningLoop()

# Metrics to track
metrics = {
    "timestamp": datetime.now().isoformat(),
    "total_interactions": 0,
    "total_prompts": 0,
    "avg_success_rate": 0.0,
    "prompts_improved": 0,
    "interaction_types": {},
    "top_prompts_by_usage": [],
}

# Collect data
for prompt in loop.db.get_all_prompts():
    analysis = loop.analyze_prompt(prompt["id"])
    metrics["total_interactions"] += analysis.total_interactions
    metrics["total_prompts"] += 1
    metrics["avg_success_rate"] += analysis.success_rate
    
    if analysis.improvement_history:
        metrics["prompts_improved"] += 1

metrics["avg_success_rate"] /= max(metrics["total_prompts"], 1)

print(json.dumps(metrics, indent=2))
```

---

## 🔗 Integration Checklist

- [ ] Learning database initialized and writable
- [ ] Tool scripts (analyze_cpp.sh, run_tests.sh) record interactions
- [ ] Analysis triggers every N interactions automatically
- [ ] Improved prompts are saved to mcp-prompts storage
- [ ] Learning status displayed to user
- [ ] Dashboard shows learning loop effectiveness
- [ ] Cron jobs scheduled for automatic analysis
- [ ] Rollback mechanism tested (can revert bad improvements)

---

## ⚠️ Important: Prevent Bad Learning

Your learning loop could learn bad patterns. Implement safeguards:

```python
# scripts/learning_loop_safeguards.py

class SafePromptImprovement:
    """Prevent bad improvements from being applied"""
    
    @staticmethod
    def validate_improvement(original, improved):
        """Check if improvement is actually better"""
        # Never remove security-critical context
        if "security" in original and "security" not in improved:
            return False, "Removed security context"
        
        # Don't shorten important instructions
        if len(improved) < len(original) * 0.5:
            return False, "Improvement too short (likely lost context)"
        
        # Don't change the core problem statement
        if original.split('\n')[0] not in improved:
            return False, "Changed core problem statement"
        
        return True, "Improvement approved"
    
    @staticmethod
    def requires_human_approval(improvement_confidence):
        """Flag improvements that need human review"""
        if improvement_confidence < 0.7:
            return True
        return False
```

---

## 📈 Success Criteria

After 1 week of integration:

- ✅ 50+ interactions recorded across prompts
- ✅ At least 1 prompt improved automatically
- ✅ Success rates improving over time
- ✅ No bad improvements applied
- ✅ Learning loop running without manual intervention
- ✅ User sees learning status in output

---

## 🚀 Next Steps (In Order)

1. **Run validation tests** (30 min)
   - Verify each component works
   - Check MCP integration
   - Test improvement triggers

2. **Integrate with dev-intelligence-orchestrator** (1 hour)
   - Add learning recording to scripts
   - Display learning status
   - Set up automatic analysis

3. **Deploy to production** (30 min)
   - Set up cron jobs
   - Configure logging
   - Monitor first week

4. **Iterate & optimize** (ongoing)
   - Adjust analysis frequency
   - Fine-tune improvement triggers
   - Collect metrics

---

## 📚 Files to Review

- `scripts/self_improving_learning_loop.py` - Core system
- `scripts/demo_learning_loop.py` - Working example
- `scripts/mcp_learning_integration.py` - MCP integration
- `docs/SELF_IMPROVING_LEARNING_LOOP.md` - Full documentation

Your learning loop is **operational**. Now make it **visible** to users and **trusted** by adding safeguards!
