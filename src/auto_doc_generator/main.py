#!/usr/bin/env python3
"""
Auto Documentation Generation System

This is the main entry point for the automatic code documentation generation system.
It analyzes Python codebases and generates comprehensive documentation.
"""

import argparse
import sys
import os
import yaml
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.code_analyzer import CodeAnalyzer
from analyzers.ai_pipeline_analyzer import AIPipelineAnalyzer
from generators.markdown_generator import MarkdownGenerator
from generators.html_generator import HTMLGenerator
from generators.ai_analysis_coordinator import AIAnalysisCoordinator


def setup_logging(config: Dict[str, Any]) -> None:
    """Set up logging configuration."""
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO').upper())
    format_str = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logging.basicConfig(level=level, format=format_str)


def load_config(config_path: str = "documentor.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"Warning: Config file {config_path} not found. Using defaults.")
        return {
            'agent': {
                'name': 'AutoDoc Agent',
                'version': '1.0.0'
            },
            'analysis': {
                'include_patterns': ['*.py'],
                'exclude_patterns': ['*/tests/*', '*/__pycache__/*', '*/.git/*', '*/venv/*'],
                'ai_analysis': {
                    'enabled': True,
                    'detect_frameworks': True,
                    'analyze_pipelines': True,
                    'generate_flow_diagrams': True
                }
            },
            'documentation': {
                'output_format': 'html',
                'theme': 'material',
                'sections': {
                    'overview': True,
                    'architecture': True,
                    'api_reference': True,
                    'onboarding': True,
                    'ai_models': True,
                    'ai_pipelines': True,
                    'complexity_report': True
                },
                'diagrams': {
                    'enabled': True
                }
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)


def analyze_codebase(repo_path: str, config: Dict[str, Any]) -> tuple:
    """Analyze the codebase and return analysis results."""
    print("=" * 60)
    print("🔍 STARTING CODEBASE ANALYSIS")
    print("=" * 60)
    
    # Initialize analyzers
    code_analyzer = CodeAnalyzer(repo_path, config)
    ai_analyzer = AIPipelineAnalyzer(config)
    
    # Perform code analysis
    print("\n📊 Analyzing code structure...")
    code_analysis = code_analyzer.analyze_codebase()
    
    # Perform AI/ML analysis
    print("🤖 Analyzing AI/ML components...")
    ai_analysis = ai_analyzer.analyze_ai_components(Path(repo_path))
    
    print("\n✅ Analysis complete!")
    print(f"   📁 {code_analysis.get('overview', {}).get('total_files', 0)} files analyzed")
    print(f"   🏗️ {code_analysis.get('overview', {}).get('total_functions', 0)} functions found")
    print(f"   📦 {code_analysis.get('overview', {}).get('total_classes', 0)} classes found")
    print(f"   🤖 {len(ai_analysis.get('ml_models', []))} ML models detected")
    
    return code_analysis, ai_analysis


def generate_documentation(code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any], 
                         config: Dict[str, Any], output_dir: str = "docs") -> None:
    """Generate documentation from analysis results."""
    print("\n" + "=" * 60)
    print("📚 GENERATING DOCUMENTATION")
    print("=" * 60)
    
    # Determine which generator to use (default to HTML)
    output_format = config.get('documentation', {}).get('output_format', 'html')
    
    if output_format == 'html':
        # Initialize HTML generator (default)
        doc_gen = HTMLGenerator(template_dir="html_templates", output_dir=output_dir, config=config)
        print("\n🌐 Generating HTML documentation...")
    else:
        # Fall back to markdown generator
        doc_gen = MarkdownGenerator(template_dir="templates", output_dir=output_dir, config=config)
        print("\n📝 Generating markdown documentation...")
    
    # Initialize AI analysis coordinator (refactored from generator)
    ai_analysis_coordinator = AIAnalysisCoordinator(config=config)
    
    # Step 1: Enhance code analysis with AI insights
    print("🧠 Enhancing analysis with AI insights...")
    enhanced_analysis = ai_analysis_coordinator.enhance_code_analysis(code_analysis, ai_analysis)
    
    # Step 2: Generate documentation using enhanced analysis
    print("📚 Generating documentation with enhanced analysis...")
    docs = doc_gen.generate_all_documentation(code_analysis, ai_analysis, enhanced_analysis)
    
    # Step 3: Use AI-enhanced diagrams (already generated in enhanced analysis)
    if 'diagrams' in enhanced_analysis and enhanced_analysis['diagrams']:
        print("✨ Using AI-enhanced diagrams...")
        
        # Regenerate architecture page with full enhanced analysis (not just diagrams)
        docs['architecture.html'] = doc_gen.generate_architecture_page(code_analysis, enhanced_analysis)
        
        # Merge enhanced diagrams into docs
        if 'diagrams' not in docs:
            docs['diagrams'] = {}
        docs['diagrams'].update(enhanced_analysis['diagrams'])
    
    # Save all documentation
    print("💾 Saving documentation files...")
    doc_gen.save_documentation(docs)
    
    print("\n✅ Documentation generation complete!")
    print(f"   📁 Documentation saved to: {output_dir}/")
    if output_format == 'html':
        print(f"   🌐 Open {output_dir}/index.html to view the documentation")
    else:
        print(f"   🌐 Open {output_dir}/index.md to view the documentation")


def build_site(output_dir: str = "docs") -> None:
    """Build the MkDocs site."""
    print("\n" + "=" * 60)
    print("🏗️ BUILDING DOCUMENTATION SITE")
    print("=" * 60)
    
    try:
        import subprocess
        
        # Build from project root (where mkdocs.yml is located)
        print("🔨 Building MkDocs site...")
        result = subprocess.run(['mkdocs', 'build'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MkDocs site built successfully!")
            print(f"   🌐 Site available at: site/index.html")
        else:
            print(f"❌ Error building site: {result.stderr}")
        
    except ImportError:
        print("⚠️ MkDocs not installed. Install with: pip install mkdocs mkdocs-material")
    except Exception as e:
        print(f"❌ Error building site: {e}")


def serve_site(output_dir: str = "docs", port: int = 8000, repo_path: str = ".") -> None:
    """Serve the documentation site locally with API integration."""
    print(f"\n🚀 Starting enhanced documentation server on port {port}...")
    print(f"📊 Repository analysis enabled for: {repo_path}")
    
    try:
        from pathlib import Path
        
        # Check if we have Flask available for API server
        try:
            from flask import Flask, jsonify, request, send_from_directory
            from flask_cors import CORS
            flask_available = True
        except ImportError:
            print("⚠️ Flask not available. Install with: pip install flask flask-cors")
            flask_available = False
        
        output_path = Path(output_dir)
        html_index = output_path / "index.html"
        mkdocs_config = Path("mkdocs.yml")
        
        if flask_available and html_index.exists():
            # Start enhanced Flask server with API endpoints
            print(f"🎯 Starting enhanced server with live repository data")
            start_enhanced_server(output_dir, port, repo_path)
        elif mkdocs_config.exists():
            # Use MkDocs serve (no API integration)
            print(f"📚 Serving MkDocs site (basic mode)")
            import subprocess
            subprocess.run(['mkdocs', 'serve', '--dev-addr', f'127.0.0.1:{port}'])
        else:
            # Fallback to simple HTTP server
            print(f"📄 Serving documentation from {output_dir} (basic mode)")
            import subprocess
            import os
            os.chdir(output_dir)
            subprocess.run(['python3', '-m', 'http.server', str(port)])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error serving site: {e}")
        # Fallback to simple HTTP server
        try:
            import subprocess
            import os
            os.chdir(output_dir)
            subprocess.run(['python3', '-m', 'http.server', str(port)])
        except Exception as fallback_error:
            print(f"❌ Fallback server also failed: {fallback_error}")


def start_enhanced_server(output_dir: str, port: int, repo_path: str) -> None:
    """Start Flask server with API endpoints and static file serving."""
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
    import ast
    import hashlib
    from pathlib import Path
    from datetime import datetime
    import os
    
    app = Flask(__name__)
    CORS(app)
    
    # Ensure output_dir is absolute path
    output_dir = os.path.abspath(output_dir)
    print(f"📁 Serving files from: {output_dir}")
    
    class RepositoryAnalyzer:
        def __init__(self, repo_path="."):
            self.repo_path = Path(repo_path)
            
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
            skip_patterns = [
                '__pycache__', '.git', 'venv', 'env', 'node_modules',
                '.pytest_cache', '.mypy_cache', 'build', 'dist'
            ]
            path_str = str(file_path)
            return any(pattern in path_str for pattern in skip_patterns)
        
        def _analyze_python_file(self, file_path):
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
                            'args': len(node.args.args)
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
                
                rel_path = file_path.relative_to(self.repo_path)
                module_type = self._infer_module_type(file_path, content)
                complexity = self._calculate_complexity(functions, classes, content)
                
                return {
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
                    'functions': functions[:5],
                    'classes': classes[:3],
                    'imports': imports[:10],
                    'embedding': self._generate_embedding(content, str(rel_path))
                }
            except Exception as e:
                print(f"Error analyzing file {file_path}: {e}")
                return None
        
        def _extract_module_docstring(self, tree):
            if (tree.body and isinstance(tree.body[0], ast.Expr) 
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)):
                return tree.body[0].value.value.strip()
            return ""
        
        def _infer_module_type(self, file_path, content):
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
            total_items = len(functions) + len(classes)
            lines = len(content.splitlines())
            complexity_score = total_items + (lines / 100)
            
            if complexity_score > 50:
                return 'high'
            elif complexity_score > 20:
                return 'medium'
            else:
                return 'low'
        
        def _generate_embedding(self, content, path):
            text = f"{path} {content[:1000]}"
            words = text.lower().split()
            embedding = []
            for i in range(50):
                hash_input = f"{text}_{i}"
                hash_val = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
                embedding.append((hash_val % 1000) / 1000.0)
            return embedding
        
        def _get_fallback_data(self):
            return {
                'modules': [],
                'totalFiles': 0,
                'totalFunctions': 0,
                'totalClasses': 0,
                'lastUpdated': datetime.now().isoformat()
            }
    
    # Initialize analyzer
    analyzer = RepositoryAnalyzer(repo_path)
    
    @app.route('/api/repository-data')
    def get_repository_data():
        try:
            data = analyzer.analyze_repository()
            return jsonify(data)
        except Exception as e:
            print(f"API error: {e}")
            return jsonify(analyzer._get_fallback_data()), 500
    
    @app.route('/api/search')
    def search_modules():
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 5))
        
        if not query:
            return jsonify({'results': []})
        
        try:
            repo_data = analyzer.analyze_repository()
            results = []
            
            for module in repo_data['modules']:
                score = 0
                query_lower = query.lower()
                
                if query_lower in module['name'].lower():
                    score += 10
                if query_lower in module.get('description', '').lower():
                    score += 5
                if query_lower in module['type'].lower():
                    score += 3
                
                if score > 0:
                    results.append({
                        'module': module,
                        'score': score
                    })
            
            results.sort(key=lambda x: x['score'], reverse=True)
            results = results[:limit]
            
            return jsonify({
                'results': [r['module'] for r in results],
                'query': query,
                'total': len(results)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/')
    def serve_index():
        try:
            return send_from_directory(output_dir, 'index.html')
        except Exception as e:
            return f"Error serving index.html: {e}", 404
    
    @app.route('/<path:path>')
    def serve_static(path):
        try:
            return send_from_directory(output_dir, path)
        except Exception as e:
            return f"Error serving {path}: {e}", 404
    
    print("🚀 Starting Enhanced Documentation Server...")
    print("📊 Repository analysis available at: http://localhost:8000/api/repository-data")
    print("🔍 Module search available at: http://localhost:8000/api/search?q=<query>")
    print("📚 Documentation available at: http://localhost:8000")
    
    app.run(host='0.0.0.0', port=port, debug=False)


def print_summary(code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> None:
    """Print analysis summary."""
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    
    overview = code_analysis.get('overview', {})
    complexity = code_analysis.get('complexity', {})
    
    print(f"\n📈 Code Statistics:")
    print(f"   • Total Files: {overview.get('total_files', 0)}")
    print(f"   • Total Lines: {overview.get('total_lines', 0):,}")
    print(f"   • Total Functions: {overview.get('total_functions', 0)}")
    print(f"   • Total Classes: {overview.get('total_classes', 0)}")
    print(f"   • Project Type: {overview.get('project_type', 'Unknown')}")
    
    if overview.get('languages_detected'):
        print(f"   • Languages: {', '.join(overview['languages_detected'])}")
    
    print(f"\n🔧 Code Quality:")
    summary = complexity.get('summary', {})
    if summary:
        print(f"   • Average Complexity: {summary.get('avg_complexity', 0):.2f}")
        print(f"   • Max Complexity: {summary.get('max_complexity', 0)}")
        print(f"   • High Complexity Functions: {len(summary.get('high_complexity_functions', []))}")
    
    print(f"\n🤖 AI/ML Components:")
    print(f"   • Frameworks Detected: {len(ai_analysis.get('frameworks_detected', []))}")
    print(f"   • ML Models: {len(ai_analysis.get('ml_models', []))}")
    print(f"   • Pipelines: {len(ai_analysis.get('pipelines', []))}")
    print(f"   • Training Scripts: {len(ai_analysis.get('training_scripts', []))}")
    print(f"   • Inference Endpoints: {len(ai_analysis.get('inference_endpoints', []))}")
    
    if ai_analysis.get('frameworks_detected'):
        print(f"   • Frameworks: {', '.join(set(ai_analysis['frameworks_detected']))}")


def main():
    """Main entry point for the documentation generator."""
    parser = argparse.ArgumentParser(
        description="Auto Documentation Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --analyze --generate                    # Analyze and generate docs
  %(prog)s --analyze --generate --build            # Analyze, generate, and build site
  %(prog)s --serve                                 # Serve existing documentation
  %(prog)s --repo /path/to/repo --output ./my-docs # Custom paths
        """
    )
    
    parser.add_argument(
        '--repo', 
        default='.',
        help='Path to repository to analyze (default: current directory)'
    )
    
    parser.add_argument(
        '--config',
        default='documentor.yaml',
        help='Path to documentor configuration file'
    )
    
    parser.add_argument(
        '--output',
        default='docs',
        help='Output directory for documentation'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze the codebase'
    )
    
    parser.add_argument(
        '--generate',
        action='store_true', 
        help='Generate documentation'
    )
    
    parser.add_argument(
        '--build',
        action='store_true',
        help='Build MkDocs site'
    )
    
    parser.add_argument(
        '--serve',
        action='store_true',
        help='Serve documentation site'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for serving site (default: 8000)'
    )
    
    parser.add_argument(
        '--format',
        choices=['html', 'markdown', 'mkdocs'],
        help='Documentation output format (default: html)'
    )
    
    parser.add_argument(
        '--deploy',
        action='store_true',
        help='Deploy to GitHub Pages (requires GitHub Actions)'
    )
    
    args = parser.parse_args()
    
    # If no action specified, default to analyze and generate
    if not any([args.analyze, args.generate, args.build, args.serve]):
        args.analyze = True
        args.generate = True
    
    # Load configuration
    config = load_config(args.config)
    
    # Override format from command line if provided
    if args.format:
        if 'documentation' not in config:
            config['documentation'] = {}
        config['documentation']['output_format'] = args.format
    
    setup_logging(config)
    
    print("🚀 Auto Documentation Generation System")
    print(f"📁 Repository: {Path(args.repo).resolve()}")
    print(f"📊 Output: {Path(args.output).resolve()}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Analysis phase
        if args.analyze:
            code_analysis, ai_analysis = analyze_codebase(args.repo, config)
            
            # Print summary
            print_summary(code_analysis, ai_analysis)
        else:
            # Load existing analysis (if available)
            code_analysis, ai_analysis = {}, {}
        
        # Generation phase
        if args.generate:
            if not (code_analysis and ai_analysis):
                print("⚠️ No analysis data available. Running analysis first...")
                code_analysis, ai_analysis = analyze_codebase(args.repo, config)
            
            generate_documentation(code_analysis, ai_analysis, config, args.output)
        
        # Build phase
        if args.build:
            build_site(args.output)
        
        # Serve phase
        if args.serve:
            serve_site(args.output, args.port, args.repo)
        
        print(f"\n🎉 Process completed successfully!")
        print(f"⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.exception("Detailed error information:")
        sys.exit(1)


if __name__ == "__main__":
    main()
