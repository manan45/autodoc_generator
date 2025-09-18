import ast
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
import re
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit


class CodeAnalyzer:
    """Analyzes Python codebase structure and generates insights."""
    
    def __init__(self, repo_path: str, config: Dict[str, Any] = None):
        self.repo_path = Path(repo_path)
        self.config = config or {}
        self.analysis_results = {}
        
        # Patterns from config
        analysis_config = self.config.get('analysis', {})
        self.include_patterns = analysis_config.get('include_patterns', ['*.py'])
        self.exclude_patterns = analysis_config.get('exclude_patterns', [])
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze entire codebase structure and generate insights."""
        print(f"Analyzing codebase at: {self.repo_path}")
        
        # Generate components first
        modules = self._analyze_modules()
        classes = self._analyze_classes()
        functions = self._analyze_functions()
        dependencies = self._analyze_dependencies()
        complexity = self._analyze_complexity()
        data_flow = self._analyze_data_flow()
        architecture = self._analyze_architecture()
        
        # Generate overview using complexity analysis for accurate function count
        overview = self._generate_overview()
        # Override function count with complexity analysis count for accuracy
        overview['total_functions'] = complexity.get('summary', {}).get('total_functions', overview['total_functions'])
        
        results = {
            'overview': overview,
            'modules': modules,
            'classes': classes,
            'functions': functions,
            'dependencies': dependencies,
            'complexity': complexity,
            'data_flow': data_flow,
            'architecture': architecture
        }
        
        self.analysis_results = results
        return results
    
    def _generate_overview(self) -> Dict[str, Any]:
        """Generate project overview statistics."""
        all_python_files = list(self.repo_path.rglob('*.py'))
        
        total_lines = 0
        total_functions = 0
        total_classes = 0
        analyzed_files = 0
        
        for py_file in all_python_files:
            if self._should_exclude_file(py_file):
                continue
            
            analyzed_files += 1
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_lines += len(content.split('\n'))
                    
                    tree = ast.parse(content)
                    total_functions += len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
                    total_classes += len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                    
            except Exception as e:
                print(f"Error analyzing overview for {py_file}: {e}")
        
        return {
            'total_files': analyzed_files,
            'total_lines': total_lines,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'languages_detected': self._detect_languages(),
            'project_type': self._detect_project_type()
        }
    
    def _analyze_modules(self) -> List[Dict]:
        """Extract module information and docstrings."""
        modules = []
        
        for py_file in self.repo_path.rglob('*.py'):
            if self._should_exclude_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                module_info = {
                    'name': py_file.stem,
                    'path': str(py_file.relative_to(self.repo_path)),
                    'docstring': ast.get_docstring(tree),
                    'classes': [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)],
                    'functions': [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)],
                    'imports': self._extract_imports(tree),
                    'lines_of_code': len(content.split('\n')),
                    'is_main': py_file.name == 'main.py' or py_file.name == '__main__.py'
                }
                modules.append(module_info)
                
            except Exception as e:
                print(f"Error analyzing module {py_file}: {e}")
        
        return modules
    
    def _analyze_classes(self) -> List[Dict]:
        """Analyze class definitions and their methods with detailed information."""
        classes = []
        
        for py_file in self.repo_path.rglob('*.py'):
            if self._should_exclude_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Analyze methods in detail
                        methods = []
                        properties = []
                        class_methods = []
                        static_methods = []
                        
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                method_info = {
                                    'name': item.name,
                                    'docstring': ast.get_docstring(item),
                                    'parameters': [arg.arg for arg in item.args.args],
                                    'decorators': [self._get_node_name(dec) for dec in item.decorator_list],
                                    'is_property': any('property' in str(dec).lower() for dec in item.decorator_list),
                                    'is_staticmethod': any('staticmethod' in str(dec).lower() for dec in item.decorator_list),
                                    'is_classmethod': any('classmethod' in str(dec).lower() for dec in item.decorator_list),
                                    'returns_type': self._get_node_name(item.returns) if item.returns else None,
                                    'line_number': item.lineno
                                }
                                
                                # Categorize methods
                                if method_info['is_property']:
                                    properties.append(method_info)
                                elif method_info['is_classmethod']:
                                    class_methods.append(method_info)
                                elif method_info['is_staticmethod']:
                                    static_methods.append(method_info)
                                else:
                                    methods.append(method_info)
                        
                        # Determine class category
                        class_category = self._categorize_class(node.name, node)
                        
                        class_info = {
                            'name': node.name,
                            'file': str(py_file.relative_to(self.repo_path)),
                            'docstring': ast.get_docstring(node),
                            'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],  # Keep for backward compatibility
                            'method_details': methods,
                            'properties': properties,
                            'class_methods': class_methods,
                            'static_methods': static_methods,
                            'bases': [self._get_node_name(base) for base in node.bases],
                            'decorators': [self._get_node_name(dec) for dec in node.decorator_list],
                            'line_number': node.lineno,
                            'end_line': getattr(node, 'end_lineno', node.lineno),
                            'category': class_category,
                            'is_abstract': any('abc' in str(base).lower() or 'abstract' in str(base).lower() for base in node.bases),
                            'is_exception': any('exception' in str(base).lower() or 'error' in str(base).lower() for base in node.bases)
                        }
                        classes.append(class_info)
                        
            except Exception as e:
                print(f"Error analyzing classes in {py_file}: {e}")
        
        return classes
    
    def _analyze_functions(self) -> List[Dict]:
        """Analyze function definitions with detailed information."""
        functions = []
        
        for py_file in self.repo_path.rglob('*.py'):
            if self._should_exclude_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Extract detailed parameter information
                        parameters = []
                        for arg in node.args.args:
                            param_info = {
                                'name': arg.arg,
                                'type': self._get_node_name(arg.annotation) if arg.annotation else 'Any',
                                'has_default': False
                            }
                            parameters.append(param_info)
                        
                        # Handle default values
                        defaults = node.args.defaults
                        if defaults:
                            for i, default in enumerate(defaults):
                                param_idx = len(parameters) - len(defaults) + i
                                if param_idx >= 0 and param_idx < len(parameters):
                                    parameters[param_idx]['has_default'] = True
                                    parameters[param_idx]['default_value'] = self._get_node_name(default)
                        
                        # Extract function complexity
                        func_complexity = self._calculate_function_complexity(node)
                        
                        # Determine function category
                        func_category = self._categorize_function(node.name, node)
                        
                        func_info = {
                            'name': node.name,
                            'file': str(py_file.relative_to(self.repo_path)),
                            'docstring': ast.get_docstring(node),
                            'parameters': parameters,
                            'args': [arg.arg for arg in node.args.args],  # Keep for backward compatibility
                            'decorators': [self._get_node_name(dec) for dec in node.decorator_list],
                            'line_number': node.lineno,
                            'end_line': getattr(node, 'end_lineno', node.lineno),
                            'is_async': isinstance(node, ast.AsyncFunctionDef),
                            'returns_type': self._get_node_name(node.returns) if node.returns else None,
                            'complexity': func_complexity,
                            'category': func_category,
                            'is_property': any('property' in str(dec).lower() for dec in node.decorator_list),
                            'is_staticmethod': any('staticmethod' in str(dec).lower() for dec in node.decorator_list),
                            'is_classmethod': any('classmethod' in str(dec).lower() for dec in node.decorator_list),
                            'calls_made': self._extract_function_calls(node)
                        }
                        functions.append(func_info)
                        
            except Exception as e:
                print(f"Error analyzing functions in {py_file}: {e}")
        
        return functions
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze import dependencies and create dependency graph."""
        dependencies = {
            'internal': {},
            'external': set(),
            'graph': {}
        }
        
        for py_file in self.repo_path.rglob('*.py'):
            if self._should_exclude_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                file_deps = self._extract_imports(tree)
                module_name = str(py_file.relative_to(self.repo_path))
                
                dependencies['graph'][module_name] = file_deps
                
                for dep in file_deps:
                    if dep.startswith('.') or any(dep.startswith(p) for p in ['src', 'app']):
                        # Internal dependency
                        if module_name not in dependencies['internal']:
                            dependencies['internal'][module_name] = []
                        dependencies['internal'][module_name].append(dep)
                    else:
                        # External dependency
                        dependencies['external'].add(dep.split('.')[0])
                        
            except Exception as e:
                print(f"Error analyzing dependencies in {py_file}: {e}")
        
        dependencies['external'] = list(dependencies['external'])
        return dependencies
    
    def _analyze_complexity(self) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        complexity_results = {
            'files': [],
            'summary': {
                'avg_complexity': 0,
                'max_complexity': 0,
                'total_functions': 0,
                'high_complexity_functions': []
            }
        }
        
        total_complexity = 0
        total_functions = 0
        
        for py_file in self.repo_path.rglob('*.py'):
            if self._should_exclude_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Cyclomatic complexity
                cc_results = cc_visit(content)
                
                # Maintainability index
                mi_score = mi_visit(content, multi=True)
                
                # Halstead metrics
                h_metrics = h_visit(content)
                
                file_complexity = {
                    'file': str(py_file.relative_to(self.repo_path)),
                    'cyclomatic_complexity': [
                        {
                            'name': result.name,
                            'complexity': result.complexity,
                            'rank': getattr(result, 'rank', 'A')  # Default rank if not available
                        } for result in cc_results
                    ],
                    'maintainability_index': mi_score,
                    'halstead_metrics': h_metrics
                }
                
                complexity_results['files'].append(file_complexity)
                
                # Update summary - use radon's count which includes all callable units
                for result in cc_results:
                    total_complexity += result.complexity
                    total_functions += 1
                    
                    if result.complexity > complexity_results['summary']['max_complexity']:
                        complexity_results['summary']['max_complexity'] = result.complexity
                    
                    if result.complexity > 10:  # High complexity threshold
                        complexity_results['summary']['high_complexity_functions'].append({
                            'name': result.name,
                            'file': str(py_file.relative_to(self.repo_path)),
                            'complexity': result.complexity
                        })
                
            except Exception as e:
                print(f"Error analyzing complexity for {py_file}: {e}")
        
        if total_functions > 0:
            complexity_results['summary']['avg_complexity'] = total_complexity / total_functions
            complexity_results['summary']['total_functions'] = total_functions
        
        return complexity_results
    
    def _analyze_data_flow(self) -> Dict[str, Any]:
        """Analyze comprehensive data flow patterns in the codebase."""
        data_flow = {
            'entry_points': [],
            'data_transformations': [],
            'output_points': [],
            'data_stores': [],
            'validators': [],
            'flow_chains': []
        }
        
        # Enhanced pattern recognition
        entry_patterns = ['main', 'run', 'start', 'execute', 'app', 'serve', 'launch']
        transform_patterns = ['process', 'transform', 'convert', 'parse', 'clean', 'filter', 'map', 'reduce']
        output_patterns = ['save', 'write', 'export', 'send', 'publish', 'output', 'render']
        store_patterns = ['load', 'read', 'fetch', 'get', 'retrieve', 'query', 'find']
        validate_patterns = ['validate', 'verify', 'check', 'is_', 'has_', 'ensure']
        
        for py_file in self.repo_path.rglob('*.py'):
            if self._should_exclude_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_name = node.name.lower()
                        docstring = ast.get_docstring(node) or ""
                        
                        # Enhanced entry point detection
                        if (any(pattern in func_name for pattern in entry_patterns) or 
                            func_name == '__main__' or 
                            'entry' in docstring.lower()):
                            data_flow['entry_points'].append({
                                'name': node.name,
                                'file': str(py_file.relative_to(self.repo_path)),
                                'line': node.lineno,
                                'description': docstring[:100] + '...' if len(docstring) > 100 else docstring,
                                'parameters': [arg.arg for arg in node.args.args]
                            })
                        
                        # Enhanced data transformations
                        if any(pattern in func_name for pattern in transform_patterns):
                            data_flow['data_transformations'].append({
                                'name': node.name,
                                'file': str(py_file.relative_to(self.repo_path)),
                                'line': node.lineno,
                                'description': docstring[:100] + '...' if len(docstring) > 100 else docstring,
                                'type': self._classify_transformation(func_name),
                                'parameters': [arg.arg for arg in node.args.args]
                            })
                        
                        # Output points
                        if any(pattern in func_name for pattern in output_patterns):
                            data_flow['output_points'].append({
                                'name': node.name,
                                'file': str(py_file.relative_to(self.repo_path)),
                                'line': node.lineno,
                                'description': docstring[:100] + '...' if len(docstring) > 100 else docstring,
                                'type': self._classify_output(func_name)
                            })
                        
                        # Data stores
                        if any(pattern in func_name for pattern in store_patterns):
                            data_flow['data_stores'].append({
                                'name': node.name,
                                'file': str(py_file.relative_to(self.repo_path)),
                                'line': node.lineno,
                                'description': docstring[:100] + '...' if len(docstring) > 100 else docstring,
                                'type': self._classify_data_store(func_name)
                            })
                        
                        # Validators
                        if any(pattern in func_name for pattern in validate_patterns):
                            data_flow['validators'].append({
                                'name': node.name,
                                'file': str(py_file.relative_to(self.repo_path)),
                                'line': node.lineno,
                                'description': docstring[:100] + '...' if len(docstring) > 100 else docstring,
                                'returns_boolean': 'bool' in str(node.returns).lower() if node.returns else True
                            })
                
            except Exception as e:
                print(f"Error analyzing data flow in {py_file}: {e}")
        
        # Analyze flow chains
        data_flow['flow_chains'] = self._analyze_flow_chains(data_flow)
        
        return data_flow
    
    def _analyze_architecture(self) -> Dict[str, Any]:
        """Analyze overall architecture patterns."""
        architecture = {
            'patterns': [],
            'layers': [],
            'components': []
        }
        
        # Detect common architectural patterns
        directories = [d for d in self.repo_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        pattern_indicators = {
            'MVC': ['models', 'views', 'controllers'],
            'Layered': ['presentation', 'business', 'data', 'services'],
            'Microservices': ['services', 'api', 'gateway'],
            'Repository': ['repositories', 'models', 'entities'],
            'Clean Architecture': ['domain', 'infrastructure', 'application', 'interface']
        }
        
        for pattern, indicators in pattern_indicators.items():
            if any(any(indicator in d.name.lower() for d in directories) for indicator in indicators):
                architecture['patterns'].append(pattern)
        
        # Identify layers based on directory structure
        for directory in directories:
            layer_type = self._classify_directory(directory.name)
            if layer_type:
                architecture['layers'].append({
                    'name': directory.name,
                    'type': layer_type,
                    'files': len(list(directory.rglob('*.py')))
                })
        
        return architecture
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    
    def _get_node_name(self, node: ast.AST) -> str:
        """Get string representation of AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return str(node.__class__.__name__)
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis."""
        str_path = str(file_path)
        
        # Quick exclusions for common directories
        exclude_dirs = ['venv', '.venv', 'env', '.env', '__pycache__', '.git', 
                       'node_modules', 'site-packages', 'build', 'dist', '.tox']
        
        # Check if any part of the path contains excluded directories
        path_parts = Path(str_path).parts
        for part in path_parts:
            if part in exclude_dirs:
                return True
        
        # Additional pattern-based exclusions
        for pattern in self.exclude_patterns:
            # Convert pattern to a more precise check
            if pattern.startswith('*/') and pattern.endswith('/*'):
                # Pattern like */venv/* - check if path contains the directory
                dir_name = pattern[2:-2]  # Remove */ and /*
                if dir_name in path_parts:
                    return True
            elif pattern.replace('*', '') in str_path:
                return True
        
        return False
    
    def _detect_languages(self) -> List[str]:
        """Detect programming languages in the project."""
        languages = set()
        
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust'
        }
        
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix
                if ext in extension_map:
                    languages.add(extension_map[ext])
        
        return list(languages)
    
    def _detect_project_type(self) -> str:
        """Detect the type of project based on files and structure."""
        # Check for common framework indicators
        if (self.repo_path / 'requirements.txt').exists() or (self.repo_path / 'setup.py').exists():
            if (self.repo_path / 'app.py').exists() or any(self.repo_path.rglob('*flask*')):
                return 'Flask Web Application'
            elif any(self.repo_path.rglob('*django*')):
                return 'Django Web Application'
            elif any(self.repo_path.rglob('*fastapi*')):
                return 'FastAPI Application'
            elif any(self.repo_path.rglob('*streamlit*')):
                return 'Streamlit Application'
            else:
                return 'Python Library/Package'
        
        if (self.repo_path / 'package.json').exists():
            return 'Node.js Application'
        
        return 'General Software Project'
    
    def _classify_directory(self, dir_name: str) -> Optional[str]:
        """Classify directory type based on name."""
        dir_lower = dir_name.lower()
        
        classifications = {
            'presentation': ['views', 'templates', 'ui', 'frontend', 'web'],
            'business': ['services', 'business', 'core', 'domain', 'logic'],
            'data': ['data', 'database', 'db', 'repositories', 'models'],
            'api': ['api', 'endpoints', 'controllers', 'routes'],
            'utilities': ['utils', 'utilities', 'helpers', 'tools'],
            'configuration': ['config', 'settings', 'configuration'],
            'testing': ['test', 'tests', 'testing', 'spec']
        }
        
        for classification, keywords in classifications.items():
            if any(keyword in dir_lower for keyword in keywords):
                return classification
        
        return None
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate basic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _categorize_function(self, func_name: str, node: ast.FunctionDef) -> str:
        """Categorize function based on name and characteristics."""
        name_lower = func_name.lower()
        
        # Check for common patterns
        if func_name.startswith('_') and not func_name.startswith('__'):
            return 'private'
        elif func_name.startswith('__') and func_name.endswith('__'):
            return 'dunder'
        elif func_name.startswith('test_'):
            return 'test'
        elif any(pattern in name_lower for pattern in ['get', 'fetch', 'load', 'read', 'retrieve']):
            return 'getter'
        elif any(pattern in name_lower for pattern in ['set', 'save', 'write', 'store', 'update']):
            return 'setter'
        elif any(pattern in name_lower for pattern in ['create', 'make', 'build', 'generate']):
            return 'creator'
        elif any(pattern in name_lower for pattern in ['delete', 'remove', 'clear', 'clean']):
            return 'deleter'
        elif any(pattern in name_lower for pattern in ['process', 'transform', 'convert', 'parse']):
            return 'processor'
        elif any(pattern in name_lower for pattern in ['validate', 'check', 'verify', 'is_', 'has_']):
            return 'validator'
        elif func_name == 'main' or name_lower in ['run', 'execute', 'start']:
            return 'entry_point'
        else:
            return 'general'
    
    def _extract_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract function calls made within a function."""
        calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(self._get_node_name(child.func))
        
        return list(set(calls))  # Remove duplicates
    
    def _categorize_class(self, class_name: str, node: ast.ClassDef) -> str:
        """Categorize class based on name and characteristics."""
        name_lower = class_name.lower()
        
        # Check for common patterns
        if any('exception' in str(base).lower() or 'error' in str(base).lower() for base in node.bases):
            return 'exception'
        elif any('test' in name_lower for name_lower in [class_name.lower()]):
            return 'test'
        elif any('config' in name_lower for name_lower in [class_name.lower()]):
            return 'configuration'
        elif any(pattern in name_lower for pattern in ['analyzer', 'parser']):
            return 'analyzer'
        elif any(pattern in name_lower for pattern in ['generator', 'builder', 'factory']):
            return 'generator'
        elif any(pattern in name_lower for pattern in ['manager', 'handler', 'controller']):
            return 'manager'
        elif any(pattern in name_lower for pattern in ['model', 'entity', 'data']):
            return 'model'
        elif any(pattern in name_lower for pattern in ['view', 'template', 'ui']):
            return 'view'
        elif any(pattern in name_lower for pattern in ['service', 'client', 'api']):
            return 'service'
        elif any('abc' in str(base).lower() or 'abstract' in str(base).lower() for base in node.bases):
            return 'abstract'
        else:
            return 'general'
    
    def _classify_transformation(self, func_name: str) -> str:
        """Classify the type of data transformation."""
        name_lower = func_name.lower()
        
        if any(pattern in name_lower for pattern in ['parse', 'decode', 'deserialize']):
            return 'parser'
        elif any(pattern in name_lower for pattern in ['clean', 'sanitize', 'normalize']):
            return 'cleaner'
        elif any(pattern in name_lower for pattern in ['convert', 'transform', 'map']):
            return 'converter'
        elif any(pattern in name_lower for pattern in ['filter', 'select', 'extract']):
            return 'filter'
        elif any(pattern in name_lower for pattern in ['aggregate', 'reduce', 'summarize']):
            return 'aggregator'
        elif any(pattern in name_lower for pattern in ['validate', 'verify', 'check']):
            return 'validator'
        else:
            return 'processor'
    
    def _classify_output(self, func_name: str) -> str:
        """Classify the type of output operation."""
        name_lower = func_name.lower()
        
        if any(pattern in name_lower for pattern in ['save', 'write', 'store']):
            return 'storage'
        elif any(pattern in name_lower for pattern in ['export', 'dump', 'serialize']):
            return 'export'
        elif any(pattern in name_lower for pattern in ['send', 'transmit', 'publish']):
            return 'communication'
        elif any(pattern in name_lower for pattern in ['render', 'display', 'show']):
            return 'presentation'
        elif any(pattern in name_lower for pattern in ['log', 'print', 'output']):
            return 'logging'
        else:
            return 'output'
    
    def _classify_data_store(self, func_name: str) -> str:
        """Classify the type of data store operation."""
        name_lower = func_name.lower()
        
        if any(pattern in name_lower for pattern in ['load', 'read', 'open']):
            return 'file_reader'
        elif any(pattern in name_lower for pattern in ['fetch', 'get', 'retrieve']):
            return 'data_fetcher'
        elif any(pattern in name_lower for pattern in ['query', 'search', 'find']):
            return 'query_engine'
        elif any(pattern in name_lower for pattern in ['connect', 'init', 'setup']):
            return 'connector'
        else:
            return 'data_accessor'
    
    def _analyze_flow_chains(self, data_flow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze potential flow chains between functions."""
        chains = []
        
        # Simple heuristic: entry points -> transformations -> outputs
        entry_points = data_flow.get('entry_points', [])
        transformations = data_flow.get('data_transformations', [])
        outputs = data_flow.get('output_points', [])
        
        for entry in entry_points[:3]:  # Limit to prevent complexity
            chain = {
                'start': entry,
                'steps': [],
                'end': None
            }
            
            # Find potential transformation steps
            for transform in transformations[:5]:  # Limit steps
                if transform['file'] == entry['file']:  # Same file heuristic
                    chain['steps'].append(transform)
            
            # Find potential end points
            for output in outputs[:3]:
                if output['file'] == entry['file']:  # Same file heuristic
                    chain['end'] = output
                    break
            
            if chain['steps'] or chain['end']:
                chains.append(chain)
        
        return chains
