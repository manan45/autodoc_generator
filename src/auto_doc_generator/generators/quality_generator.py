#!/usr/bin/env python3
"""
Quality Generator - 🔬 Quality Scoring Pipeline Generator

Generates comprehensive quality reports, visualizations, and documentation
using the quality analysis results from QualityAnalyzer.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from datetime import datetime
from dataclasses import asdict


class QualityGenerator:
    """Generates quality reports and visualizations from quality analysis."""
    
    def __init__(self, template_dir: str = "html_templates", output_dir: str = "docs", config: Dict[str, Any] = None):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_quality_report(self, quality_analysis: Dict[str, Any], 
                              code_analysis: Dict[str, Any] = None,
                              enhanced_analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Generate comprehensive quality report.
        
        Args:
            quality_analysis: Results from QualityAnalyzer
            code_analysis: Original code analysis results
            enhanced_analysis: Enhanced analysis with AI insights
            
        Returns:
            Dictionary of generated content
        """
        self.logger.info("🔬 Generating quality scoring report...")
        
        report_content = {}
        
        # Generate main quality page
        report_content['quality.html'] = self._generate_quality_page(quality_analysis, code_analysis)
        
        # Generate quality dashboard data
        report_content['quality_data.json'] = self._generate_quality_data(quality_analysis)
        
        # Generate quality metrics visualization data
        report_content['quality_metrics.json'] = self._generate_metrics_visualization_data(quality_analysis)
        
        # Generate module-specific quality reports
        module_reports = self._generate_module_quality_reports(quality_analysis)
        report_content.update(module_reports)
        
        # Generate quality trends data (if available)
        if quality_analysis.get('trends'):
            report_content['quality_trends.json'] = self._generate_trends_data(quality_analysis)
        
        self.logger.info(f"🔬 Quality report generated with {len(report_content)} components")
        return report_content
    
    def _generate_quality_page(self, quality_analysis: Dict[str, Any], 
                             code_analysis: Dict[str, Any] = None) -> str:
        """Generate the main quality scoring HTML page."""
        
        overview = quality_analysis.get('overview', {})
        distribution = quality_analysis.get('quality_distribution', {})
        recommendations = quality_analysis.get('recommendations', [])
        metadata = quality_analysis.get('metadata', {})
        
        # Generate quality level distribution chart data
        quality_ranges = distribution.get('quality_ranges', {})
        chart_data = {
            'labels': list(quality_ranges.keys()),
            'data': list(quality_ranges.values()),
            'colors': {
                'excellent': '#10B981',
                'good': '#3B82F6', 
                'fair': '#F59E0B',
                'poor': '#EF4444',
                'critical': '#7C2D12'
            }
        }
        
        # Generate metrics radar chart data
        metric_averages = distribution.get('metric_averages', {})
        radar_data = {
            'labels': list(metric_averages.keys()),
            'datasets': [{
                'label': 'Average Scores',
                'data': [metric_averages[metric]['average'] for metric in metric_averages.keys()],
                'backgroundColor': 'rgba(59, 130, 246, 0.2)',
                'borderColor': 'rgb(59, 130, 246)',
                'borderWidth': 2
            }]
        }
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔬 Quality Scoring Pipeline - Code Quality Analysis</title>
    <link rel="stylesheet" href="assets/css/modern-styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        .quality-dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .quality-card {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #3B82F6;
        }}
        
        .quality-score {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #1F2937;
            margin-bottom: 0.5rem;
        }}
        
        .quality-level {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
        }}
        
        .level-excellent {{ background-color: #D1FAE5; color: #065F46; }}
        .level-good {{ background-color: #DBEAFE; color: #1E40AF; }}
        .level-fair {{ background-color: #FEF3C7; color: #92400E; }}
        .level-poor {{ background-color: #FEE2E2; color: #991B1B; }}
        .level-critical {{ background-color: #FEE2E2; color: #7C2D12; }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        
        .metric-card {{
            background: #F9FAFB;
            padding: 1rem;
            border-radius: 6px;
            border: 1px solid #E5E7EB;
        }}
        
        .metric-score {{
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.25rem;
        }}
        
        .metric-name {{
            color: #6B7280;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 2rem 0;
        }}
        
        .recommendations-list {{
            background: #F0F9FF;
            border: 1px solid #0EA5E9;
            border-radius: 6px;
            padding: 1.5rem;
            margin: 2rem 0;
        }}
        
        .recommendation-item {{
            margin-bottom: 0.75rem;
            padding-left: 1.5rem;
            position: relative;
        }}
        
        .recommendation-item::before {{
            content: "💡";
            position: absolute;
            left: 0;
        }}
        
        .module-quality-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            background: white;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .module-quality-table th,
        .module-quality-table td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid #E5E7EB;
        }}
        
        .module-quality-table th {{
            background-color: #F9FAFB;
            font-weight: 600;
            color: #374151;
        }}
        
        .quality-progress {{
            width: 100%;
            height: 8px;
            background-color: #E5E7EB;
            border-radius: 4px;
            overflow: hidden;
            margin: 0.25rem 0;
        }}
        
        .quality-progress-bar {{
            height: 100%;
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="page-header">
            <h1>🔬 Quality Scoring Pipeline</h1>
            <p>Comprehensive code quality analysis using repository analysis, vector embeddings, and LLM insights</p>
            <div class="analysis-meta">
                <span>📊 {overview.get('total_modules', 0)} modules analyzed</span>
                <span>⏰ {metadata.get('analysis_timestamp', 'Unknown')}</span>
                <span>🧠 Embeddings: {'✅ Enabled' if metadata.get('embeddings_enabled') else '❌ Disabled'}</span>
            </div>
        </header>

        <!-- Quality Dashboard -->
        <section class="quality-dashboard">
            <div class="quality-card">
                <div class="quality-score">{overview.get('average_quality_score', 0):.2f}</div>
                <h3>Average Quality Score</h3>
                <p>Overall quality across all modules</p>
            </div>
            
            <div class="quality-card">
                <div class="quality-score">{overview.get('median_quality_score', 0):.2f}</div>
                <h3>Median Quality Score</h3>
                <p>Middle point of quality distribution</p>
            </div>
            
            <div class="quality-card">
                <div class="quality-score">{overview.get('quality_std_dev', 0):.3f}</div>
                <h3>Quality Consistency</h3>
                <p>Standard deviation of scores</p>
            </div>
            
            <div class="quality-card">
                <div class="quality-score">{len(overview.get('top_quality_modules', []))}</div>
                <h3>Top Quality Modules</h3>
                <p>Highest scoring modules</p>
            </div>
        </section>

        <!-- Quality Level Distribution -->
        <section>
            <h2>📊 Quality Level Distribution</h2>
            <div class="chart-container">
                <canvas id="qualityDistributionChart"></canvas>
            </div>
        </section>

        <!-- Quality Metrics Overview -->
        <section>
            <h2>📈 Quality Metrics Overview</h2>
            <div class="chart-container">
                <canvas id="metricsRadarChart"></canvas>
            </div>
            
            <div class="metrics-grid">
                {self._generate_metrics_cards(metric_averages)}
            </div>
        </section>

        <!-- Top and Bottom Performing Modules -->
        <section>
            <h2>🏆 Module Performance</h2>
            
            <h3>🥇 Top Quality Modules</h3>
            <div class="module-list">
                {self._generate_module_list(overview.get('top_quality_modules', []), 'top')}
            </div>
            
            <h3>⚠️ Modules Needing Improvement</h3>
            <div class="module-list">
                {self._generate_module_list(overview.get('lowest_quality_modules', []), 'bottom')}
            </div>
        </section>

        <!-- Detailed Module Quality Table -->
        <section>
            <h2>📋 Detailed Module Analysis</h2>
            {self._generate_module_quality_table(quality_analysis.get('module_assessments', {}))}
        </section>

        <!-- Global Recommendations -->
        <section>
            <h2>💡 Global Recommendations</h2>
            <div class="recommendations-list">
                <h3>Priority Improvements</h3>
                {self._generate_recommendations_html(recommendations)}
            </div>
        </section>

        <!-- Quality Trends (if available) -->
        {self._generate_trends_section(quality_analysis.get('trends', {}))}
    </div>

    <script>
        // Initialize charts
        document.addEventListener('DOMContentLoaded', function() {{
            // Quality Distribution Chart
            const distributionCtx = document.getElementById('qualityDistributionChart').getContext('2d');
            new Chart(distributionCtx, {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(chart_data['labels'])},
                    datasets: [{{
                        data: {json.dumps(chart_data['data'])},
                        backgroundColor: [
                            '#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#7C2D12'
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }},
                        title: {{
                            display: true,
                            text: 'Quality Level Distribution'
                        }}
                    }}
                }}
            }});

            // Metrics Radar Chart
            const radarCtx = document.getElementById('metricsRadarChart').getContext('2d');
            new Chart(radarCtx, {{
                type: 'radar',
                data: {json.dumps(radar_data)},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        r: {{
                            beginAtZero: true,
                            max: 1.0,
                            ticks: {{
                                stepSize: 0.2
                            }}
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Average Quality Metrics'
                        }}
                    }}
                }}
            }});
        }});
    </script>
</body>
</html>"""
        
        return html_content
    
    def _generate_metrics_cards(self, metric_averages: Dict[str, Any]) -> str:
        """Generate HTML for metrics cards."""
        cards_html = ""
        
        for metric_name, data in metric_averages.items():
            score = data.get('average', 0)
            score_color = self._get_score_color(score)
            
            cards_html += f"""
            <div class="metric-card">
                <div class="metric-score" style="color: {score_color};">{score:.2f}</div>
                <div class="metric-name">{metric_name.replace('_', ' ').title()}</div>
                <div class="quality-progress">
                    <div class="quality-progress-bar" style="width: {score * 100}%; background-color: {score_color};"></div>
                </div>
            </div>
            """
        
        return cards_html
    
    def _generate_module_list(self, modules: List[str], list_type: str) -> str:
        """Generate HTML for module lists."""
        if not modules:
            return "<p>No modules to display.</p>"
        
        list_html = "<ul>"
        for module in modules[:5]:  # Limit to top 5
            icon = "🥇" if list_type == "top" else "⚠️"
            list_html += f"<li>{icon} <code>{module}</code></li>"
        list_html += "</ul>"
        
        return list_html
    
    def _generate_module_quality_table(self, module_assessments: Dict[str, Any]) -> str:
        """Generate HTML table for module quality details."""
        if not module_assessments:
            return "<p>No module assessments available.</p>"
        
        table_html = """
        <table class="module-quality-table">
            <thead>
                <tr>
                    <th>Module</th>
                    <th>Overall Score</th>
                    <th>Quality Level</th>
                    <th>Top Metric</th>
                    <th>Needs Improvement</th>
                    <th>Vector Similarity</th>
                </tr>
            </thead>
            <tbody>
        """
        
        # Sort modules by overall score
        sorted_modules = sorted(module_assessments.items(), 
                              key=lambda x: x[1].get('overall_score', 0), reverse=True)
        
        for module_path, assessment in sorted_modules[:20]:  # Limit to top 20
            overall_score = assessment.get('overall_score', 0)
            quality_level = assessment.get('quality_level', 'unknown')
            vector_similarity = assessment.get('vector_similarity_score', 0)
            
            # Find best and worst metrics
            metrics = assessment.get('metrics', {})
            if metrics:
                best_metric = max(metrics.items(), key=lambda x: x[1].get('score', 0))
                worst_metric = min(metrics.items(), key=lambda x: x[1].get('score', 0))
                
                best_metric_name = best_metric[0].replace('_', ' ').title()
                worst_metric_name = worst_metric[0].replace('_', ' ').title()
            else:
                best_metric_name = "N/A"
                worst_metric_name = "N/A"
            
            level_class = f"level-{quality_level}"
            score_color = self._get_score_color(overall_score)
            
            table_html += f"""
            <tr>
                <td><code>{module_path}</code></td>
                <td style="color: {score_color}; font-weight: bold;">{overall_score:.3f}</td>
                <td><span class="quality-level {level_class}">{quality_level}</span></td>
                <td>{best_metric_name}</td>
                <td>{worst_metric_name}</td>
                <td>{vector_similarity:.3f}</td>
            </tr>
            """
        
        table_html += "</tbody></table>"
        return table_html
    
    def _generate_recommendations_html(self, recommendations: List[str]) -> str:
        """Generate HTML for recommendations list."""
        if not recommendations:
            return "<p>No specific recommendations at this time.</p>"
        
        html = ""
        for rec in recommendations[:10]:  # Limit to top 10
            html += f'<div class="recommendation-item">{rec}</div>'
        
        return html
    
    def _generate_trends_section(self, trends: Dict[str, Any]) -> str:
        """Generate trends section if data is available."""
        if not trends or not trends.get('current_snapshot'):
            return ""
        
        return f"""
        <section>
            <h2>📈 Quality Trends</h2>
            <div class="quality-card">
                <h3>Current Snapshot</h3>
                <p><strong>Timestamp:</strong> {trends['current_snapshot'].get('timestamp', 'N/A')}</p>
                <p><strong>Average Score:</strong> {trends['current_snapshot'].get('average_score', 0):.3f}</p>
                <p><strong>Total Modules:</strong> {trends['current_snapshot'].get('total_modules', 0)}</p>
                {trends.get('trend_analysis', {}).get('note', '')}
            </div>
        </section>
        """
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score value."""
        if score >= 0.85:
            return "#10B981"  # Green
        elif score >= 0.70:
            return "#3B82F6"  # Blue
        elif score >= 0.55:
            return "#F59E0B"  # Yellow
        elif score >= 0.40:
            return "#EF4444"  # Red
        else:
            return "#7C2D12"  # Dark red
    
    def _generate_quality_data(self, quality_analysis: Dict[str, Any]) -> str:
        """Generate JSON data for quality dashboard."""
        
        # Prepare data for frontend consumption
        dashboard_data = {
            'overview': quality_analysis.get('overview', {}),
            'distribution': quality_analysis.get('quality_distribution', {}),
            'recommendations': quality_analysis.get('recommendations', []),
            'metadata': quality_analysis.get('metadata', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        return json.dumps(dashboard_data, indent=2)
    
    def _generate_metrics_visualization_data(self, quality_analysis: Dict[str, Any]) -> str:
        """Generate JSON data for metrics visualizations."""
        
        distribution = quality_analysis.get('quality_distribution', {})
        metric_averages = distribution.get('metric_averages', {})
        
        # Prepare data for various chart types
        visualization_data = {
            'radar_chart': {
                'labels': list(metric_averages.keys()),
                'datasets': [{
                    'label': 'Average Scores',
                    'data': [metric_averages[metric]['average'] for metric in metric_averages.keys()],
                    'backgroundColor': 'rgba(59, 130, 246, 0.2)',
                    'borderColor': 'rgb(59, 130, 246)',
                    'borderWidth': 2
                }]
            },
            'bar_chart': {
                'labels': list(metric_averages.keys()),
                'datasets': [{
                    'label': 'Average Scores',
                    'data': [metric_averages[metric]['average'] for metric in metric_averages.keys()],
                    'backgroundColor': [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(124, 45, 18, 0.8)',
                        'rgba(147, 51, 234, 0.8)',
                        'rgba(6, 182, 212, 0.8)'
                    ]
                }]
            },
            'quality_ranges': distribution.get('quality_ranges', {}),
            'metric_details': metric_averages
        }
        
        return json.dumps(visualization_data, indent=2)
    
    def _generate_module_quality_reports(self, quality_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate individual quality reports for each module."""
        
        module_reports = {}
        module_assessments = quality_analysis.get('module_assessments', {})
        
        for module_path, assessment in module_assessments.items():
            # Generate individual module report
            safe_module_name = module_path.replace('/', '_').replace('.', '_')
            report_filename = f"quality_module_{safe_module_name}.html"
            
            module_report = self._generate_individual_module_report(module_path, assessment)
            module_reports[report_filename] = module_report
        
        return module_reports
    
    def _generate_individual_module_report(self, module_path: str, assessment: Dict[str, Any]) -> str:
        """Generate detailed quality report for a single module."""
        
        overall_score = assessment.get('overall_score', 0)
        quality_level = assessment.get('quality_level', 'unknown')
        # Normalize enum to string value for rendering
        if hasattr(quality_level, 'value'):
            quality_level_str = str(quality_level.value)
        else:
            quality_level_str = str(quality_level)
        metrics = assessment.get('metrics', {})
        recommendations = assessment.get('recommendations', [])
        llm_assessment = assessment.get('llm_assessment', {})
        vector_similarity = assessment.get('vector_similarity_score', 0)
        
        # Generate metrics breakdown
        metrics_html = ""
        for metric_name, metric_data in metrics.items():
            score = metric_data.get('score', 0)
            weight = metric_data.get('weight', 0)
            description = metric_data.get('description', '')
            suggestions = metric_data.get('suggestions', [])
            details = metric_data.get('details', {})
            
            score_color = self._get_score_color(score)
            
            suggestions_html = ""
            if suggestions:
                suggestions_html = "<ul>" + "".join(f"<li>{s}</li>" for s in suggestions) + "</ul>"
            
            details_html = ""
            if details:
                details_html = "<ul>" + "".join(f"<li><strong>{k}:</strong> {v}</li>" for k, v in details.items()) + "</ul>"
            
            metrics_html += f"""
            <div class="metric-detail-card">
                <h3>{metric_name.replace('_', ' ').title()}</h3>
                <div class="metric-score-large" style="color: {score_color};">{score:.3f}</div>
                <p><strong>Weight:</strong> {weight:.1%}</p>
                <p>{description}</p>
                
                {f'<h4>Details:</h4>{details_html}' if details_html else ''}
                {f'<h4>Suggestions:</h4>{suggestions_html}' if suggestions_html else ''}
            </div>
            """
        
        level_class = f"level-{quality_level_str}"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quality Report - {module_path}</title>
    <link rel="stylesheet" href="../assets/css/modern-styles.css">
    <style>
        .module-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}
        
        .quality-score-large {{
            font-size: 4rem;
            font-weight: bold;
            margin: 1rem 0;
        }}
        
        .metric-detail-card {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #3B82F6;
        }}
        
        .metric-score-large {{
            font-size: 2rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }}
        
        .quality-level {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 1rem;
            font-weight: 500;
            text-transform: uppercase;
        }}
        
        .level-excellent {{ background-color: #D1FAE5; color: #065F46; }}
        .level-good {{ background-color: #DBEAFE; color: #1E40AF; }}
        .level-fair {{ background-color: #FEF3C7; color: #92400E; }}
        .level-poor {{ background-color: #FEE2E2; color: #991B1B; }}
        .level-critical {{ background-color: #FEE2E2; color: #7C2D12; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="module-header">
            <h1>🔬 Quality Report</h1>
            <h2><code>{module_path}</code></h2>
            <div class="quality-score-large">{overall_score:.3f}</div>
            <span class="quality-level {level_class}">{quality_level}</span>
        </div>
        
        <section>
            <h2>📊 Quality Overview</h2>
            <div class="quality-card">
                <p><strong>Overall Score:</strong> {overall_score:.3f}</p>
                <p><strong>Quality Level:</strong> {quality_level_str.title()}</p>
                <p><strong>Vector Similarity:</strong> {vector_similarity:.3f}</p>
                <p><strong>Analysis Timestamp:</strong> {assessment.get('timestamp', 'N/A')}</p>
            </div>
        </section>
        
        <section>
            <h2>📈 Detailed Metrics</h2>
            {metrics_html}
        </section>
        
        <section>
            <h2>🤖 LLM Assessment</h2>
            <div class="quality-card">
                <p><strong>Overall Assessment:</strong> {llm_assessment.get('overall_assessment', 'N/A')}</p>
                <p><strong>Strengths:</strong></p>
                <ul>
                    {self._generate_list_items(llm_assessment.get('strengths', []))}
                </ul>
                <p><strong>Weaknesses:</strong></p>
                <ul>
                    {self._generate_list_items(llm_assessment.get('weaknesses', []))}
                </ul>
                <p><strong>Improvement Priority:</strong></p>
                <ul>
                    {self._generate_list_items(llm_assessment.get('improvement_priority', []))}
                </ul>
            </div>
        </section>
        
        <section>
            <h2>💡 Recommendations</h2>
            <div class="recommendations-list">
                {self._generate_recommendations_html(recommendations)}
            </div>
        </section>
        
        <div style="margin-top: 2rem; text-align: center;">
            <a href="../quality.html" class="btn-primary">← Back to Quality Dashboard</a>
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
    def _generate_list_items(self, items: List[str]) -> str:
        """Generate HTML list items."""
        if not items:
            return "<li>None identified</li>"
        
        return "".join(f"<li>{item}</li>" for item in items)
    
    def _generate_trends_data(self, quality_analysis: Dict[str, Any]) -> str:
        """Generate JSON data for quality trends."""
        
        trends = quality_analysis.get('trends', {})
        
        # Prepare trend data for visualization
        trends_data = {
            'current_snapshot': trends.get('current_snapshot', {}),
            'historical_data': trends.get('historical_data', []),
            'trend_analysis': trends.get('trend_analysis', {}),
            'predictions': trends.get('predictions', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        return json.dumps(trends_data, indent=2)
    
    def save_quality_reports(self, reports: Dict[str, str]) -> None:
        """Save all quality reports to files."""
        
        for filename, content in reports.items():
            file_path = self.output_dir / filename
            
            # Create subdirectories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.debug(f"Saved quality report: {filename}")
            except Exception as e:
                self.logger.error(f"Failed to save quality report {filename}: {e}")
        
        self.logger.info(f"🔬 Saved {len(reports)} quality report files")
