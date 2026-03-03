#!/usr/bin/env python3
"""
Technical SEO Auditor - Site-wide technical SEO audit and health assessment.

Analyzes site structure, crawlability, indexation signals, and common
technical SEO issues from HTML files or site exports.

Author: Claude Skills Team
Version: 1.0.0
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
import html.parser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

__version__ = "1.0.0"


class SimpleHTMLParser(html.parser.HTMLParser):
    """Simple HTML parser to extract SEO-relevant elements."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.meta_robots = ""
        self.canonical = ""
        self.headings = {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []}
        self.links = {'internal': [], 'external': []}
        self.images = []
        self.scripts = 0
        self.stylesheets = 0
        self.structured_data = []
        self.og_tags = {}
        self.twitter_tags = {}

        self._current_tag = None
        self._current_heading = None
        self._in_title = False
        self._in_script = False
        self._script_content = ""

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]):
        attrs_dict = dict(attrs)
        self._current_tag = tag

        if tag == 'title':
            self._in_title = True
        elif tag == 'script':
            self._in_script = True
            self._script_content = ""
            if 'src' in attrs_dict:
                self.scripts += 1
        elif tag == 'link':
            rel = attrs_dict.get('rel', '')
            if 'stylesheet' in rel:
                self.stylesheets += 1
            elif 'canonical' in rel:
                self.canonical = attrs_dict.get('href', '')
        elif tag == 'meta':
            name = attrs_dict.get('name', '').lower()
            prop = attrs_dict.get('property', '').lower()
            content = attrs_dict.get('content', '')

            if name == 'description':
                self.meta_description = content
            elif name == 'robots':
                self.meta_robots = content
            elif prop.startswith('og:'):
                self.og_tags[prop] = content
            elif name.startswith('twitter:'):
                self.twitter_tags[name] = content
        elif tag in self.headings:
            self._current_heading = tag
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                if href.startswith('http') and 'example.com' not in href:
                    self.links['external'].append(href)
                else:
                    self.links['internal'].append(href)
        elif tag == 'img':
            self.images.append({
                'src': attrs_dict.get('src', ''),
                'alt': attrs_dict.get('alt', ''),
                'has_alt': 'alt' in attrs_dict
            })

    def handle_endtag(self, tag: str):
        if tag == 'title':
            self._in_title = False
        elif tag == 'script':
            self._in_script = False
            # Check for structured data
            if 'application/ld+json' in self._script_content.lower() or '"@context"' in self._script_content:
                self.structured_data.append(self._script_content)
        elif tag in self.headings:
            self._current_heading = None

    def handle_data(self, data: str):
        if self._in_title:
            self.title += data.strip()
        elif self._current_heading:
            text = data.strip()
            if text:
                self.headings[self._current_heading].append(text)
        elif self._in_script:
            self._script_content += data


