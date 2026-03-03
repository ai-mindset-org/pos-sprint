#!/usr/bin/env python3
"""
Keyword Researcher - Keyword research, clustering, and content mapping tool.

Analyzes keyword lists for search volume grouping, competition assessment,
topic clusters, and keyword mapping to content pillars.

Author: Claude Skills Team
Version: 1.0.0
"""

import argparse
import csv
import json
import logging
import re
import sys
from collections import defaultdict
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

__version__ = "1.0.0"


class KeywordResearcher:
    """Keyword research and clustering tool for SEO strategy."""

    # Search intent patterns
    INTENT_PATTERNS = {
        'informational': [
            r'\bwhat\b', r'\bhow\b', r'\bwhy\b', r'\bwhen\b', r'\bwhere\b',
            r'\bguide\b', r'\btutorial\b', r'\bexplain\b', r'\blearn\b',
            r'\bdefinition\b', r'\bmeaning\b', r'\bexample\b', r'\btips\b'
        ],
        'navigational': [
            r'\blogin\b', r'\bsign in\b', r'\bwebsite\b', r'\bofficial\b',
            r'\bcontact\b', r'\bsupport\b', r'\bdownload\b', r'\bapp\b'
        ],
        'transactional': [
            r'\bbuy\b', r'\bpurchase\b', r'\border\b', r'\bprice\b',
            r'\bcheap\b', r'\bdiscount\b', r'\bdeal\b', r'\bcoupon\b',
            r'\bsale\b', r'\bshop\b', r'\bstore\b'
        ],
        'commercial': [
            r'\bbest\b', r'\btop\b', r'\breview\b', r'\bcompar\b',
            r'\bvs\b', r'\balternative\b', r'\brating\b', r'\brecommend\b'
        ]
    }

    # Common stop words for clustering
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall',
        'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
        'we', 'they', 'my', 'your', 'his', 'her', 'our', 'their', 'what', 'how'
    }

    def __init__(self, verbose: bool = False):
        """Initialize keyword researcher."""
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("KeywordResearcher initialized")

    def load_keywords(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load keywords from CSV file.

        Expected columns: keyword, volume (optional), competition (optional), cpc (optional)
        """
        keywords = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Try to detect if file has headers
                sample = f.read(1024)
                f.seek(0)

                has_header = csv.Sniffer().has_header(sample)
                reader = csv.DictReader(f) if has_header else None

                if not reader:
                    # Simple list of keywords, one per line
                    f.seek(0)
                    for line in f:
                        keyword = line.strip()
                        if keyword:
                            keywords.append({
                                'keyword': keyword,
                                'volume': 0,
                                'competition': 0.5,
                                'cpc': 0.0
                            })
                else:
                    for row in reader:
                        # Normalize column names
                        keyword_data = {
                            'keyword': row.get('keyword', row.get('Keyword', '')).strip(),
                            'volume': int(row.get('volume', row.get('Volume', row.get('search_volume', 0))) or 0),
                            'competition': float(row.get('competition', row.get('Competition', 0.5)) or 0.5),
                            'cpc': float(row.get('cpc', row.get('CPC', 0.0)) or 0.0)
                        }
                        if keyword_data['keyword']:
                            keywords.append(keyword_data)

            logger.info(f"Loaded {len(keywords)} keywords from {file_path}")
            return keywords

        except Exception as e:
            logger.error(f"Error loading keywords: {e}")
            raise

    def classify_intent(self, keyword: str) -> str:
        """Classify search intent for a keyword."""
        keyword_lower = keyword.lower()

        intent_scores = defaultdict(int)
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, keyword_lower):
                    intent_scores[intent] += 1

        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return 'informational'  # Default intent

    def extract_core_terms(self, keyword: str) -> Set[str]:
        """Extract core terms from a keyword for clustering."""
        words = re.findall(r'\b[a-z]+\b', keyword.lower())
        return {w for w in words if w not in self.STOP_WORDS and len(w) > 2}

    def calculate_similarity(self, terms1: Set[str], terms2: Set[str]) -> float:
        """Calculate Jaccard similarity between term sets."""
        if not terms1 or not terms2:
            return 0.0
        intersection = len(terms1 & terms2)
        union = len(terms1 | terms2)
        return intersection / union if union > 0 else 0.0

    def cluster_keywords(self, keywords: List[Dict[str, Any]],
                        min_cluster_size: int = 2,
                        similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Cluster keywords by semantic similarity.

        Uses a simple greedy clustering algorithm based on term overlap.
        """
        logger.debug(f"Clustering {len(keywords)} keywords")

        # Extract core terms for each keyword
        keyword_terms = []
        for kw in keywords:
            terms = self.extract_core_terms(kw['keyword'])
            keyword_terms.append({
                **kw,
                'terms': terms,
                'intent': self.classify_intent(kw['keyword']),
                'cluster_id': None
            })

        clusters = []
        cluster_id = 0

        # Greedy clustering
        for i, kw1 in enumerate(keyword_terms):
            if kw1['cluster_id'] is not None:
                continue

            # Start new cluster
            cluster_keywords = [kw1]
            kw1['cluster_id'] = cluster_id
            cluster_terms = kw1['terms'].copy()

            # Find similar keywords
            for j, kw2 in enumerate(keyword_terms):
                if i == j or kw2['cluster_id'] is not None:
                    continue

                similarity = self.calculate_similarity(cluster_terms, kw2['terms'])
                if similarity >= similarity_threshold:
                    cluster_keywords.append(kw2)
                    kw2['cluster_id'] = cluster_id
                    cluster_terms |= kw2['terms']

            # Only keep clusters that meet minimum size
            if len(cluster_keywords) >= min_cluster_size:
                # Identify pillar keyword (highest volume)
                pillar = max(cluster_keywords, key=lambda x: x['volume'])

                cluster = {
                    'cluster_id': cluster_id,
                    'name': self._generate_cluster_name(cluster_terms),
                    'pillar_keyword': pillar['keyword'],
                    'pillar_volume': pillar['volume'],
                    'total_volume': sum(kw['volume'] for kw in cluster_keywords),
                    'keyword_count': len(cluster_keywords),
                    'avg_competition': sum(kw['competition'] for kw in cluster_keywords) / len(cluster_keywords),
                    'primary_intent': self._get_primary_intent(cluster_keywords),
                    'core_terms': list(cluster_terms)[:10],
                    'keywords': [
                        {
                            'keyword': kw['keyword'],
                            'volume': kw['volume'],
                            'competition': kw['competition'],
                            'intent': kw['intent']
                        }
                        for kw in sorted(cluster_keywords, key=lambda x: x['volume'], reverse=True)
                    ]
                }
                clusters.append(cluster)
                cluster_id += 1
            else:
                # Reset cluster IDs for unclustered keywords
                for kw in cluster_keywords:
                    kw['cluster_id'] = None

        # Handle unclustered keywords
        unclustered = [kw for kw in keyword_terms if kw['cluster_id'] is None]
        if unclustered:
            clusters.append({
                'cluster_id': -1,
                'name': 'Unclustered',
                'pillar_keyword': None,
                'pillar_volume': 0,
                'total_volume': sum(kw['volume'] for kw in unclustered),
                'keyword_count': len(unclustered),
                'avg_competition': sum(kw['competition'] for kw in unclustered) / len(unclustered) if unclustered else 0,
                'primary_intent': 'mixed',
                'core_terms': [],
                'keywords': [
                    {
                        'keyword': kw['keyword'],
                        'volume': kw['volume'],
                        'competition': kw['competition'],
                        'intent': kw['intent']
                    }
                    for kw in sorted(unclustered, key=lambda x: x['volume'], reverse=True)
                ]
            })

        logger.info(f"Created {len(clusters)} clusters")
        return sorted(clusters, key=lambda x: x['total_volume'], reverse=True)

    def _generate_cluster_name(self, terms: Set[str]) -> str:
        """Generate a descriptive name for a cluster."""
        if not terms:
            return "General"
        # Use most common terms (would need frequency in real implementation)
        sorted_terms = sorted(terms, key=len, reverse=True)[:3]
        return ' '.join(sorted_terms).title()

    def _get_primary_intent(self, keywords: List[Dict[str, Any]]) -> str:
        """Determine primary intent for a cluster."""
        intent_counts = defaultdict(int)
        for kw in keywords:
            intent_counts[kw['intent']] += 1
        return max(intent_counts, key=intent_counts.get) if intent_counts else 'informational'

    def calculate_priority_score(self, keyword_data: Dict[str, Any]) -> float:
        """Calculate priority score for a keyword or cluster.

        Score = (Volume Score * 0.4) + (Competition Score * 0.3) + (Intent Score * 0.3)
        """
        volume = keyword_data.get('total_volume', keyword_data.get('volume', 0))
        competition = keyword_data.get('avg_competition', keyword_data.get('competition', 0.5))
        intent = keyword_data.get('primary_intent', keyword_data.get('intent', 'informational'))

        # Volume score (logarithmic scale)
        if volume > 10000:
            volume_score = 100
        elif volume > 5000:
            volume_score = 80
        elif volume > 1000:
            volume_score = 60
        elif volume > 500:
            volume_score = 40
        elif volume > 100:
            volume_score = 20
        else:
            volume_score = 10

        # Competition score (inverse - lower competition = higher score)
        competition_score = (1 - competition) * 100

        # Intent score (transactional/commercial = higher business value)
        intent_scores = {
            'transactional': 100,
            'commercial': 80,
            'informational': 50,
            'navigational': 30,
            'mixed': 50
        }
        intent_score = intent_scores.get(intent, 50)

        # Weighted calculation
        priority = (volume_score * 0.4) + (competition_score * 0.3) + (intent_score * 0.3)
        return round(priority, 1)

    def score_clusters(self, clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add priority scores to clusters."""
        for cluster in clusters:
            cluster['priority_score'] = self.calculate_priority_score(cluster)

            # Score individual keywords too
            for kw in cluster['keywords']:
                kw['priority_score'] = self.calculate_priority_score(kw)

        return sorted(clusters, key=lambda x: x['priority_score'], reverse=True)

    def identify_content_gaps(self, clusters: List[Dict[str, Any]],
                             existing_content: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Identify content gaps based on clusters and existing content."""
        gaps = []
        existing = set(c.lower() for c in (existing_content or []))

        for cluster in clusters:
            if cluster['cluster_id'] == -1:
                continue

            # Check if pillar content exists
            has_pillar = any(
                cluster['pillar_keyword'].lower() in content
                for content in existing
            ) if existing else False

            # Check coverage of cluster keywords
            covered_keywords = 0
            for kw in cluster['keywords']:
                if any(kw['keyword'].lower() in content for content in existing):
                    covered_keywords += 1

            coverage = covered_keywords / cluster['keyword_count'] if cluster['keyword_count'] > 0 else 0

            gap = {
                'cluster_name': cluster['name'],
                'pillar_keyword': cluster['pillar_keyword'],
                'has_pillar_content': has_pillar,
                'keyword_coverage': round(coverage * 100, 1),
                'total_opportunity_volume': cluster['total_volume'],
                'priority_score': cluster['priority_score'],
                'recommendation': self._get_gap_recommendation(has_pillar, coverage),
                'suggested_content_types': self._suggest_content_types(cluster['primary_intent'])
            }
            gaps.append(gap)

        return sorted(gaps, key=lambda x: x['priority_score'], reverse=True)

    def _get_gap_recommendation(self, has_pillar: bool, coverage: float) -> str:
        """Generate recommendation based on gap analysis."""
        if not has_pillar:
            return "Create pillar content for this topic cluster"
        elif coverage < 0.3:
            return "Expand cluster with supporting content pieces"
        elif coverage < 0.7:
            return "Fill remaining content gaps in cluster"
        else:
            return "Optimize existing content for better rankings"

    def _suggest_content_types(self, intent: str) -> List[str]:
        """Suggest content types based on search intent."""
        suggestions = {
            'informational': ['How-to guide', 'Tutorial', 'FAQ page', 'Glossary'],
            'commercial': ['Comparison article', 'Review roundup', 'Buying guide', 'Best-of list'],
            'transactional': ['Product page', 'Landing page', 'Pricing page', 'Sales page'],
            'navigational': ['About page', 'Contact page', 'Documentation', 'Help center'],
            'mixed': ['Blog post', 'Resource page', 'Case study']
        }
        return suggestions.get(intent, suggestions['mixed'])

    def analyze(self, keywords: List[Dict[str, Any]],
                cluster: bool = True,
                score: bool = True,
                min_cluster_size: int = 2,
                existing_content: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run full keyword analysis."""
        logger.info("Starting keyword analysis")

        results = {
            'summary': {
                'total_keywords': len(keywords),
                'total_volume': sum(kw['volume'] for kw in keywords),
                'avg_competition': sum(kw['competition'] for kw in keywords) / len(keywords) if keywords else 0,
                'analysis_date': datetime.now().isoformat()
            },
            'intent_distribution': defaultdict(int),
            'clusters': [],
            'content_gaps': [],
            'recommendations': []
        }

        # Classify intents
        for kw in keywords:
            intent = self.classify_intent(kw['keyword'])
            results['intent_distribution'][intent] += 1
        results['intent_distribution'] = dict(results['intent_distribution'])

        # Cluster keywords
        if cluster:
            clusters = self.cluster_keywords(keywords, min_cluster_size=min_cluster_size)

            if score:
                clusters = self.score_clusters(clusters)

            results['clusters'] = clusters
            results['summary']['cluster_count'] = len([c for c in clusters if c['cluster_id'] != -1])

            # Content gap analysis
            if existing_content is not None:
                results['content_gaps'] = self.identify_content_gaps(clusters, existing_content)

        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []

        # Volume recommendations
        total_volume = results['summary']['total_volume']
        if total_volume > 50000:
            recommendations.append("High-volume keyword portfolio - focus on competitive differentiation")
        elif total_volume < 5000:
            recommendations.append("Consider expanding keyword research for more opportunities")

        # Cluster recommendations
        cluster_count = results['summary'].get('cluster_count', 0)
        if cluster_count > 10:
            recommendations.append(f"Large topic coverage ({cluster_count} clusters) - prioritize top 3-5 for initial focus")
        elif cluster_count < 3:
            recommendations.append("Limited topic clusters - expand keyword research to find more topic areas")

        # Intent recommendations
        intent_dist = results.get('intent_distribution', {})
        if intent_dist.get('transactional', 0) < intent_dist.get('informational', 0) * 0.2:
            recommendations.append("Low transactional keywords - add more bottom-of-funnel terms")

        # Competition recommendations
        avg_competition = results['summary']['avg_competition']
        if avg_competition > 0.7:
            recommendations.append("High competition portfolio - identify long-tail opportunities")
        elif avg_competition < 0.3:
            recommendations.append("Low competition keywords - potential quick wins available")

        return recommendations


def format_text_output(results: Dict[str, Any]) -> str:
    """Format results as human-readable text."""
    output = []

    output.append("=" * 60)
    output.append("KEYWORD RESEARCH ANALYSIS")
    output.append("=" * 60)
    output.append("")

    # Summary
    summary = results['summary']
    output.append("SUMMARY")
    output.append("-" * 40)
    output.append(f"Total Keywords: {summary['total_keywords']}")
    output.append(f"Total Search Volume: {summary['total_volume']:,}")
    output.append(f"Average Competition: {summary['avg_competition']:.2f}")
    output.append(f"Topic Clusters: {summary.get('cluster_count', 'N/A')}")
    output.append(f"Analysis Date: {summary['analysis_date'][:10]}")
    output.append("")

    # Intent Distribution
    output.append("SEARCH INTENT DISTRIBUTION")
    output.append("-" * 40)
    for intent, count in results['intent_distribution'].items():
        pct = count / summary['total_keywords'] * 100 if summary['total_keywords'] > 0 else 0
        output.append(f"  {intent.title()}: {count} ({pct:.1f}%)")
    output.append("")

    # Top Clusters
    clusters = results.get('clusters', [])
    if clusters:
        output.append("TOP TOPIC CLUSTERS")
        output.append("-" * 40)
        for i, cluster in enumerate(clusters[:10], 1):
            if cluster['cluster_id'] == -1:
                continue
            output.append(f"\n{i}. {cluster['name']}")
            output.append(f"   Pillar: {cluster['pillar_keyword']}")
            output.append(f"   Keywords: {cluster['keyword_count']} | Volume: {cluster['total_volume']:,}")
            output.append(f"   Intent: {cluster['primary_intent']} | Priority: {cluster.get('priority_score', 'N/A')}")
            if cluster['keywords'][:3]:
                output.append("   Top Keywords:")
                for kw in cluster['keywords'][:3]:
                    output.append(f"     - {kw['keyword']} (vol: {kw['volume']})")
        output.append("")

    # Content Gaps
    gaps = results.get('content_gaps', [])
    if gaps:
        output.append("CONTENT GAP ANALYSIS")
        output.append("-" * 40)
        for gap in gaps[:5]:
            output.append(f"\n  {gap['cluster_name']}")
            output.append(f"    Coverage: {gap['keyword_coverage']}%")
            output.append(f"    Recommendation: {gap['recommendation']}")
        output.append("")

    # Recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        output.append("STRATEGIC RECOMMENDATIONS")
        output.append("-" * 40)
        for rec in recommendations:
            output.append(f"  * {rec}")
        output.append("")

    return "\n".join(output)


def format_csv_output(results: Dict[str, Any]) -> str:
    """Format cluster results as CSV."""
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'cluster_id', 'cluster_name', 'pillar_keyword', 'keyword_count',
        'total_volume', 'avg_competition', 'primary_intent', 'priority_score'
    ])

    for cluster in results.get('clusters', []):
        writer.writerow([
            cluster['cluster_id'],
            cluster['name'],
            cluster['pillar_keyword'] or '',
            cluster['keyword_count'],
            cluster['total_volume'],
            f"{cluster['avg_competition']:.2f}",
            cluster['primary_intent'],
            cluster.get('priority_score', '')
        ])

    return output.getvalue()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Keyword research, clustering, and content mapping tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic clustering
  %(prog)s keywords.csv --cluster

  # With priority scoring
  %(prog)s keywords.csv --cluster --score --output json

  # Content gap analysis
  %(prog)s keywords.csv --cluster --content-file content-inventory.txt

  # Minimum cluster size
  %(prog)s keywords.csv --cluster --min-cluster-size 5

  # CSV output
  %(prog)s keywords.csv --cluster --output csv > clusters.csv

Input CSV format:
  keyword,volume,competition,cpc
  "python tutorial",5000,0.3,1.50
  "learn python",8000,0.4,2.00

  Or simple list (one keyword per line)
        """
    )

    parser.add_argument(
        'input',
        help='Input CSV file with keywords'
    )

    parser.add_argument(
        '--cluster', '-c',
        action='store_true',
        help='Enable keyword clustering'
    )

    parser.add_argument(
        '--score', '-s',
        action='store_true',
        help='Calculate priority scores'
    )

    parser.add_argument(
        '--min-cluster-size',
        type=int,
        default=2,
        help='Minimum keywords per cluster (default: 2)'
    )

    parser.add_argument(
        '--content-file',
        help='File with existing content titles (one per line) for gap analysis'
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
        # Initialize researcher
        researcher = KeywordResearcher(verbose=args.verbose)

        # Load keywords
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)

        keywords = researcher.load_keywords(input_path)

        if not keywords:
            print("Error: No keywords found in input file", file=sys.stderr)
            sys.exit(1)

        # Load existing content if provided
        existing_content = None
        if args.content_file:
            content_path = Path(args.content_file)
            if content_path.exists():
                with open(content_path, 'r', encoding='utf-8') as f:
                    existing_content = [line.strip() for line in f if line.strip()]
                logger.info(f"Loaded {len(existing_content)} existing content items")

        # Run analysis
        results = researcher.analyze(
            keywords,
            cluster=args.cluster,
            score=args.score,
            min_cluster_size=args.min_cluster_size,
            existing_content=existing_content
        )

        # Format output
        if args.output == 'json':
            output = json.dumps(results, indent=2)
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
