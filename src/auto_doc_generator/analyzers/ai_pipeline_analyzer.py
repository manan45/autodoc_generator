import re
import ast
from typing import Dict, List, Any, Optional
from pathlib import Path


class AIPipelineAnalyzer:
    """Analyzes AI/ML pipeline components and generates specialized documentation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # ML frameworks and libraries to detect
        ai_analysis_config = self.config.get('analysis', {}).get('ai_analysis', {})
        self.ml_frameworks = ai_analysis_config.get('frameworks', [
            'tensorflow', 'torch', 'pytorch', 'sklearn', 'pandas', 'numpy',
            'keras', 'mlflow', 'wandb', 'transformers', 'lightgbm', 'xgboost'
        ])
        
        # Common ML pipeline patterns
        self.pipeline_patterns = [
            r'class.*Pipeline',
            r'class.*Model',
            r'class.*Classifier',
            r'class.*Regressor',
            r'def.*train',
            r'def.*predict',
            r'def.*fit',
            r'def.*transform',
            r'def.*preprocess',
            r'def.*evaluate',
            r'def.*validate'
        ]
        
        # Data processing patterns
        self.data_patterns = [
            r'def.*load_data',
            r'def.*clean_data',
            r'def.*process_data',
            r'def.*feature_engineering',
            r'def.*feature_selection',
            r'DataFrame',
            r'\.csv',
            r'\.json',
            r'\.parquet'
        ]
    
    def analyze_ai_components(self, repo_path: Path) -> Dict[str, Any]:
        """Main method to analyze AI/ML components in the repository."""
        print("Analyzing AI/ML pipeline components...")
        
        ai_analysis = {
            'frameworks_detected': [],
            'ml_models': [],
            'pipelines': [],
            'data_processors': [],
            'training_scripts': [],
            'inference_endpoints': [],
            'experiment_tracking': [],
            'model_deployment': [],
            'data_sources': []
        }
        
        for py_file in repo_path.rglob('*.py'):
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Analyze file content
                file_analysis = self._analyze_file(content, py_file, repo_path)
                
                # Merge results
                for key in ai_analysis:
                    if key in file_analysis:
                        ai_analysis[key].extend(file_analysis[key])
                        
            except Exception as e:
                print(f"Error analyzing AI components in {py_file}: {e}")
        
        # Remove duplicates and post-process
        for key in ai_analysis:
            if isinstance(ai_analysis[key], list):
                # Remove duplicates while preserving order
                seen = set()
                unique_items = []
                for item in ai_analysis[key]:
                    if isinstance(item, dict):
                        # Use a combination of fields as identifier
                        identifier = (item.get('name', ''), item.get('file', ''))
                        if identifier not in seen:
                            seen.add(identifier)
                            unique_items.append(item)
                    elif item not in seen:
                        seen.add(item)
                        unique_items.append(item)
                ai_analysis[key] = unique_items
        
        return ai_analysis
    
    def _analyze_file(self, content: str, file_path: Path, repo_path: Path) -> Dict[str, Any]:
        """Analyze a single file for AI/ML components."""
        results = {
            'frameworks_detected': [],
            'ml_models': [],
            'pipelines': [],
            'data_processors': [],
            'training_scripts': [],
            'inference_endpoints': [],
            'experiment_tracking': [],
            'model_deployment': [],
            'data_sources': []
        }
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return results
        
        relative_path = str(file_path.relative_to(repo_path))
        
        # Detect frameworks through imports
        imports = self._extract_imports(tree)
        for imp in imports:
            for framework in self.ml_frameworks:
                if framework in imp.lower():
                    results['frameworks_detected'].append(framework)
        
        # Analyze classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_analysis = self._analyze_class(node, content, relative_path)
                for key, value in class_analysis.items():
                    if value:
                        results[key].extend(value)
            
            elif isinstance(node, ast.FunctionDef):
                func_analysis = self._analyze_function(node, content, relative_path)
                for key, value in func_analysis.items():
                    if value:
                        results[key].extend(value)
        
        # Analyze file-level patterns
        file_analysis = self._analyze_file_patterns(content, relative_path)
        for key, value in file_analysis.items():
            if value:
                results[key].extend(value)
        
        return results
    
    def _analyze_class(self, node: ast.ClassDef, content: str, file_path: str) -> Dict[str, List]:
        """Analyze a class for ML patterns."""
        results = {
            'ml_models': [],
            'pipelines': [],
            'data_processors': []
        }
        
        class_name = node.name
        docstring = ast.get_docstring(node) or ""
        
        # Check if it's a model class
        model_indicators = ['model', 'classifier', 'regressor', 'network', 'estimator']
        if any(indicator in class_name.lower() for indicator in model_indicators):
            
            # Extract methods
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append({
                        'name': item.name,
                        'docstring': ast.get_docstring(item) or "",
                        'args': [arg.arg for arg in item.args.args if arg.arg != 'self']
                    })
            
            results['ml_models'].append({
                'name': class_name,
                'file': file_path,
                'docstring': docstring,
                'methods': methods,
                'line_number': node.lineno,
                'base_classes': [self._get_node_name(base) for base in node.bases]
            })
        
        # Check if it's a pipeline class
        pipeline_indicators = ['pipeline', 'workflow', 'processor']
        if any(indicator in class_name.lower() for indicator in pipeline_indicators):
            
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append({
                        'name': item.name,
                        'docstring': ast.get_docstring(item) or ""
                    })
            
            results['pipelines'].append({
                'name': class_name,
                'file': file_path,
                'docstring': docstring,
                'methods': methods,
                'line_number': node.lineno
            })
        
        # Check if it's a data processor
        processor_indicators = ['preprocessor', 'transformer', 'cleaner', 'loader']
        if any(indicator in class_name.lower() for indicator in processor_indicators):
            results['data_processors'].append({
                'name': class_name,
                'file': file_path,
                'docstring': docstring,
                'line_number': node.lineno
            })
        
        return results
    
    def _analyze_function(self, node: ast.FunctionDef, content: str, file_path: str) -> Dict[str, List]:
        """Analyze a function for ML patterns."""
        results = {
            'training_scripts': [],
            'inference_endpoints': [],
            'experiment_tracking': [],
            'data_processors': []
        }
        
        func_name = node.name
        docstring = ast.get_docstring(node) or ""
        
        # Training functions
        train_indicators = ['train', 'fit', 'learn', 'optimize']
        if any(indicator in func_name.lower() for indicator in train_indicators):
            results['training_scripts'].append({
                'name': func_name,
                'file': file_path,
                'docstring': docstring,
                'line_number': node.lineno,
                'args': [arg.arg for arg in node.args.args]
            })
        
        # Inference/prediction functions
        inference_indicators = ['predict', 'infer', 'classify', 'score', 'evaluate']
        if any(indicator in func_name.lower() for indicator in inference_indicators):
            results['inference_endpoints'].append({
                'name': func_name,
                'file': file_path,
                'docstring': docstring,
                'line_number': node.lineno,
                'args': [arg.arg for arg in node.args.args]
            })
        
        # Data processing functions
        process_indicators = ['preprocess', 'clean', 'transform', 'feature', 'load_data', 'process_data']
        if any(indicator in func_name.lower() for indicator in process_indicators):
            results['data_processors'].append({
                'name': func_name,
                'file': file_path,
                'docstring': docstring,
                'line_number': node.lineno,
                'args': [arg.arg for arg in node.args.args]
            })
        
        # Check function body for experiment tracking
        func_source = ast.get_source_segment(content, node) if hasattr(ast, 'get_source_segment') else ""
        if func_source:
            experiment_indicators = ['mlflow', 'wandb', 'tensorboard', 'log_metric', 'log_param']
            if any(indicator in func_source.lower() for indicator in experiment_indicators):
                results['experiment_tracking'].append({
                    'name': func_name,
                    'file': file_path,
                    'docstring': docstring,
                    'line_number': node.lineno,
                    'tracking_tools': [ind for ind in experiment_indicators if ind in func_source.lower()]
                })
        
        return results
    
    def _analyze_file_patterns(self, content: str, file_path: str) -> Dict[str, List]:
        """Analyze file-level patterns."""
        results = {
            'model_deployment': [],
            'data_sources': []
        }
        
        # Model deployment patterns
        deployment_patterns = ['flask', 'fastapi', 'serve', 'deploy', 'endpoint', 'api']
        if any(pattern in content.lower() for pattern in deployment_patterns):
            # Check if it's actually serving ML models
            ml_serving_indicators = ['model.predict', 'model.load', '.pkl', '.joblib', '.h5', '.pt']
            if any(indicator in content.lower() for indicator in ml_serving_indicators):
                results['model_deployment'].append({
                    'file': file_path,
                    'type': 'Model Serving',
                    'indicators': [ind for ind in ml_serving_indicators if ind in content.lower()]
                })
        
        # Data source patterns
        data_patterns = ['.csv', '.json', '.parquet', '.sql', 'database', 'mongodb', 'postgres']
        found_patterns = [pattern for pattern in data_patterns if pattern in content.lower()]
        if found_patterns:
            results['data_sources'].append({
                'file': file_path,
                'data_types': found_patterns
            })
        
        return results
    
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
                    # Also add the specific imports
                    for alias in node.names:
                        imports.append(f"{node.module}.{alias.name}")
        
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
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        str_path = str(file_path)
        
        # Quick exclusions for common directories
        exclude_dirs = ['venv', '.venv', 'env', '.env', '__pycache__', '.git', 
                       'node_modules', 'site-packages', 'build', 'dist', '.tox', 
                       'tests', 'test']
        
        # Check if any part of the path contains excluded directories
        path_parts = Path(str_path).parts
        for part in path_parts:
            if part in exclude_dirs or part.startswith('test_'):
                return True
        
        return False
    
    def generate_pipeline_documentation(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate documentation sections for AI pipelines."""
        docs = {}
        
        # Model documentation
        if analysis_results.get('ml_models'):
            model_docs = "# Machine Learning Models\n\n"
            for model in analysis_results['ml_models']:
                model_docs += f"## {model['name']}\n\n"
                if model['docstring']:
                    model_docs += f"{model['docstring']}\n\n"
                model_docs += f"**File:** `{model['file']}`\n"
                model_docs += f"**Line:** {model['line_number']}\n\n"
                
                if model['methods']:
                    model_docs += "**Methods:**\n"
                    for method in model['methods']:
                        model_docs += f"- `{method['name']}()`"
                        if method['docstring']:
                            model_docs += f": {method['docstring'][:100]}..."
                        model_docs += "\n"
                    model_docs += "\n"
                
                model_docs += "---\n\n"
            docs['models'] = model_docs
        
        # Pipeline documentation
        if analysis_results.get('pipelines'):
            pipeline_docs = "# ML Pipelines\n\n"
            for pipeline in analysis_results['pipelines']:
                pipeline_docs += f"## {pipeline['name']}\n\n"
                if pipeline['docstring']:
                    pipeline_docs += f"{pipeline['docstring']}\n\n"
                pipeline_docs += f"**File:** `{pipeline['file']}`\n\n"
                pipeline_docs += "---\n\n"
            docs['pipelines'] = pipeline_docs
        
        # Training documentation
        if analysis_results.get('training_scripts'):
            training_docs = "# Training Components\n\n"
            for training in analysis_results['training_scripts']:
                training_docs += f"## {training['name']}\n\n"
                if training['docstring']:
                    training_docs += f"{training['docstring']}\n\n"
                training_docs += f"**File:** `{training['file']}`\n"
                if training['args']:
                    training_docs += f"**Parameters:** {', '.join(training['args'])}\n"
                training_docs += "\n---\n\n"
            docs['training'] = training_docs
        
        # Data processing documentation
        if analysis_results.get('data_processors'):
            data_docs = "# Data Processing Components\n\n"
            for processor in analysis_results['data_processors']:
                data_docs += f"## {processor['name']}\n\n"
                if processor['docstring']:
                    data_docs += f"{processor['docstring']}\n\n"
                data_docs += f"**File:** `{processor['file']}`\n\n"
                data_docs += "---\n\n"
            docs['data_processing'] = data_docs
        
        return docs
