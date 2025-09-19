#!/usr/bin/env python3
"""
Auto Documentation Generator Package

A comprehensive automatic documentation generation system with AI/ML pipeline support.
"""

__version__ = "1.0.0"
__author__ = "Auto Documentation Team"
__email__ = "docs@example.com"

from .main import main
from .analyzers.code_analyzer import CodeAnalyzer
from .analyzers.ai_pipeline_analyzer import AIPipelineAnalyzer
from .generators.markdown_generator import MarkdownGenerator
from .generators.ai_analysis_generator import AIAnalysisGenerator
from .remote_editor import RemoteEditor

__all__ = [
    "main",
    "CodeAnalyzer", 
    "AIPipelineAnalyzer",
    "MarkdownGenerator",
    "AIAnalysisGenerator",
    "RemoteEditor"
]
