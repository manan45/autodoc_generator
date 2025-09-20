#!/usr/bin/env python3
"""
Simple API server to provide repository data for the documentation interface
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import ast
import subprocess
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

class RepositoryAnalyzer:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.analysis_cache = {}
        
    def analyze_repository(self):
        """Analyze the repository and extract module information"""
        try:
            modules = []
            total_files = 0
            total_functions = 0
            total_classes = 0
            
            # Find Python files
            python_files = list(self.repo_path.rglob("*.py"))
            
            for file_path in python_files:
                if self._should_skip_file(file_path):
                    continue
                    
                try:
                    module_info = self._analyze_python_file(file_path)
                    if module_info:
                        modules.append(module_info)
                        total_files += 1
                        total_functions += module_info.get('stats', {}).get('functions', 0)
                        total_classes += module_info.get('stats', {}).get('classes', 0)
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
                    
            return {
                'modules': modules,
                'totalFiles': total_files,
                'totalFunctions': total_functions,
                'totalClasses': total_classes,
                'lastUpdated': datetime.now().isoformat(),
                'repositoryPath': str(self.repo_path.absolute())
            }
        except Exception as e:
            print(f"Repository analysis error: {e}")
            return self._get_fallback_data()
    
    def _should_skip_file(self, file_path):
        """Check if file should be skipped during analysis"""
        skip_patterns = [
            '__pycache__', '.git', 'venv', 'env', 'node_modules',
            '.pytest_cache', '.mypy_cache', 'build', 'dist'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _analyze_python_file(self, file_path):
        """Analyze a Python file and extract information"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node),
                        'args': [
                            {
                                'name': a.arg,
                                'annotation': getattr(a.annotation, 'id', None) or getattr(getattr(a.annotation, 'attr', None), '__str__', lambda: None)() if a.annotation else None
                            } for a in node.args.args
                        ]
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node),
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            imports.append(f"{module}.{alias.name}")
                    else:
                        for alias in node.names:
                            imports.append(alias.name)
            
            # Calculate relative path
            rel_path = file_path.relative_to(self.repo_path)
            
            # Determine module type
            module_type = self._infer_module_type(file_path, content)
            
            # Calculate complexity
            complexity = self._calculate_complexity(functions, classes, content)
            
            result = {
                'id': str(rel_path).replace('/', '_').replace('.py', ''),
                'name': file_path.stem,
                'path': str(rel_path),
                'description': self._extract_module_docstring(tree),
                'type': module_type,
                'complexity': complexity,
                'stats': {
                    'functions': len(functions),
                    'classes': len(classes),
                    'imports': len(imports),
                    'lines': len(content.splitlines())
                },
                'functions': functions[:25],  # return more for richer UI
                'classes': classes[:15],
                'imports': imports[:10],     # Top 10 imports
                'embedding': self._generate_embedding(content, str(rel_path))
            }

            # cache per-file result keyed by path+mtime
            try:
                mtime = os.path.getmtime(file_path)
                cache_key = f"{result['path']}::{mtime}"
                self.analysis_cache[result['path']] = { 'key': cache_key, 'data': result }
            except Exception:
                pass

            return result
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            return None
    
    def _extract_module_docstring(self, tree):
        """Extract module-level docstring"""
        if (tree.body and isinstance(tree.body[0], ast.Expr) 
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)):
            return tree.body[0].value.value.strip()
        return ""
    
    def _infer_module_type(self, file_path, content):
        """Infer the type of module based on path and content"""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        if 'api' in path_str or 'endpoint' in path_str or 'flask' in content_lower:
            return 'api'
        elif 'test' in path_str or 'spec' in path_str:
            return 'test'
        elif any(ai_term in content_lower for ai_term in ['tensorflow', 'torch', 'sklearn', 'model']):
            return 'ai'
        elif 'pipeline' in path_str or 'workflow' in path_str:
            return 'pipeline'
        elif 'util' in path_str or 'helper' in path_str:
            return 'utility'
        elif 'service' in path_str or 'manager' in path_str:
            return 'service'
        elif 'component' in path_str or 'widget' in path_str:
            return 'component'
        else:
            return 'module'
    
    def _calculate_complexity(self, functions, classes, content):
        """Calculate module complexity"""
        total_items = len(functions) + len(classes)
        lines = len(content.splitlines())
        
        # Simple complexity calculation
        complexity_score = total_items + (lines / 100)
        
        if complexity_score > 50:
            return 'high'
        elif complexity_score > 20:
            return 'medium'
        else:
            return 'low'
    
    def _generate_embedding(self, content, path):
        """Generate a simple embedding for the module"""
        # This is a simplified embedding - in production, use proper embeddings
        import hashlib
        
        # Combine content and path for embedding
        text = f"{path} {content[:1000]}"  # First 1000 chars
        words = text.lower().split()
        
        # Create a simple hash-based embedding
        embedding = []
        for i in range(50):  # 50-dimensional embedding
            hash_input = f"{text}_{i}"
            hash_val = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
            embedding.append((hash_val % 1000) / 1000.0)  # Normalize to 0-1
        
        return embedding
    
    def _get_fallback_data(self):
        """Return fallback data when analysis fails"""
        return {
            'modules': [
                {
                    'id': 'main_module',
                    'name': 'Main Module',
                    'path': 'src/main.py',
                    'description': 'Main application module',
                    'type': 'module',
                    'complexity': 'medium',
                    'stats': {'functions': 5, 'classes': 2, 'imports': 8, 'lines': 150},
                    'embedding': [0.1] * 50
                }
            ],
            'totalFiles': 1,
            'totalFunctions': 5,
            'totalClasses': 2,
            'lastUpdated': datetime.now().isoformat()
        }

