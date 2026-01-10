# Self-Improving Learning Loop for MCP Prompts

## Overview

The Self-Improving Learning Loop is an automated system that tracks AI interactions, analyzes outcomes, and continuously refines prompts in the MCP Prompts server. This creates a **self-improving AI system** that gets better over time without manual intervention.

## Architecture

```
┌─────────────────┐
│  AI Interaction │
│  (MCP Client)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MCP Server     │
│  (mcp-prompts)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Learning Loop  │────▶│  SQLite Database    │
│  Integration    │      │  (Interactions)   │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐
│  Analysis Engine│
│  (Performance)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Refinement     │
│  Engine         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Updated Prompt │
│  (mcp-prompts)  │
└─────────────────┘
```

## Components

### 1. Learning Database (`LearningDatabase`)

Stores all AI interactions with:
- User queries and responses
- Success/failure indicators
- Performance metrics (response time, accuracy, satisfaction)
- User feedback and improvement suggestions

**Schema:**
- `interactions` table: Records every prompt usage
- `prompt_versions` table: Tracks prompt evolution

### 2. Performance Analyzer (`PromptAnalysis`)

Analyzes prompt performance by:
- Calculating success rates
- Identifying failure patterns
- Detecting improvement opportunities
- Aggregating metrics over time

### 3. Refinement Engine (`PromptRefinementEngine`)

Generates improved prompts by:
- Adding context guidance for low success rates
- Including examples for common failure patterns
- Updating metadata with learning data
- Versioning prompts automatically

### 4. Learning Loop Orchestrator (`SelfImprovingLearningLoop`)

Coordinates the entire system:
- Records interactions automatically
- Triggers analysis at intervals
- Applies improvements when needed
- Maintains prompt version history

## Usage

### Basic Usage

```python
from self_improving_learning_loop import SelfImprovingLearningLoop, Interaction

# Initialize the learning loop
loop = SelfImprovingLearningLoop(
    prompts_dir="/path/to/prompts",
    db_path="learning_loop.db"
)

# Record an interaction
interaction = Interaction(
    timestamp=datetime.utcnow().isoformat() + 'Z',
    prompt_id="analysis-assistant",
    prompt_version="1.0",
    user_query="Analyze this code",
    prompt_content="...",
    variables={},
    response="Analysis result",
    success=True,
    success_metrics={"response_time": 2.5, "accuracy": 0.9}
)

loop.record_interaction(interaction)

# Analyze and improve
loop.analyze_and_improve("analysis-assistant")
```

### Command Line Interface

```bash
# Analyze a specific prompt
python3 scripts/self_improving_learning_loop.py --analyze analysis-assistant

# Run improvement cycle on all prompts
python3 scripts/self_improving_learning_loop.py --improve-all

# Run demonstration
python3 scripts/demo_learning_loop.py
```

### MCP Integration

```bash
# Record an interaction from MCP usage
python3 scripts/mcp_learning_integration.py --record --prompt-id analysis-assistant

# Analyze after interactions
python3 scripts/mcp_learning_integration.py --analyze analysis-assistant
```

## Learning Metrics

The system tracks:

1. **Success Rate**: Percentage of successful interactions
2. **Response Time**: Average time to generate response
3. **Accuracy**: Quality of responses (0.0 - 1.0)
4. **User Satisfaction**: User feedback scores
5. **Failure Patterns**: Common queries that fail

## Improvement Triggers

Prompts are automatically improved when:

- Success rate drops below 70%
- Response time exceeds 5 seconds
- Failure rate exceeds 30%
- Every 10 interactions (periodic review)

## Example Output

```
🔍 Analyzing prompt: analysis-assistant
  Total interactions: 15
  Success rate: 80.0%
  Average metrics:
    - response_time: 2.70
    - accuracy: 0.84
    - user_satisfaction: 0.81

  🔧 Generating improvement...
✓ Saved improved prompt: analysis-assistant (version: 183a7e87)
  ✅ Prompt improved! New version: 183a7e87
```

## Integration with MCP Server

The learning loop can be integrated with the MCP server to automatically record interactions:

1. **Automatic Recording**: When prompts are used via MCP, interactions are recorded
2. **Periodic Analysis**: Analysis runs automatically after N interactions
3. **Continuous Improvement**: Prompts are refined based on real-world usage

## Best Practices

1. **Start with Baseline**: Record initial interactions to establish baseline metrics
2. **Monitor Regularly**: Review analysis results periodically
3. **User Feedback**: Encourage user feedback to improve accuracy
4. **Version Control**: Keep track of prompt versions for rollback if needed
5. **A/B Testing**: Test improved prompts against previous versions

## Future Enhancements

- [ ] NLP-based failure pattern detection
- [ ] Automatic example extraction from successful interactions
- [ ] Multi-prompt correlation analysis
- [ ] Integration with Claude Skills
- [ ] Real-time improvement suggestions
- [ ] Performance dashboards

## Related Documentation

- [MCP Prompts Server Documentation](../../ai-mcp-monorepo/packages/mcp-prompts/README.md)
- [Claude Skills Configuration](../.cursor/rules/claude-skills.mdc)
- [Self-Improving Prompts Rules](../../.cursor/rules/self-improving-prompts-tools.mdc)