#!/usr/bin/env python3
"""
HTML Documentation Generator
Generates HTML documentation from analysis results using HTML templates.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime
from .diagram_generator import DiagramGenerator


class HTMLGenerator:
    """Generates HTML documentation from analysis results using HTML templates."""
    
    def __init__(self, template_dir: str = "html_templates", output_dir: str = "docs", config: Dict[str, Any] = None):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.config = config or {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up Jinja2 environment for HTML templates
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True  # Enable autoescape for HTML
        )
        
        # Add custom filters
        self.env.filters['format_complexity'] = self._format_complexity
        self.env.filters['truncate_docstring'] = self._truncate_docstring
        self.env.filters['format_list'] = self._format_list
        self.env.filters['to_json'] = lambda obj: json.dumps(obj, default=str)
    
    def generate_all_documentation(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> Dict[str, str]:
        """Generate all documentation pages from analysis results."""
        
        docs = {}
        
        # Generate each documentation section with enhanced analysis
        docs['index.html'] = self.generate_index_page(code_analysis, ai_analysis, enhanced_analysis)
        docs['architecture.html'] = self.generate_architecture_page(code_analysis, enhanced_analysis)
        docs['modules.html'] = self.generate_modules_page(code_analysis, enhanced_analysis)
        docs['all_modules.html'] = self.generate_all_modules_page(code_analysis, enhanced_analysis)
        docs['api.html'] = self.generate_api_page(code_analysis, enhanced_analysis)
        docs['onboarding.html'] = self.generate_onboarding_page(code_analysis, ai_analysis)
        docs['ai_models.html'] = self.generate_ai_models_page(ai_analysis)
        docs['ai_pipelines.html'] = self.generate_ai_pipelines_page(ai_analysis)
        docs['components.html'] = self.generate_components_page(code_analysis, enhanced_analysis)
        docs['complexity.html'] = self.generate_complexity_page(code_analysis)
        
        # Store enhanced analysis for use by main.py
        if enhanced_analysis:
            docs['enhanced_analysis'] = enhanced_analysis
        
        return docs
    
    def generate_index_page(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> str:
        """Generate the main index page."""
        
        # Extract project name from analysis or path
        project_name = self._extract_project_name(code_analysis)
        overview = code_analysis.get('overview', {})
        
        # Prepare data for the template
        context = {
            'title': f'{project_name} Documentation',
            'project_name': project_name,
            'project_title': f'{project_name} Documentation',
            'project_description': f'Comprehensive documentation for the {project_name} {overview.get("project_type", "application")}. This trading platform uses advanced AI/ML techniques for market analysis and intelligent trading suggestions.',
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_files': overview.get('total_files', len(code_analysis.get('modules', []))),
            'total_functions': overview.get('total_functions', sum(len(m.get('functions', [])) for m in code_analysis.get('modules', []))),
            'total_classes': overview.get('total_classes', sum(len(m.get('classes', [])) for m in code_analysis.get('modules', []))),
            'total_lines': overview.get('total_lines', sum(m.get('lines_of_code', 0) for m in code_analysis.get('modules', []))),
            'project_type': overview.get('project_type', 'Unknown'),
            'languages_detected': overview.get('languages_detected', []),
            'frameworks_detected': ai_analysis.get('frameworks_detected', []),
            'has_ai_components': bool(ai_analysis.get('ml_models', [])),
            'ml_models_count': len(ai_analysis.get('ml_models', [])),
            'code_analysis': code_analysis,
            'ai_analysis': ai_analysis
        }
        
        template = self.env.get_template('index.html')
        return template.render(**context)
    
    def generate_architecture_page(self, code_analysis: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> str:
        """Generate architecture documentation page."""
        
        # Extract project name and overview
        project_name = self._extract_project_name(code_analysis)
        overview = code_analysis.get('overview', {})
        
        # Process modules for architecture diagram
        modules = code_analysis.get('modules', [])
        components = self._analyze_components(modules)
        
        # Get enhanced architecture data if available
        enhanced_arch = enhanced_analysis.get('architecture_analysis', {}) if enhanced_analysis else {}
        enhanced_components = enhanced_analysis.get('component_analysis', {}) if enhanced_analysis else {}
        enhanced_diagrams = enhanced_analysis.get('diagrams', {}) if enhanced_analysis else {}
        
        context = {
            'title': f'{project_name} Architecture',
            'project_name': project_name,
            'project_type': overview.get('project_type', 'Application'),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'components': components,
            'modules': modules,
            'total_modules': len(modules),
            'architecture_patterns': self._detect_architecture_patterns(code_analysis),
            'code_analysis': code_analysis,
            'diagrams': enhanced_diagrams,  # AI-enhanced diagrams
            'enhanced_architecture': enhanced_arch,
            'enhanced_components': enhanced_components,
            'architecture_layers': enhanced_arch.get('layers', []),
            'design_patterns': enhanced_arch.get('patterns', []),
            'architecture_principles': enhanced_arch.get('principles', [])
        }
        
        template = self.env.get_template('architecture.html')
        return template.render(**context)
    
    def generate_modules_page(self, code_analysis: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> str:
        """Generate modules documentation page with class diagrams."""
        
        # Extract project name and modules
        project_name = self._extract_project_name(code_analysis)
        modules = code_analysis.get('modules', [])
        
        # Get enhanced module diagrams if available
        enhanced_diagrams = enhanced_analysis.get('diagrams', {}) if enhanced_analysis else {}
        
        # Sort modules by complexity/importance
        sorted_modules = sorted(modules, key=lambda m: (
            len(m.get('classes', [])) * 2 + 
            len(m.get('functions', [])) + 
            m.get('lines_of_code', 0) / 100
        ), reverse=True)
        
        context = {
            'title': f'{project_name} Modules',
            'project_name': project_name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'modules': sorted_modules,
            'total_modules': len(modules),
            'total_classes': sum(len(m.get('classes', [])) for m in modules),
            'total_functions': sum(len(m.get('functions', [])) for m in modules),
            'total_lines': sum(m.get('lines_of_code', 0) for m in modules),
            'code_analysis': code_analysis,
            'diagrams': enhanced_diagrams,
            'enhanced_analysis': enhanced_analysis
        }
        
        template = self.env.get_template('modules.html')
        return template.render(**context)

    def generate_components_page(self, code_analysis: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> str:
        """Generate standalone Components page (JS-populated grid)."""
        project_name = self._extract_project_name(code_analysis)
        context = {
            'title': f'{project_name} Components',
            'project_name': project_name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        template = self.env.get_template('components.html')
        return template.render(**context)

    def generate_all_modules_page(self, code_analysis: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> str:
        """Generate Key Contributing Modules page with an all-modules table."""
        project_name = self._extract_project_name(code_analysis)
        modules = code_analysis.get('modules', [])
        sorted_modules = sorted(modules, key=lambda m: (
            len(m.get('classes', [])) * 2 +
            len(m.get('functions', [])) +
            m.get('lines_of_code', 0) / 100
        ), reverse=True)
        context = {
            'title': f'{project_name} Key Contributing Modules',
            'project_name': project_name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'modules': sorted_modules,
            'total_modules': len(modules),
            'total_classes': sum(len(m.get('classes', [])) for m in modules),
            'total_functions': sum(len(m.get('functions', [])) for m in modules),
            'total_lines': sum(m.get('lines_of_code', 0) for m in modules),
            'code_analysis': code_analysis,
            'enhanced_analysis': enhanced_analysis
        }
        template = self.env.get_template('all_modules.html')
        return template.render(**context)
    
    def generate_api_page(self, code_analysis: Dict[str, Any], enhanced_analysis: Dict[str, Any] = None) -> str:
        """Generate API documentation page."""
        
        # Extract API endpoints and interfaces
        api_endpoints = self._extract_api_endpoints(code_analysis)
        
        # Get enhanced API data if available
        enhanced_api = enhanced_analysis.get('api_analysis', {}) if enhanced_analysis else {}
        
        context = {
            'title': 'API Reference',
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'api_endpoints': api_endpoints,
            'classes': code_analysis.get('classes', []),
            'functions': code_analysis.get('functions', []),
            'code_analysis': code_analysis,
            'enhanced_api': enhanced_api,
            'api_interfaces': enhanced_api.get('interfaces', []),
            'api_patterns': enhanced_api.get('patterns', []),
            'api_diagram': enhanced_analysis.get('diagrams', {}).get('api', {}) if enhanced_analysis else {}
        }
        
        template = self.env.get_template('api.html')
        return template.render(**context)
    
    def generate_onboarding_page(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> str:
        """Generate developer onboarding guide."""
        
        # Find entry points and key modules
        entry_points = self._find_entry_points(code_analysis)
        key_modules = self._identify_key_modules(code_analysis)
        
        context = {
            'title': 'Developer Onboarding',
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'project_name': code_analysis.get('project_name', 'Project'),
            'entry_points': entry_points,
            'key_modules': key_modules,
            'has_ai_components': bool(ai_analysis.get('ml_models', [])),
            'frameworks': ai_analysis.get('frameworks_detected', []),
            'setup_files': {
                'requirements': Path('requirements.txt').exists(),
                'setup_py': Path('setup.py').exists()
            },
            'code_analysis': code_analysis,
            'ai_analysis': ai_analysis
        }
        
        template = self.env.get_template('onboarding.html')
        return template.render(**context)
    
    def generate_ai_models_page(self, ai_analysis: Dict[str, Any]) -> str:
        """Generate AI models documentation page."""
        
        # Safely extract models and other AI analysis data
        models = ai_analysis.get('ml_models', []) if ai_analysis else []
        training_scripts = ai_analysis.get('training_scripts', []) if ai_analysis else []
        inference_endpoints = ai_analysis.get('inference_endpoints', []) if ai_analysis else []
        frameworks_detected = ai_analysis.get('frameworks_detected', []) if ai_analysis else []
        
        # Extract project name dynamically
        project_name = ai_analysis.get('project_name', 'Project') if ai_analysis else 'Project'
        
        context = {
            'title': 'AI Models & Machine Learning',
            'project_name': project_name,
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ml_models': models,
            'total_models': len(models),
            'frameworks_detected': frameworks_detected,
            'training_scripts': len(training_scripts),
            'inference_endpoints': len(inference_endpoints),
            'ai_analysis': ai_analysis or {}
        }
        
        template = self.env.get_template('ai_models.html')
        return template.render(**context)
    
    def generate_ai_pipelines_page(self, ai_analysis: Dict[str, Any]) -> str:
        """Generate AI pipelines documentation page."""
        
        context = {
            'title': 'AI Pipelines',
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pipelines': ai_analysis.get('pipelines', []),
            'data_flows': ai_analysis.get('data_flows', []),
            'ai_analysis': ai_analysis
        }
        
        template = self.env.get_template('ai_pipelines.html')
        return template.render(**context)
    
    def generate_complexity_page(self, code_analysis: Dict[str, Any]) -> str:
        """Generate code complexity documentation page."""
        
        complexity_data = self._calculate_complexity_metrics(code_analysis)
        
        # Derive additional metrics expected by the template
        complexity_values = []
        for module in code_analysis.get('modules', []):
            for func in module.get('functions', []):
                if isinstance(func, dict):
                    try:
                        complexity_values.append(int(func.get('complexity', 0)))
                    except Exception:
                        continue
        
        average_complexity = (sum(complexity_values) / len(complexity_values)) if complexity_values else 0
        max_complexity = max(complexity_values) if complexity_values else 0
        
        # Transform high complexity functions to the shape expected by the template
        high_funcs_raw = complexity_data.get('high_complexity_functions', [])
        high_funcs = []
        for item in high_funcs_raw:
            high_funcs.append({
                'name': item.get('name', ''),
                'module': item.get('file', ''),
                'complexity': item.get('complexity', 0),
                'line_number': item.get('line', 0),
                'suggestion': 'Refactor into smaller units'
            })
        
        context = {
            'title': 'Code Quality',
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            # Backwards-compatible keys used by complexity.html
            'complexity_analysis': {
                'average_complexity': average_complexity,
                'max_complexity': max_complexity,
                'high_complexity_functions': len(high_funcs)
            },
            'high_complexity_functions': high_funcs,
            'modules': code_analysis.get('modules', []),
            'total_lines': complexity_data.get('total_lines', 0),
            # Keep original payloads for future use
            'complexity_data': complexity_data,
            'code_analysis': code_analysis
        }
        
        template = self.env.get_template('complexity.html')
        return template.render(**context)
    
    def save_documentation(self, docs: Dict[str, str]) -> None:
        """Save generated documentation to files."""
        for filename, content in docs.items():
            # Skip non-string content (like metadata dictionaries)
            if not isinstance(content, str):
                continue
                
            output_path = self.output_dir / filename
            output_path.write_text(content, encoding='utf-8')
            print(f"Generated: {output_path}")
        
        # Copy assets if they exist in template directory
        self._copy_assets()
    
    def _copy_assets(self) -> None:
        """Copy CSS, JS, and other assets from template directory."""
        import shutil
        
        assets_src = self.template_dir / "assets"
        assets_dest = self.output_dir / "assets"
        
        if assets_src.exists():
            if assets_dest.exists():
                shutil.rmtree(assets_dest)
            shutil.copytree(assets_src, assets_dest)
            print(f"Copied assets to: {assets_dest}")
    
    # Helper methods
    def _analyze_components(self, modules: list) -> list:
        """Analyze modules to identify high-level components."""
        components = {}
        
        for module in modules:
            # Group modules by directory structure
            path_parts = Path(module.get('path', '')).parts
            if len(path_parts) > 1:
                component_name = path_parts[0]
                if component_name not in components:
                    components[component_name] = {
                        'name': component_name.title(),
                        'files': 0,
                        'functions': 0,
                        'classes': 0,
                        'description': f"{component_name.title()} components"
                    }
                
                components[component_name]['files'] += 1
                components[component_name]['functions'] += len(module.get('functions', []))
                components[component_name]['classes'] += len(module.get('classes', []))
        
        return list(components.values())
    
    def _detect_architecture_patterns(self, code_analysis: Dict[str, Any]) -> list:
        """Detect common architecture patterns in the codebase."""
        patterns = []
        
        # Look for MVC pattern
        modules = [m.get('path', '') for m in code_analysis.get('modules', [])]
        if any('controller' in m.lower() or 'view' in m.lower() or 'model' in m.lower() for m in modules):
            patterns.append("MVC")
        
        # Look for Repository pattern
        if any('repository' in m.lower() for m in modules):
            patterns.append("Repository")
        
        # Look for Service pattern
        if any('service' in m.lower() for m in modules):
            patterns.append("Service Layer")
        
        return patterns
    
    def _extract_api_endpoints(self, code_analysis: Dict[str, Any]) -> list:
        """Extract API endpoints from the codebase analysis."""
        endpoints = []
        
        # Look for Flask/FastAPI routes in project files only (exclude venv and site-packages)
        for module in code_analysis.get('modules', []):
            module_path = module.get('path', '')
            
            # Filter out virtual environment and third-party library files
            if self._is_project_file(module_path):
                for func in module.get('functions', []):
                    # Handle both string and dict function representations
                    if isinstance(func, dict):
                        decorators = func.get('decorators', [])
                        func_name = func.get('name', '')
                        func_docstring = func.get('docstring', '')
                    elif isinstance(func, str):
                        # If func is just a string (function name), skip decorator checking
                        continue
                    else:
                        continue
                        
                    for decorator in decorators:
                        if isinstance(decorator, str) and any(route in decorator.lower() for route in ['route', 'get', 'post', 'put', 'delete']):
                            endpoints.append({
                                'method': self._extract_http_method(decorator),
                                'endpoint': func_name,
                                'file': module_path,
                                'description': func_docstring.split('\n')[0] if func_docstring else 'No description'
                            })
        
        return endpoints
    
    def _is_project_file(self, file_path: str) -> bool:
        """Check if a file is part of the actual project (not venv or third-party)."""
        # Get exclusion patterns from configuration
        api_config = self.config.get('analysis', {}).get('api_documentation', {})
        
        # Check if API filtering is enabled
        if not api_config.get('include_only_project_files', True):
            return True
            
        # Get exclusion patterns from config
        excluded_paths = api_config.get('exclude_from_api_reference', [])
        
        # Convert to lowercase for case-insensitive matching
        path_lower = file_path.lower()
        
        # Return False if path contains any excluded patterns
        for excluded in excluded_paths:
            excluded_lower = excluded.lower()
            if excluded_lower in path_lower:
                return False
        
        return True
    
    def _extract_http_method(self, decorator: str) -> str:
        """Extract HTTP method from decorator string."""
        decorator_lower = decorator.lower()
        if 'post' in decorator_lower:
            return 'POST'
        elif 'put' in decorator_lower:
            return 'PUT'
        elif 'delete' in decorator_lower:
            return 'DELETE'
        else:
            return 'GET'
    
    def _find_entry_points(self, code_analysis: Dict[str, Any]) -> list:
        """Find main entry points in the codebase."""
        entry_points = []
        
        for module in code_analysis.get('modules', []):
            # Look for main.py, app.py, or files with if __name__ == "__main__"
            module_path = module.get('path', '')
            if any(name in module_path.lower() for name in ['main.py', 'app.py', 'run.py']):
                module_docstring = module.get('docstring', '')
                entry_points.append({
                    'name': Path(module_path).stem,
                    'file': module_path,
                    'description': module_docstring.split('\n')[0] if module_docstring else 'Main entry point'
                })
        
        return entry_points
    
    def _identify_key_modules(self, code_analysis: Dict[str, Any]) -> list:
        """Identify key modules for onboarding."""
        modules = []
        
        for module in code_analysis.get('modules', []):
            # Prioritize modules with many functions/classes or important names
            functions_count = len(module.get('functions', []))
            classes_count = len(module.get('classes', []))
            module_path = module.get('path', '')
            module_docstring = module.get('docstring', '')
            
            # Score based on content and importance
            score = functions_count + classes_count * 2
            
            # Boost score for important directory names
            important_dirs = ['core', 'main', 'service', 'api', 'model', 'controller']
            if any(dir_name in module_path.lower() for dir_name in important_dirs):
                score += 10
            
            if score > 5:  # Threshold for "key" modules
                modules.append({
                    'name': Path(module_path).stem,
                    'path': module_path,
                    'description': module_docstring.split('\n')[0] if module_docstring else f'Contains {functions_count} functions and {classes_count} classes',
                    'score': score
                })
        
        # Sort by score and return top modules
        modules.sort(key=lambda x: x['score'], reverse=True)
        return modules[:10]  # Top 10 key modules
    
    def _calculate_complexity_metrics(self, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate complexity metrics from code analysis."""
        metrics = {
            'total_files': len(code_analysis.get('modules', [])),
            'total_functions': 0,
            'total_classes': 0,
            'total_lines': 0,
            'high_complexity_functions': [],
            'complexity_distribution': {'low': 0, 'medium': 0, 'high': 0}
        }
        
        for module in code_analysis.get('modules', []):
            functions = module.get('functions', [])
            classes = module.get('classes', [])
            
            # Handle both string and dict representations
            if isinstance(functions, list):
                metrics['total_functions'] += len(functions)
            if isinstance(classes, list):
                metrics['total_classes'] += len(classes)
            
            metrics['total_lines'] += module.get('lines_of_code', 0)
            
            # Analyze function complexity
            for func in functions:
                if isinstance(func, dict):
                    complexity = func.get('complexity', 1)
                    if complexity > 10:
                        metrics['high_complexity_functions'].append({
                            'name': func.get('name', ''),
                            'file': module.get('path', ''),
                            'complexity': complexity,
                            'line': func.get('line_number', 0)
                        })
                    
                    # Categorize complexity
                    if complexity <= 5:
                        metrics['complexity_distribution']['low'] += 1
                    elif complexity <= 10:
                        metrics['complexity_distribution']['medium'] += 1
                    else:
                        metrics['complexity_distribution']['high'] += 1
        
        return metrics
    
    # Custom Jinja2 filters
    def _format_complexity(self, complexity: int) -> str:
        """Format complexity score with color coding."""
        if complexity <= 5:
            return f'<span class="complexity-low">{complexity}</span>'
        elif complexity <= 10:
            return f'<span class="complexity-medium">{complexity}</span>'
        else:
            return f'<span class="complexity-high">{complexity}</span>'
    
    def _truncate_docstring(self, docstring: str, max_length: int = 200) -> str:
        """Truncate docstring to specified length."""
        if not docstring:
            return ""
        
        if len(docstring) <= max_length:
            return docstring
        
        # Try to truncate at sentence boundary
        truncated = docstring[:max_length]
        last_period = truncated.rfind('.')
        if last_period > max_length * 0.7:  # If we can find a period in the last 30%
            return truncated[:last_period + 1]
        else:
            return truncated + "..."
    
    def _extract_project_name(self, code_analysis: Dict[str, Any]) -> str:
        """Extract project name from code analysis or default to directory name."""
        # Try to get project name from analysis
        if 'project_name' in code_analysis:
            return code_analysis['project_name']
        
        # Try to extract from repository path if available
        if 'repository_path' in code_analysis:
            return Path(code_analysis['repository_path']).name.title()
        
        # Try to extract from overview
        overview = code_analysis.get('overview', {})
        if 'project_name' in overview:
            return overview['project_name']
        
        # Look for main module or common patterns
        modules = code_analysis.get('modules', [])
        for module in modules:
            if module.get('is_main', False):
                # Extract project name from main module path
                module_path = module.get('path', '')
                if module_path:
                    return Path(module_path).parent.name.title()
    
    def _format_list(self, items: list, max_items: int = 5) -> str:
        """Format a list for display, truncating if necessary."""
        if not items:
            return ""
        
        if len(items) <= max_items:
            return ", ".join(str(item) for item in items)
        else:
            shown = ", ".join(str(item) for item in items[:max_items])
            remaining = len(items) - max_items
            return f"{shown} (and {remaining} more)"
