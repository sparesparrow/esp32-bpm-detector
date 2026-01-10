#!/usr/bin/env python3
"""
MCP Learning Integration
Automatically records interactions when prompts are used via MCP server.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from self_improving_learning_loop import (
    SelfImprovingLearningLoop,
    Interaction
)
from notification_manager import NotificationManager
from datetime import datetime, timezone
import json
import subprocess

class MCPLearningIntegration:
    """Integrates learning loop with MCP prompt usage."""
    
    def __init__(self, prompts_dir: str = None, db_path: str = "learning_loop.db", enable_notifications: bool = True):
        if prompts_dir is None:
            prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
        
        self.loop = SelfImprovingLearningLoop(prompts_dir, db_path)
        self.prompts_dir = prompts_dir
        self.enable_notifications = enable_notifications
        
        # Initialize notification manager if enabled
        if self.enable_notifications:
            self.notify = NotificationManager(enable_mqtt=True, enable_serial=False)
        else:
            self.notify = None
    
    def record_mcp_interaction(
        self,
        prompt_id: str,
        user_query: str,
        response: str,
        success: bool = True,
        metrics: dict = None,
        variables: dict = None
    ):
        """Record an interaction from MCP prompt usage."""
        # Load prompt to get current version
        prompt_file = os.path.join(self.prompts_dir, f"{prompt_id}.json")
        
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_data = json.load(f)
            prompt_version = prompt_data.get('version', '1.0')
            prompt_content = prompt_data.get('content', '')
        else:
            prompt_version = '1.0'
            prompt_content = ''
        
        if metrics is None:
            metrics = {
                "response_time": 0.0,
                "accuracy": 1.0 if success else 0.0,
                "user_satisfaction": 1.0 if success else 0.5
            }
        
        if variables is None:
            variables = {}
        
        interaction = Interaction(
            timestamp=datetime.now(timezone.utc).isoformat(),
            prompt_id=prompt_id,
            prompt_version=prompt_version,
            user_query=user_query,
            prompt_content=prompt_content,
            variables=variables,
            response=response,
            success=success,
            success_metrics=metrics,
            user_feedback=None,
            improvement_suggestions=None
        )
        
        self.loop.record_interaction(interaction)
        print(f"📝 Recorded interaction for prompt: {prompt_id} (Success: {success})")
        
        # Notify if enabled
        if self.notify:
            self.notify.notify_interaction_recorded(prompt_id, success)
    
    def analyze_prompt(self, prompt_id: str):
        """Analyze and improve a specific prompt."""
        if self.notify:
            self.notify.notify_phase_start(f"Analyzing prompt {prompt_id}")
        
        self.loop.analyze_and_improve(prompt_id)
        
        if self.notify:
            # Get analysis to determine improvements
            analysis = self.loop.db.analyze_prompt_performance(prompt_id)
            improvements = len(analysis.improvement_opportunities) if analysis else 0
            self.notify.notify_analysis_complete(prompt_id, improvements)
    
    def run_improvement_cycle(self):
        """Run improvement cycle on all prompts."""
        if self.notify:
            self.notify.notify_phase_start("Running improvement cycle on all prompts")
            self.notify.set_light_color("purple", blink=True)
        
        self.loop.run_continuous_improvement()
        
        if self.notify:
            self.notify.notify_success("Improvement cycle complete")
            self.notify.set_light_color("green")

def main():
    """CLI interface for MCP learning integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Learning Integration")
    parser.add_argument("--record", action="store_true",
                       help="Record a test interaction")
    parser.add_argument("--prompt-id", type=str,
                       help="Prompt ID to use")
    parser.add_argument("--analyze", type=str,
                       help="Analyze a specific prompt")
    parser.add_argument("--improve-all", action="store_true",
                       help="Run improvement cycle on all prompts")
    
    args = parser.parse_args()
    
    integration = MCPLearningIntegration()
    
    if args.record:
        if not args.prompt_id:
            print("Error: --prompt-id required with --record")
            return
        
        integration.record_mcp_interaction(
            prompt_id=args.prompt_id,
            user_query="Test query from MCP integration",
            response="Test response",
            success=True
        )
    
    elif args.analyze:
        integration.analyze_prompt(args.analyze)
    
    elif args.improve_all:
        integration.run_improvement_cycle()
    
    else:
        print("Use --record --prompt-id PROMPT_ID, --analyze PROMPT_ID, or --improve-all")

if __name__ == "__main__":
    main()