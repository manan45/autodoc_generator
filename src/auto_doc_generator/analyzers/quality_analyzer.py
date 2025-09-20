#!/usr/bin/env python3
"""
Quality Analyzer - 🔬 Quality Scoring Pipeline

Analyzes code quality using repository analysis, vector embeddings, and LLM responses.
Provides comprehensive quality assessment factors and module quality analysis.
"""

import ast
import os
import sys
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re
import hashlib
import json
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# Optional: Advanced analysis libraries
try:
    from radon.complexity import cc_visit
    from radon.metrics import mi_visit, h_visit
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None


class QualityLevel(Enum):
    """Quality level enumeration."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class QualityMetric:
    """Individual quality metric."""
    name: str
    score: float  # 0.0 to 1.0
    weight: float  # Importance weight
    description: str
    details: Dict[str, Any]
    suggestions: List[str]


@dataclass
class QualityAssessment:
    """Complete quality assessment for a module."""
    module_path: str
    overall_score: float
    quality_level: QualityLevel
    metrics: Dict[str, QualityMetric]
    vector_similarity_score: float
    llm_assessment: Dict[str, Any]
    timestamp: str
    recommendations: List[str]


class QualityAnalyzer:
    """🔬 Quality Scoring Pipeline - Comprehensive code quality analysis."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Quality configuration
        quality_config = self.config.get('quality', {})
        self.weights = quality_config.get('weights', {
            'complexity': 0.20,
            'documentation': 0.15,
            'maintainability': 0.20,
            'testability': 0.15,
            'design_patterns': 0.10,
            'code_style': 0.10,
            'security': 0.10
        })
        
        # Thresholds for quality levels
        self.quality_thresholds = quality_config.get('thresholds', {
            'excellent': 0.85,
            'good': 0.70,
            'fair': 0.55,
            'poor': 0.40
        })
        
        # Vector embeddings for similarity analysis
        self.embeddings_enabled = EMBEDDINGS_AVAILABLE and quality_config.get('embeddings_enabled', True)
        if self.embeddings_enabled:
            model_name = quality_config.get('embedding_model', 'all-MiniLM-L6-v2')
            try:
                self.embedding_model = SentenceTransformer(model_name)
                self.logger.info(f"🔬 Quality analyzer loaded embedding model: {model_name}")
            except Exception as e:
                self.logger.warning(f"Failed to load embedding model: {e}")
                self.embeddings_enabled = False
        
        # Initialize quality patterns database
        self._init_quality_patterns()
    
    def _init_quality_patterns(self):
        """Initialize patterns for quality assessment."""
        self.quality_patterns = {
            'good_patterns': [
                r'class\s+\w+\([A-Z]\w*\):',  # Proper class inheritance
                r'def\s+test_\w+\(',  # Test functions
                r'""".*?"""',  # Docstrings
                r'@property',  # Properties
                r'@staticmethod|@classmethod',  # Method decorators
                r'if\s+__name__\s*==\s*["\']__main__["\']:',  # Main guard
                r'logging\.',  # Logging usage
                r'try:.*?except.*?:',  # Exception handling
            ],
            'bad_patterns': [
                r'global\s+\w+',  # Global variables
                r'exec\s*\(',  # Exec usage
                r'eval\s*\(',  # Eval usage
                r'import\s*\*',  # Wildcard imports
                r'#\s*TODO|#\s*FIXME|#\s*HACK',  # TODO comments
                r'print\s*\(',  # Print statements (should use logging)
                r'pass\s*$',  # Empty pass statements
            ],
            'design_patterns': [
                r'class\s+\w*Factory\w*:',  # Factory pattern
                r'class\s+\w*Singleton\w*:',  # Singleton pattern
                r'class\s+\w*Observer\w*:',  # Observer pattern
                r'class\s+\w*Strategy\w*:',  # Strategy pattern
                r'class\s+\w*Builder\w*:',  # Builder pattern
                r'def\s+__enter__\s*\(|def\s+__exit__\s*\(',  # Context manager
            ]
        }
    
    def analyze_quality(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main method to analyze code quality across all modules.
        
        Args:
            code_analysis: Results from CodeAnalyzer
            ai_analysis: Results from AIPipelineAnalyzer
            
        Returns:
            Comprehensive quality analysis results
        """
        self.logger.info("🔬 Starting quality scoring pipeline...")
        
        quality_results = {
            'overview': {},
            'module_assessments': {},
            'quality_distribution': {},
            'recommendations': [],
            'trends': {},
            'metadata': {
                'analyzer_version': '1.0.0',
                'analysis_timestamp': datetime.now().isoformat(),
                'total_modules_analyzed': 0,
                'embeddings_enabled': self.embeddings_enabled
            }
        }
        
        # Analyze each module
        modules = code_analysis.get('modules', [])
        assessments = []
        
        for module in modules:
            try:
                # Handle case where module might be a string instead of dict
                if isinstance(module, str):
                    module_path = module
                    self.logger.warning(f"Module {module_path} is a string, expected dict. Skipping analysis.")
                    continue
                elif isinstance(module, dict):
                    module_path = module.get('path', 'unknown')
                else:
                    self.logger.warning(f"Module {module} has unexpected type {type(module)}. Skipping analysis.")
                    continue
                
                assessment = self._analyze_module_quality(module, code_analysis, ai_analysis)
                assessments.append(assessment)
                quality_results['module_assessments'][module_path] = asdict(assessment)
            except Exception as e:
                module_path = module.get('path', 'unknown') if isinstance(module, dict) else str(module)
                self.logger.error(f"Error analyzing module {module_path}: {e}")
        
        # Generate overview and trends
        quality_results['overview'] = self._generate_quality_overview(assessments)
        quality_results['quality_distribution'] = self._analyze_quality_distribution(assessments)
        quality_results['recommendations'] = self._generate_global_recommendations(assessments)
        quality_results['trends'] = self._analyze_quality_trends(assessments)
        quality_results['metadata']['total_modules_analyzed'] = len(assessments)
        
        self.logger.info(f"🔬 Quality analysis complete. Analyzed {len(assessments)} modules.")
        return quality_results
    
    def _analyze_module_quality(self, module: Dict[str, Any], code_analysis: Dict[str, Any], 
                               ai_analysis: Dict[str, Any] = None) -> QualityAssessment:
        """Analyze quality of a single module."""
        
        module_path = module.get('path', 'unknown')
        content = module.get('content', '')
        
        # Calculate individual quality metrics
        metrics = {}
        
        # 1. Complexity Analysis
        metrics['complexity'] = self._analyze_complexity_quality(module, code_analysis)
        
        # 2. Documentation Quality
        metrics['documentation'] = self._analyze_documentation_quality(module, content)
        
        # 3. Maintainability
        metrics['maintainability'] = self._analyze_maintainability(module, content)
        
        # 4. Testability
        metrics['testability'] = self._analyze_testability(module, content, code_analysis)
        
        # 5. Design Patterns
        metrics['design_patterns'] = self._analyze_design_patterns(content)
        
        # 6. Code Style
        metrics['code_style'] = self._analyze_code_style(content)
        
        # 7. Security
        metrics['security'] = self._analyze_security_quality(content)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(metrics)
        quality_level = self._determine_quality_level(overall_score)
        
        # Vector similarity analysis
        vector_similarity_score = self._calculate_vector_similarity(content, code_analysis)
        
        # LLM assessment (if available)
        llm_assessment = self._get_llm_assessment(module, metrics, ai_analysis)
        
        # Generate recommendations
        recommendations = self._generate_module_recommendations(metrics, llm_assessment)
        
        return QualityAssessment(
            module_path=module_path,
            overall_score=overall_score,
            quality_level=quality_level,
            metrics=metrics,
            vector_similarity_score=vector_similarity_score,
            llm_assessment=llm_assessment,
            timestamp=datetime.now().isoformat(),
            recommendations=recommendations
        )
    
    def _analyze_complexity_quality(self, module: Dict[str, Any], code_analysis: Dict[str, Any]) -> QualityMetric:
        """Analyze complexity-related quality factors."""
        
        complexity_data = code_analysis.get('complexity', {})
        functions = module.get('functions', [])
        
        # Calculate complexity metrics
        function_complexities = []
        for func in functions:
            complexity = func.get('complexity', 1)
            function_complexities.append(complexity)
        
        avg_complexity = np.mean(function_complexities) if function_complexities else 1
        max_complexity = max(function_complexities) if function_complexities else 1
        
        # Scoring (lower complexity = higher score)
        complexity_score = max(0.0, min(1.0, (10 - avg_complexity) / 10))
        
        suggestions = []
        if avg_complexity > 5:
            suggestions.append("Consider breaking down complex functions into smaller ones")
        if max_complexity > 10:
            suggestions.append("Refactor highly complex functions (complexity > 10)")
        
        return QualityMetric(
            name="Complexity",
            score=complexity_score,
            weight=self.weights['complexity'],
            description="Cyclomatic complexity and function size analysis",
            details={
                'average_complexity': avg_complexity,
                'max_complexity': max_complexity,
                'total_functions': len(functions),
                'high_complexity_functions': [f['name'] for f in functions if f.get('complexity', 0) > 7]
            },
            suggestions=suggestions
        )
    
    def _analyze_documentation_quality(self, module: Dict[str, Any], content: str) -> QualityMetric:
        """Analyze documentation quality."""
        
        # Count docstrings
        docstring_pattern = r'""".*?"""'
        docstrings = re.findall(docstring_pattern, content, re.DOTALL)
        
        # Count functions and classes
        functions = len(re.findall(r'def\s+\w+\s*\(', content))
        classes = len(re.findall(r'class\s+\w+\s*[\(:]', content))
        
        total_items = functions + classes
        documented_items = len(docstrings)
        
        # Calculate documentation ratio
        doc_ratio = documented_items / total_items if total_items > 0 else 0
        
        # Check for comprehensive documentation
        has_module_docstring = content.strip().startswith('"""') or content.strip().startswith("'''")
        has_inline_comments = len(re.findall(r'#[^#]', content)) > 0
        
        # Scoring
        base_score = doc_ratio
        if has_module_docstring:
            base_score += 0.2
        if has_inline_comments:
            base_score += 0.1
        
        doc_score = min(1.0, base_score)
        
        suggestions = []
        if doc_ratio < 0.5:
            suggestions.append("Add docstrings to functions and classes")
        if not has_module_docstring:
            suggestions.append("Add module-level docstring")
        if not has_inline_comments:
            suggestions.append("Add inline comments for complex logic")
        
        return QualityMetric(
            name="Documentation",
            score=doc_score,
            weight=self.weights['documentation'],
            description="Documentation coverage and quality",
            details={
                'documentation_ratio': doc_ratio,
                'total_items': total_items,
                'documented_items': documented_items,
                'has_module_docstring': has_module_docstring,
                'inline_comments': len(re.findall(r'#[^#]', content))
            },
            suggestions=suggestions
        )
    
    def _analyze_maintainability(self, module: Dict[str, Any], content: str) -> QualityMetric:
        """Analyze maintainability factors."""
        
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # Function length analysis
        function_lengths = []
        current_function_length = 0
        in_function = False
        
        for line in lines:
            if re.match(r'\s*def\s+', line):
                if in_function and current_function_length > 0:
                    function_lengths.append(current_function_length)
                in_function = True
                current_function_length = 1
            elif in_function:
                if line.strip():
                    current_function_length += 1
                if re.match(r'^[a-zA-Z]', line):  # New top-level definition
                    function_lengths.append(current_function_length)
                    in_function = False
        
        avg_function_length = np.mean(function_lengths) if function_lengths else 0
        
        # Check for maintainability patterns
        good_patterns = sum(1 for pattern in self.quality_patterns['good_patterns'] 
                           if re.search(pattern, content, re.MULTILINE))
        bad_patterns = sum(1 for pattern in self.quality_patterns['bad_patterns'] 
                          if re.search(pattern, content, re.MULTILINE))
        
        # Scoring
        length_score = max(0.0, min(1.0, (50 - avg_function_length) / 50))
        pattern_score = max(0.0, min(1.0, (good_patterns - bad_patterns * 2) / max(1, good_patterns + bad_patterns)))
        
        maintainability_score = (length_score + pattern_score) / 2
        
        suggestions = []
        if avg_function_length > 30:
            suggestions.append("Break down large functions (>30 lines)")
        if bad_patterns > 0:
            suggestions.append("Avoid anti-patterns like global variables and eval()")
        
        return QualityMetric(
            name="Maintainability",
            score=maintainability_score,
            weight=self.weights['maintainability'],
            description="Code maintainability and readability factors",
            details={
                'average_function_length': avg_function_length,
                'total_lines': total_lines,
                'code_lines': code_lines,
                'good_patterns': good_patterns,
                'bad_patterns': bad_patterns
            },
            suggestions=suggestions
        )
    
    def _analyze_testability(self, module: Dict[str, Any], content: str, code_analysis: Dict[str, Any]) -> QualityMetric:
        """Analyze testability factors."""
        
        # Check for test-related patterns
        test_functions = len(re.findall(r'def\s+test_\w+\s*\(', content))
        assert_statements = len(re.findall(r'assert\s+', content))
        mock_usage = len(re.findall(r'mock\.|Mock\(|patch\(', content))
        
        # Check for dependency injection patterns
        constructor_params = len(re.findall(r'def\s+__init__\s*\([^)]*\w+[^)]*\)', content))
        
        # Check for testable structure
        has_main_guard = bool(re.search(r'if\s+__name__\s*==\s*["\']__main__["\']:', content))
        
        total_functions = len(re.findall(r'def\s+\w+\s*\(', content))
        
        # Scoring
        test_coverage_score = test_functions / max(1, total_functions) if total_functions > 0 else 0
        testability_indicators = (assert_statements > 0) + (mock_usage > 0) + has_main_guard + (constructor_params > 0)
        
        testability_score = (test_coverage_score + testability_indicators / 4) / 2
        
        suggestions = []
        if test_functions == 0:
            suggestions.append("Add unit tests for functions")
        if not has_main_guard:
            suggestions.append("Add if __name__ == '__main__': guard")
        if constructor_params == 0 and total_functions > 0:
            suggestions.append("Consider dependency injection for better testability")
        
        return QualityMetric(
            name="Testability",
            score=testability_score,
            weight=self.weights['testability'],
            description="Code testability and test coverage indicators",
            details={
                'test_functions': test_functions,
                'total_functions': total_functions,
                'assert_statements': assert_statements,
                'mock_usage': mock_usage,
                'has_main_guard': has_main_guard,
                'test_coverage_ratio': test_coverage_score
            },
            suggestions=suggestions
        )
    
    def _analyze_design_patterns(self, content: str) -> QualityMetric:
        """Analyze design pattern usage."""
        
        pattern_matches = {}
        total_patterns = 0
        
        for pattern_name, pattern_regex in [
            ('Factory', r'class\s+\w*Factory\w*:'),
            ('Singleton', r'class\s+\w*Singleton\w*:|def\s+__new__\s*\('),
            ('Observer', r'class\s+\w*Observer\w*:|def\s+notify\s*\('),
            ('Strategy', r'class\s+\w*Strategy\w*:'),
            ('Builder', r'class\s+\w*Builder\w*:'),
            ('Context Manager', r'def\s+__enter__\s*\(|def\s+__exit__\s*\('),
            ('Decorator', r'@\w+|def\s+\w+\s*\([^)]*\)\s*:.*?def\s+wrapper'),
        ]:
            matches = len(re.findall(pattern_regex, content, re.MULTILINE))
            pattern_matches[pattern_name] = matches
            total_patterns += matches
        
        # Bonus for good OOP practices
        has_inheritance = bool(re.search(r'class\s+\w+\s*\([^)]+\):', content))
        has_properties = bool(re.search(r'@property', content))
        has_abstract_methods = bool(re.search(r'@abstractmethod|@abc\.abstractmethod', content))
        
        oop_score = (has_inheritance + has_properties + has_abstract_methods) / 3
        
        # Calculate overall design pattern score
        pattern_density = total_patterns / max(1, len(content.split('\n'))) * 100
        design_score = min(1.0, pattern_density + oop_score)
        
        suggestions = []
        if total_patterns == 0:
            suggestions.append("Consider using design patterns where appropriate")
        if not has_properties and has_inheritance:
            suggestions.append("Use @property decorators for getter/setter methods")
        
        return QualityMetric(
            name="Design Patterns",
            score=design_score,
            weight=self.weights['design_patterns'],
            description="Design pattern usage and OOP practices",
            details={
                'pattern_matches': pattern_matches,
                'total_patterns': total_patterns,
                'has_inheritance': has_inheritance,
                'has_properties': has_properties,
                'has_abstract_methods': has_abstract_methods,
                'oop_score': oop_score
            },
            suggestions=suggestions
        )
    
    def _analyze_code_style(self, content: str) -> QualityMetric:
        """Analyze code style and formatting."""
        
        lines = content.split('\n')
        
        # Check various style aspects
        long_lines = [i for i, line in enumerate(lines) if len(line) > 88]  # PEP 8 suggests 79, but 88 is common
        inconsistent_indentation = self._check_indentation_consistency(lines)
        has_trailing_whitespace = any(line.endswith(' ') or line.endswith('\t') for line in lines)
        
        # Check naming conventions
        snake_case_functions = len(re.findall(r'def\s+[a-z_][a-z0-9_]*\s*\(', content))
        camel_case_classes = len(re.findall(r'class\s+[A-Z][a-zA-Z0-9]*\s*[\(:]', content))
        total_functions = len(re.findall(r'def\s+\w+\s*\(', content))
        total_classes = len(re.findall(r'class\s+\w+\s*[\(:]', content))
        
        # Scoring
        line_length_score = max(0.0, 1.0 - len(long_lines) / max(1, len(lines)))
        indentation_score = 1.0 if not inconsistent_indentation else 0.5
        whitespace_score = 0.0 if has_trailing_whitespace else 1.0
        naming_score = ((snake_case_functions / max(1, total_functions)) + 
                       (camel_case_classes / max(1, total_classes))) / 2 if (total_functions + total_classes) > 0 else 1.0
        
        style_score = (line_length_score + indentation_score + whitespace_score + naming_score) / 4
        
        suggestions = []
        if long_lines:
            suggestions.append(f"Fix {len(long_lines)} lines that are too long (>88 characters)")
        if inconsistent_indentation:
            suggestions.append("Fix inconsistent indentation")
        if has_trailing_whitespace:
            suggestions.append("Remove trailing whitespace")
        
        return QualityMetric(
            name="Code Style",
            score=style_score,
            weight=self.weights['code_style'],
            description="Code formatting and style conventions",
            details={
                'long_lines': len(long_lines),
                'inconsistent_indentation': inconsistent_indentation,
                'has_trailing_whitespace': has_trailing_whitespace,
                'naming_convention_score': naming_score,
                'total_lines': len(lines)
            },
            suggestions=suggestions
        )
    
    def _analyze_security_quality(self, content: str) -> QualityMetric:
        """Analyze security-related quality factors."""
        
        # Security anti-patterns
        security_issues = {
            'eval_usage': len(re.findall(r'eval\s*\(', content)),
            'exec_usage': len(re.findall(r'exec\s*\(', content)),
            'shell_injection': len(re.findall(r'os\.system\s*\(|subprocess\.call\s*\([^)]*shell\s*=\s*True', content)),
            'hardcoded_secrets': len(re.findall(r'password\s*=\s*["\'][^"\']+["\']|api_key\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE)),
            'sql_injection': len(re.findall(r'execute\s*\([^)]*%[sf]|cursor\.execute\s*\([^)]*\+', content)),
        }
        
        # Security good practices
        security_practices = {
            'input_validation': len(re.findall(r'isinstance\s*\(|hasattr\s*\(|assert\s+', content)),
            'exception_handling': len(re.findall(r'try\s*:|except\s+\w+:', content)),
            'logging_usage': len(re.findall(r'logging\.|logger\.', content)),
        }
        
        total_issues = sum(security_issues.values())
        total_practices = sum(security_practices.values())
        
        # Scoring (fewer issues = higher score)
        issue_penalty = min(1.0, total_issues * 0.2)
        practice_bonus = min(0.5, total_practices * 0.1)
        
        security_score = max(0.0, 1.0 - issue_penalty + practice_bonus)
        
        suggestions = []
        if security_issues['eval_usage'] > 0:
            suggestions.append("Avoid using eval() - security risk")
        if security_issues['hardcoded_secrets'] > 0:
            suggestions.append("Remove hardcoded passwords/API keys")
        if security_issues['shell_injection'] > 0:
            suggestions.append("Avoid shell=True in subprocess calls")
        
        return QualityMetric(
            name="Security",
            score=security_score,
            weight=self.weights['security'],
            description="Security practices and vulnerability assessment",
            details={
                'security_issues': security_issues,
                'security_practices': security_practices,
                'total_issues': total_issues,
                'total_practices': total_practices
            },
            suggestions=suggestions
        )
    
    def _check_indentation_consistency(self, lines: List[str]) -> bool:
        """Check for consistent indentation."""
        indentations = []
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indentations.append(indent)
        
        if not indentations:
            return False
        
        # Check if all indentations are multiples of the same base
        min_indent = min(indentations)
        return not all(indent % min_indent == 0 for indent in indentations)
    
    def _calculate_overall_score(self, metrics: Dict[str, QualityMetric]) -> float:
        """Calculate weighted overall quality score."""
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for metric in metrics.values():
            total_weighted_score += metric.score * metric.weight
            total_weight += metric.weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level based on score."""
        if score >= self.quality_thresholds['excellent']:
            return QualityLevel.EXCELLENT
        elif score >= self.quality_thresholds['good']:
            return QualityLevel.GOOD
        elif score >= self.quality_thresholds['fair']:
            return QualityLevel.FAIR
        elif score >= self.quality_thresholds['poor']:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def _calculate_vector_similarity(self, content: str, code_analysis: Dict[str, Any]) -> float:
        """Calculate vector similarity with high-quality code patterns."""
        if not self.embeddings_enabled:
            return 0.0
        
        try:
            # Generate embedding for current content
            content_embedding = self.embedding_model.encode(content)
            
            # Compare with high-quality code patterns (you could build a database of these)
            high_quality_patterns = [
                "well documented function with proper error handling and type hints",
                "clean class design with single responsibility principle",
                "comprehensive test coverage with unit tests and mocks",
                "proper use of design patterns and SOLID principles"
            ]
            
            similarities = []
            for pattern in high_quality_patterns:
                pattern_embedding = self.embedding_model.encode(pattern)
                similarity = np.dot(content_embedding, pattern_embedding) / (
                    np.linalg.norm(content_embedding) * np.linalg.norm(pattern_embedding)
                )
                similarities.append(similarity)
            
            return float(np.mean(similarities))
            
        except Exception as e:
            self.logger.error(f"Error calculating vector similarity: {e}")
            return 0.0
    
    def _get_llm_assessment(self, module: Dict[str, Any], metrics: Dict[str, QualityMetric], 
                           ai_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get LLM-based quality assessment (placeholder for future integration)."""
        
        # This would integrate with the existing AI analysis system
        # For now, return a structured assessment based on metrics
        
        overall_score = self._calculate_overall_score(metrics)
        
        # Simulate LLM assessment based on metrics
        assessment = {
            'overall_assessment': self._generate_llm_summary(overall_score, metrics),
            'strengths': self._identify_strengths(metrics),
            'weaknesses': self._identify_weaknesses(metrics),
            'improvement_priority': self._get_improvement_priority(metrics),
            'confidence': 0.85  # Placeholder confidence score
        }
        
        return assessment
    
    def _generate_llm_summary(self, score: float, metrics: Dict[str, QualityMetric]) -> str:
        """Generate LLM-style quality summary."""
        level = self._determine_quality_level(score)
        
        if level == QualityLevel.EXCELLENT:
            return "This module demonstrates excellent code quality with strong adherence to best practices."
        elif level == QualityLevel.GOOD:
            return "This module shows good code quality with minor areas for improvement."
        elif level == QualityLevel.FAIR:
            return "This module has fair code quality but would benefit from several improvements."
        elif level == QualityLevel.POOR:
            return "This module has poor code quality and requires significant refactoring."
        else:
            return "This module has critical quality issues that need immediate attention."
    
    def _identify_strengths(self, metrics: Dict[str, QualityMetric]) -> List[str]:
        """Identify code strengths based on metrics."""
        strengths = []
        for name, metric in metrics.items():
            if metric.score >= 0.8:
                strengths.append(f"Strong {name.lower()} (score: {metric.score:.2f})")
        return strengths
    
    def _identify_weaknesses(self, metrics: Dict[str, QualityMetric]) -> List[str]:
        """Identify code weaknesses based on metrics."""
        weaknesses = []
        for name, metric in metrics.items():
            if metric.score < 0.5:
                weaknesses.append(f"Weak {name.lower()} (score: {metric.score:.2f})")
        return weaknesses
    
    def _get_improvement_priority(self, metrics: Dict[str, QualityMetric]) -> List[str]:
        """Get prioritized list of improvements."""
        # Sort by weighted impact (low score * high weight)
        priorities = []
        for name, metric in metrics.items():
            impact = (1.0 - metric.score) * metric.weight
            priorities.append((name, impact))
        
        priorities.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in priorities[:3]]  # Top 3 priorities
    
    def _generate_module_recommendations(self, metrics: Dict[str, QualityMetric], 
                                       llm_assessment: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations for the module."""
        recommendations = []
        
        # Collect suggestions from all metrics
        for metric in metrics.values():
            recommendations.extend(metric.suggestions)
        
        # Add priority-based recommendations
        priorities = llm_assessment.get('improvement_priority', [])
        for priority in priorities[:2]:  # Top 2 priorities
            recommendations.append(f"Focus on improving {priority.lower()} as a priority")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _generate_quality_overview(self, assessments: List[QualityAssessment]) -> Dict[str, Any]:
        """Generate overall quality overview."""
        if not assessments:
            return {}
        
        # Filter out assessments with None scores
        valid_assessments = [a for a in assessments if a.overall_score is not None]
        if not valid_assessments:
            return {
                'average_quality_score': 0.0,
                'median_quality_score': 0.0,
                'quality_std_dev': 0.0,
                'total_modules': len(assessments),
                'quality_level_distribution': {},
                'top_quality_modules': [],
                'lowest_quality_modules': []
            }
        
        scores = [a.overall_score for a in valid_assessments]
        levels = [a.quality_level.value for a in valid_assessments]
        
        return {
            'average_quality_score': float(np.mean(scores)),
            'median_quality_score': float(np.median(scores)),
            'quality_std_dev': float(np.std(scores)),
            'total_modules': len(assessments),
            'quality_level_distribution': {level: levels.count(level) for level in set(levels)},
            'top_quality_modules': [a.module_path for a in sorted(valid_assessments, key=lambda x: x.overall_score, reverse=True)[:5]],
            'lowest_quality_modules': [a.module_path for a in sorted(valid_assessments, key=lambda x: x.overall_score)[:5]]
        }
    
    def _analyze_quality_distribution(self, assessments: List[QualityAssessment]) -> Dict[str, Any]:
        """Analyze quality distribution across modules."""
        if not assessments:
            return {}
        
        # Metric-wise analysis
        metric_averages = {}
        all_metrics = assessments[0].metrics.keys() if assessments else []
        
        for metric_name in all_metrics:
            scores = [a.metrics[metric_name].score for a in assessments if metric_name in a.metrics]
            metric_averages[metric_name] = {
                'average': float(np.mean(scores)) if scores else 0.0,
                'std_dev': float(np.std(scores)) if scores else 0.0,
                'min': float(np.min(scores)) if scores else 0.0,
                'max': float(np.max(scores)) if scores else 0.0
            }
        
        return {
            'metric_averages': metric_averages,
            'quality_ranges': {
                'excellent': len([a for a in assessments if a.quality_level == QualityLevel.EXCELLENT]),
                'good': len([a for a in assessments if a.quality_level == QualityLevel.GOOD]),
                'fair': len([a for a in assessments if a.quality_level == QualityLevel.FAIR]),
                'poor': len([a for a in assessments if a.quality_level == QualityLevel.POOR]),
                'critical': len([a for a in assessments if a.quality_level == QualityLevel.CRITICAL])
            }
        }
    
    def _generate_global_recommendations(self, assessments: List[QualityAssessment]) -> List[str]:
        """Generate global recommendations across all modules."""
        if not assessments:
            return []
        
        # Aggregate common issues
        all_recommendations = []
        for assessment in assessments:
            all_recommendations.extend(assessment.recommendations)
        
        # Count frequency of recommendations
        recommendation_counts = {}
        for rec in all_recommendations:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        
        # Sort by frequency and return top recommendations
        sorted_recs = sorted(recommendation_counts.items(), key=lambda x: x[1], reverse=True)
        
        global_recs = []
        for rec, count in sorted_recs[:10]:  # Top 10
            if count > 1:  # Only include if it affects multiple modules
                global_recs.append(f"{rec} (affects {count} modules)")
        
        return global_recs
    
    def _analyze_quality_trends(self, assessments: List[QualityAssessment]) -> Dict[str, Any]:
        """Analyze quality trends (placeholder for future trend analysis)."""
        
        # This could be enhanced with historical data
        return {
            'current_snapshot': {
                'timestamp': datetime.now().isoformat(),
                'total_modules': len(assessments),
                'average_score': float(np.mean([a.overall_score for a in assessments])) if assessments else 0.0
            },
            'trend_analysis': {
                'note': 'Historical trend analysis requires multiple analysis runs over time'
            }
        }
