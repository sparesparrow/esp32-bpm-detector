#!/usr/bin/env python3
"""
Learning Loop Integration Bridge
Connects dev-intelligence-orchestrator tool scripts with self-improving learning loop.
Records every tool execution, analyzes patterns, improves prompts automatically.
"""

import sys
import os
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import uuid4

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from self_improving_learning_loop import (
    SelfImprovingLearningLoop,
    LearningDatabase,
)

class ToolExecutionRecorder:
    """Records tool executions and integrates with learning loop"""
    
    def __init__(self, learning_loop: SelfImprovingLearningLoop):
        self.loop = learning_loop
        self.db = learning_loop.db
    
    def record_analysis(self, 
                       tool: str,
                       target: str, 
                       focus: str,
                       project: str,
                       result: Dict[str, Any],
                       execution_time_ms: float) -> str:
        """
        Record a code analysis execution.
        
        Args:
            tool: 'cppcheck', 'pylint', 'clang-tidy'
            target: File or directory analyzed
            focus: 'security', 'performance', 'memory', 'general'
            project: 'esp32', 'sparetools', 'mia', 'cliphist'
            result: Tool output/analysis result
            execution_time_ms: Time to execute
        
        Returns:
            interaction_id for tracking
        """
        interaction_id = str(uuid4())
        
        # Determine success (found meaningful findings)
        findings = result.get('findings', [])
        errors = [f for f in findings if f.get('severity') == 'error']
        success = len(errors) > 0  # Success = found actual issues
        
        # Extract metrics
        metrics = {
            "tool": tool,
            "target": target,
            "focus": focus,
            "project": project,
            "findings_count": len(findings),
            "errors_count": len(errors),
            "warnings_count": len([f for f in findings if f.get('severity') == 'warning']),
            "execution_time_ms": execution_time_ms,
            "false_positive_rate": self._estimate_false_positives(findings),
        }
        
        # Prompt ID follows pattern: {tool}-{focus}-{project}
        prompt_id = f"{tool}-{focus}-{project}"
        
        # Record interaction
        self.loop.record_interaction(
            prompt_id=prompt_id,
            query=f"Analyze {target} for {focus} issues",
            success=success,
            metrics=metrics,
            metadata={
                "interaction_id": interaction_id,
                "timestamp": datetime.now().isoformat(),
            }
        )
        
        print(f"💾 Recorded analysis execution: {interaction_id}", file=sys.stderr)
        return interaction_id
    
    def record_test_execution(self,
                             framework: str,
                             project: str,
                             result: Dict[str, Any],
                             execution_time_ms: float) -> str:
        """Record test execution"""
        interaction_id = str(uuid4())
        
        # Success = all tests passed
        passed = result.get('summary', {}).get('passed', 0)
        failed = result.get('summary', {}).get('failed', 0)
        total = result.get('summary', {}).get('total', 1)
        success = failed == 0
        
        metrics = {
            "framework": framework,
            "project": project,
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "execution_time_ms": execution_time_ms,
        }
        
        prompt_id = f"test-{framework}-{project}"
        
        self.loop.record_interaction(
            prompt_id=prompt_id,
            query=f"Run {framework} tests in {project}",
            success=success,
            metrics=metrics,
            metadata={
                "interaction_id": interaction_id,
                "timestamp": datetime.now().isoformat(),
            }
        )
        
        print(f"💾 Recorded test execution: {interaction_id}", file=sys.stderr)
        return interaction_id
    
    def record_build_error_analysis(self,
                                   project: str,
                                   build_system: str,
                                   result: Dict[str, Any],
                                   execution_time_ms: float) -> str:
        """Record build error diagnosis"""
        interaction_id = str(uuid4())
        
        # Success = provided diagnosis and recommendations
        diagnosis = result.get('diagnosis', {})
        recommendations = result.get('recommendations', [])
        success = len(diagnosis) > 0 or len(recommendations) > 0
        
        metrics = {
            "project": project,
            "build_system": build_system,
            "error_count": len(result.get('errors', [])),
            "diagnosis_count": len(diagnosis),
            "recommendations_count": len(recommendations),
            "severity": result.get('severity', 'unknown'),
            "execution_time_ms": execution_time_ms,
        }
        
        prompt_id = f"build-error-{build_system}-{project}"
        
        self.loop.record_interaction(
            prompt_id=prompt_id,
            query=f"Diagnose {build_system} build errors in {project}",
            success=success,
            metrics=metrics,
            metadata={
                "interaction_id": interaction_id,
                "timestamp": datetime.now().isoformat(),
            }
        )
        
        print(f"💾 Recorded build analysis: {interaction_id}", file=sys.stderr)
        return interaction_id
    
    @staticmethod
    def _estimate_false_positives(findings: List[Dict]) -> float:
        """Estimate false positive rate (placeholder)"""
        # In real implementation, this would be populated from user feedback
        # For now, return 0 (assume all findings are accurate until proven otherwise)
        return 0.0
    
    def get_learning_status(self) -> str:
        """Get current learning loop status for display"""
        output = []
        output.append("📊 Learning Loop Status")
        output.append("=" * 60)
        
        try:
            # Get stats from database
            stats = self.db.get_statistics()
            
            output.append(f"\n📈 Overall Statistics:")
            output.append(f"  Total Interactions: {stats.get('total_interactions', 0)}")
            output.append(f"  Total Prompts: {stats.get('total_prompts', 0)}")
            output.append(f"  Average Success Rate: {stats.get('avg_success_rate', 0):.1f}%")
            
            # Get top performing prompts
            output.append(f"\n🏆 Top Performing Prompts:")
            top_prompts = self.db.get_top_prompts(limit=3)
            
            for prompt in top_prompts:
                analysis = self.loop.analyze_prompt(prompt['id'])
                confidence = "🟢 High" if analysis.success_rate > 80 else "🟡 Medium" if analysis.success_rate > 60 else "🔴 Low"
                output.append(f"  • {prompt['id']}: {analysis.success_rate:.1f}% ({confidence})")
            
            # Get prompts needing improvement
            output.append(f"\n⚠️  Prompts Needing Improvement:")
            for prompt in self.db.get_low_performing_prompts(threshold=0.7):
                analysis = self.loop.analyze_prompt(prompt['id'])
                output.append(f"  • {prompt['id']}: {analysis.success_rate:.1f}% (only {analysis.total_interactions} interactions)")
            
        except Exception as e:
            output.append(f"Error gathering stats: {e}")
        
        output.append("\n" + "=" * 60)
        return "\n".join(output)


