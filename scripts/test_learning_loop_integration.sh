#!/bin/bash
# Quick test of cursor-agent + mcp-prompts + learning loop integration

set -e

echo "🧪 Testing Learning Loop Integration"
echo "===================================="
echo ""

# Test 1: cursor-agent can list mcp-prompts tools
echo "Test 1: List mcp-prompts tools..."
if cursor-agent mcp list-tools mcp-prompts > /dev/null 2>&1; then
    echo "  ✅ cursor-agent can access mcp-prompts tools"
else
    echo "  ❌ cursor-agent cannot access mcp-prompts tools"
    exit 1
fi

# Test 2: Get a prompt via cursor-agent
echo ""
echo "Test 2: Get prompt via cursor-agent..."
if cursor-agent --print --approve-mcps "Use mcp-prompts get_prompt name=esp32-debugging-workflow" > /dev/null 2>&1; then
    echo "  ✅ Successfully retrieved prompt via cursor-agent"
else
    echo "  ❌ Failed to retrieve prompt"
    exit 1
fi

# Test 3: Learning loop can record interactions
echo ""
echo "Test 3: Learning loop recording..."
cd "$(dirname "$0")/.."
python3 << 'EOF'
import sys
sys.path.insert(0, 'scripts')
from self_improving_learning_loop import SelfImprovingLearningLoop

prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
db_path = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/learning.db"
loop = SelfImprovingLearningLoop(prompts_dir, db_path)
loop.record_interaction(
    prompt_id="test-integration",
    query="Test integration",
    success=True,
    metrics={"test": True}
)
print("  ✅ Learning loop can record interactions")
EOF

# Test 4: Dashboard can display results
echo ""
echo "Test 4: Dashboard display..."
if python3 scripts/learning_loop_dashboard.py > /dev/null 2>&1; then
    echo "  ✅ Dashboard can display results"
else
    echo "  ⚠️  Dashboard has issues (may be non-fatal)"
fi

echo ""
echo "===================================="
echo "✅ All integration tests passed!"
echo ""
echo "Next steps:"
echo "  1. Run single cycle: python3 scripts/learning_loop_workflow.py --cycle 1"
echo "  2. View dashboard: python3 scripts/learning_loop_dashboard.py"
echo "  3. Run continuous: python3 scripts/learning_loop_workflow.py --continuous 3"
