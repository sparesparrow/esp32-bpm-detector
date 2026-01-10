#!/usr/bin/env python3
"""
Learning Loop Status Dashboard
Real-time monitoring of self-improving learning system performance.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from self_improving_learning_loop import SelfImprovingLearningLoop
from notification_manager import NotificationManager

class LearningLoopDashboard:
    """Real-time dashboard for learning loop monitoring"""
    
    def __init__(self, prompts_dir: str = None, db_path: str = None, enable_notifications: bool = True):
        if prompts_dir is None:
            prompts_dir = "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
        if db_path is None:
            db_path = os.path.join(os.path.dirname(prompts_dir), "learning.db")
        
        self.loop = SelfImprovingLearningLoop(prompts_dir, db_path)
        self.db = self.loop.db
        self.enable_notifications = enable_notifications
        
        # Initialize notification manager if enabled
        if self.enable_notifications:
            self.notify = NotificationManager(enable_mqtt=True, enable_serial=False)
        else:
            self.notify = None
    
    def print_header(self, title: str):
        """Print formatted header"""
        width = 70
        print("\n" + "=" * width)
        print(f"  {title}")
        print("=" * width)
    
    def print_metric(self, label: str, value: str, emoji: str = ""):
        """Print formatted metric"""
        print(f"  {emoji} {label}: {value}")
    
    def print_section(self, title: str):
        """Print section header"""
        print(f"\n  📋 {title}")
        print("  " + "-" * 65)
    
    def show_overall_stats(self):
        """Display overall learning loop statistics"""
        self.print_header("Learning Loop Dashboard")
        
        stats = self.db.get_statistics()
        
        print(f"\n  Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.print_section("Overall Statistics")
        self.print_metric("Total Interactions", str(stats.get('total_interactions', 0)), "📊")
        self.print_metric("Active Prompts", str(stats.get('total_prompts', 0)), "📚")
        self.print_metric("Average Success Rate", f"{stats.get('avg_success_rate', 0):.1f}%", "✅")
        self.print_metric("Prompts Improved", str(len(self.db.get_improved_prompts())), "🔄")
        
    def show_top_prompts(self):
        """Show top performing prompts"""
        self.print_section("🏆 Top Performing Prompts")
        
        try:
            top_prompts = self.db.get_top_prompts(limit=5)
            
            if not top_prompts:
                print("  No interactions recorded yet. Start using the learning loop!")
                return
            
            for i, prompt in enumerate(top_prompts, 1):
                try:
                    prompt_id = prompt.get('prompt_id') or prompt.get('id')
                    analysis = self.loop.analyze_prompt(prompt_id)
                    
                    # Confidence indicator (success_rate is 0.0-1.0)
                    success_rate_pct = analysis.success_rate * 100
                    if success_rate_pct >= 85:
                        confidence = "🟢 High"
                    elif success_rate_pct >= 70:
                        confidence = "🟡 Medium"
                    else:
                        confidence = "🔴 Low"
                    
                    print(f"\n  {i}. {prompt_id}")
                    print(f"     Success Rate: {success_rate_pct:.1f}%")
                    print(f"     Uses: {analysis.total_interactions}")
                    print(f"     Confidence: {confidence}")
                    
                except Exception as e:
                    print(f"\n  {i}. {prompt_id} (error: {e})")
        
        except Exception as e:
            print(f"  Error loading top prompts: {e}")
    
    def show_low_performers(self):
        """Show prompts needing improvement"""
        self.print_section("⚠️  Prompts Needing Improvement")
        
        try:
            low_performers = self.db.get_low_performing_prompts(threshold=0.75)
            
            if not low_performers:
                print("  ✅ All prompts are performing well!")
                return
            
            for i, prompt in enumerate(low_performers, 1):
                try:
                    prompt_id = prompt.get('prompt_id') or prompt.get('id')
                    analysis = self.loop.analyze_prompt(prompt_id)
                    
                    issues = []
                    success_rate_pct = analysis.success_rate * 100
                    if success_rate_pct < 50:
                        issues.append("Very low success rate")
                    if analysis.total_interactions < 5:
                        issues.append("Insufficient data")
                    
                    print(f"\n  {i}. {prompt_id}")
                    print(f"     Success Rate: {success_rate_pct:.1f}%")
                    print(f"     Uses: {analysis.total_interactions}")
                    print(f"     Issues: {', '.join(issues)}")
                
                except Exception as e:
                    print(f"\n  {i}. {prompt_id} (error: {e})")
        
        except Exception as e:
            print(f"  Error loading low performers: {e}")
    
    def show_recent_improvements(self):
        """Show recently improved prompts"""
        self.print_section("📈 Recently Improved Prompts")
        
        try:
            improvements = self.db.get_improved_prompts()
            
            if not improvements:
                print("  No improvements yet. The learning loop will improve prompts automatically!")
                return
            
            for i, improvement in enumerate(improvements[:5], 1):
                print(f"\n  {i}. {improvement['prompt_id']}")
                print(f"     Version: {improvement.get('improvement_version', 'unknown')}")
                print(f"     Improvement Date: {improvement.get('improvement_date', 'unknown')}")
                print(f"     Previous Success: {improvement.get('previous_success_rate', 'unknown')}%")
        
        except Exception as e:
            print(f"  Error loading improvements: {e}")
    
    def show_interaction_trends(self):
        """Show interaction trends over time"""
        self.print_section("📉 Interaction Trends")
        
        try:
            # Get interactions from last 24 hours
            interactions_24h = self.db.get_recent_interactions(hours=24)
            interactions_7d = self.db.get_recent_interactions(hours=24*7)
            interactions_30d = self.db.get_recent_interactions(hours=24*30)
            
            print(f"\n  Last 24 hours: {len(interactions_24h)} interactions")
            print(f"  Last 7 days: {len(interactions_7d)} interactions")
            print(f"  Last 30 days: {len(interactions_30d)} interactions")
            
            # Calculate success rate for last 24h
            if interactions_24h:
                successful = sum(1 for i in interactions_24h if i.get('success'))
                success_rate_24h = (successful / len(interactions_24h)) * 100
                print(f"\n  Success rate (24h): {success_rate_24h:.1f}%")
        
        except Exception as e:
            print(f"  Error loading trends: {e}")
    
    def show_recommendations(self):
        """Show recommendations for improving learning"""
        self.print_section("💡 Recommendations")
        
        try:
            stats = self.db.get_statistics()
            
            recommendations = []
            
            # Check if enough interactions
            if stats.get('total_interactions', 0) < 50:
                recommendations.append("Run more interactions (target: 100+) for better analysis")
            
            # Check if prompts are diverse
            if stats.get('total_prompts', 0) < 5:
                recommendations.append("Use more prompts to build comprehensive knowledge")
            
            # Check success rate
            if stats.get('avg_success_rate', 100) < 70:
                recommendations.append("Average success rate is low - review failure patterns")
            
            # Check for improvements
            if len(self.db.get_improved_prompts()) == 0:
                recommendations.append("Run learning analysis to generate prompt improvements")
            
            if not recommendations:
                recommendations.append("✅ Learning loop is performing optimally!")
            
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        except Exception as e:
            print(f"  Error generating recommendations: {e}")
    
    def show_next_steps(self):
        """Show suggested next steps"""
        self.print_section("🚀 Next Steps")
        
        stats = self.db.get_statistics()
        interactions = stats.get('total_interactions', 0)
        
        if interactions == 0:
            print("  1. Run your first tool analysis to start learning")
            print("  2. Use: analyze_cpp.sh, run_tests.sh, or parse_build_errors.py")
            print("  3. Watch as the system learns and improves")
        elif interactions < 10:
            print("  1. Continue running analyses to build interaction history")
            print("  2. Target: 10+ interactions to trigger first analysis")
            print(f"  3. Current: {interactions}/10")
        elif interactions < 50:
            print("  1. System is analyzing performance patterns")
            print("  2. Continue running tools to improve confidence")
            print(f"  3. Current: {interactions} interactions (building knowledge)")
        else:
            print("  1. Learning loop is active and generating improvements")
            print("  2. Check top performers and improvement suggestions")
            print("  3. System will continue improving automatically")
    
    def display(self):
        """Display complete dashboard"""
        try:
            # Notify dashboard refresh
            if self.notify:
                self.notify.speak("Dashboard refreshed", run_async=True)
            
            self.show_overall_stats()
            self.show_top_prompts()
            self.show_low_performers()
            self.show_recent_improvements()
            self.show_interaction_trends()
            self.show_recommendations()
            self.show_next_steps()
            
            # Get stats for notification
            stats = self.db.get_statistics()
            success_rate = stats.get('avg_success_rate', 0)
            
            # Set light color based on success rate
            if self.notify:
                if success_rate >= 80:
                    self.notify.set_light_color("green")
                elif success_rate >= 60:
                    self.notify.set_light_color("yellow")
                else:
                    self.notify.set_light_color("red", blink=True)
            
            print("\n" + "=" * 70)
            print(f"  Dashboard refreshed: {datetime.now().strftime('%H:%M:%S')}")
            print(f"  Data location: {self.db.db_path}")
            print("=" * 70 + "\n")
        
        except Exception as e:
            print(f"\n❌ Error displaying dashboard: {e}")
            if self.notify:
                self.notify.notify_failure(f"Dashboard error: {e}")
            import traceback
            traceback.print_exc()


def continuous_monitor(refresh_interval: int = 60):
    """Continuously monitor learning loop"""
    import time
    
    dashboard = LearningLoopDashboard()
    
    # Notify continuous monitoring start
    if dashboard.notify:
        dashboard.notify.speak("Starting continuous dashboard monitoring")
        dashboard.notify.set_light_color("blue", blink=True)
    
    try:
        while True:
            dashboard.display()
            print(f"Refreshing in {refresh_interval} seconds... (Ctrl+C to stop)\n")
            time.sleep(refresh_interval)
    except KeyboardInterrupt:
        print("\n📊 Dashboard closed")
        if dashboard.notify:
            dashboard.notify.speak("Dashboard monitoring stopped")
            dashboard.notify.cleanup()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Learning Loop Status Dashboard")
    parser.add_argument("--continuous", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=60, help="Refresh interval in seconds (for continuous mode)")
    
    args = parser.parse_args()
    
    dashboard = LearningLoopDashboard()
    
    if args.continuous:
        continuous_monitor(refresh_interval=args.interval)
    else:
        dashboard.display()