class SmartToolSelector:
    """Uses learning loop to select best tool configuration"""
    
    def __init__(self, learning_loop: SelfImprovingLearningLoop):
        self.loop = learning_loop
    
    def get_best_config(self, tool: str, focus: str, project: str) -> Optional[Dict[str, Any]]:
        """
        Get the best-performing configuration for a tool.
        Uses historical data from learning loop.
        """
        prompt_id = f"{tool}-{focus}-{project}"
        
        try:
            analysis = self.loop.analyze_prompt(prompt_id)
            
            if analysis.total_interactions == 0:
                return None  # No historical data
            
            # Return metadata about performance
            return {
                "prompt_id": prompt_id,
                "success_rate": analysis.success_rate,
                "total_uses": analysis.total_interactions,
                "confidence": "high" if analysis.success_rate > 80 else "medium" if analysis.success_rate > 60 else "low",
                "avg_metrics": analysis.avg_metrics,
            }
        except Exception as e:
            print(f"Warning: Could not get config for {prompt_id}: {e}", file=sys.stderr)
            return None
    
    def display_selection_info(self, config: Optional[Dict[str, Any]]) -> str:
        """Display info about selected configuration"""
        if not config:
            return "ℹ️  Using defaults (no historical data)"
        
        lines = []
        lines.append(f"✓ Using learned configuration: {config['prompt_id']}")
        lines.append(f"  Success rate: {config['success_rate']:.1f}% ({config['total_uses']} uses)")
        lines.append(f"  Confidence: {config['confidence'].upper()}")
        
        return "\n".join(lines)


# Example usage functions