# Initialize analyzer
analyzer = RepositoryAnalyzer()

@app.route('/api/repository-data')
def get_repository_data():
    """Get repository analysis data"""
    try:
        data = analyzer.analyze_repository()
        return jsonify(data)
    except Exception as e:
        print(f"API error: {e}")
        return jsonify(analyzer._get_fallback_data()), 500

@app.route('/api/module/<module_id>')
def get_module_details(module_id):
    """Get detailed information about a specific module"""
    try:
        repo_data = analyzer.analyze_repository()
        module = next((m for m in repo_data['modules'] if m['id'] == module_id), None)
        
        if not module:
            return jsonify({'error': 'Module not found'}), 404
        
        return jsonify(module)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_modules():
    """Search modules using vector similarity"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 5))
    
    if not query:
        return jsonify({'results': []})
    
    try:
        repo_data = analyzer.analyze_repository()
        # Simple text-based search (in production, use proper vector search)
        results = []
        
        for module in repo_data['modules']:
            score = 0
            query_lower = query.lower()
            
            # Check name match
            if query_lower in module['name'].lower():
                score += 10
            
            # Check description match
            if query_lower in module.get('description', '').lower():
                score += 5
            
            # Check type match
            if query_lower in module['type'].lower():
                score += 3
            
            if score > 0:
                results.append({
                    'module': module,
                    'score': score
                })
        
        # Sort by score and limit results
        results.sort(key=lambda x: x['score'], reverse=True)
        results = results[:limit]
        
        return jsonify({
            'results': [r['module'] for r in results],
            'query': query,
            'total': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/code/<path:module_path>')
def view_code(module_path):
    """View source code for a module"""
    try:
        file_path = Path(module_path)
        
        # Security check - ensure path is within repository
        full_path = (analyzer.repo_path / file_path).resolve()
        if not str(full_path).startswith(str(analyzer.repo_path.resolve())):
            return jsonify({'error': 'Access denied'}), 403
        
        if not full_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'path': str(file_path),
            'content': content,
            'language': 'python' if file_path.suffix == '.py' else 'text'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve static files
@app.route('/')
def serve_index():
    return send_from_directory('docs', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('docs', path)

if __name__ == '__main__':
    print("🚀 Starting Repository Data API Server...")
    print("📊 Repository analysis available at: http://localhost:8000/api/repository-data")
    print("🔍 Module search available at: http://localhost:8000/api/search?q=<query>")
    print("📁 Code viewer available at: http://localhost:8000/code/<path>")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
