# 📋 Self-Improving Learning Loop - Quick Reference Card

## 🎯 What Is This?

A system that automatically learns from your development tool usage and improves itself over time. Every time you run code analysis, tests, or debug builds, the system records what worked and what didn't, then automatically improves its behavior.

---

## ⚡ Most Common Commands

```bash
# View learning loop status (do this daily)
python3 ~/projects/ai-mcp-monorepo/packages/mcp-prompts/learning_loop_dashboard.py

# Continuous monitoring (watch in real-time)
python3 ~/projects/ai-mcp-monorepo/packages/mcp-prompts/learning_loop_dashboard.py --continuous

# Manually trigger analysis
python3 ~/projects/ai-mcp-monorepo/packages/mcp-prompts/scripts/self_improving_learning_loop.py --analyze-all

# See learning statistics
python3 ~/projects/ai-mcp-monorepo/packages/mcp-prompts/learning_loop_integration.py status
```

---

## 📊 Dashboard Interpretation

When you run the dashboard, you'll see:

```
📊 Total Interactions: 24      ← Number of tool runs recorded
📚 Active Prompts: 3           ← Different tool configs being learned
✅ Average Success Rate: 82%   ← How well tools are working
🔄 Prompts Improved: 2         ← Versions automatically generated
```

**What's Good:**
- ✅ Total Interactions: 100+ is ideal
- ✅ Success Rate: >70% is good, >85% is excellent
- ✅ Prompts Improved: 3+ means system is learning
- ✅ 🟢 High confidence: System is reliable

**What Needs Attention:**
- ⚠️ Success Rate <50%: Something's wrong, review failures
- ⚠️ 🔴 Low confidence: Run more tests to build confidence
- ⚠️ Few interactions: Keep using the tools, system learns from usage

---

## 🔄 The Loop (Simplified)

```
1. You run a tool (cppcheck, pytest, etc)
                    ↓
2. System records: Did it work? How fast? How accurate?
                    ↓
3. After 10+ runs, system analyzes patterns
                    ↓
4. If success rate low, system improves the configuration
                    ↓
5. Next time you run tool, it uses improved config
                    ↓
6. Loop continues (step 1)
```

---

## 🚀 Integration Checklist

### ✅ Learning is Automatic If:
- [ ] You're using `dev-intelligence-orchestrator` skills
- [ ] Tool scripts (analyze_cpp.sh, run_tests.sh) have learning code
- [ ] Dashboard shows "Total Interactions > 0"
- [ ] "Prompts Improved" counter increasing

### 🔧 If Nothing is Happening:
1. Check: `python3 learning_loop_dashboard.py`
2. See if "Total Interactions" is 0
3. If yes, run actual analysis: `./scripts/analyze_cpp.sh src/file.cpp memory .`
4. Check dashboard again - should see 1+ interaction

---

## 📈 Weekly Metrics to Check

Every week, run:

```bash
python3 ~/projects/ai-mcp-monorepo/packages/mcp-prompts/learning_loop_dashboard.py
```

Track:
- **Total Interactions**: Should grow by ~50-100/week
- **Success Rate**: Should trend upward (>70% goal)
- **Prompts Improved**: Should increase (target: 3-5 improvements)

---

## 🎯 Success Indicators

After **1 week**:
- ✅ 50+ interactions recorded
- ✅ Dashboard shows statistics
- ✅ At least 1 prompt improved

After **2 weeks**:
- ✅ 150+ interactions
- ✅ 3+ prompts improved
- ✅ Success rate >75%

After **1 month**:
- ✅ 500+ interactions
- ✅ 5+ prompts improved
- ✅ Success rate >85%
- ✅ Cross-project learning visible

---

## 🛑 When to Investigate

```
Issue: Dashboard shows 0 interactions
Fix: Run a tool and check again
  $ ./scripts/analyze_cpp.sh src/test.cpp memory .
  $ python3 learning_loop_dashboard.py

Issue: Success rate very low (<40%)
Fix: Review low performers section
  $ python3 learning_loop_dashboard.py | grep "Needing Improvement"

Issue: Same prompt being improved multiple times
Fix: This is normal - system is fine-tuning
  $ Check "Recently Improved Prompts" section

Issue: No improvements after 50+ interactions
Fix: Manually trigger analysis
  $ python3 scripts/self_improving_learning_loop.py --analyze-all
```

---

## 💾 Data & Storage

```
Database location: ~/projects/ai-mcp-monorepo/packages/mcp-prompts/data/learning.db
Prompts location: ~/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts/
Backup: sqlite3 data/learning.db ".backup backup.db"
Reset: rm data/learning.db (then system reinitializes)
```

---

## 🔐 Safety

The system has built-in safeguards:
- ✅ Won't remove important context
- ✅ Won't shorten critical instructions
- ✅ Won't change core problem statements
- ✅ Tracks all changes (can revert if needed)

**Manual override if needed:**
```bash
# Revert to previous prompt version
sqlite3 data/learning.db "SELECT id, improvement_version FROM improvements ORDER BY id DESC LIMIT 1;"
# Then manually restore from version history
```

---

## 📚 Learn More

- **Full documentation**: `docs/SELF_IMPROVING_LEARNING_LOOP.md`
- **Deployment guide**: `DEPLOYMENT_PLAN.md`
- **Validation steps**: `LEARNING_LOOP_VALIDATION.md`
- **Implementation details**: `IMPLEMENTATION_SUMMARY.md`

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Dashboard shows nothing | Run a tool, wait 10 seconds, refresh dashboard |
| Success rate stuck at 0% | Increase interactions (run tools more) |
| No improvements generated | Run `--analyze-all` manually |
| Database error | Delete `data/learning.db`, let system reinitialize |
| Tool not recording | Check if integration module is accessible |

---

## 💡 Pro Tips

1. **View continuous stats**: 
   ```bash
   python3 learning_loop_dashboard.py --continuous
   ```

2. **Analyze single prompt**:
   ```bash
   python3 scripts/self_improving_learning_loop.py --analyze cppcheck-memory-esp32
   ```

3. **Export metrics to CSV**:
   ```bash
   sqlite3 -header -csv data/learning.db "SELECT * FROM interactions;" > metrics.csv
   ```

4. **Watch improvements in real-time**:
   ```bash
   watch "python3 learning_loop_dashboard.py"
   ```

---

## 🎓 Expected Timeline

| Week | Milestone |
|------|-----------|
| Week 1 | System activated, initial learning begins |
| Week 2 | First improvements generated, patterns emerge |
| Week 3 | Cross-project knowledge transfer starts |
| Week 4+ | Significant productivity improvements visible |

---

## 📞 When to Check In

- **Daily**: Glance at dashboard (5 min)
- **Weekly**: Full review + metrics check (15 min)
- **Monthly**: Summary + optimization review (30 min)

---

## ✨ What Gets Better

1. **Code Analysis**: More accurate issue detection
2. **Testing**: Faster, more efficient test execution
3. **Build Debugging**: Smarter error diagnosis
4. **Configuration**: Optimized tool settings
5. **Speed**: Reduced execution time through optimization

---

## 🚀 You're All Set!

The system is running. Every tool you use teaches it. Every analysis it runs improves it. Every improvement compounds over time.

**Just use your development tools normally and watch the system learn!**

Last updated: 2026-01-01
Version: 1.0
Status: ✅ OPERATIONAL