def example_analyze_cpp_with_learning(target: str, focus: str, project: str):
    """Example: How to integrate learning into analyze_cpp.sh"""
    
    prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
    db_path = os.path.join(os.path.dirname(prompts_dir), "learning.db")
    loop = SelfImprovingLearningLoop(prompts_dir, db_path)
    recorder = ToolExecutionRecorder(loop)
    selector = SmartToolSelector(loop)
    
    # Get recommended config from learning loop
    config = selector.get_best_config("cppcheck", focus, project)
    print(selector.display_selection_info(config), file=sys.stderr)
    
    # Run analysis
    start_time = time.time()
    
    # Simulate tool execution (in reality, run actual cppcheck)
    result = {
        "findings": [
            {"severity": "error", "type": "memory leak"},
            {"severity": "warning", "type": "unused variable"},
        ]
    }
    
    execution_time_ms = (time.time() - start_time) * 1000
    
    # Record for learning
    interaction_id = recorder.record_analysis(
        tool="cppcheck",
        target=target,
        focus=focus,
        project=project,
        result=result,
        execution_time_ms=execution_time_ms
    )
    
    print(f"Analysis complete. Interaction recorded: {interaction_id}")
    print(recorder.get_learning_status(), file=sys.stderr)


def example_run_tests_with_learning(project: str):
    """Example: How to integrate learning into run_tests.sh"""
    
    prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
    db_path = os.path.join(os.path.dirname(prompts_dir), "learning.db")
    loop = SelfImprovingLearningLoop(prompts_dir, db_path)
    recorder = ToolExecutionRecorder(loop)
    
    # Run tests
    start_time = time.time()
    
    result = {
        "framework": "pytest",
        "summary": {
            "passed": 42,
            "failed": 2,
            "total": 44,
        }
    }
    
    execution_time_ms = (time.time() - start_time) * 1000
    
    # Record for learning
    interaction_id = recorder.record_test_execution(
        framework="pytest",
        project=project,
        result=result,
        execution_time_ms=execution_time_ms
    )
    
    print(f"Tests complete. Interaction recorded: {interaction_id}")
    print(recorder.get_learning_status(), file=sys.stderr)


def example_debug_build_with_learning(project: str, build_system: str):
    """Example: How to integrate learning into build error debugging"""
    
    prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
    db_path = os.path.join(os.path.dirname(prompts_dir), "learning.db")
    loop = SelfImprovingLearningLoop(prompts_dir, db_path)
    recorder = ToolExecutionRecorder(loop)
    
    # Analyze build errors
    start_time = time.time()
    
    result = {
        "errors": [
            {"type": "compilation", "message": "undefined reference"},
        ],
        "diagnosis": {
            "dependency_issue": {
                "detected": True,
                "description": "Missing Conan packages",
            }
        },
        "recommendations": [
            {"priority": "high", "title": "Install missing dependencies"}
        ],
        "severity": "moderate",
    }
    
    execution_time_ms = (time.time() - start_time) * 1000
    
    # Record for learning
    interaction_id = recorder.record_build_error_analysis(
        project=project,
        build_system=build_system,
        result=result,
        execution_time_ms=execution_time_ms
    )
    
    print(f"Build analysis complete. Interaction recorded: {interaction_id}")
    print(recorder.get_learning_status(), file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: learning_loop_integration.py <command> [args]")
        print("\nCommands:")
        print("  analyze <tool> <target> <focus> <project>")
        print("  test <framework> <project>")
        print("  build <project> <build_system>")
        print("  status")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze" and len(sys.argv) >= 5:
        example_analyze_cpp_with_learning(sys.argv[3], sys.argv[4], sys.argv[5])
    elif command == "test" and len(sys.argv) >= 4:
        example_run_tests_with_learning(sys.argv[3])
    elif command == "build" and len(sys.argv) >= 4:
        example_debug_build_with_learning(sys.argv[3], sys.argv[4])
    elif command == "status":
        prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
        db_path = os.path.join(os.path.dirname(prompts_dir), "learning.db")
        loop = SelfImprovingLearningLoop(prompts_dir, db_path)
        recorder = ToolExecutionRecorder(loop)
        print(recorder.get_learning_status())
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
