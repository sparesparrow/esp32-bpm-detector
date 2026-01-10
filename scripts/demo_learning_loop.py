#!/usr/bin/env python3
"""
Demonstration of the Self-Improving Learning Loop
Simulates AI interactions and shows how prompts improve over time.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from self_improving_learning_loop import (
    SelfImprovingLearningLoop,
    Interaction,
    PromptAnalysis
)
from notification_manager import NotificationManager
from datetime import datetime, timezone
import json
import time

def simulate_interactions(loop: SelfImprovingLearningLoop, notify: NotificationManager, prompt_id: str, num_interactions: int = 15):
    """Simulate a series of interactions with varying success rates."""
    print(f"\n📊 Simulating {num_interactions} interactions for prompt: {prompt_id}")
    print("=" * 60)
    
    # Notify simulation start
    notify.notify_phase_start(f"Simulating {num_interactions} interactions")
    notify.set_light_color("blue", blink=True)
    
    # Spawn progress monitor terminal
    notify.spawn_terminal(
        f"watch -n 1 'echo \"Simulation in progress...\"'",
        "Simulation Monitor"
    )
    
    # Simulate interactions with improving success rate over time
    for i in range(num_interactions):
        # Success rate improves from 50% to 90% over time
        success_rate = 0.5 + (i / num_interactions) * 0.4
        success = (i % 10) < (success_rate * 10)
        
        interaction = Interaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            prompt_id=prompt_id,
            prompt_version="v1.0",
            user_query=f"Test query #{i+1}",
            prompt_content="Example prompt content",
            variables={"query": f"test_{i+1}"},
            response=f"Response to query {i+1}",
            success=success,
            success_metrics={
                "response_time": 2.0 + (i * 0.1),
                "accuracy": 0.7 + (i * 0.02),
                "user_satisfaction": 0.6 + (i * 0.03)
            },
            user_feedback="Good" if success else "Needs improvement",
            improvement_suggestions=["Add more examples"] if not success else None
        )
        
        loop.record_interaction(interaction)
        notify.notify_interaction_recorded(prompt_id, success)
        
        # Update progress
        notify.notify_learning_progress("Simulation", i + 1, num_interactions)
        
        status = "✅" if success else "❌"
        print(f"  {status} Interaction {i+1}/{num_interactions} - Success: {success}")
        
        # Trigger analysis every 5 interactions
        if (i + 1) % 5 == 0:
            print(f"\n  🔄 Triggering analysis after {i+1} interactions...")
            notify.notify_phase_start(f"Analyzing prompt after {i+1} interactions")
            loop.analyze_and_improve(prompt_id)
            notify.notify_analysis_complete(prompt_id, improvements=1)
            time.sleep(0.5)

def demonstrate_learning_cycle():
    """Demonstrate a complete learning cycle."""
    print("🚀 Self-Improving Learning Loop Demonstration")
    print("=" * 60)
    
    # Initialize notification manager
    notify = NotificationManager(enable_mqtt=True, enable_serial=False)
    notify.speak("Starting learning loop demonstration")
    notify.set_light_color("blue", blink=True)
    
    prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
    db_path = "/tmp/learning_loop_demo.db"
    
    # Clean up previous demo database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    loop = SelfImprovingLearningLoop(prompts_dir, db_path)
    
    # Test with a real prompt if available
    test_prompt_id = "analysis-assistant"
    
    # Check if prompt exists
    prompt_file = os.path.join(prompts_dir, f"{test_prompt_id}.json")
    if not os.path.exists(prompt_file):
        print(f"⚠️  Prompt file not found: {prompt_file}")
        print("Creating a test prompt for demonstration...")
        
        test_prompt = {
            "id": test_prompt_id,
            "name": "Analysis Assistant",
            "description": "Test prompt for learning loop demonstration",
            "content": "You are a helpful assistant. Analyze the following: {{query}}",
            "isTemplate": True,
            "tags": ["test", "demo"],
            "variables": ["query"],
            "version": "1.0",
            "createdAt": datetime.utcnow().isoformat() + 'Z',
            "updatedAt": datetime.utcnow().isoformat() + 'Z'
        }
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            json.dump(test_prompt, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Created test prompt: {test_prompt_id}")
    
    # Simulate interactions
    simulate_interactions(loop, notify, test_prompt_id, num_interactions=15)
    
    # Final analysis
    print("\n" + "=" * 60)
    print("📈 Final Analysis")
    print("=" * 60)
    
    analysis = loop.db.analyze_prompt_performance(test_prompt_id)
    
    print(f"\nPrompt: {analysis.prompt_id}")
    print(f"Total Interactions: {analysis.total_interactions}")
    print(f"Success Rate: {analysis.success_rate:.1%}")
    print(f"Average Metrics:")
    for key, value in analysis.average_metrics.items():
        print(f"  - {key}: {value:.2f}")
    
    print(f"\nImprovement Opportunities:")
    for opp in analysis.improvement_opportunities:
        print(f"  - {opp}")
    
    if analysis.common_failure_patterns:
        print(f"\nCommon Failure Patterns:")
        for pattern in analysis.common_failure_patterns[:3]:
            print(f"  - {pattern}")
    
    # Show improvement
    print("\n" + "=" * 60)
    print("🔧 Generating Improved Prompt")
    print("=" * 60)
    
    notify.notify_phase_start("Generating improved prompt")
    loop.analyze_and_improve(test_prompt_id)
    notify.notify_prompt_improvement(test_prompt_id, "enhanced")
    
    print("\n✅ Learning loop demonstration complete!")
    print(f"📊 Database saved to: {db_path}")
    print(f"📝 Check the prompt file for improvements: {prompt_file}")
    
    # Final notification
    notify.notify_success("Learning loop demonstration complete")
    notify.set_light_color("green")
    notify.cleanup()

if __name__ == "__main__":
    demonstrate_learning_cycle()