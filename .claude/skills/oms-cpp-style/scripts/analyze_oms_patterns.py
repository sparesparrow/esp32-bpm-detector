#!/usr/bin/env python3
"""
OMS Code Pattern Analyzer

Helper script to systematically analyze C++ code in OMS projects
and extract patterns for documentation.

Usage:
    python analyze_oms_patterns.py [--oms-path ~/projects/oms/] [--output references/]
"""

import os
import re
import argparse
from pathlib import Path
from collections import defaultdict, Counter


class OMSAnalyzer:
    def __init__(self, oms_path):
        self.oms_path = Path(oms_path).expanduser()
        self.patterns = {
            'naming': defaultdict(list),
            'style': defaultdict(list),
            'includes': defaultdict(list),
            'classes': [],
            'functions': [],
            'variables': [],
        }
    
    def find_cpp_files(self):
        """Find all C++ source and header files."""
        patterns = ['**/*.cpp', '**/*.cc', '**/*.h', '**/*.hpp']
        files = []
        for pattern in patterns:
            files.extend(self.oms_path.glob(pattern))
        return [f for f in files if '.git' not in str(f)]
    
    def find_test_files(self):
        """Find test files."""
        patterns = ['**/test_*.cpp', '**/*_test.cpp', '**/test_*.py']
        files = []
        for pattern in patterns:
            files.extend(self.oms_path.glob(pattern))
        return files
    
    def find_flatbuffers_schemas(self):
        """Find flatbuffers schema files."""
        return list(self.oms_path.glob('**/*.fbs'))
    
    def analyze_naming_patterns(self, content, filepath):
        """Extract naming patterns from code."""
        # Class names
        class_matches = re.finditer(r'\bclass\s+(\w+)', content)
        for match in class_matches:
            self.patterns['naming']['classes'].append({
                'name': match.group(1),
                'file': filepath.name
            })
        
        # Function names
        func_matches = re.finditer(r'\b(\w+)\s*\([^)]*\)\s*(?:const)?\s*{', content)
        for match in func_matches:
            if match.group(1) not in ['if', 'for', 'while', 'switch']:
                self.patterns['naming']['functions'].append({
                    'name': match.group(1),
                    'file': filepath.name
                })
        
        # Member variables (looking for m_ prefix or trailing _)
        member_var_matches = re.finditer(r'\b(m_\w+|[a-z_]+_)\b', content)
        for match in member_matches:
            self.patterns['naming']['member_variables'].append(match.group(1))
    
    def analyze_style_patterns(self, content):
        """Extract style patterns from code."""
        # Indentation
        indent_matches = re.finditer(r'^( +)\S', content, re.MULTILINE)
        indents = [len(m.group(1)) for m in indent_matches]
        if indents:
            self.patterns['style']['indentation'].extend(indents)
        
        # Brace style
        opening_brace_same_line = len(re.findall(r'\)\s*{', content))
        opening_brace_next_line = len(re.findall(r'\)\s*\n\s*{', content))
        self.patterns['style']['brace_style'].append({
            'same_line': opening_brace_same_line,
            'next_line': opening_brace_next_line
        })
    
    def analyze_include_patterns(self, content, filepath):
        """Extract include patterns."""
        include_matches = re.finditer(r'#include\s*[<"]([^>"]+)[>"]', content)
        for match in include_matches:
            self.patterns['includes']['files'].append({
                'include': match.group(1),
                'file': filepath.name
            })
    
    def analyze_file(self, filepath):
        """Analyze a single file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                self.analyze_naming_patterns(content, filepath)
                self.analyze_style_patterns(content)
                self.analyze_include_patterns(content, filepath)
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
    
    def generate_report(self):
        """Generate analysis report."""
        report = []
        report.append("# OMS Code Analysis Report\n")
        
        # Naming patterns
        report.append("## Naming Patterns\n")
        
        if self.patterns['naming']['classes']:
            class_names = [c['name'] for c in self.patterns['naming']['classes'][:10]]
            report.append(f"### Sample Class Names\n")
            for name in class_names:
                report.append(f"- {name}\n")
        
        if self.patterns['naming']['functions']:
            func_names = [f['name'] for f in self.patterns['naming']['functions'][:10]]
            report.append(f"\n### Sample Function Names\n")
            for name in func_names:
                report.append(f"- {name}\n")
        
        # Style patterns
        report.append("\n## Style Patterns\n")
        
        if self.patterns['style']['indentation']:
            indent_counter = Counter(self.patterns['style']['indentation'])
            most_common = indent_counter.most_common(1)[0]
            report.append(f"### Indentation\n")
            report.append(f"- Most common: {most_common[0]} spaces\n")
        
        if self.patterns['style']['brace_style']:
            same_line = sum(b['same_line'] for b in self.patterns['style']['brace_style'])
            next_line = sum(b['next_line'] for b in self.patterns['style']['brace_style'])
            report.append(f"\n### Brace Style\n")
            report.append(f"- Same line: {same_line} occurrences\n")
            report.append(f"- Next line: {next_line} occurrences\n")
        
        return ''.join(report)
    
    def run_analysis(self):
        """Run complete analysis."""
        print(f"Analyzing OMS code in: {self.oms_path}")
        
        cpp_files = self.find_cpp_files()
        print(f"Found {len(cpp_files)} C++ files")
        
        for filepath in cpp_files[:50]:  # Analyze first 50 files
            print(f"Analyzing: {filepath.name}")
            self.analyze_file(filepath)
        
        test_files = self.find_test_files()
        print(f"\nFound {len(test_files)} test files")
        
        fbs_files = self.find_flatbuffers_schemas()
        print(f"Found {len(fbs_files)} flatbuffers schemas")
        
        return self.generate_report()


def main():
    parser = argparse.ArgumentParser(description='Analyze OMS code patterns')
    parser.add_argument('--oms-path', default='~/projects/oms/',
                       help='Path to OMS projects')
    parser.add_argument('--output', default=None,
                       help='Output file for analysis report')
    
    args = parser.parse_args()
    
    analyzer = OMSAnalyzer(args.oms_path)
    report = analyzer.run_analysis()
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"\nReport written to: {output_path}")
    else:
        print("\n" + "="*60)
        print(report)


if __name__ == '__main__':
    main()
