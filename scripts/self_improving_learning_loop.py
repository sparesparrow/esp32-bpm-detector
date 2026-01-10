#!/usr/bin/env python3
"""
Self-Improving Learning Loop for MCP Prompts
Tracks AI interactions, analyzes outcomes, and automatically refines prompts.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib

# Import code fix engine for efficacy tracking
try:
    from code_fix_engine import CodeFixEngine, CodeFix, FixResult
    CODE_FIX_AVAILABLE = True
except ImportError:
    CODE_FIX_AVAILABLE = False

@dataclass
class Interaction:
    """Represents a single AI interaction with context and outcome."""
    timestamp: str
    prompt_id: str
    prompt_version: str
    user_query: str
    prompt_content: str
    variables: Dict[str, Any]
    response: str
    success: bool
    success_metrics: Dict[str, float]
    user_feedback: Optional[str] = None
    improvement_suggestions: Optional[List[str]] = None

@dataclass
class PromptAnalysis:
    """Analysis of a prompt's performance over time."""
    prompt_id: str
    total_interactions: int
    success_rate: float
    average_metrics: Dict[str, float]
    common_failure_patterns: List[str]
    improvement_opportunities: List[str]
    recommended_changes: Optional[str] = None

class LearningDatabase:
    """SQLite database for storing interaction history."""
    
    def __init__(self, db_path: str = "learning_loop.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                prompt_id TEXT NOT NULL,
                prompt_version TEXT NOT NULL,
                user_query TEXT NOT NULL,
                prompt_content TEXT NOT NULL,
                variables TEXT NOT NULL,
                response TEXT NOT NULL,
                success INTEGER NOT NULL,
                success_metrics TEXT NOT NULL,
                user_feedback TEXT,
                improvement_suggestions TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id TEXT NOT NULL,
                version TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                performance_score REAL,
                UNIQUE(prompt_id, version)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_id ON interactions(prompt_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON interactions(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def record_interaction(self, interaction: Interaction):
        """Record a new interaction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interactions 
            (timestamp, prompt_id, prompt_version, user_query, prompt_content,
             variables, response, success, success_metrics, user_feedback, improvement_suggestions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction.timestamp,
            interaction.prompt_id,
            interaction.prompt_version,
            interaction.user_query,
            interaction.prompt_content,
            json.dumps(interaction.variables),
            interaction.response,
            1 if interaction.success else 0,
            json.dumps(interaction.success_metrics),
            interaction.user_feedback,
            json.dumps(interaction.improvement_suggestions) if interaction.improvement_suggestions else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_prompt_interactions(self, prompt_id: str, limit: int = 100) -> List[Dict]:
        """Get all interactions for a specific prompt."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM interactions 
            WHERE prompt_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (prompt_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def analyze_prompt_performance(self, prompt_id: str) -> PromptAnalysis:
        """Analyze performance metrics for a prompt."""
        interactions = self.get_prompt_interactions(prompt_id)
        
        if not interactions:
            return PromptAnalysis(
                prompt_id=prompt_id,
                total_interactions=0,
                success_rate=0.0,
                average_metrics={},
                common_failure_patterns=[],
                improvement_opportunities=[]
            )
        
        total = len(interactions)
        successful = sum(1 for i in interactions if i['success'] == 1)
        success_rate = successful / total if total > 0 else 0.0
        
        # Aggregate metrics
        all_metrics = []
        for i in interactions:
            metrics = json.loads(i['success_metrics'])
            all_metrics.append(metrics)
        
        # Calculate averages (only for numeric values)
        if all_metrics:
            avg_metrics = {}
            for key in all_metrics[0].keys():
                numeric_values = [m.get(key) for m in all_metrics if isinstance(m.get(key), (int, float))]
                if numeric_values:
                    avg_metrics[key] = sum(numeric_values) / len(numeric_values)
        else:
            avg_metrics = {}
        
        # Identify failure patterns
        failures = [i for i in interactions if i['success'] == 0]
        failure_patterns = []
        if failures:
            # Simple pattern detection - could be enhanced with NLP
            failure_queries = [f['user_query'] for f in failures[:10]]
            failure_patterns = list(set(failure_queries))[:5]
        
        # Generate improvement opportunities
        improvements = []
        if success_rate < 0.7:
            improvements.append("Low success rate - consider refining prompt clarity")
        if avg_metrics.get('response_time', 0) > 5.0:
            improvements.append("High response time - simplify prompt complexity")
        if len(failures) > total * 0.3:
            improvements.append("High failure rate - add more context or examples")
        
        return PromptAnalysis(
            prompt_id=prompt_id,
            total_interactions=total,
            success_rate=success_rate,
            average_metrics=avg_metrics,
            common_failure_patterns=failure_patterns,
            improvement_opportunities=improvements
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics for the learning loop."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total interactions
        cursor.execute("SELECT COUNT(*) FROM interactions")
        total_interactions = cursor.fetchone()[0]
        
        # Total unique prompts
        cursor.execute("SELECT COUNT(DISTINCT prompt_id) FROM interactions")
        total_prompts = cursor.fetchone()[0]
        
        # Average success rate
        cursor.execute("SELECT AVG(success) FROM interactions")
        avg_success = cursor.fetchone()[0] or 0.0
        avg_success_rate = avg_success * 100.0
        
        conn.close()
        
        return {
            'total_interactions': total_interactions,
            'total_prompts': total_prompts,
            'avg_success_rate': avg_success_rate
        }
    
    def get_top_prompts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing prompts by interaction count."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT prompt_id, COUNT(*) as count, AVG(success) as avg_success
            FROM interactions
            GROUP BY prompt_id
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list and add 'id' alias for compatibility
        result = []
        for row in rows:
            d = dict(row)
            d['id'] = d.get('prompt_id', d.get('id'))
            result.append(d)
        
        return result
    
    def get_low_performing_prompts(self, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Get prompts with success rate below threshold."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT prompt_id, COUNT(*) as count, AVG(success) as avg_success
            FROM interactions
            GROUP BY prompt_id
            HAVING avg_success < ?
            ORDER BY avg_success ASC
        """, (threshold,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list and add 'id' alias for compatibility
        result = []
        for row in rows:
            d = dict(row)
            d['id'] = d.get('prompt_id', d.get('id'))
            result.append(d)
        
        return result
    
    def get_improved_prompts(self) -> List[Dict[str, Any]]:
        """Get list of prompts that have been improved."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT prompt_id, MAX(created_at) as improvement_date
            FROM prompt_versions
            GROUP BY prompt_id
            ORDER BY improvement_date DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        improvements = []
        for row in rows:
            # Get the latest version info
            prompt_id = row['prompt_id']
            analysis = self.analyze_prompt_performance(prompt_id)
            
            improvements.append({
                'prompt_id': prompt_id,
                'improvement_date': row['improvement_date'],
                'previous_success_rate': analysis.success_rate * 100,
                'improvement_version': 'latest'
            })
        
        return improvements
    
    def get_recent_interactions(self, hours: int = 24) -> List[Dict]:
        """Get interactions from the last N hours."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat().replace('+00:00', 'Z')
        
        cursor.execute("""
            SELECT * FROM interactions
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (cutoff,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

class PromptRefinementEngine:
    """Engine that generates improved prompts based on analysis."""
    
    def __init__(self, prompts_dir: str):
        self.prompts_dir = Path(prompts_dir)
    
    def generate_improved_prompt(self, analysis: PromptAnalysis, current_prompt: Dict) -> Dict:
        """Generate an improved version of a prompt based on analysis."""
        improved = current_prompt.copy()
        
        # Generate version hash
        version_hash = hashlib.md5(
            json.dumps(improved, sort_keys=True).encode()
        ).hexdigest()[:8]
        improved['version'] = version_hash
        improved['updatedAt'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # Add improvement metadata
        if 'metadata' not in improved:
            improved['metadata'] = {}
        
        improved['metadata']['learning_data'] = {
            'previous_success_rate': analysis.success_rate,
            'total_interactions': analysis.total_interactions,
            'improvements_applied': analysis.improvement_opportunities,
            'refined_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        # Apply improvements to content
        content = improved['content']
        
        # If low success rate, add more context
        if analysis.success_rate < 0.7:
            content = self._add_context_guidance(content, analysis)
        
        # If high failure patterns, add examples
        if analysis.common_failure_patterns:
            content = self._add_examples(content, analysis)
        
        improved['content'] = content
        
        return improved
    
    def _add_context_guidance(self, content: str, analysis: PromptAnalysis) -> str:
        """Add context guidance to improve clarity."""
        guidance = "\n\n## Important Context\n"
        guidance += "Based on analysis of " + str(analysis.total_interactions) + " interactions:\n"
        guidance += "- Success rate: " + f"{analysis.success_rate:.1%}\n"
        
        if analysis.improvement_opportunities:
            guidance += "- Key improvements: " + ", ".join(analysis.improvement_opportunities[:3]) + "\n"
        
        return content + guidance
    
    def _add_examples(self, content: str, analysis: PromptAnalysis) -> str:
        """Add examples to help with common failure patterns."""
        examples = "\n\n## Common Scenarios\n"
        examples += "The following scenarios have been successfully handled:\n"
        
        # This would ideally use successful interactions as examples
        examples += "- Example scenarios will be added based on successful interactions\n"
        
        return content + examples
    
    def save_improved_prompt(self, prompt: Dict, prompt_id: str):
        """Save improved prompt to the prompts directory."""
        prompt_file = self.prompts_dir / f"{prompt_id}.json"
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            json.dump(prompt, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved improved prompt: {prompt_id} (version: {prompt['version']})")

class SelfImprovingLearningLoop:
    """Main orchestrator for the self-improving learning loop."""
    
    def __init__(self, prompts_dir: str, db_path: str = "learning_loop.db"):
        self.db = LearningDatabase(db_path)
        self.refinement_engine = PromptRefinementEngine(prompts_dir)
        self.prompts_dir = Path(prompts_dir)
    
    def record_interaction(self, interaction: Interaction = None, 
                          prompt_id: str = None, query: str = None, 
                          success: bool = True, metrics: Dict = None,
                          metadata: Dict = None):
        """Record a new interaction and trigger analysis if needed.
        
        Can be called with either:
        - Full Interaction object: record_interaction(interaction)
        - Simplified parameters: record_interaction(prompt_id="...", query="...", success=True, metrics={})
        """
        if interaction is None:
            # Create Interaction from simplified parameters
            if prompt_id is None or query is None:
                raise ValueError("prompt_id and query required when not using Interaction object")
            
            # Load prompt to get version and content
            prompt_file = self.prompts_dir / f"{prompt_id}.json"
            prompt_version = "1.0"
            prompt_content = ""
            
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_data = json.load(f)
                    prompt_version = prompt_data.get('version', '1.0')
                    prompt_content = prompt_data.get('content', '')
            
            interaction = Interaction(
                timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                prompt_id=prompt_id,
                prompt_version=prompt_version,
                user_query=query,
                prompt_content=prompt_content,
                variables=metadata.get('variables', {}) if metadata else {},
                response=metadata.get('response', '') if metadata else '',
                success=success,
                success_metrics=metrics or {},
                user_feedback=metadata.get('user_feedback') if metadata else None,
                improvement_suggestions=metadata.get('improvement_suggestions') if metadata else None
            )
        
        self.db.record_interaction(interaction)
        
        # Trigger analysis after every 10 interactions
        interactions = self.db.get_prompt_interactions(interaction.prompt_id)
        if len(interactions) % 10 == 0:
            self.analyze_and_improve(interaction.prompt_id)
    
    def analyze_prompt(self, prompt_id: str) -> PromptAnalysis:
        """Analyze a specific prompt's performance."""
        return self.db.analyze_prompt_performance(prompt_id)
    
    def analyze_and_improve(self, prompt_id: str):
        """Analyze prompt performance and generate improvements."""
        print(f"\n🔍 Analyzing prompt: {prompt_id}")
        
        # Get analysis
        analysis = self.db.analyze_prompt_performance(prompt_id)
        
        print(f"  Total interactions: {analysis.total_interactions}")
        print(f"  Success rate: {analysis.success_rate:.1%}")
        print(f"  Average metrics: {analysis.average_metrics}")
        
        if analysis.total_interactions < 5:
            print("  ⚠️  Not enough data for improvement yet")
            return
        
        # Load current prompt
        prompt_file = self.prompts_dir / f"{prompt_id}.json"
        if not prompt_file.exists():
            print(f"  ⚠️  Prompt file not found: {prompt_file}")
            return
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            current_prompt = json.load(f)
        
        # Generate improvement
        if analysis.success_rate < 0.8 or analysis.improvement_opportunities:
            print(f"  🔧 Generating improvement...")
            
            improved_prompt = self.refinement_engine.generate_improved_prompt(
                analysis, current_prompt
            )
            
            # Save improved version
            self.refinement_engine.save_improved_prompt(improved_prompt, prompt_id)
            
            print(f"  ✅ Prompt improved! New version: {improved_prompt['version']}")
        else:
            print(f"  ✓ Prompt performing well ({analysis.success_rate:.1%} success rate)")
    
    def run_continuous_improvement(self, check_interval: int = 100):
        """Run continuous improvement loop checking all prompts."""
        print("🚀 Starting continuous improvement loop...")
        
        # Find all prompt files
        prompt_files = list(self.prompts_dir.glob("*.json"))
        
        for prompt_file in prompt_files:
            prompt_id = prompt_file.stem
            if prompt_id == "index":
                continue
            
            try:
                self.analyze_and_improve(prompt_id)
            except Exception as e:
                print(f"  ❌ Error analyzing {prompt_id}: {e}")
        
        print("✅ Improvement cycle complete!")

    def get_code_fix_engine(self, project_root: str = ".") -> Optional['CodeFixEngine']:
        """Get the code fix engine for applying fixes."""
        if not CODE_FIX_AVAILABLE:
            print("⚠️  Code fix engine not available (module not found)")
            return None
        return CodeFixEngine(project_root)

    def apply_code_fixes(self, review_json: Dict, project_root: str = ".",
                         severity_filter: List[str] = None,
                         dry_run: bool = False) -> List[Dict]:
        """Apply code fixes from review findings with efficacy tracking.

        Args:
            review_json: Review findings in JSON format
            project_root: Root directory of the project
            severity_filter: List of severities to fix (default: critical, high)
            dry_run: If True, preview without applying

        Returns:
            List of fix results with efficacy data
        """
        engine = self.get_code_fix_engine(project_root)
        if not engine:
            return []

        results = engine.apply_review_fixes(
            review_json,
            severity_filter=severity_filter or ["critical", "high"],
            dry_run=dry_run,
            auto_verify=not dry_run
        )

        # Record results as interactions for learning
        for result in results:
            self.db.record_interaction(Interaction(
                timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                prompt_id="code-fix-engine",
                prompt_version="1.0",
                user_query=f"Apply fix {result.fix_id}",
                prompt_content="",
                variables={"dry_run": dry_run},
                response=result.diff_preview[:500],
                success=result.success and not result.rollback_needed,
                success_metrics={
                    "build_passed": result.build_passed or False,
                    "tests_passed": result.tests_passed or False,
                    "rollback_needed": result.rollback_needed
                }
            ))

        return [asdict(r) if hasattr(r, '__dataclass_fields__') else r for r in results]

    def get_efficacy_stats(self, project_root: str = ".") -> Dict[str, Any]:
        """Get combined efficacy statistics for prompts and code fixes.

        Returns comprehensive statistics including:
        - Prompt performance metrics
        - Code fix success rates
        - Improvement trends
        """
        stats = {
            "prompts": self.db.get_statistics(),
            "code_fixes": {},
            "combined": {}
        }

        # Get code fix stats if available
        engine = self.get_code_fix_engine(project_root)
        if engine:
            stats["code_fixes"] = engine.get_stats()

        # Calculate combined metrics
        prompt_success = stats["prompts"].get("avg_success_rate", 0)
        fix_success = stats["code_fixes"].get("success_rate", 0)

        stats["combined"] = {
            "prompt_success_rate": prompt_success,
            "code_fix_success_rate": fix_success,
            "overall_efficacy": (prompt_success + fix_success) / 2 if fix_success else prompt_success,
            "total_improvements": (
                stats["prompts"].get("total_interactions", 0) +
                stats["code_fixes"].get("applied_fixes", 0)
            )
        }

        return stats

    def print_efficacy_report(self, project_root: str = "."):
        """Print a formatted efficacy report."""
        stats = self.get_efficacy_stats(project_root)

        print("\n" + "=" * 60)
        print("       LEARNING LOOP EFFICACY REPORT")
        print("=" * 60)

        print("\n📊 Prompt Performance:")
        print(f"   Total interactions: {stats['prompts'].get('total_interactions', 0)}")
        print(f"   Unique prompts: {stats['prompts'].get('total_prompts', 0)}")
        print(f"   Success rate: {stats['prompts'].get('avg_success_rate', 0):.1f}%")

        if stats["code_fixes"]:
            print("\n🔧 Code Fix Performance:")
            cf = stats["code_fixes"]
            print(f"   Total fixes recorded: {cf.get('total_fixes', 0)}")
            print(f"   Applied fixes: {cf.get('applied_fixes', 0)}")
            print(f"   Successful fixes: {cf.get('successful_fixes', 0)}")
            print(f"   Success rate: {cf.get('success_rate', 0):.1f}%")
            print(f"   Rollback rate: {cf.get('rollback_rate', 0):.1f}%")

            if cf.get("by_issue_type"):
                print("\n   By Issue Type:")
                for issue, data in cf["by_issue_type"].items():
                    print(f"     {issue}: {data['success']}/{data['total']} ({data['rate']:.1f}%)")

        print("\n📈 Combined Metrics:")
        print(f"   Total improvements applied: {stats['combined']['total_improvements']}")
        print(f"   Overall efficacy: {stats['combined']['overall_efficacy']:.1f}%")
        print("=" * 60 + "\n")


def main():
    """Main entry point for the learning loop."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Improving Learning Loop for MCP Prompts")
    parser.add_argument("--prompts-dir", default="/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts",
                       help="Directory containing prompt JSON files")
    parser.add_argument("--db-path", default="learning_loop.db",
                       help="Path to SQLite database")
    parser.add_argument("--analyze", type=str, metavar="PROMPT_ID",
                       help="Analyze a specific prompt")
    parser.add_argument("--improve-all", action="store_true",
                       help="Run improvement cycle on all prompts")
    parser.add_argument("--efficacy-stats", action="store_true",
                       help="Show efficacy statistics for prompts and code fixes")
    parser.add_argument("--apply-fixes", type=str, metavar="REVIEW_FILE",
                       help="Apply code fixes from a review JSON file")
    parser.add_argument("--project-root", default=".",
                       help="Project root directory for code fixes")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview fixes without applying")
    parser.add_argument("--severity", nargs="+", default=["critical", "high"],
                       help="Severity levels to fix (default: critical, high)")

    args = parser.parse_args()

    loop = SelfImprovingLearningLoop(args.prompts_dir, args.db_path)

    if args.efficacy_stats:
        loop.print_efficacy_report(args.project_root)
    elif args.apply_fixes:
        with open(args.apply_fixes, 'r') as f:
            review_json = json.load(f)
        results = loop.apply_code_fixes(
            review_json,
            project_root=args.project_root,
            severity_filter=args.severity,
            dry_run=args.dry_run
        )
        print(f"\nApplied {len(results)} fixes")
        for r in results:
            status = "OK" if r.get("success") else "FAILED"
            print(f"  [{status}] {r.get('fix_id')}")
    elif args.analyze:
        loop.analyze_and_improve(args.analyze)
    elif args.improve_all:
        loop.run_continuous_improvement()
    else:
        print("Use --analyze PROMPT_ID, --improve-all, or --efficacy-stats")
        print("For code fixes: --apply-fixes REVIEW_FILE [--dry-run]")


if __name__ == "__main__":
    main()