class TechnicalSEOAuditor:
    """Technical SEO site auditor."""

    # SEO best practices thresholds
    THRESHOLDS = {
        'title_length': (30, 60),
        'meta_description_length': (120, 160),
        'h1_count': (1, 1),
        'images_without_alt_pct': 0.1,  # Max 10% without alt
        'internal_links_min': 3,
        'external_links_max': 50,
        'heading_hierarchy_valid': True,
        'canonical_required': True,
        'robots_txt_required': True,
        'sitemap_required': True
    }

    # Issue severity levels
    SEVERITY = {
        'critical': 1,
        'high': 2,
        'medium': 3,
        'low': 4
    }

    def __init__(self, verbose: bool = False):
        """Initialize auditor."""
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("TechnicalSEOAuditor initialized")

    def audit_html_file(self, file_path: Path) -> Dict[str, Any]:
        """Audit a single HTML file."""
        logger.debug(f"Auditing file: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {'error': str(e), 'file': str(file_path)}

        parser = SimpleHTMLParser()
        try:
            parser.feed(content)
        except Exception as e:
            logger.warning(f"HTML parsing warning for {file_path}: {e}")

        # Calculate file metrics
        file_size = len(content.encode('utf-8'))

        return {
            'file': str(file_path),
            'file_size_bytes': file_size,
            'title': parser.title,
            'title_length': len(parser.title),
            'meta_description': parser.meta_description,
            'meta_description_length': len(parser.meta_description),
            'meta_robots': parser.meta_robots,
            'canonical': parser.canonical,
            'headings': {k: len(v) for k, v in parser.headings.items()},
            'heading_texts': parser.headings,
            'links': {
                'internal_count': len(parser.links['internal']),
                'external_count': len(parser.links['external']),
                'internal': parser.links['internal'][:20],  # Limit for output
                'external': parser.links['external'][:20]
            },
            'images': {
                'total': len(parser.images),
                'without_alt': sum(1 for img in parser.images if not img['has_alt']),
                'details': parser.images[:10]  # Limit for output
            },
            'resources': {
                'scripts': parser.scripts,
                'stylesheets': parser.stylesheets
            },
            'structured_data': len(parser.structured_data) > 0,
            'og_tags': bool(parser.og_tags),
            'twitter_cards': bool(parser.twitter_tags)
        }

    def check_robots_txt(self, site_path: Path) -> Dict[str, Any]:
        """Check robots.txt file."""
        robots_path = site_path / 'robots.txt'

        result = {
            'exists': False,
            'content': '',
            'issues': [],
            'directives': {
                'user_agents': [],
                'disallows': [],
                'allows': [],
                'sitemaps': []
            }
        }

        if not robots_path.exists():
            result['issues'].append({
                'severity': 'high',
                'message': 'robots.txt file not found'
            })
            return result

        result['exists'] = True

        try:
            with open(robots_path, 'r', encoding='utf-8') as f:
                content = f.read()
                result['content'] = content

            # Parse directives
            for line in content.split('\n'):
                line = line.strip().lower()
                if line.startswith('user-agent:'):
                    result['directives']['user_agents'].append(line.split(':', 1)[1].strip())
                elif line.startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    result['directives']['disallows'].append(path)
                    if path == '/':
                        result['issues'].append({
                            'severity': 'critical',
                            'message': 'robots.txt blocks all crawlers with Disallow: /'
                        })
                elif line.startswith('allow:'):
                    result['directives']['allows'].append(line.split(':', 1)[1].strip())
                elif line.startswith('sitemap:'):
                    result['directives']['sitemaps'].append(line.split(':', 1)[1].strip())

            if not result['directives']['sitemaps']:
                result['issues'].append({
                    'severity': 'medium',
                    'message': 'No sitemap reference in robots.txt'
                })

        except Exception as e:
            result['issues'].append({
                'severity': 'high',
                'message': f'Error parsing robots.txt: {e}'
            })

        return result

    def check_sitemap(self, site_path: Path) -> Dict[str, Any]:
        """Check sitemap.xml file."""
        sitemap_path = site_path / 'sitemap.xml'

        result = {
            'exists': False,
            'url_count': 0,
            'issues': [],
            'urls': []
        }

        if not sitemap_path.exists():
            result['issues'].append({
                'severity': 'high',
                'message': 'sitemap.xml file not found'
            })
            return result

        result['exists'] = True

        try:
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple XML parsing for URLs
            urls = re.findall(r'<loc>(.*?)</loc>', content, re.IGNORECASE)
            result['url_count'] = len(urls)
            result['urls'] = urls[:50]  # Limit for output

            if len(urls) == 0:
                result['issues'].append({
                    'severity': 'high',
                    'message': 'Sitemap contains no URLs'
                })
            elif len(urls) > 50000:
                result['issues'].append({
                    'severity': 'medium',
                    'message': f'Sitemap exceeds 50,000 URLs ({len(urls)}). Consider splitting.'
                })

        except Exception as e:
            result['issues'].append({
                'severity': 'high',
                'message': f'Error parsing sitemap.xml: {e}'
            })

        return result

    def analyze_page_issues(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a page for SEO issues."""
        issues = []

        # Title issues
        title_len = page_data['title_length']
        if title_len == 0:
            issues.append({
                'severity': 'critical',
                'category': 'meta',
                'message': 'Missing title tag',
                'recommendation': 'Add a unique, descriptive title tag (30-60 characters)'
            })
        elif title_len < self.THRESHOLDS['title_length'][0]:
            issues.append({
                'severity': 'medium',
                'category': 'meta',
                'message': f'Title too short ({title_len} characters)',
                'recommendation': 'Expand title to 30-60 characters with target keyword'
            })
        elif title_len > self.THRESHOLDS['title_length'][1]:
            issues.append({
                'severity': 'low',
                'category': 'meta',
                'message': f'Title may be truncated ({title_len} characters)',
                'recommendation': 'Consider shortening to under 60 characters'
            })

        # Meta description issues
        desc_len = page_data['meta_description_length']
        if desc_len == 0:
            issues.append({
                'severity': 'high',
                'category': 'meta',
                'message': 'Missing meta description',
                'recommendation': 'Add meta description (120-160 characters) with call-to-action'
            })
        elif desc_len < self.THRESHOLDS['meta_description_length'][0]:
            issues.append({
                'severity': 'low',
                'category': 'meta',
                'message': f'Meta description short ({desc_len} characters)',
                'recommendation': 'Expand to 120-160 characters for better SERP display'
            })
        elif desc_len > self.THRESHOLDS['meta_description_length'][1]:
            issues.append({
                'severity': 'low',
                'category': 'meta',
                'message': f'Meta description may be truncated ({desc_len} characters)',
                'recommendation': 'Consider shortening to under 160 characters'
            })

        # H1 issues
        h1_count = page_data['headings'].get('h1', 0)
        if h1_count == 0:
            issues.append({
                'severity': 'high',
                'category': 'content',
                'message': 'Missing H1 heading',
                'recommendation': 'Add exactly one H1 heading with primary keyword'
            })
        elif h1_count > 1:
            issues.append({
                'severity': 'medium',
                'category': 'content',
                'message': f'Multiple H1 headings ({h1_count})',
                'recommendation': 'Use only one H1 per page; convert others to H2'
            })

        # Heading hierarchy
        headings = page_data['headings']
        if headings.get('h3', 0) > 0 and headings.get('h2', 0) == 0:
            issues.append({
                'severity': 'medium',
                'category': 'content',
                'message': 'H3 used without H2 (broken hierarchy)',
                'recommendation': 'Maintain proper heading hierarchy: H1 > H2 > H3'
            })

        # Image alt text
        images = page_data['images']
        if images['total'] > 0:
            alt_missing_pct = images['without_alt'] / images['total']
            if alt_missing_pct > self.THRESHOLDS['images_without_alt_pct']:
                issues.append({
                    'severity': 'medium',
                    'category': 'accessibility',
                    'message': f'{images["without_alt"]} of {images["total"]} images missing alt text',
                    'recommendation': 'Add descriptive alt text to all images'
                })

        # Internal linking
        internal_links = page_data['links']['internal_count']
        if internal_links < self.THRESHOLDS['internal_links_min']:
            issues.append({
                'severity': 'low',
                'category': 'linking',
                'message': f'Few internal links ({internal_links})',
                'recommendation': 'Add more internal links to related content'
            })

        # Canonical tag
        if not page_data['canonical']:
            issues.append({
                'severity': 'medium',
                'category': 'indexation',
                'message': 'Missing canonical tag',
                'recommendation': 'Add self-referencing canonical tag'
            })

        # Structured data
        if not page_data['structured_data']:
            issues.append({
                'severity': 'low',
                'category': 'rich_results',
                'message': 'No structured data detected',
                'recommendation': 'Add JSON-LD structured data for rich results eligibility'
            })

        # Open Graph
        if not page_data['og_tags']:
            issues.append({
                'severity': 'low',
                'category': 'social',
                'message': 'Missing Open Graph tags',
                'recommendation': 'Add og:title, og:description, og:image for social sharing'
            })

        # Robots meta
        robots = page_data['meta_robots'].lower()
        if 'noindex' in robots:
            issues.append({
                'severity': 'high',
                'category': 'indexation',
                'message': 'Page has noindex directive',
                'recommendation': 'Remove noindex if page should be indexed'
            })

        return issues

    def calculate_seo_score(self, all_issues: List[Dict[str, Any]],
                           page_count: int,
                           robots_result: Dict[str, Any],
                           sitemap_result: Dict[str, Any]) -> int:
        """Calculate overall SEO score (0-100)."""
        score = 100

        # Deduct for robots.txt issues
        if not robots_result['exists']:
            score -= 10
        for issue in robots_result.get('issues', []):
            if issue['severity'] == 'critical':
                score -= 20
            elif issue['severity'] == 'high':
                score -= 10

        # Deduct for sitemap issues
        if not sitemap_result['exists']:
            score -= 10
        for issue in sitemap_result.get('issues', []):
            if issue['severity'] == 'high':
                score -= 5

        # Deduct for page issues (averaged)
        if page_count > 0:
            severity_weights = {
                'critical': 5,
                'high': 3,
                'medium': 1,
                'low': 0.5
            }

            total_deduction = 0
            for issue in all_issues:
                total_deduction += severity_weights.get(issue['severity'], 1)

            # Average deduction per page, capped
            avg_deduction = min(total_deduction / page_count, 50)
            score -= int(avg_deduction)

        return max(0, min(100, score))

    def audit_site(self, site_path: Path,
                  checks: Optional[List[str]] = None,
                  max_files: int = 100) -> Dict[str, Any]:
        """Audit entire site directory."""
        logger.info(f"Starting site audit: {site_path}")

        if not site_path.exists():
            raise FileNotFoundError(f"Path not found: {site_path}")

        results = {
            'audit_date': datetime.now().isoformat(),
            'site_path': str(site_path),
            'summary': {
                'pages_audited': 0,
                'total_issues': 0,
                'critical_issues': 0,
                'high_issues': 0,
                'medium_issues': 0,
                'low_issues': 0,
                'seo_score': 0
            },
            'robots_txt': {},
            'sitemap': {},
            'pages': [],
            'issues_by_category': defaultdict(list),
            'recommendations': []
        }

        # Check robots.txt
        if not checks or 'crawlability' in checks or 'all' in checks:
            results['robots_txt'] = self.check_robots_txt(site_path)

        # Check sitemap
        if not checks or 'crawlability' in checks or 'all' in checks:
            results['sitemap'] = self.check_sitemap(site_path)

        # Find and audit HTML files
        html_files = list(site_path.rglob('*.html'))[:max_files]
        html_files.extend(list(site_path.rglob('*.htm'))[:max_files - len(html_files)])

        logger.info(f"Found {len(html_files)} HTML files")

        all_issues = []

        for html_file in html_files:
            page_data = self.audit_html_file(html_file)
            if 'error' in page_data:
                continue

            page_issues = self.analyze_page_issues(page_data)
            all_issues.extend(page_issues)

            # Categorize issues
            for issue in page_issues:
                category = issue.get('category', 'other')
                results['issues_by_category'][category].append({
                    'file': page_data['file'],
                    **issue
                })

            results['pages'].append({
                'file': page_data['file'],
                'title': page_data['title'],
                'issues_count': len(page_issues),
                'issues': page_issues
            })

        results['summary']['pages_audited'] = len(results['pages'])
        results['summary']['total_issues'] = len(all_issues)

        # Count by severity
        for issue in all_issues:
            severity = issue['severity']
            key = f'{severity}_issues'
            if key in results['summary']:
                results['summary'][key] += 1

        # Add robots.txt and sitemap issues to counts
        for issue in results['robots_txt'].get('issues', []):
            results['summary']['total_issues'] += 1
            key = f'{issue["severity"]}_issues'
            if key in results['summary']:
                results['summary'][key] += 1

        for issue in results['sitemap'].get('issues', []):
            results['summary']['total_issues'] += 1
            key = f'{issue["severity"]}_issues'
            if key in results['summary']:
                results['summary'][key] += 1

        # Calculate SEO score
        results['summary']['seo_score'] = self.calculate_seo_score(
            all_issues,
            len(results['pages']),
            results['robots_txt'],
            results['sitemap']
        )

        # Convert defaultdict to dict
        results['issues_by_category'] = dict(results['issues_by_category'])

        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []

        summary = results['summary']

        # Critical issues first
        if summary['critical_issues'] > 0:
            recommendations.append(f"URGENT: Fix {summary['critical_issues']} critical issues immediately")

        # Robots.txt
        if not results['robots_txt'].get('exists'):
            recommendations.append("Create robots.txt file with sitemap reference")

        # Sitemap
        if not results['sitemap'].get('exists'):
            recommendations.append("Create XML sitemap and submit to search engines")

        # High-volume issues by category
        categories = results.get('issues_by_category', {})
        if len(categories.get('meta', [])) > summary['pages_audited'] * 0.3:
            recommendations.append("Many pages have meta tag issues - prioritize title and description optimization")

        if len(categories.get('content', [])) > summary['pages_audited'] * 0.3:
            recommendations.append("Content structure issues common - review heading hierarchy site-wide")

        if len(categories.get('accessibility', [])) > 0:
            recommendations.append("Add missing alt text to images for accessibility and SEO")

        if len(categories.get('indexation', [])) > 0:
            recommendations.append("Review indexation directives - ensure important pages are indexable")

        # Score-based recommendations
        score = summary['seo_score']
        if score < 50:
            recommendations.append("Low SEO score - comprehensive technical SEO overhaul needed")
        elif score < 70:
            recommendations.append("Moderate SEO score - address high-priority issues for quick wins")
        elif score < 90:
            recommendations.append("Good SEO foundation - focus on optimization refinements")

        return recommendations


def format_text_output(results: Dict[str, Any]) -> str:
    """Format results as human-readable text."""
    output = []

    output.append("=" * 60)
    output.append("TECHNICAL SEO AUDIT REPORT")
    output.append("=" * 60)
    output.append("")

    # Summary
    summary = results['summary']
    output.append("SUMMARY")
    output.append("-" * 40)
    output.append(f"SEO Score: {summary['seo_score']}/100")
    output.append(f"Pages Audited: {summary['pages_audited']}")
    output.append(f"Total Issues: {summary['total_issues']}")
    output.append(f"  Critical: {summary['critical_issues']}")
    output.append(f"  High: {summary['high_issues']}")
    output.append(f"  Medium: {summary['medium_issues']}")
    output.append(f"  Low: {summary['low_issues']}")
    output.append(f"Audit Date: {results['audit_date'][:10]}")
    output.append("")

    # Robots.txt
    robots = results.get('robots_txt', {})
    output.append("ROBOTS.TXT")
    output.append("-" * 40)
    output.append(f"Status: {'Found' if robots.get('exists') else 'NOT FOUND'}")
    if robots.get('directives', {}).get('sitemaps'):
        output.append(f"Sitemaps: {', '.join(robots['directives']['sitemaps'])}")
    for issue in robots.get('issues', []):
        output.append(f"  [{issue['severity'].upper()}] {issue['message']}")
    output.append("")

    # Sitemap
    sitemap = results.get('sitemap', {})
    output.append("SITEMAP.XML")
    output.append("-" * 40)
    output.append(f"Status: {'Found' if sitemap.get('exists') else 'NOT FOUND'}")
    if sitemap.get('url_count'):
        output.append(f"URLs: {sitemap['url_count']}")
    for issue in sitemap.get('issues', []):
        output.append(f"  [{issue['severity'].upper()}] {issue['message']}")
    output.append("")

    # Issues by Category
    categories = results.get('issues_by_category', {})
    if categories:
        output.append("ISSUES BY CATEGORY")
        output.append("-" * 40)
        for category, issues in categories.items():
            output.append(f"\n{category.upper()} ({len(issues)} issues)")
            for issue in issues[:5]:
                output.append(f"  [{issue['severity'].upper()}] {issue['message']}")
                output.append(f"    File: {issue.get('file', 'N/A')}")
        output.append("")

    # Recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        output.append("RECOMMENDATIONS")
        output.append("-" * 40)
        for i, rec in enumerate(recommendations, 1):
            output.append(f"{i}. {rec}")
        output.append("")

    return "\n".join(output)


def format_csv_output(results: Dict[str, Any]) -> str:
    """Format issues as CSV."""
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(['file', 'severity', 'category', 'message', 'recommendation'])

    # Page issues
    for page in results.get('pages', []):
        for issue in page.get('issues', []):
            writer.writerow([
                page['file'],
                issue['severity'],
                issue['category'],
                issue['message'],
                issue.get('recommendation', '')
            ])

    # Robots.txt issues
    for issue in results.get('robots_txt', {}).get('issues', []):
        writer.writerow([
            'robots.txt',
            issue['severity'],
            'crawlability',
            issue['message'],
            ''
        ])

    # Sitemap issues
    for issue in results.get('sitemap', {}).get('issues', []):
        writer.writerow([
            'sitemap.xml',
            issue['severity'],
            'crawlability',
            issue['message'],
            ''
        ])

    return output.getvalue()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Technical SEO site audit and health assessment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Audit site directory
  %(prog)s ./site-export/

  # Specific checks only
  %(prog)s ./site-export/ --checks crawlability,structure

  # JSON output
  %(prog)s ./site-export/ --output json > audit.json

  # Limit files
  %(prog)s ./site-export/ --max-files 50

Available checks:
  crawlability  - robots.txt, sitemap.xml
  structure     - headings, internal links
  meta          - title, description, canonical
  all           - run all checks (default)
        """
    )

    parser.add_argument(
        'path',
        help='Path to site directory or HTML files'
    )

    parser.add_argument(
        '--checks', '-c',
        help='Comma-separated list of checks to run (default: all)'
    )

    parser.add_argument(
        '--max-files',
        type=int,
        default=100,
        help='Maximum HTML files to audit (default: 100)'
    )

    parser.add_argument(
        '--output', '-o',
        choices=['text', 'json', 'csv'],
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
        # Initialize auditor
        auditor = TechnicalSEOAuditor(verbose=args.verbose)

        # Parse checks
        checks = None
        if args.checks:
            checks = [c.strip().lower() for c in args.checks.split(',')]

        # Run audit
        site_path = Path(args.path)
        results = auditor.audit_site(
            site_path,
            checks=checks,
            max_files=args.max_files
        )

        # Format output
        if args.output == 'json':
            output = json.dumps(results, indent=2, default=str)
        elif args.output == 'csv':
            output = format_csv_output(results)
        else:
            output = format_text_output(results)

        # Write output
        if args.file:
            output_path = Path(args.file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Output saved to: {args.file}")
        else:
            print(output)

        # Exit code based on score
        score = results['summary']['seo_score']
        if score < 50:
            sys.exit(2)  # Critical issues
        elif score < 70:
            sys.exit(1)  # Needs attention
        else:
            sys.exit(0)  # OK

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
