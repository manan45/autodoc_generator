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


def serve_site(output_dir: str = "docs", port: int = 8000) -> None:
    """Serve the documentation site locally."""
    print(f"\n🚀 Starting documentation server on port {port}...")
    
    try:
        import subprocess
        import os
        from pathlib import Path
        
        # Check if we're serving HTML or MkDocs format
        output_path = Path(output_dir)
        html_index = output_path / "index.html"
        mkdocs_config = Path("mkdocs.yml")
        
        if html_index.exists() and not mkdocs_config.exists():
            # Serve HTML files directly using Python's built-in server
            print(f"📄 Serving HTML documentation from {output_dir}")
            os.chdir(output_dir)
            subprocess.run(['python3', '-m', 'http.server', str(port)])
        elif mkdocs_config.exists():
            # Use MkDocs serve
            print(f"📚 Serving MkDocs site")
            subprocess.run(['mkdocs', 'serve', '--dev-addr', f'127.0.0.1:{port}'])
        else:
            # Fallback to simple HTTP server
            print(f"📄 Serving documentation from {output_dir}")
            os.chdir(output_dir)
            subprocess.run(['python3', '-m', 'http.server', str(port)])
        
    except ImportError:
        print("⚠️ MkDocs not installed. Install with: pip install mkdocs mkdocs-material")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error serving site: {e}")
        # Fallback to simple HTTP server
        try:
            import os
            os.chdir(output_dir)
            subprocess.run(['python3', '-m', 'http.server', str(port)])
        except Exception as fallback_error:
            print(f"❌ Fallback server also failed: {fallback_error}")


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
            serve_site(args.output, args.port)
        
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
