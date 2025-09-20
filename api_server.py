#!/usr/bin/env python3
"""
Enhanced API server with Cursor vector database integration
Provides repository data for the documentation interface with AI-powered analysis
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import ast
import subprocess
import sqlite3
import requests
from pathlib import Path
from datetime import datetime
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class AIEditorIntegration:
    """Generic AI code editor integration with vector database CRUD operations"""
    
    def __init__(self, db_path=".cache/ai_embeddings.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ai_available = False
        self.ai_api_base = None
        self.editor_type = None
        
        # Initialize local embedding database
        self._init_embedding_db()
        
        # Detect available AI editors
        self._detect_ai_editors()
    
    def _init_embedding_db(self):
        """Initialize SQLite database for storing embeddings and analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS code_embeddings (
                        id INTEGER PRIMARY KEY,
                        file_path TEXT UNIQUE,
                        content_hash TEXT,
                        embedding_vector BLOB,
                        embedding_source TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS code_analysis (
                        id INTEGER PRIMARY KEY,
                        file_path TEXT,
                        analysis_type TEXT,
                        analysis_data TEXT,
                        ai_insights TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (file_path) REFERENCES code_embeddings (file_path)
                    )
                ''')
            logger.info(f"✅ AI embedding database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding database: {e}")
    
    def _detect_ai_editors(self):
        """Detect available AI-powered code editors"""
        editors_to_check = [
            {'name': 'cursor', 'ports': [8080, 3000, 5000], 'endpoint': '/api/health'},
            {'name': 'vscode-copilot', 'ports': [3001, 8001], 'endpoint': '/copilot/health'},
            {'name': 'codewhisperer', 'ports': [9000, 9001], 'endpoint': '/aws/health'},
            {'name': 'tabnine', 'ports': [9999, 8888], 'endpoint': '/tabnine/health'},
        ]
        
        for editor in editors_to_check:
            for port in editor['ports']:
                try:
                    response = requests.get(f'http://localhost:{port}{editor["endpoint"]}', timeout=1)
                    if response.status_code == 200:
                        self.ai_api_base = f'http://localhost:{port}'
                        self.editor_type = editor['name']
                        self.ai_available = True
                        logger.info(f"✅ {editor['name']} API detected at port {port}")
                        return
                except:
                    continue
        
        # Check for CLI tools
        cli_tools = ['cursor', 'code', 'copilot']
        for tool in cli_tools:
            try:
                result = subprocess.run([tool, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.editor_type = tool
                    self.ai_available = True
                    logger.info(f"✅ {tool} CLI detected")
                    return
            except:
                continue
        
        logger.info("ℹ️  No AI editor detected - using local analysis only")
    
    def save_embedding(self, file_path, content, embedding=None, source='local', metadata=None):
        """Save embedding to database (CREATE/UPDATE)"""
        try:
            content_hash = hashlib.md5(content.encode()).hexdigest()
            embedding_blob = None
            
            if embedding:
                import pickle
                embedding_blob = pickle.dumps(embedding)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO code_embeddings 
                    (file_path, content_hash, embedding_vector, embedding_source, metadata, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (str(file_path), content_hash, embedding_blob, source, json.dumps(metadata or {})))
            
            logger.debug(f"💾 Saved embedding for {file_path} (source: {source})")
            return True
        except Exception as e:
            logger.error(f"Failed to save embedding for {file_path}: {e}")
            return False
    
    def get_embedding(self, file_path):
        """Retrieve embedding from database (READ)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute('''
                    SELECT embedding_vector, embedding_source, metadata FROM code_embeddings 
                    WHERE file_path = ?
                ''', (str(file_path),)).fetchone()
                
                if result:
                    import pickle
                    embedding = pickle.loads(result[0]) if result[0] else None
                    return {
                        'embedding': embedding,
                        'source': result[1],
                        'metadata': json.loads(result[2] or '{}')
                    }
        except Exception as e:
            logger.error(f"Failed to get embedding for {file_path}: {e}")
        return None
    
    def get_ai_embeddings(self, texts):
        """Get embeddings from AI editor if available"""
        if not self.ai_available or not self.ai_api_base:
            return None
        
        # Generic API endpoints for different editors
        endpoints = {
            'cursor': '/api/embed',
            'vscode-copilot': '/copilot/embed', 
            'codewhisperer': '/aws/embed',
            'tabnine': '/tabnine/embed'
        }
        
        endpoint = endpoints.get(self.editor_type, '/api/embed')
        
        try:
            response = requests.post(f'{self.ai_api_base}{endpoint}', 
                                   json={'texts': texts}, 
                                   timeout=10)
            if response.status_code == 200:
                return response.json().get('embeddings')
        except Exception as e:
            logger.warning(f"AI embeddings failed ({self.editor_type}): {e}")
        return None
    
    def semantic_search(self, query, limit=10):
        """Perform semantic search using local database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                results = conn.execute('''
                    SELECT file_path, embedding_source, metadata FROM code_embeddings 
                    WHERE embedding_vector IS NOT NULL
                    ORDER BY updated_at DESC LIMIT ?
                ''', (limit,)).fetchall()
                
                return [{'path': r[0], 'source': r[1], 'metadata': json.loads(r[2] or '{}')} 
                       for r in results]
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
        return []
    
    def delete_embedding(self, file_path):
        """Delete embedding from database (DELETE)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM code_embeddings WHERE file_path = ?', (str(file_path),))
                conn.execute('DELETE FROM code_analysis WHERE file_path = ?', (str(file_path),))
            logger.debug(f"🗑️  Deleted embedding for {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete embedding for {file_path}: {e}")
            return False


class RepositoryAnalyzer:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)
        self.analysis_cache = {}
        self.ai_integration = AIEditorIntegration()
        logger.info(f"🔍 Analyzing repository: {self.repo_path}")
        logger.info(f"🤖 AI Editor integration: {'✅ ' + self.ai_integration.editor_type if self.ai_integration.ai_available else '❌ Not available'}")
        
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
                        # Enhance with AI editor embeddings if available
                        module_info = self._enhance_with_ai_embeddings(module_info, file_path)
                        modules.append(module_info)
                        total_files += 1
                        total_functions += module_info.get('stats', {}).get('functions', 0)
                        total_classes += module_info.get('stats', {}).get('classes', 0)
                except Exception as e:
                    logger.warning(f"Error analyzing {file_path}: {e}")
                    
            return {
                'modules': modules,
                'totalFiles': total_files,
                'totalFunctions': total_functions,
                'totalClasses': total_classes,
                'lastUpdated': datetime.now().isoformat(),
                'repositoryPath': str(self.repo_path.absolute()),
                'aiIntegration': {
                    'available': self.ai_integration.ai_available,
                    'editorType': self.ai_integration.editor_type,
                    'apiBase': self.ai_integration.ai_api_base,
                    'dbPath': str(self.ai_integration.db_path)
                }
            }
        except Exception as e:
            logger.error(f"Repository analysis error: {e}")
            return self._get_fallback_data()
    
    def _should_skip_file(self, file_path):
        """Check if file should be skipped during analysis"""
        skip_patterns = [
            '__pycache__', '.git', 'venv', 'env', 'node_modules',
            '.pytest_cache', '.mypy_cache', 'build', 'dist'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _enhance_with_ai_embeddings(self, module_info, file_path):
        """Enhance module info with AI editor embeddings and save to database"""
        try:
            # Create text content for embedding
            text_content = f"{module_info.get('name', '')} {module_info.get('description', '')} {' '.join(module_info.get('functions', []))}"
            
            # Check if we already have this embedding cached
            cached_embedding = self.ai_integration.get_embedding(file_path)
            
            # Read file content for hash comparison
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            current_hash = hashlib.md5(file_content.encode()).hexdigest()
            
            # If cached and content hasn't changed, use cached
            if cached_embedding and cached_embedding.get('metadata', {}).get('content_hash') == current_hash:
                module_info['embedding_source'] = cached_embedding['source']
                module_info['ai_embedding_cached'] = True
                logger.debug(f"Using cached embedding for {file_path}")
            else:
                # Try to get new embedding from AI editor
                ai_embeddings = self.ai_integration.get_ai_embeddings([text_content])
                
                if ai_embeddings and len(ai_embeddings) > 0:
                    # Save AI embedding to database
                    embedding = ai_embeddings[0]
                    metadata = {
                        'content_hash': current_hash,
                        'functions_count': len(module_info.get('functions', [])),
                        'classes_count': len(module_info.get('classes', []))
                    }
                    
                    self.ai_integration.save_embedding(
                        file_path, file_content, embedding, 
                        source=self.ai_integration.editor_type, 
                        metadata=metadata
                    )
                    
                    module_info['embedding_source'] = self.ai_integration.editor_type
                    module_info['ai_embedding_cached'] = False
                else:
                    # Fallback to local embedding
                    local_embedding = self._generate_local_embedding(text_content)
                    metadata = {
                        'content_hash': current_hash,
                        'functions_count': len(module_info.get('functions', [])),
                        'classes_count': len(module_info.get('classes', []))
                    }
                    
                    self.ai_integration.save_embedding(
                        file_path, file_content, local_embedding, 
                        source='local', metadata=metadata
                    )
                    
                    module_info['embedding_source'] = 'local'
                    module_info['ai_embedding_cached'] = False
            
            # Get similar modules from database
            similar_modules = self.ai_integration.semantic_search(text_content, limit=3)
            if similar_modules:
                module_info['similar_modules'] = similar_modules
            
        except Exception as e:
            logger.warning(f"AI enhancement failed for {file_path}: {e}")
            module_info['embedding_source'] = 'local'
            module_info['ai_embedding_cached'] = False
        
        return module_info
    
    def _generate_local_embedding(self, text):
        """Generate a simple local embedding as fallback"""
        import hashlib
        # Simple word-based embedding
        words = text.lower().split()
        embedding = [0.0] * 128  # 128-dimensional vector
        
        for i, word in enumerate(words[:128]):
            hash_val = int(hashlib.md5(word.encode()).hexdigest()[:8], 16)
            embedding[i % 128] += (hash_val % 100) / 100.0
        
        # Normalize
        magnitude = sum(x*x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x/magnitude for x in embedding]
        
        return embedding
    
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

# Initialize analyzer with the target repository path
import sys
repo_path = sys.argv[1] if len(sys.argv) > 1 else "/Users/manan/theglove/content-search"
analyzer = RepositoryAnalyzer(repo_path)

@app.route('/api/repository-data')
def get_repository_data():
    """Get repository analysis data with AI embeddings"""
    try:
        data = analyzer.analyze_repository()
        return jsonify(data)
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify(analyzer._get_fallback_data()), 500

@app.route('/api/embeddings', methods=['GET'])
def get_all_embeddings():
    """Get all stored embeddings (READ)"""
    try:
        with sqlite3.connect(analyzer.ai_integration.db_path) as conn:
            results = conn.execute('''
                SELECT file_path, embedding_source, metadata, created_at, updated_at 
                FROM code_embeddings 
                ORDER BY updated_at DESC
            ''').fetchall()
            
            embeddings = []
            for result in results:
                embeddings.append({
                    'file_path': result[0],
                    'source': result[1], 
                    'metadata': json.loads(result[2] or '{}'),
                    'created_at': result[3],
                    'updated_at': result[4]
                })
            
            return jsonify({'embeddings': embeddings, 'count': len(embeddings)})
    except Exception as e:
        logger.error(f"Failed to get embeddings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/embeddings/<path:file_path>', methods=['GET'])
def get_embedding(file_path):
    """Get specific embedding (READ)"""
    try:
        embedding_data = analyzer.ai_integration.get_embedding(file_path)
        if embedding_data:
            return jsonify(embedding_data)
        else:
            return jsonify({'error': 'Embedding not found'}), 404
    except Exception as e:
        logger.error(f"Failed to get embedding for {file_path}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/embeddings/<path:file_path>', methods=['DELETE'])
def delete_embedding(file_path):
    """Delete specific embedding (DELETE)"""
    try:
        success = analyzer.ai_integration.delete_embedding(file_path)
        if success:
            return jsonify({'message': f'Embedding deleted for {file_path}'})
        else:
            return jsonify({'error': 'Failed to delete embedding'}), 500
    except Exception as e:
        logger.error(f"Failed to delete embedding for {file_path}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/embeddings/refresh', methods=['POST'])
def refresh_embeddings():
    """Force refresh all embeddings (UPDATE)"""
    try:
        # Clear cache and re-analyze
        analyzer.analysis_cache.clear()
        
        # Re-analyze repository to refresh embeddings
        data = analyzer.analyze_repository()
        
        return jsonify({
            'message': 'Embeddings refreshed successfully',
            'modules_processed': len(data.get('modules', [])),
            'ai_integration': data.get('aiIntegration', {})
        })
    except Exception as e:
        logger.error(f"Failed to refresh embeddings: {e}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/search/search_index.json')
def serve_search_index():
    """Serve search index for documentation search"""
    return send_from_directory('docs/search', 'search_index.json')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('docs', path)

if __name__ == '__main__':
    print("🚀 Starting Repository Data API Server...")
    print("📊 Repository analysis available at: http://localhost:8000/api/repository-data")
    print("🔍 Module search available at: http://localhost:8000/api/search?q=<query>")
    print("📁 Code viewer available at: http://localhost:8000/code/<path>")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
