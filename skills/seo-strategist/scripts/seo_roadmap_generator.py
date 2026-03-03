#!/usr/bin/env python3
"""
SEO Roadmap Generator - Generate prioritized SEO action plans and roadmaps.

Creates quarterly SEO strategies based on audit findings with impact/effort
prioritization, quick wins identification, and KPI targets.

Author: Claude Skills Team
Version: 1.0.0
"""

import argparse
import csv
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

__version__ = "1.0.0"


class SEORoadmapGenerator:
    """Generate prioritized SEO roadmaps from audit data."""

    # Task templates with impact/effort scores
    TASK_TEMPLATES = {
        # Critical priority tasks
        'fix_noindex': {
            'name': 'Remove blocking noindex directives',
            'category': 'indexation',
            'impact': 10,
            'effort': 2,
            'hours': 2,
            'description': 'Remove noindex meta tags from pages that should be indexed'
        },
        'create_robots': {
            'name': 'Create robots.txt file',
            'category': 'crawlability',
            'impact': 8,
            'effort': 2,
            'hours': 1,
            'description': 'Create robots.txt with proper directives and sitemap reference'
        },
        'create_sitemap': {
            'name': 'Create XML sitemap',
            'category': 'crawlability',
            'impact': 8,
            'effort': 3,
            'hours': 2,
            'description': 'Generate and submit XML sitemap to search engines'
        },
        'fix_blocking_robots': {
            'name': 'Fix robots.txt blocking crawlers',
            'category': 'crawlability',
            'impact': 10,
            'effort': 1,
            'hours': 1,
            'description': 'Remove or modify Disallow: / directive blocking all crawlers'
        },

        # High priority tasks
        'add_title_tags': {
            'name': 'Add missing title tags',
            'category': 'meta',
            'impact': 9,
            'effort': 3,
            'hours': 4,
            'description': 'Add unique, keyword-optimized title tags to all pages'
        },
        'add_meta_descriptions': {
            'name': 'Add missing meta descriptions',
            'category': 'meta',
            'impact': 7,
            'effort': 4,
            'hours': 6,
            'description': 'Write compelling meta descriptions with CTAs for all pages'
        },
        'fix_h1_tags': {
            'name': 'Fix H1 heading issues',
            'category': 'content',
            'impact': 7,
            'effort': 3,
            'hours': 3,
            'description': 'Ensure each page has exactly one H1 with primary keyword'
        },
        'add_canonical_tags': {
            'name': 'Implement canonical tags',
            'category': 'indexation',
            'impact': 7,
            'effort': 3,
            'hours': 2,
            'description': 'Add self-referencing canonical tags to all pages'
        },

        # Medium priority tasks
        'optimize_title_length': {
            'name': 'Optimize title tag lengths',
            'category': 'meta',
            'impact': 5,
            'effort': 4,
            'hours': 4,
            'description': 'Adjust titles to 30-60 characters for optimal SERP display'
        },
        'optimize_meta_length': {
            'name': 'Optimize meta description lengths',
            'category': 'meta',
            'impact': 4,
            'effort': 4,
            'hours': 6,
            'description': 'Adjust descriptions to 120-160 characters'
        },
        'fix_heading_hierarchy': {
            'name': 'Fix heading hierarchy',
            'category': 'content',
            'impact': 5,
            'effort': 4,
            'hours': 4,
            'description': 'Restructure headings to follow H1 > H2 > H3 hierarchy'
        },
        'add_image_alt_text': {
            'name': 'Add missing image alt text',
            'category': 'accessibility',
            'impact': 5,
            'effort': 5,
            'hours': 8,
            'description': 'Add descriptive alt text to all images'
        },
        'increase_internal_links': {
            'name': 'Improve internal linking',
            'category': 'linking',
            'impact': 6,
            'effort': 5,
            'hours': 8,
            'description': 'Add contextual internal links between related content'
        },

        # Lower priority / optimization tasks
        'add_structured_data': {
            'name': 'Implement structured data',
            'category': 'rich_results',
            'impact': 6,
            'effort': 6,
            'hours': 12,
            'description': 'Add JSON-LD schema markup for rich results eligibility'
        },
        'add_og_tags': {
            'name': 'Add Open Graph tags',
            'category': 'social',
            'impact': 4,
            'effort': 3,
            'hours': 4,
            'description': 'Implement og:title, og:description, og:image for social sharing'
        },
        'add_twitter_cards': {
            'name': 'Implement Twitter Cards',
            'category': 'social',
            'impact': 3,
            'effort': 3,
            'hours': 2,
            'description': 'Add Twitter Card meta tags for better social previews'
        },

        # Ongoing tasks
        'keyword_research': {
            'name': 'Conduct keyword research',
            'category': 'strategy',
            'impact': 8,
            'effort': 6,
            'hours': 16,
            'description': 'Research and prioritize target keywords with topic clustering'
        },
        'content_optimization': {
            'name': 'Optimize existing content',
            'category': 'content',
            'impact': 7,
            'effort': 6,
            'hours': 20,
            'description': 'Update existing content with target keywords and improved structure'
        },
        'content_creation': {
            'name': 'Create new content',
            'category': 'content',
            'impact': 8,
            'effort': 8,
            'hours': 40,
            'description': 'Develop new content targeting identified keyword gaps'
        },
        'technical_monitoring': {
            'name': 'Set up technical monitoring',
            'category': 'monitoring',
            'impact': 6,
            'effort': 4,
            'hours': 4,
            'description': 'Configure GSC, crawl monitoring, and rank tracking'
        }
    }

    # Issue to task mapping
    ISSUE_TASK_MAP = {
        ('meta', 'Missing title tag'): 'add_title_tags',
        ('meta', 'Title too short'): 'optimize_title_length',
        ('meta', 'Title may be truncated'): 'optimize_title_length',
        ('meta', 'Missing meta description'): 'add_meta_descriptions',
        ('meta', 'Meta description short'): 'optimize_meta_length',
        ('meta', 'Meta description may be truncated'): 'optimize_meta_length',
        ('content', 'Missing H1 heading'): 'fix_h1_tags',
        ('content', 'Multiple H1 headings'): 'fix_h1_tags',
        ('content', 'H3 used without H2'): 'fix_heading_hierarchy',
        ('accessibility', 'images missing alt text'): 'add_image_alt_text',
        ('linking', 'Few internal links'): 'increase_internal_links',
        ('indexation', 'Missing canonical tag'): 'add_canonical_tags',
        ('indexation', 'Page has noindex directive'): 'fix_noindex',
        ('rich_results', 'No structured data detected'): 'add_structured_data',
        ('social', 'Missing Open Graph tags'): 'add_og_tags',
        ('crawlability', 'robots.txt file not found'): 'create_robots',
        ('crawlability', 'sitemap.xml file not found'): 'create_sitemap',
        ('crawlability', 'robots.txt blocks all crawlers'): 'fix_blocking_robots'
    }

    def __init__(self, verbose: bool = False):
        """Initialize roadmap generator."""
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("SEORoadmapGenerator initialized")

    def load_audit_data(self, file_path: Path) -> Dict[str, Any]:
        """Load audit results from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded audit data from {file_path}")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in audit file: {e}")
        except Exception as e:
            raise IOError(f"Error loading audit file: {e}")

    def identify_tasks_from_audit(self, audit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify required tasks from audit results."""
        tasks = {}
        task_counts = defaultdict(int)

        # Process issues by category
        issues_by_category = audit_data.get('issues_by_category', {})

        for category, issues in issues_by_category.items():
            for issue in issues:
                message = issue.get('message', '')
                severity = issue.get('severity', 'medium')

                # Find matching task template
                task_key = None
                for (cat, msg_pattern), tkey in self.ISSUE_TASK_MAP.items():
                    if cat == category and msg_pattern.lower() in message.lower():
                        task_key = tkey
                        break

                if task_key and task_key in self.TASK_TEMPLATES:
                    task_counts[task_key] += 1

                    if task_key not in tasks:
                        template = self.TASK_TEMPLATES[task_key].copy()
                        template['task_key'] = task_key
                        template['affected_pages'] = 0
                        template['severity_boost'] = 0
                        tasks[task_key] = template

                    tasks[task_key]['affected_pages'] += 1

                    # Boost priority based on severity
                    if severity == 'critical':
                        tasks[task_key]['severity_boost'] += 3
                    elif severity == 'high':
                        tasks[task_key]['severity_boost'] += 2
                    elif severity == 'medium':
                        tasks[task_key]['severity_boost'] += 1

        # Process robots.txt issues
        robots = audit_data.get('robots_txt', {})
        if not robots.get('exists'):
            tasks['create_robots'] = self.TASK_TEMPLATES['create_robots'].copy()
            tasks['create_robots']['task_key'] = 'create_robots'
            tasks['create_robots']['affected_pages'] = 1
            tasks['create_robots']['severity_boost'] = 3

        for issue in robots.get('issues', []):
            if 'blocks all crawlers' in issue.get('message', '').lower():
                tasks['fix_blocking_robots'] = self.TASK_TEMPLATES['fix_blocking_robots'].copy()
                tasks['fix_blocking_robots']['task_key'] = 'fix_blocking_robots'
                tasks['fix_blocking_robots']['affected_pages'] = 1
                tasks['fix_blocking_robots']['severity_boost'] = 5

        # Process sitemap issues
        sitemap = audit_data.get('sitemap', {})
        if not sitemap.get('exists'):
            tasks['create_sitemap'] = self.TASK_TEMPLATES['create_sitemap'].copy()
            tasks['create_sitemap']['task_key'] = 'create_sitemap'
            tasks['create_sitemap']['affected_pages'] = 1
            tasks['create_sitemap']['severity_boost'] = 3

        # Add strategic tasks if not already present
        if audit_data.get('summary', {}).get('seo_score', 100) < 70:
            if 'keyword_research' not in tasks:
                tasks['keyword_research'] = self.TASK_TEMPLATES['keyword_research'].copy()
                tasks['keyword_research']['task_key'] = 'keyword_research'
                tasks['keyword_research']['affected_pages'] = 0
                tasks['keyword_research']['severity_boost'] = 0

            if 'technical_monitoring' not in tasks:
                tasks['technical_monitoring'] = self.TASK_TEMPLATES['technical_monitoring'].copy()
                tasks['technical_monitoring']['task_key'] = 'technical_monitoring'
                tasks['technical_monitoring']['affected_pages'] = 0
                tasks['technical_monitoring']['severity_boost'] = 0

        return list(tasks.values())

    def calculate_priority_score(self, task: Dict[str, Any]) -> float:
        """Calculate priority score for a task.

        Score = (Impact * 2 + Severity Boost) / Effort
        Higher score = higher priority
        """
        impact = task.get('impact', 5)
        effort = task.get('effort', 5)
        severity_boost = task.get('severity_boost', 0)
        affected_pages = task.get('affected_pages', 0)

        # Scale factor based on affected pages
        scale = 1 + min(affected_pages / 10, 2)  # Cap at 3x multiplier

        score = ((impact * 2) + severity_boost) * scale / max(effort, 1)
        return round(score, 2)

    def identify_quick_wins(self, tasks: List[Dict[str, Any]],
                           max_hours: int = 8) -> List[Dict[str, Any]]:
        """Identify quick win tasks (high impact, low effort)."""
        quick_wins = []

        for task in tasks:
            hours = task.get('hours', 0)
            impact = task.get('impact', 0)

            # Quick wins: <= max_hours AND impact >= 5
            if hours <= max_hours and impact >= 5:
                quick_wins.append(task)

        return sorted(quick_wins, key=lambda x: x.get('priority_score', 0), reverse=True)

    def generate_quarterly_plan(self, tasks: List[Dict[str, Any]],
                               quarters: int = 4,
                               hours_per_quarter: int = 80) -> List[Dict[str, Any]]:
        """Distribute tasks across quarters based on priority."""
        quarters_plan = []
        remaining_tasks = sorted(tasks, key=lambda x: x.get('priority_score', 0), reverse=True)

        for q in range(1, quarters + 1):
            quarter = {
                'quarter': q,
                'start_date': (datetime.now() + timedelta(days=(q-1)*90)).strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=q*90-1)).strftime('%Y-%m-%d'),
                'tasks': [],
                'total_hours': 0,
                'focus_areas': set()
            }

            # Allocate tasks to quarter
            tasks_to_remove = []
            for task in remaining_tasks:
                task_hours = task.get('hours', 0)

                if quarter['total_hours'] + task_hours <= hours_per_quarter:
                    quarter['tasks'].append(task)
                    quarter['total_hours'] += task_hours
                    quarter['focus_areas'].add(task.get('category', 'other'))
                    tasks_to_remove.append(task)

            # Remove allocated tasks
            for task in tasks_to_remove:
                remaining_tasks.remove(task)

            quarter['focus_areas'] = list(quarter['focus_areas'])
            quarter['task_count'] = len(quarter['tasks'])
            quarters_plan.append(quarter)

        return quarters_plan

    def generate_kpis(self, audit_data: Dict[str, Any],
                     quarters_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate KPI targets based on current state and planned work."""
        current_score = audit_data.get('summary', {}).get('seo_score', 50)
        current_issues = audit_data.get('summary', {}).get('total_issues', 0)

        kpis = {
            'current_state': {
                'seo_score': current_score,
                'total_issues': current_issues
            },
            'targets': []
        }

        # Project improvement per quarter
        score_improvement_per_quarter = min(10, (100 - current_score) / 4)
        issues_reduction_per_quarter = max(5, current_issues / 4)

        projected_score = current_score
        projected_issues = current_issues

        for q, quarter in enumerate(quarters_plan, 1):
            projected_score = min(100, projected_score + score_improvement_per_quarter)
            projected_issues = max(0, projected_issues - issues_reduction_per_quarter)

            target = {
                'quarter': q,
                'target_seo_score': round(projected_score),
                'target_issues': round(projected_issues),
                'organic_traffic_growth': f"+{q * 10}%",
                'key_milestones': []
            }

            # Add milestones based on quarter tasks
            if quarter['tasks']:
                categories = set(t.get('category') for t in quarter['tasks'])
                if 'crawlability' in categories:
                    target['key_milestones'].append('Crawlability issues resolved')
                if 'indexation' in categories:
                    target['key_milestones'].append('Indexation optimized')
                if 'meta' in categories:
                    target['key_milestones'].append('Meta tags optimized')
                if 'content' in categories:
                    target['key_milestones'].append('Content structure improved')

            kpis['targets'].append(target)

        return kpis

    def generate_roadmap(self, audit_data: Dict[str, Any],
                        quarters: int = 4,
                        quick_wins_only: bool = False,
                        hours_per_quarter: int = 80) -> Dict[str, Any]:
        """Generate complete SEO roadmap."""
        logger.info("Generating SEO roadmap")

        # Identify tasks from audit
        tasks = self.identify_tasks_from_audit(audit_data)

        # Calculate priority scores
        for task in tasks:
            task['priority_score'] = self.calculate_priority_score(task)

        # Sort by priority
        tasks = sorted(tasks, key=lambda x: x['priority_score'], reverse=True)

        # Identify quick wins
        quick_wins = self.identify_quick_wins(tasks)

        roadmap = {
            'generated_date': datetime.now().isoformat(),
            'audit_date': audit_data.get('audit_date', 'Unknown'),
            'current_seo_score': audit_data.get('summary', {}).get('seo_score', 'N/A'),
            'summary': {
                'total_tasks': len(tasks),
                'total_hours': sum(t.get('hours', 0) for t in tasks),
                'quick_wins_count': len(quick_wins),
                'quick_wins_hours': sum(t.get('hours', 0) for t in quick_wins),
                'categories': list(set(t.get('category', 'other') for t in tasks))
            },
            'quick_wins': quick_wins[:10],  # Top 10 quick wins
            'all_tasks': tasks if not quick_wins_only else quick_wins,
            'quarterly_plan': [],
            'kpis': {}
        }

        if not quick_wins_only:
            # Generate quarterly plan
            roadmap['quarterly_plan'] = self.generate_quarterly_plan(
                tasks, quarters=quarters, hours_per_quarter=hours_per_quarter
            )

            # Generate KPIs
            roadmap['kpis'] = self.generate_kpis(audit_data, roadmap['quarterly_plan'])

        return roadmap


def format_text_output(roadmap: Dict[str, Any]) -> str:
    """Format roadmap as human-readable text."""
    output = []

    output.append("=" * 60)
    output.append("SEO ROADMAP")
    output.append("=" * 60)
    output.append("")

    # Summary
    summary = roadmap['summary']
    output.append("SUMMARY")
    output.append("-" * 40)
    output.append(f"Current SEO Score: {roadmap['current_seo_score']}")
    output.append(f"Total Tasks: {summary['total_tasks']}")
    output.append(f"Total Hours: {summary['total_hours']}")
    output.append(f"Quick Wins: {summary['quick_wins_count']} ({summary['quick_wins_hours']} hours)")
    output.append(f"Categories: {', '.join(summary['categories'])}")
    output.append("")

    # Quick Wins
    quick_wins = roadmap.get('quick_wins', [])
    if quick_wins:
        output.append("QUICK WINS (High Impact, Low Effort)")
        output.append("-" * 40)
        for i, task in enumerate(quick_wins[:5], 1):
            output.append(f"\n{i}. {task['name']}")
            output.append(f"   Category: {task['category']} | Hours: {task['hours']}")
            output.append(f"   Impact: {task['impact']}/10 | Priority Score: {task['priority_score']}")
            output.append(f"   {task['description']}")
        output.append("")

    # Quarterly Plan
    quarterly = roadmap.get('quarterly_plan', [])
    if quarterly:
        output.append("QUARTERLY PLAN")
        output.append("-" * 40)
        for quarter in quarterly:
            output.append(f"\nQ{quarter['quarter']}: {quarter['start_date']} to {quarter['end_date']}")
            output.append(f"Tasks: {quarter['task_count']} | Hours: {quarter['total_hours']}")
            output.append(f"Focus Areas: {', '.join(quarter['focus_areas'])}")
            for task in quarter['tasks'][:3]:
                output.append(f"  - {task['name']} ({task['hours']}h)")
            if len(quarter['tasks']) > 3:
                output.append(f"  ... and {len(quarter['tasks']) - 3} more tasks")
        output.append("")

    # KPIs
    kpis = roadmap.get('kpis', {})
    if kpis.get('targets'):
        output.append("KPI TARGETS")
        output.append("-" * 40)
        current = kpis.get('current_state', {})
        output.append(f"Current State: Score {current.get('seo_score', 'N/A')}, Issues {current.get('total_issues', 'N/A')}")
        output.append("")
        for target in kpis['targets']:
            output.append(f"Q{target['quarter']} Targets:")
            output.append(f"  SEO Score: {target['target_seo_score']}")
            output.append(f"  Issues: ≤{target['target_issues']}")
            output.append(f"  Traffic Growth: {target['organic_traffic_growth']}")
            if target['key_milestones']:
                output.append(f"  Milestones: {', '.join(target['key_milestones'])}")
        output.append("")

    # All Tasks (prioritized)
    all_tasks = roadmap.get('all_tasks', [])
    if all_tasks:
        output.append("ALL TASKS (By Priority)")
        output.append("-" * 40)
        for i, task in enumerate(all_tasks, 1):
            output.append(f"{i}. [{task['category'].upper()}] {task['name']}")
            output.append(f"   Hours: {task['hours']} | Priority: {task['priority_score']}")
        output.append("")

    return "\n".join(output)


def format_markdown_output(roadmap: Dict[str, Any]) -> str:
    """Format roadmap as Markdown."""
    output = []

    output.append("# SEO Roadmap")
    output.append("")
    output.append(f"**Generated:** {roadmap['generated_date'][:10]}")
    output.append(f"**Audit Date:** {roadmap['audit_date'][:10] if roadmap['audit_date'] != 'Unknown' else 'N/A'}")
    output.append(f"**Current SEO Score:** {roadmap['current_seo_score']}/100")
    output.append("")

    # Summary
    summary = roadmap['summary']
    output.append("## Summary")
    output.append("")
    output.append(f"| Metric | Value |")
    output.append(f"|--------|-------|")
    output.append(f"| Total Tasks | {summary['total_tasks']} |")
    output.append(f"| Total Hours | {summary['total_hours']} |")
    output.append(f"| Quick Wins | {summary['quick_wins_count']} ({summary['quick_wins_hours']}h) |")
    output.append("")

    # Quick Wins
    quick_wins = roadmap.get('quick_wins', [])
    if quick_wins:
        output.append("## Quick Wins")
        output.append("")
        output.append("*High impact tasks completable in ≤8 hours*")
        output.append("")
        for i, task in enumerate(quick_wins[:5], 1):
            output.append(f"### {i}. {task['name']}")
            output.append("")
            output.append(f"- **Category:** {task['category']}")
            output.append(f"- **Hours:** {task['hours']}")
            output.append(f"- **Impact:** {task['impact']}/10")
            output.append(f"- **Description:** {task['description']}")
            output.append("")

    # Quarterly Plan
    quarterly = roadmap.get('quarterly_plan', [])
    if quarterly:
        output.append("## Quarterly Plan")
        output.append("")
        for quarter in quarterly:
            output.append(f"### Q{quarter['quarter']}: {quarter['start_date']} - {quarter['end_date']}")
            output.append("")
            output.append(f"**Tasks:** {quarter['task_count']} | **Hours:** {quarter['total_hours']}")
            output.append(f"**Focus:** {', '.join(quarter['focus_areas'])}")
            output.append("")
            output.append("| Task | Category | Hours |")
            output.append("|------|----------|-------|")
            for task in quarter['tasks']:
                output.append(f"| {task['name']} | {task['category']} | {task['hours']} |")
            output.append("")

    # KPIs
    kpis = roadmap.get('kpis', {})
    if kpis.get('targets'):
        output.append("## KPI Targets")
        output.append("")
        output.append("| Quarter | SEO Score | Max Issues | Traffic Growth |")
        output.append("|---------|-----------|------------|----------------|")
        for target in kpis['targets']:
            output.append(f"| Q{target['quarter']} | {target['target_seo_score']} | {target['target_issues']} | {target['organic_traffic_growth']} |")
        output.append("")

    return "\n".join(output)


def format_csv_output(roadmap: Dict[str, Any]) -> str:
    """Format tasks as CSV."""
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'priority_rank', 'task_name', 'category', 'hours',
        'impact', 'effort', 'priority_score', 'description'
    ])

    for i, task in enumerate(roadmap.get('all_tasks', []), 1):
        writer.writerow([
            i,
            task['name'],
            task['category'],
            task['hours'],
            task['impact'],
            task['effort'],
            task['priority_score'],
            task['description']
        ])

    return output.getvalue()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate prioritized SEO roadmaps from audit data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate quarterly roadmap
  %(prog)s audit.json --quarters 4

  # Quick wins only
  %(prog)s audit.json --quick-wins

  # Markdown output
  %(prog)s audit.json --output md > roadmap.md

  # Custom hours per quarter
  %(prog)s audit.json --quarters 4 --hours-per-quarter 120

Input: JSON output from technical_seo_auditor.py
        """
    )

    parser.add_argument(
        'audit_file',
        help='Path to audit JSON file (from technical_seo_auditor.py)'
    )

    parser.add_argument(
        '--quarters', '-q',
        type=int,
        default=4,
        help='Number of quarters to plan (default: 4)'
    )

    parser.add_argument(
        '--hours-per-quarter',
        type=int,
        default=80,
        help='Hours budget per quarter (default: 80)'
    )

    parser.add_argument(
        '--quick-wins',
        action='store_true',
        help='Show only quick wins (high impact, low effort)'
    )

    parser.add_argument(
        '--output', '-o',
        choices=['text', 'json', 'md', 'csv'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '--file', '-f',
        help='Write output to file instead of stdout'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    args = parser.parse_args()

    try:
        # Initialize generator
        generator = SEORoadmapGenerator(verbose=args.verbose)

        # Load audit data
        audit_path = Path(args.audit_file)
        if not audit_path.exists():
            print(f"Error: Audit file not found: {args.audit_file}", file=sys.stderr)
            sys.exit(1)

        audit_data = generator.load_audit_data(audit_path)

        # Generate roadmap
        roadmap = generator.generate_roadmap(
            audit_data,
            quarters=args.quarters,
            quick_wins_only=args.quick_wins,
            hours_per_quarter=args.hours_per_quarter
        )

        # Format output
        if args.output == 'json':
            output = json.dumps(roadmap, indent=2, default=str)
        elif args.output == 'md':
            output = format_markdown_output(roadmap)
        elif args.output == 'csv':
            output = format_csv_output(roadmap)
        else:
            output = format_text_output(roadmap)

        # Write output
        if args.file:
            output_path = Path(args.file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Output saved to: {args.file}")
        else:
            print(output)

        sys.exit(0)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
