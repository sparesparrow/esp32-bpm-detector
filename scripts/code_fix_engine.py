#!/usr/bin/env python3
"""
Code Fix Engine - Auto-apply code fixes from review findings with efficacy tracking.
Integrates with the self-improving learning loop.
"""

import json
import os
import re
import sqlite3
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

@dataclass
class CodeFix:
    """Represents a code fix to be applied."""
    id: str
    file_path: str
    issue_type: str
    severity: str  # critical, high, medium, low
    description: str
    old_code: str
    new_code: str
    line_start: int
    line_end: int
    confidence: float  # 0.0 to 1.0

@dataclass
class FixResult:
    """Result of applying a code fix."""
    fix_id: str
    success: bool
    applied_at: str
    diff_preview: str
    error_message: Optional[str] = None
    build_passed: Optional[bool] = None
    tests_passed: Optional[bool] = None
    rollback_needed: bool = False

class FixDatabase:
    """SQLite database for tracking code fix efficacy."""

    def __init__(self, db_path: str = "code_fixes.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_fixes (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                file_path TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                old_code TEXT NOT NULL,
                new_code TEXT NOT NULL,
                line_start INTEGER NOT NULL,
                line_end INTEGER NOT NULL,
                confidence REAL NOT NULL,
                applied INTEGER DEFAULT 0,
                verified_success INTEGER,
                build_passed INTEGER,
                tests_passed INTEGER,
                rollback_needed INTEGER DEFAULT 0,
                rollback_at TEXT,
                metrics TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fix_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_type TEXT NOT NULL,
                pattern TEXT NOT NULL,
                fix_template TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_confidence REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(issue_type, pattern)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fix_issue_type
            ON code_fixes(issue_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fix_file_path
            ON code_fixes(file_path)
        """)

        conn.commit()
        conn.close()

    def record_fix(self, fix: CodeFix) -> None:
        """Record a new code fix."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO code_fixes
            (id, timestamp, file_path, issue_type, severity, description,
             old_code, new_code, line_start, line_end, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fix.id,
            datetime.now(timezone.utc).isoformat(),
            fix.file_path,
            fix.issue_type,
            fix.severity,
            fix.description,
            fix.old_code,
            fix.new_code,
            fix.line_start,
            fix.line_end,
            fix.confidence
        ))

        conn.commit()
        conn.close()

    def update_fix_result(self, result: FixResult) -> None:
        """Update fix with application result."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE code_fixes SET
                applied = 1,
                verified_success = ?,
                build_passed = ?,
                tests_passed = ?,
                rollback_needed = ?,
                metrics = ?
            WHERE id = ?
        """, (
            1 if result.success else 0,
            1 if result.build_passed else (0 if result.build_passed is not None else None),
            1 if result.tests_passed else (0 if result.tests_passed is not None else None),
            1 if result.rollback_needed else 0,
            json.dumps({
                "applied_at": result.applied_at,
                "diff_preview": result.diff_preview[:1000],  # Truncate
                "error": result.error_message
            }),
            result.fix_id
        ))

        conn.commit()
        conn.close()

        # Update pattern success/failure counts
        self._update_pattern_stats(result.fix_id, result.success)

    def _update_pattern_stats(self, fix_id: str, success: bool) -> None:
        """Update pattern statistics based on fix result."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT issue_type FROM code_fixes WHERE id = ?",
            (fix_id,)
        )
        row = cursor.fetchone()
        if row:
            issue_type = row[0]
            if success:
                cursor.execute("""
                    UPDATE fix_patterns SET success_count = success_count + 1
                    WHERE issue_type = ?
                """, (issue_type,))
            else:
                cursor.execute("""
                    UPDATE fix_patterns SET failure_count = failure_count + 1
                    WHERE issue_type = ?
                """, (issue_type,))

        conn.commit()
        conn.close()

    def get_efficacy_stats(self) -> Dict[str, Any]:
        """Get overall efficacy statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_fixes,
                SUM(CASE WHEN applied = 1 THEN 1 ELSE 0 END) as applied_fixes,
                SUM(CASE WHEN verified_success = 1 THEN 1 ELSE 0 END) as successful_fixes,
                SUM(CASE WHEN build_passed = 1 THEN 1 ELSE 0 END) as build_passed,
                SUM(CASE WHEN tests_passed = 1 THEN 1 ELSE 0 END) as tests_passed,
                SUM(CASE WHEN rollback_needed = 1 THEN 1 ELSE 0 END) as rollbacks
            FROM code_fixes
        """)

        row = cursor.fetchone()

        stats = {
            "total_fixes": row[0] or 0,
            "applied_fixes": row[1] or 0,
            "successful_fixes": row[2] or 0,
            "build_passed": row[3] or 0,
            "tests_passed": row[4] or 0,
            "rollbacks": row[5] or 0,
            "success_rate": (row[2] / row[1] * 100) if row[1] else 0,
            "rollback_rate": (row[5] / row[1] * 100) if row[1] else 0
        }

        # Per-issue type stats
        cursor.execute("""
            SELECT issue_type,
                COUNT(*) as total,
                SUM(CASE WHEN verified_success = 1 THEN 1 ELSE 0 END) as success
            FROM code_fixes
            WHERE applied = 1
            GROUP BY issue_type
        """)

        stats["by_issue_type"] = {}
        for row in cursor.fetchall():
            issue_type, total, success = row
            stats["by_issue_type"][issue_type] = {
                "total": total,
                "success": success or 0,
                "rate": (success / total * 100) if total else 0
            }

        conn.close()
        return stats


class CodeFixEngine:
    """Engine for parsing, applying, and tracking code fixes."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.db = FixDatabase(str(self.project_root / "code_fixes.db"))

    def parse_review_findings(self, review_json: Dict) -> List[CodeFix]:
        """Parse code review findings into actionable fixes."""
        fixes = []

        for finding in review_json.get("findings", []):
            if not finding.get("fix_available", False):
                continue

            fix = CodeFix(
                id=f"fix-{hash(json.dumps(finding, sort_keys=True)) & 0xFFFFFF:06x}",
                file_path=finding.get("file", ""),
                issue_type=finding.get("type", "unknown"),
                severity=finding.get("severity", "medium"),
                description=finding.get("description", ""),
                old_code=finding.get("old_code", ""),
                new_code=finding.get("new_code", ""),
                line_start=finding.get("line_start", 0),
                line_end=finding.get("line_end", 0),
                confidence=finding.get("confidence", 0.8)
            )

            if fix.old_code and fix.new_code and fix.file_path:
                fixes.append(fix)
                self.db.record_fix(fix)

        return fixes

    def generate_diff_preview(self, fix: CodeFix) -> str:
        """Generate a git-style diff preview for a fix."""
        lines_old = fix.old_code.split('\n')
        lines_new = fix.new_code.split('\n')

        diff = []
        diff.append(f"--- a/{fix.file_path}")
        diff.append(f"+++ b/{fix.file_path}")
        diff.append(f"@@ -{fix.line_start},{len(lines_old)} +{fix.line_start},{len(lines_new)} @@")

        for line in lines_old:
            diff.append(f"-{line}")
        for line in lines_new:
            diff.append(f"+{line}")

        return '\n'.join(diff)

    def apply_fix(self, fix: CodeFix, dry_run: bool = False) -> FixResult:
        """Apply a code fix to the file."""
        file_path = self.project_root / fix.file_path
        applied_at = datetime.now(timezone.utc).isoformat()
        diff_preview = self.generate_diff_preview(fix)

        if not file_path.exists():
            return FixResult(
                fix_id=fix.id,
                success=False,
                applied_at=applied_at,
                diff_preview=diff_preview,
                error_message=f"File not found: {file_path}"
            )

        try:
            content = file_path.read_text()

            if fix.old_code not in content:
                return FixResult(
                    fix_id=fix.id,
                    success=False,
                    applied_at=applied_at,
                    diff_preview=diff_preview,
                    error_message="Old code not found in file - may have been modified"
                )

            if dry_run:
                return FixResult(
                    fix_id=fix.id,
                    success=True,
                    applied_at=applied_at,
                    diff_preview=diff_preview,
                    error_message="Dry run - not applied"
                )

            # Apply the fix
            new_content = content.replace(fix.old_code, fix.new_code, 1)
            file_path.write_text(new_content)

            return FixResult(
                fix_id=fix.id,
                success=True,
                applied_at=applied_at,
                diff_preview=diff_preview
            )

        except Exception as e:
            return FixResult(
                fix_id=fix.id,
                success=False,
                applied_at=applied_at,
                diff_preview=diff_preview,
                error_message=str(e)
            )

    def verify_fix(self, fix: CodeFix, result: FixResult) -> FixResult:
        """Verify fix by running build and tests."""
        if not result.success:
            self.db.update_fix_result(result)
            return result

        # Try to build
        build_result = self._run_build()
        result.build_passed = build_result

        if not build_result:
            result.rollback_needed = True
            self._rollback_fix(fix)
        else:
            # Run tests
            test_result = self._run_tests()
            result.tests_passed = test_result

            if not test_result:
                result.rollback_needed = True
                self._rollback_fix(fix)

        self.db.update_fix_result(result)
        return result

    def _run_build(self) -> bool:
        """Run the project build."""
        try:
            # Check for platformio.ini
            if (self.project_root / "platformio.ini").exists():
                proc = subprocess.run(
                    ["pio", "run", "--environment", "esp32s3"],
                    cwd=self.project_root,
                    capture_output=True,
                    timeout=300
                )
                return proc.returncode == 0

            # Fallback to make
            if (self.project_root / "Makefile").exists():
                proc = subprocess.run(
                    ["make"],
                    cwd=self.project_root,
                    capture_output=True,
                    timeout=300
                )
                return proc.returncode == 0

            return True  # No build system found

        except Exception:
            return False

    def _run_tests(self) -> bool:
        """Run project tests."""
        try:
            if (self.project_root / "run_tests.py").exists():
                proc = subprocess.run(
                    ["python3", "run_tests.py"],
                    cwd=self.project_root,
                    capture_output=True,
                    timeout=600
                )
                return proc.returncode == 0

            return True  # No test runner found

        except Exception:
            return False

    def _rollback_fix(self, fix: CodeFix) -> bool:
        """Rollback a fix by restoring original code."""
        file_path = self.project_root / fix.file_path

        try:
            content = file_path.read_text()
            if fix.new_code in content:
                new_content = content.replace(fix.new_code, fix.old_code, 1)
                file_path.write_text(new_content)
                return True
            return False
        except Exception:
            return False

    def apply_review_fixes(
        self,
        review_json: Dict,
        severity_filter: List[str] = None,
        dry_run: bool = False,
        auto_verify: bool = True
    ) -> List[FixResult]:
        """Apply all fixes from a code review with optional filtering."""

        if severity_filter is None:
            severity_filter = ["critical", "high"]

        fixes = self.parse_review_findings(review_json)
        filtered_fixes = [f for f in fixes if f.severity in severity_filter]

        results = []
        for fix in filtered_fixes:
            result = self.apply_fix(fix, dry_run=dry_run)

            if auto_verify and result.success and not dry_run:
                result = self.verify_fix(fix, result)
            else:
                self.db.update_fix_result(result)

            results.append(result)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get fix efficacy statistics."""
        return self.db.get_efficacy_stats()


def main():
    """Demo usage of the code fix engine."""
    import argparse

    parser = argparse.ArgumentParser(description="Code Fix Engine")
    parser.add_argument("--project", default=".", help="Project root directory")
    parser.add_argument("--review-file", help="JSON file with review findings")
    parser.add_argument("--dry-run", action="store_true", help="Preview without applying")
    parser.add_argument("--stats", action="store_true", help="Show efficacy statistics")
    parser.add_argument("--severity", nargs="+", default=["critical", "high"],
                       help="Severity levels to fix")

    args = parser.parse_args()

    engine = CodeFixEngine(args.project)

    if args.stats:
        stats = engine.get_stats()
        print("\n=== Code Fix Efficacy Statistics ===")
        print(f"Total fixes recorded: {stats['total_fixes']}")
        print(f"Applied fixes: {stats['applied_fixes']}")
        print(f"Successful fixes: {stats['successful_fixes']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Rollback rate: {stats['rollback_rate']:.1f}%")

        if stats['by_issue_type']:
            print("\nBy Issue Type:")
            for issue_type, data in stats['by_issue_type'].items():
                print(f"  {issue_type}: {data['success']}/{data['total']} ({data['rate']:.1f}%)")
        return

    if args.review_file:
        with open(args.review_file) as f:
            review_json = json.load(f)

        results = engine.apply_review_fixes(
            review_json,
            severity_filter=args.severity,
            dry_run=args.dry_run
        )

        print(f"\n=== Applied {len(results)} fixes ===")
        for result in results:
            status = "OK" if result.success else "FAILED"
            print(f"  [{status}] {result.fix_id}")
            if result.error_message:
                print(f"       Error: {result.error_message}")
            if result.rollback_needed:
                print(f"       ⚠️  Rolled back due to build/test failure")


if __name__ == "__main__":
    main()
