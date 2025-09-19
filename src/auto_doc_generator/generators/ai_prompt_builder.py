#!/usr/bin/env python3
"""
AI Prompt Builder

Builds intelligent prompts for different types of analysis with rich context.
Handles prompt templates, context injection, and optimization.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class AIPromptBuilder:
    """Builds optimized prompts for AI analysis with rich context."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_context_tokens = self.config.get('ai', {}).get('max_context_tokens', 3000)
    
    def build_api_analysis_prompt(self, code_analysis: Dict[str, Any]) -> str:
        """Build prompt for API endpoint analysis."""
        
        # Extract concise context for AI analysis (reduce token usage)
        functions = code_analysis.get('functions', [])[:10]  # Limit to 10
        classes = code_analysis.get('classes', [])[:8]       # Limit to 8  
        modules = code_analysis.get('modules', [])[:6]       # Limit to 6
        
        # Create summarized context instead of full data
        context = {
            'function_names': [str(f.get('name', '')) for f in functions],
            'class_names': [str(c.get('name', '')) for c in classes],
            'module_names': [str(m.get('name', '')) for m in modules],
            'project_type': str(code_analysis.get('overview', {}).get('project_type', 'Unknown'))
        }
        
        # Build prompt safely with proper escaping
        function_list = ', '.join(context['function_names'][:15])
        class_list = ', '.join(context['class_names'][:10])
        module_list = ', '.join(context['module_names'][:8])
        
        prompt = f"""Based on this code summary, identify API patterns and interfaces:

Project Type: {context['project_type']}
Functions: {function_list}
Classes: {class_list}
Modules: {module_list}

Identify:
1. Public API interfaces
2. Possible HTTP endpoints 
3. Main service classes
4. Data access patterns

Return JSON:
{{
  "endpoints": [{{"path": "/api/example", "method": "GET", "function": "get_data", "description": "brief desc"}}],
  "interfaces": [{{"name": "ServiceClass", "type": "class", "purpose": "brief purpose", "methods": ["method1"]}}],
  "patterns": [{{"pattern": "REST API", "description": "brief desc"}}]
}}

Return ONLY valid JSON."""
        
        return prompt
    
    def build_architecture_analysis_prompt(self, code_analysis: Dict[str, Any]) -> str:
        """Build prompt for architecture pattern analysis."""
        
        # Prepare concise context
        overview = code_analysis.get('overview', {})
        modules = code_analysis.get('modules', [])[:8]  # Limit to 8 modules
        
        # Safely build context summary
        project_type = str(overview.get('project_type', 'Unknown'))
        total_files = str(overview.get('total_files', 0))
        module_names = [str(m.get('name', '')) for m in modules if m.get('name')]
        languages = [str(lang) for lang in overview.get('languages_detected', [])]
        
        # Build prompt safely to avoid f-string issues
        module_list = ', '.join(module_names)
        language_list = ', '.join(languages)
        
        prompt = f"""Analyze architecture patterns for this project:

Project: {project_type}
Files: {total_files}
Modules: {module_list}
Languages: {language_list}

Identify:
1. Main architectural layers
2. Design patterns used
3. Separation principles

Return JSON:
{{
  "layers": [{{"name": "Application Layer", "purpose": "brief purpose", "components": ["main"], "responsibilities": ["startup"]}}],
  "patterns": [{{"name": "Layered Architecture", "type": "Architectural", "implementation": "brief desc", "benefits": ["separation"]}}],
  "principles": [{{"principle": "Single Responsibility", "description": "brief desc"}}]
}}

Return ONLY valid JSON."""
        
        return prompt
    
    def build_component_analysis_prompt(self, code_analysis: Dict[str, Any]) -> str:
        """Build prompt for component relationship analysis."""
        
        # Prepare concise context
        modules = code_analysis.get('modules', [])[:6]  # Limit to 6 modules
        dependencies = code_analysis.get('dependencies', {})
        
        module_names = [str(m.get('name', '')) for m in modules]
        internal_deps = [str(dep) for dep in dependencies.get('internal_dependencies', [])[:8]]
        external_deps = [str(dep) for dep in dependencies.get('external_dependencies', [])[:8]]
        
        # Build prompt with proper escaping
        module_str = ', '.join(module_names)
        internal_str = ', '.join(internal_deps)
        external_str = ', '.join(external_deps)
        
        prompt = f"""Analyze component relationships:

Modules: {module_str}
Internal deps: {internal_str}
External deps: {external_str}

Identify:
1. Main components and their types
2. Key relationships between components
3. Communication patterns

Return JSON:
{{
  "components": [{{"name": "ComponentName", "type": "service", "purpose": "brief purpose", "dependencies": ["dep1"]}}],
  "relationships": [{{"source": "A", "target": "B", "type": "uses", "description": "brief desc"}}],
  "communication_patterns": [{{"pattern": "Direct Call", "components": ["A", "B"], "description": "brief desc"}}]
}}

Return ONLY valid JSON."""
        
        return prompt
    
    def build_dataflow_analysis_prompt(self, code_analysis: Dict[str, Any]) -> str:
        """Build prompt for data flow pattern analysis."""
        
        # Prepare concise context
        data_flow = code_analysis.get('data_flow', {})
        functions = code_analysis.get('functions', [])[:8]  # Limit functions
        
        entry_points = data_flow.get('entry_points', [])[:5]
        transformations = data_flow.get('transformations', [])[:5]
        output_points = data_flow.get('output_points', [])[:5]
        func_names = [str(f.get('name', '')) for f in functions]
        
        # Handle cases where items might be strings or dicts
        entry_point_names = []
        for ep in entry_points:
            if isinstance(ep, dict):
                entry_point_names.append(ep.get('name', str(ep)))
            else:
                entry_point_names.append(str(ep))
        
        transformation_names = []
        for t in transformations:
            if isinstance(t, dict):
                transformation_names.append(t.get('name', str(t)))
            else:
                transformation_names.append(str(t))
        
        output_point_names = []
        for op in output_points:
            if isinstance(op, dict):
                output_point_names.append(op.get('name', str(op)))
            else:
                output_point_names.append(str(op))
        
        # Build prompt with proper escaping
        entry_str = ', '.join(entry_point_names)
        transform_str = ', '.join(transformation_names)
        output_str = ', '.join(output_point_names)
        func_str = ', '.join(func_names)
        
        prompt = f"""Analyze data flow patterns:

Entry points: {entry_str}
Transformations: {transform_str}
Output points: {output_str}
Key functions: {func_str}

Identify:
1. Data sources and formats
2. Processing transformations
3. Storage patterns
4. Flow stages

Return JSON:
{{
  "data_sources": [{{"name": "InputData", "type": "file", "format": "json", "description": "brief desc"}}],
  "transformations": [{{"name": "ProcessData", "input": "raw", "output": "processed", "purpose": "brief purpose"}}],
  "data_stores": [{{"name": "Cache", "type": "memory", "purpose": "brief purpose", "access_pattern": "read_write"}}],
  "flow_patterns": [{{"name": "ETL", "stages": ["extract", "transform", "load"], "description": "brief desc"}}]
}}

Return ONLY valid JSON."""
        
        return prompt
    
    def build_ml_analysis_prompt(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> str:
        """Build prompt for ML component analysis."""
        
        # Prepare concise context
        ml_models = ai_analysis.get('ml_models', [])[:3]
        pipelines = ai_analysis.get('pipelines', [])[:3]
        frameworks = ai_analysis.get('frameworks_detected', [])[:5]
        training_scripts = ai_analysis.get('training_scripts', [])[:3]
        
        # Build prompt with proper escaping
        frameworks_str = ', '.join(frameworks)
        
        prompt = f"""Analyze ML components:

ML Models: {len(ml_models)} detected
Pipelines: {len(pipelines)} detected
Frameworks: {frameworks_str}
Training Scripts: {len(training_scripts)} detected

Identify:
1. Main ML models and their types
2. Pipeline stages and purposes
3. Infrastructure components

Return JSON:
{{
  "models": [{{"name": "ModelName", "type": "classification", "framework": "sklearn", "purpose": "brief purpose"}}],
  "pipelines": [{{"name": "TrainingPipeline", "type": "training", "stages": ["data_prep", "train", "eval"], "description": "brief desc"}}],
  "infrastructure": [{{"component": "MLFlow", "purpose": "tracking", "technology": "mlflow"}}]
}}

Return ONLY valid JSON."""
        
        return prompt
    
    def optimize_prompt_length(self, prompt: str, max_tokens: int = None) -> str:
        """Optimize prompt length to fit within token limits."""
        max_tokens = max_tokens or self.max_context_tokens
        
        # Simple token estimation (roughly 4 characters per token)
        estimated_tokens = len(prompt) // 4
        
        if estimated_tokens <= max_tokens:
            return prompt
        
        # Truncate and add ellipsis if too long
        target_chars = max_tokens * 4 - 100  # Leave room for ellipsis
        if len(prompt) > target_chars:
            return prompt[:target_chars] + "\n\n... (truncated for length)\n\nReturn ONLY valid JSON."
        
        return prompt
    
    def add_context_enhancement(self, prompt: str, context: Dict[str, Any]) -> str:
        """Add additional context to enhance prompt quality."""
        
        enhancements = []
        
        # Add project context if available
        if context.get('project_name'):
            enhancements.append(f"Project: {context['project_name']}")
        
        # Add domain context
        if context.get('domain'):
            enhancements.append(f"Domain: {context['domain']}")
        
        # Add complexity hints
        if context.get('complexity_level'):
            enhancements.append(f"Complexity: {context['complexity_level']}")
        
        if enhancements:
            context_header = "Context:\n" + "\n".join(enhancements) + "\n\n"
            return context_header + prompt
        
        return prompt
