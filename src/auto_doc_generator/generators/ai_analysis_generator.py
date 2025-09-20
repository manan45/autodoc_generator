#!/usr/bin/env python3
"""
AI Analysis Generator

Uses ChatGPT-4 to enhance code analysis with intelligent insights about:
- API endpoints and interfaces
- System architecture patterns
- Component relationships
- Data flow patterns
- ML pipelines and modules

Creates structured metadata that drives documentation and diagram generation.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import openai
from datetime import datetime, timedelta
import hashlib
import sqlite3
import pickle
import numpy as np

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not available, environment variables will still work
    pass

# Optional: Vector embeddings for semantic search
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None


class AIAnalysisGenerator:
    """Generates enhanced code analysis using AI to create structured documentation metadata."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Set up OpenAI client
        self.api_key = self.config.get('ai', {}).get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.logger.warning("OpenAI API key not found. AI analysis enhancement will be skipped.")
            self.client = None
        else:
            try:
                # Initialize OpenAI client (requires v1.0+)
                self.client = openai.OpenAI(api_key=self.api_key)
                self.logger.info("OpenAI client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
                self.logger.warning("Falling back to basic analysis without AI enhancement")
                self.client = None

        # Caching configuration for LLM responses
        ai_config = (self.config.get('ai') or {})
        cache_config = (ai_config.get('cache') or {})

        # Enable caching by default
        self.cache_enabled: bool = bool(cache_config.get('enabled', True))
        # Default cache directory
        default_cache_dir = os.path.join('.cache', 'ai_responses')
        self.cache_dir: Path = Path(cache_config.get('dir', default_cache_dir))
        # TTL in hours (falls back to global performance cache duration if present)
        perf_config = (self.config.get('performance') or {})
        self.cache_ttl_hours: int = int(cache_config.get('ttl_hours', perf_config.get('cache_duration_hours', 24)))

        if self.cache_enabled:
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"LLM response cache enabled at: {self.cache_dir} (TTL: {self.cache_ttl_hours}h)")
            except Exception as e:
                self.logger.warning(f"Could not create cache directory {self.cache_dir}: {e}")
                self.cache_enabled = False
    
    def enhance_code_analysis(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance code analysis with AI-powered insights and structured metadata."""
        self.logger.info("🚀 STARTING AI-ENHANCED CODE ANALYSIS")
        self.logger.info(f"🔑 API Key available: {'Yes' if self.api_key else 'No'}")
        self.logger.info(f"🤖 OpenAI Client: {'Initialized' if self.client else 'Not available'}")
        
        if not self.client:
            self.logger.warning("⚠️ OpenAI client not available. Using basic analysis.")
            return self._create_basic_enhanced_analysis(code_analysis, ai_analysis)
        
        enhanced_analysis = {}
        
        try:
            # 1. API Analysis
            self.logger.info("Analyzing API endpoints and interfaces...")
            enhanced_analysis['api_analysis'] = self._analyze_api_endpoints(code_analysis)
            
            # 2. Architecture Analysis
            self.logger.info("Analyzing system architecture patterns...")
            enhanced_analysis['architecture_analysis'] = self._analyze_architecture_patterns(code_analysis)
            
            # 3. Component Analysis
            self.logger.info("Analyzing component relationships...")
            enhanced_analysis['component_analysis'] = self._analyze_component_relationships(code_analysis)
            
            # 4. Data Flow Analysis
            self.logger.info("Analyzing data flow patterns...")
            enhanced_analysis['dataflow_analysis'] = self._analyze_data_flow_patterns(code_analysis)
            
            # 5. ML Pipeline Analysis
            self.logger.info("Analyzing ML pipelines and modules...")
            enhanced_analysis['ml_analysis'] = self._analyze_ml_components(code_analysis, ai_analysis)
            
            # 6. Generate Mermaid Diagrams
            self.logger.info("Generating Mermaid diagrams...")
            enhanced_analysis['diagrams'] = self._generate_mermaid_diagrams(enhanced_analysis)
            
            # Add metadata
            enhanced_analysis['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'analysis_type': 'ai_enhanced',
                'model_used': 'gpt-4'
            }
            
        except Exception as e:
            self.logger.error(f"Error during AI analysis: {e}")
            self.logger.warning("Using basic analysis without AI enhancement")
            enhanced_analysis = self._create_basic_enhanced_analysis(code_analysis, ai_analysis)
        
        return enhanced_analysis
    
    def _analyze_api_endpoints(self, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API endpoints and interfaces using AI."""
        
        self.logger.info("🔍 Starting API endpoint analysis...")
        
        # Prepare concise context for AI analysis (reduce token usage)
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
        
        self.logger.info("📤 SENDING API ANALYSIS PROMPT:")
        self.logger.info("=" * 50)
        self.logger.info(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        self.logger.info("=" * 50)
        
        response = self._query_gpt4(prompt, use_gpt35=False)  # Force GPT-4 family for higher quality
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]   # Remove ```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse API analysis JSON")
            self.logger.error(f"Raw response: {response[:200]}...")
            return {"endpoints": [], "interfaces": [], "patterns": []}
    
    def _analyze_architecture_patterns(self, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system architecture patterns using AI."""
        
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
        
        response = self._query_gpt4(prompt, use_gpt35=False)
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]   # Remove ```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse architecture analysis JSON")
            self.logger.error(f"Raw response: {response[:200]}...")
            return {"layers": [], "patterns": [], "principles": []}
    
    def _analyze_component_relationships(self, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze component relationships and interactions using AI."""
        
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
        
        response = self._query_gpt4(prompt, use_gpt35=False)  # Force GPT-4 family
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]   # Remove ```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse component analysis JSON")
            self.logger.error(f"Raw response: {response[:200]}...")
            return {"components": [], "relationships": [], "communication_patterns": []}
    
    def _analyze_data_flow_patterns(self, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data flow patterns using AI."""
        
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
        
        response = self._query_gpt4(prompt, use_gpt35=False)  # Force GPT-4 family
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]   # Remove ```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse data flow analysis JSON")
            self.logger.error(f"Raw response: {response[:200]}...")
            return {"data_sources": [], "transformations": [], "data_stores": [], "flow_patterns": []}
    
    def _analyze_ml_components(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ML pipelines and components using AI."""
        
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
        
        response = self._query_gpt4(prompt, use_gpt35=False)  # Force GPT-4 family
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]   # Remove ```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse ML analysis JSON")
            self.logger.error(f"Raw response: {response[:200]}...")
            return {"models": [], "pipelines": [], "infrastructure": []}
    
    def _generate_mermaid_diagrams(self, enhanced_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive hierarchical Mermaid diagrams based on enhanced analysis."""
        
        diagrams = {}
        
        # 1. Repository Overview - High Level
        diagrams['repository_overview'] = self._create_repository_overview_mermaid(enhanced_analysis)
        
        # 2. Enterprise/System Level Architecture
        diagrams['enterprise_architecture'] = self._create_enterprise_architecture_mermaid(enhanced_analysis.get('architecture_analysis', {}))
        
        # 3. Logical Architecture - Component Relationships
        diagrams['logical_architecture'] = self._create_logical_architecture_mermaid(enhanced_analysis.get('component_analysis', {}))
        
        # 4. Physical Architecture - Deployment View
        diagrams['physical_architecture'] = self._create_physical_architecture_mermaid(enhanced_analysis.get('architecture_analysis', {}))
        
        # 5. Data/ML Pipelines
        diagrams['pipeline_architecture'] = self._create_pipeline_architecture_mermaid(enhanced_analysis.get('dataflow_analysis', {}), enhanced_analysis.get('ml_analysis', {}))
        
        # 6. API Structure
        diagrams['api_architecture'] = self._create_api_architecture_mermaid(enhanced_analysis.get('api_analysis', {}))
        
        # 7. Module Deep Dive Diagrams
        diagrams['module_diagrams'] = self._create_module_deep_dive_diagrams(enhanced_analysis)
        
        # Legacy diagrams for backward compatibility
        diagrams['architecture'] = diagrams['enterprise_architecture']
        diagrams['components'] = diagrams['logical_architecture'] 
        diagrams['dataflow'] = diagrams['pipeline_architecture']
        diagrams['api'] = diagrams['api_architecture']
        
        return diagrams
    
    def _create_repository_overview_mermaid(self, enhanced_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create high-level repository overview diagram showing folder structure and main components."""
        
        mermaid = """flowchart TD
    subgraph "Repository Structure"
        ROOT[/"🏠 auto_doc_generator"/]
        
        subgraph "Core Application"
            SRC[/"📦 src/auto_doc_generator"/]
            ANALYZERS[/"🔍 analyzers/"/]
            GENERATORS[/"⚙️ generators/"/]
            MAIN[/"🚀 main.py"/]
        end
        
        subgraph "Configuration"
            CONFIG[/"⚙️ config/"/]
            TEMPLATES[/"📄 templates/"/] 
            HTML_TEMPLATES[/"🌐 html_templates/"/]
        end
        
        subgraph "Documentation Output"
            DOCS[/"📚 docs/"/]
            SITE[/"🌍 site/"/]
        end
        
        subgraph "Deployment"
            DOCKER[/"🐳 Dockerfile"/]
            REQUIREMENTS[/"📋 requirements.txt"/]
            SETUP[/"🔧 setup.py"/]
        end
        
        ROOT --> SRC
        ROOT --> CONFIG
        ROOT --> TEMPLATES
        ROOT --> HTML_TEMPLATES
        ROOT --> DOCS
        ROOT --> SITE
        ROOT --> DOCKER
        ROOT --> REQUIREMENTS
        ROOT --> SETUP
        
        SRC --> ANALYZERS
        SRC --> GENERATORS
        SRC --> MAIN
    end
    
    classDef core fill:#e3f2fd
    classDef config fill:#f3e5f5
    classDef output fill:#e8f5e8
    classDef deploy fill:#fff3e0
    
    class SRC,ANALYZERS,GENERATORS,MAIN core
    class CONFIG,TEMPLATES,HTML_TEMPLATES config
    class DOCS,SITE output
    class DOCKER,REQUIREMENTS,SETUP deploy"""
        
        description = "Repository structure overview showing main folders, core application components, configuration, documentation output, and deployment files."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'repository_overview'
        }
    
    def _create_enterprise_architecture_mermaid(self, architecture_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create enterprise/system level architecture diagram."""
        
        layers = architecture_analysis.get('layers', [])
        patterns = architecture_analysis.get('patterns', [])
        
        mermaid = """graph TB
    subgraph "Enterprise Architecture"
        subgraph "External Systems"
            USER[👤 Developer/User]
            OPENAI[🤖 OpenAI API]
            GITHUB[📁 GitHub Repository]
        end
        
        subgraph "Documentation System"
            subgraph "Analysis Layer"
                CODE_ANALYZER[📊 Code Analyzer]
                AI_ANALYZER[🧠 AI Pipeline Analyzer]
                AI_ENHANCER[✨ AI Analysis Generator]
            end
            
            subgraph "Generation Layer"  
                HTML_GEN[🌐 HTML Generator]
                MD_GEN[📝 Markdown Generator]
                DIAGRAM_GEN[📈 Diagram Generator]
            end
            
            subgraph "Output Layer"
                HTML_DOCS[📄 HTML Documentation]
                STATIC_SITE[🌍 Static Site]
                DIAGRAMS[📊 Mermaid Diagrams]
            end
        end
        
        subgraph "Infrastructure"
            TEMPLATES[📋 Jinja2 Templates]
            ASSETS[🎨 CSS/JS Assets]
            CACHE[💾 Response Cache]
        end
    end
    
    %% Connections
    USER --> CODE_ANALYZER
    GITHUB --> CODE_ANALYZER
    CODE_ANALYZER --> AI_ANALYZER
    AI_ANALYZER --> AI_ENHANCER
    AI_ENHANCER --> OPENAI
    
    AI_ENHANCER --> HTML_GEN
    AI_ENHANCER --> MD_GEN
    AI_ENHANCER --> DIAGRAM_GEN
    
    HTML_GEN --> HTML_DOCS
    HTML_GEN --> STATIC_SITE
    DIAGRAM_GEN --> DIAGRAMS
    
    TEMPLATES --> HTML_GEN
    ASSETS --> HTML_DOCS
    CACHE --> AI_ENHANCER
    
    HTML_DOCS --> USER
    STATIC_SITE --> USER
    
    classDef external fill:#ffebee
    classDef analysis fill:#e3f2fd  
    classDef generation fill:#e8f5e8
    classDef output fill:#fff3e0
    classDef infra fill:#f3e5f5
    
    class USER,OPENAI,GITHUB external
    class CODE_ANALYZER,AI_ANALYZER,AI_ENHANCER analysis
    class HTML_GEN,MD_GEN,DIAGRAM_GEN generation
    class HTML_DOCS,STATIC_SITE,DIAGRAMS output
    class TEMPLATES,ASSETS,CACHE infra"""
        
        description = "Enterprise architecture showing the complete documentation generation system with external integrations, processing layers, and infrastructure components."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'enterprise_architecture'
        }
    
    def _create_logical_architecture_mermaid(self, component_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create logical architecture showing component relationships and data flow."""
        
        components = component_analysis.get('components', [])
        relationships = component_analysis.get('relationships', [])
        
        mermaid = """graph TD
    subgraph "Logical Architecture - Data Flow"
        subgraph "Input Processing"
            REPO_SCAN[🔍 Repository Scanner]
            FILE_PARSER[📄 File Parser]
            AST_ANALYZER[🌳 AST Analyzer]
        end
        
        subgraph "Analysis Engine"
            CODE_METRICS[📊 Code Metrics]
            COMPLEXITY_CALC[🧮 Complexity Calculator]
            PATTERN_DETECTOR[🔍 Pattern Detector]
            AI_PROCESSOR[🧠 AI Processor]
        end
        
        subgraph "Knowledge Base"
            ANALYSIS_DATA[(📊 Analysis Data)]
            AI_INSIGHTS[(🧠 AI Insights)]
            DIAGRAM_SPECS[(📈 Diagram Specs)]
        end
        
        subgraph "Content Generation"
            TEMPLATE_ENGINE[📋 Template Engine]
            CONTENT_BUILDER[🏗️ Content Builder]
            ASSET_MANAGER[🎨 Asset Manager]
        end
        
        subgraph "Output Generation"
            HTML_RENDERER[🌐 HTML Renderer]
            DIAGRAM_RENDERER[📊 Diagram Renderer]
            SITE_BUILDER[🏗️ Site Builder]
        end
    end
    
    %% Data Flow
    REPO_SCAN --> FILE_PARSER
    FILE_PARSER --> AST_ANALYZER
    AST_ANALYZER --> CODE_METRICS
    AST_ANALYZER --> COMPLEXITY_CALC
    AST_ANALYZER --> PATTERN_DETECTOR
    
    CODE_METRICS --> ANALYSIS_DATA
    COMPLEXITY_CALC --> ANALYSIS_DATA
    PATTERN_DETECTOR --> ANALYSIS_DATA
    
    ANALYSIS_DATA --> AI_PROCESSOR
    AI_PROCESSOR --> AI_INSIGHTS
    AI_INSIGHTS --> DIAGRAM_SPECS
    
    ANALYSIS_DATA --> TEMPLATE_ENGINE
    AI_INSIGHTS --> TEMPLATE_ENGINE
    DIAGRAM_SPECS --> TEMPLATE_ENGINE
    
    TEMPLATE_ENGINE --> CONTENT_BUILDER
    CONTENT_BUILDER --> HTML_RENDERER
    CONTENT_BUILDER --> DIAGRAM_RENDERER
    
    HTML_RENDERER --> SITE_BUILDER
    DIAGRAM_RENDERER --> SITE_BUILDER
    ASSET_MANAGER --> SITE_BUILDER
    
    classDef input fill:#e3f2fd
    classDef analysis fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef generation fill:#f3e5f5
    classDef output fill:#ffebee
    
    class REPO_SCAN,FILE_PARSER,AST_ANALYZER input
    class CODE_METRICS,COMPLEXITY_CALC,PATTERN_DETECTOR,AI_PROCESSOR analysis
    class ANALYSIS_DATA,AI_INSIGHTS,DIAGRAM_SPECS data
    class TEMPLATE_ENGINE,CONTENT_BUILDER,ASSET_MANAGER generation
    class HTML_RENDERER,DIAGRAM_RENDERER,SITE_BUILDER output"""
        
        description = "Logical architecture showing data flow from repository scanning through analysis, AI enhancement, content generation, and final output rendering."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'logical_architecture'
        }
    
    def _create_physical_architecture_mermaid(self, architecture_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create physical architecture showing deployment and infrastructure."""
        
        mermaid = """graph TB
    subgraph "Development Environment"
        subgraph "Local Machine"
            DEV_ENV[💻 Developer Environment]
            PYTHON_ENV[🐍 Python 3.9+ Virtual Env]
            CODE_EDITOR[📝 IDE/Code Editor]
        end
        
        subgraph "Local Services"
            FILE_SYSTEM[💾 File System]
            CACHE_DIR[📁 .cache/ai_responses/]
            OUTPUT_DIR[📁 docs/]
        end
    end
    
    subgraph "External Services"
        OPENAI_API[🤖 OpenAI API<br/>gpt-4.1/gpt-4/gpt-3.5]
        GITHUB_REPO[📁 GitHub Repository]
        PACKAGE_REGISTRY[📦 PyPI Registry]
    end
    
    subgraph "Runtime Components"
        subgraph "Python Process"
            MAIN_PROCESS[🚀 main.py Process]
            ANALYZER_WORKERS[⚙️ Analysis Workers]
            GENERATOR_WORKERS[🏭 Generator Workers]
        end
        
        subgraph "Memory"
            CODE_CACHE[🧠 Code Analysis Cache]
            AI_RESPONSE_CACHE[💭 AI Response Cache]
            TEMPLATE_CACHE[📋 Template Cache]
        end
    end
    
    subgraph "Output Deployment"
        subgraph "Static Site"
            HTML_FILES[📄 HTML Files]
            CSS_JS_ASSETS[🎨 CSS/JS Assets]
            MERMAID_DIAGRAMS[📊 Mermaid Diagrams]
        end
        
        subgraph "Hosting Options"
            GITHUB_PAGES[🌐 GitHub Pages]
            LOCAL_SERVER[🖥️ Local HTTP Server]
            STATIC_HOST[☁️ Static Hosting]
        end
    end
    
    %% Connections
    DEV_ENV --> PYTHON_ENV
    PYTHON_ENV --> MAIN_PROCESS
    CODE_EDITOR --> FILE_SYSTEM
    
    MAIN_PROCESS --> ANALYZER_WORKERS
    MAIN_PROCESS --> GENERATOR_WORKERS
    
    ANALYZER_WORKERS --> FILE_SYSTEM
    ANALYZER_WORKERS --> CODE_CACHE
    
    GENERATOR_WORKERS --> OPENAI_API
    GENERATOR_WORKERS --> AI_RESPONSE_CACHE
    GENERATOR_WORKERS --> TEMPLATE_CACHE
    
    AI_RESPONSE_CACHE --> CACHE_DIR
    
    GENERATOR_WORKERS --> HTML_FILES
    HTML_FILES --> OUTPUT_DIR
    CSS_JS_ASSETS --> OUTPUT_DIR
    MERMAID_DIAGRAMS --> OUTPUT_DIR
    
    OUTPUT_DIR --> GITHUB_PAGES
    OUTPUT_DIR --> LOCAL_SERVER
    OUTPUT_DIR --> STATIC_HOST
    
    GITHUB_REPO --> ANALYZER_WORKERS
    PACKAGE_REGISTRY --> PYTHON_ENV
    
    classDef dev fill:#e3f2fd
    classDef external fill:#ffebee
    classDef runtime fill:#e8f5e8
    classDef output fill:#fff3e0
    classDef hosting fill:#f3e5f5
    
    class DEV_ENV,PYTHON_ENV,CODE_EDITOR,FILE_SYSTEM,CACHE_DIR,OUTPUT_DIR dev
    class OPENAI_API,GITHUB_REPO,PACKAGE_REGISTRY external
    class MAIN_PROCESS,ANALYZER_WORKERS,GENERATOR_WORKERS,CODE_CACHE,AI_RESPONSE_CACHE,TEMPLATE_CACHE runtime
    class HTML_FILES,CSS_JS_ASSETS,MERMAID_DIAGRAMS output
    class GITHUB_PAGES,LOCAL_SERVER,STATIC_HOST hosting"""
        
        description = "Physical architecture showing deployment environment, runtime components, external services, caching layers, and hosting options."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'physical_architecture'
        }
    
    def _create_pipeline_architecture_mermaid(self, dataflow_analysis: Dict[str, Any], ml_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create detailed pipeline architecture for data/ML workflows."""
        
        sources = dataflow_analysis.get('data_sources', [])
        transformations = dataflow_analysis.get('transformations', [])
        models = ml_analysis.get('models', [])
        
        mermaid = """flowchart LR
    subgraph "Data Ingestion Pipeline"
        subgraph "Source Analysis"
            REPO_INPUT[📁 Repository Files]
            CONFIG_INPUT[⚙️ Configuration Files]
            TEMPLATE_INPUT[📋 Template Files]
        end
        
        subgraph "File Processing"
            FILE_FILTER[🔍 File Filter<br/>*.py, *.yaml, *.md]
            SYNTAX_PARSER[📝 Syntax Parser<br/>AST, YAML, MD]
            CONTENT_EXTRACTOR[📤 Content Extractor]
        end
    end
    
    subgraph "Analysis Pipeline"
        subgraph "Code Analysis"
            STRUCTURE_ANALYZER[🏗️ Structure Analyzer]
            COMPLEXITY_ANALYZER[📊 Complexity Analyzer] 
            PATTERN_ANALYZER[🔍 Pattern Analyzer]
        end
        
        subgraph "AI Enhancement Pipeline"
            AI_PROMPT_BUILDER[🧠 AI Prompt Builder]
            OPENAI_PROCESSOR[🤖 OpenAI Processor]
            RESPONSE_PARSER[📥 Response Parser]
            DIAGRAM_GENERATOR[📈 Diagram Generator]
        end
    end
    
    subgraph "Content Generation Pipeline"
        subgraph "Template Processing"
            TEMPLATE_LOADER[📋 Template Loader]
            DATA_MERGER[🔄 Data Merger]
            JINJA_RENDERER[⚙️ Jinja2 Renderer]
        end
        
        subgraph "Asset Pipeline"
            CSS_PROCESSOR[🎨 CSS Processor]
            JS_BUNDLER[📦 JS Bundler]
            ASSET_OPTIMIZER[⚡ Asset Optimizer]
        end
    end
    
    subgraph "Output Pipeline"
        HTML_GENERATOR[🌐 HTML Generator]
        DIAGRAM_RENDERER[📊 Diagram Renderer]
        SITE_ASSEMBLER[🏗️ Site Assembler]
        FINAL_OUTPUT[📄 Documentation Site]
    end
    
    %% Pipeline Flow
    REPO_INPUT --> FILE_FILTER
    CONFIG_INPUT --> FILE_FILTER
    TEMPLATE_INPUT --> FILE_FILTER
    
    FILE_FILTER --> SYNTAX_PARSER
    SYNTAX_PARSER --> CONTENT_EXTRACTOR
    
    CONTENT_EXTRACTOR --> STRUCTURE_ANALYZER
    CONTENT_EXTRACTOR --> COMPLEXITY_ANALYZER
    CONTENT_EXTRACTOR --> PATTERN_ANALYZER
    
    STRUCTURE_ANALYZER --> AI_PROMPT_BUILDER
    COMPLEXITY_ANALYZER --> AI_PROMPT_BUILDER
    PATTERN_ANALYZER --> AI_PROMPT_BUILDER
    
    AI_PROMPT_BUILDER --> OPENAI_PROCESSOR
    OPENAI_PROCESSOR --> RESPONSE_PARSER
    RESPONSE_PARSER --> DIAGRAM_GENERATOR
    
    STRUCTURE_ANALYZER --> DATA_MERGER
    COMPLEXITY_ANALYZER --> DATA_MERGER
    PATTERN_ANALYZER --> DATA_MERGER
    RESPONSE_PARSER --> DATA_MERGER
    DIAGRAM_GENERATOR --> DATA_MERGER
    
    TEMPLATE_LOADER --> JINJA_RENDERER
    DATA_MERGER --> JINJA_RENDERER
    
    JINJA_RENDERER --> HTML_GENERATOR
    CSS_PROCESSOR --> HTML_GENERATOR
    JS_BUNDLER --> HTML_GENERATOR
    ASSET_OPTIMIZER --> HTML_GENERATOR
    
    HTML_GENERATOR --> SITE_ASSEMBLER
    DIAGRAM_RENDERER --> SITE_ASSEMBLER
    SITE_ASSEMBLER --> FINAL_OUTPUT
    
    classDef ingestion fill:#e3f2fd
    classDef analysis fill:#e8f5e8
    classDef ai fill:#fff3e0
    classDef generation fill:#f3e5f5
    classDef output fill:#ffebee
    
    class REPO_INPUT,CONFIG_INPUT,TEMPLATE_INPUT,FILE_FILTER,SYNTAX_PARSER,CONTENT_EXTRACTOR ingestion
    class STRUCTURE_ANALYZER,COMPLEXITY_ANALYZER,PATTERN_ANALYZER analysis
    class AI_PROMPT_BUILDER,OPENAI_PROCESSOR,RESPONSE_PARSER,DIAGRAM_GENERATOR ai
    class TEMPLATE_LOADER,DATA_MERGER,JINJA_RENDERER,CSS_PROCESSOR,JS_BUNDLER,ASSET_OPTIMIZER generation
    class HTML_GENERATOR,DIAGRAM_RENDERER,SITE_ASSEMBLER,FINAL_OUTPUT output"""
        
        description = "Complete pipeline architecture showing data ingestion, analysis, AI enhancement, content generation, and output assembly workflows."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'pipeline_architecture'
        }
    
    def _create_api_architecture_mermaid(self, api_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create API architecture diagram showing interfaces and endpoints."""
        
        endpoints = api_analysis.get('endpoints', [])
        interfaces = api_analysis.get('interfaces', [])
        
        mermaid = """graph TB
    subgraph "API Architecture"
        subgraph "External APIs"
            OPENAI_API[🤖 OpenAI API]
            GITHUB_API[📁 GitHub API]
        end
        
        subgraph "Internal APIs & Interfaces"
            subgraph "Analysis Interfaces"
                ICODE_ANALYZER[📊 ICodeAnalyzer]
                IAI_ANALYZER[🧠 IAIAnalyzer] 
                IDIAGRAM_GEN[📈 IDiagramGenerator]
            end
            
            subgraph "Generator Interfaces"
                IHTML_GEN[🌐 IHTMLGenerator]
                IMARKDOWN_GEN[📝 IMarkdownGenerator]
                ITEMPLATE_ENGINE[📋 ITemplateEngine]
            end
            
            subgraph "Data Interfaces"
                ICONFIG_LOADER[⚙️ IConfigLoader]
                IFILE_HANDLER[📄 IFileHandler]
                ICACHE_MANAGER[💾 ICacheManager]
            end
        end
        
        subgraph "CLI Interface"
            MAIN_CLI[🖥️ Main CLI]
            ARG_PARSER[📝 Argument Parser]
            COMMAND_ROUTER[🔀 Command Router]
        end
        
        subgraph "Core Components"
            CODE_ANALYZER[📊 CodeAnalyzer]
            AI_PIPELINE_ANALYZER[🧠 AIPipelineAnalyzer]
            HTML_GENERATOR[🌐 HTMLGenerator]
            MARKDOWN_GENERATOR[📝 MarkdownGenerator]
        end
    end
    
    %% Interface Implementations
    CODE_ANALYZER -.->|implements| ICODE_ANALYZER
    AI_PIPELINE_ANALYZER -.->|implements| IAI_ANALYZER
    HTML_GENERATOR -.->|implements| IHTML_GEN
    MARKDOWN_GENERATOR -.->|implements| IMARKDOWN_GEN
    
    %% API Connections
    AI_PIPELINE_ANALYZER --> OPENAI_API
    CODE_ANALYZER --> GITHUB_API
    
    %% CLI Flow
    MAIN_CLI --> ARG_PARSER
    ARG_PARSER --> COMMAND_ROUTER
    COMMAND_ROUTER --> CODE_ANALYZER
    COMMAND_ROUTER --> AI_PIPELINE_ANALYZER
    COMMAND_ROUTER --> HTML_GENERATOR
    COMMAND_ROUTER --> MARKDOWN_GENERATOR
    
    %% Internal Dependencies
    HTML_GENERATOR --> ITEMPLATE_ENGINE
    MARKDOWN_GENERATOR --> ITEMPLATE_ENGINE
    CODE_ANALYZER --> IFILE_HANDLER
    AI_PIPELINE_ANALYZER --> ICACHE_MANAGER
    
    classDef external fill:#ffebee
    classDef interface fill:#e3f2fd
    classDef cli fill:#e8f5e8
    classDef component fill:#fff3e0
    
    class OPENAI_API,GITHUB_API external
    class ICODE_ANALYZER,IAI_ANALYZER,IDIAGRAM_GEN,IHTML_GEN,IMARKDOWN_GEN,ITEMPLATE_ENGINE,ICONFIG_LOADER,IFILE_HANDLER,ICACHE_MANAGER interface
    class MAIN_CLI,ARG_PARSER,COMMAND_ROUTER cli
    class CODE_ANALYZER,AI_PIPELINE_ANALYZER,HTML_GENERATOR,MARKDOWN_GENERATOR component"""
        
        description = "API architecture showing external APIs, internal interfaces, CLI components, and their relationships with core implementation classes."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'api_architecture'
        }
    
    def _create_module_deep_dive_diagrams(self, enhanced_analysis: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Create detailed diagrams for each major module."""
        
        module_diagrams = {}
        
        # 1. Analyzers Module
        module_diagrams['analyzers'] = {
            'mermaid': """classDiagram
    class CodeAnalyzer {
        +repo_path: str
        +config: Dict
        +analyze_codebase() Dict
        +_analyze_file(file_path) Dict
        +_extract_functions(node) List
        +_extract_classes(node) List
        +_calculate_complexity(node) int
    }
    
    class AIPipelineAnalyzer {
        +config: Dict
        +analyze_ai_components(path) Dict
        +_detect_ml_frameworks() List
        +_find_model_files() List
        +_analyze_training_scripts() List
        +_detect_inference_endpoints() List
    }
    
    CodeAnalyzer --> "uses" AIPipelineAnalyzer
    CodeAnalyzer --> "analyzes" PythonFiles
    AIPipelineAnalyzer --> "detects" MLFrameworks
    AIPipelineAnalyzer --> "finds" ModelFiles""",
            'description': 'Analyzers module showing code analysis and AI pipeline detection components',
            'type': 'module_detail'
        }
        
        # 2. Generators Module  
        module_diagrams['generators'] = {
            'mermaid': """classDiagram
    class HTMLGenerator {
        +template_dir: str
        +output_dir: str
        +config: Dict
        +generate_all_documentation() Dict
        +generate_index_page() str
        +generate_architecture_page() str
        +generate_api_page() str
    }
    
    class MarkdownGenerator {
        +template_dir: str
        +output_dir: str
        +generate_documentation() Dict
        +_render_template() str
    }
    
    class AIAnalysisGenerator {
        +config: Dict
        +client: OpenAI
        +enhance_code_analysis() Dict
        +_analyze_api_endpoints() Dict
        +_generate_mermaid_diagrams() Dict
    }
    
    class DiagramGenerator {
        +create_architecture_diagram() str
        +create_flow_diagram() str
        +render_mermaid() str
    }
    
    HTMLGenerator --> "uses" AIAnalysisGenerator
    MarkdownGenerator --> "uses" AIAnalysisGenerator
    AIAnalysisGenerator --> "creates" DiagramGenerator
    AIAnalysisGenerator --> "calls" OpenAIAPI""",
            'description': 'Generators module showing HTML, Markdown, AI analysis, and diagram generation components',
            'type': 'module_detail'
        }
        
        # 3. Main Application Flow
        module_diagrams['main_flow'] = {
            'mermaid': """sequenceDiagram
    participant User
    participant Main
    participant CodeAnalyzer
    participant AIPipelineAnalyzer
    participant AIAnalysisGenerator
    participant HTMLGenerator
    participant OpenAI
    
    User->>Main: python main.py --analyze --generate
    Main->>CodeAnalyzer: analyze_codebase()
    CodeAnalyzer->>Main: code_analysis
    Main->>AIPipelineAnalyzer: analyze_ai_components()
    AIPipelineAnalyzer->>Main: ai_analysis
    Main->>AIAnalysisGenerator: enhance_code_analysis()
    AIAnalysisGenerator->>OpenAI: API calls for analysis
    OpenAI->>AIAnalysisGenerator: enhanced insights
    AIAnalysisGenerator->>Main: enhanced_analysis
    Main->>HTMLGenerator: generate_all_documentation()
    HTMLGenerator->>Main: documentation files
    Main->>User: Documentation generated successfully""",
            'description': 'Main application flow showing the sequence of operations from user input to documentation output',
            'type': 'sequence_diagram'
        }
        
        return module_diagrams
    
    def _create_architecture_mermaid(self, architecture_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create architecture Mermaid diagram."""
        
        layers = architecture_analysis.get('layers', [])
        patterns = architecture_analysis.get('patterns', [])
        
        if not layers:
            mermaid = """flowchart TD
    A[Application Layer] --> B[Business Logic Layer]
    B --> C[Data Access Layer]
    C --> D[Database Layer]"""
            
            description = "Basic layered architecture pattern with separation of concerns."
        else:
            mermaid = "flowchart TD\n"
            for i, layer in enumerate(layers):
                layer_id = f"L{i}"
                layer_name = layer.get('name', f'Layer {i}')
                mermaid += f"    {layer_id}[{layer_name}]\n"
                
                if i > 0:
                    prev_id = f"L{i-1}"
                    mermaid += f"    {prev_id} --> {layer_id}\n"
            
            # Add components to layers
            for i, layer in enumerate(layers):
                layer_id = f"L{i}"
                components = layer.get('components', [])[:3]  # Max 3 components per layer
                for j, component in enumerate(components):
                    comp_id = f"C{i}_{j}"
                    component_str = str(component) if component else f"Component{j}"
                    mermaid += f"    {comp_id}[{component_str}]\n"
                    mermaid += f"    {layer_id} -.-> {comp_id}\n"
            
            layer_names = [str(l.get('name', '')) for l in layers if l.get('name')]
            description = f"System architecture with {len(layers)} layers: " + ", ".join(layer_names)
            if patterns:
                pattern_names = [str(p.get('name', '')) for p in patterns if p.get('name')]
                description += f". Implements patterns: " + ", ".join(pattern_names)
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'architecture'
        }
    
    def _create_component_mermaid(self, component_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create component relationship Mermaid diagram."""
        
        components = component_analysis.get('components', [])
        relationships = component_analysis.get('relationships', [])
        
        if not components:
            mermaid = """graph TD
    A[Core Module] --> B[Service Layer]
    B --> C[Data Layer]
    A --> D[Utilities]"""
            
            description = "Basic component structure showing module dependencies."
        else:
            mermaid = "graph TD\n"
            
            # Add components
            comp_map = {}
            for i, comp in enumerate(components[:10]):  # Max 10 components
                comp_id = f"C{i}"
                comp_name = str(comp.get('name', f'Component {i}'))
                comp_type = str(comp.get('type', 'module'))
                comp_map[comp_name] = comp_id
                
                # Style based on type
                if comp_type == 'service':
                    mermaid += f"    {comp_id}[{comp_name}]:::service\n"
                elif comp_type == 'interface':
                    mermaid += f"    {comp_id}({comp_name}):::interface\n"
                else:
                    mermaid += f"    {comp_id}[{comp_name}]\n"
            
            # Add relationships
            for rel in relationships[:15]:  # Max 15 relationships
                source = rel.get('source', '')
                target = rel.get('target', '')
                rel_type = rel.get('type', 'uses')
                
                source_id = comp_map.get(source)
                target_id = comp_map.get(target)
                
                if source_id and target_id:
                    if rel_type == 'extends':
                        mermaid += f"    {source_id} -.->|extends| {target_id}\n"
                    elif rel_type == 'implements':
                        mermaid += f"    {source_id} ==>|implements| {target_id}\n"
                    else:
                        mermaid += f"    {source_id} --> {target_id}\n"
            
            # Add styling
            mermaid += """
    classDef service fill:#e1f5fe
    classDef interface fill:#f3e5f5"""
            
            description = f"Component relationships showing {len(components)} components and their interactions."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'components'
        }
    
    def _create_dataflow_mermaid(self, dataflow_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create data flow Mermaid diagram."""
        
        sources = dataflow_analysis.get('data_sources', [])
        transformations = dataflow_analysis.get('transformations', [])
        stores = dataflow_analysis.get('data_stores', [])
        
        if not any([sources, transformations, stores]):
            mermaid = """flowchart LR
    A[Data Input] --> B[Processing]
    B --> C[Validation]
    C --> D[Storage]
    D --> E[Output]"""
            
            description = "Basic data flow pattern with input, processing, and output stages."
        else:
            mermaid = "flowchart LR\n"
            
            # Add data sources
            for i, source in enumerate(sources[:5]):
                source_id = f"S{i}"
                source_name = str(source.get('name', f'Source {i}'))
                source_type = str(source.get('type', 'data'))
                
                if source_type == 'database':
                    mermaid += f"    {source_id}[({source_name})]\n"
                elif source_type == 'api':
                    mermaid += f"    {source_id}[/{source_name}/]\n"
                else:
                    mermaid += f"    {source_id}[{source_name}]\n"
            
            # Add transformations
            for i, transform in enumerate(transformations[:5]):
                trans_id = f"T{i}"
                trans_name = str(transform.get('name', f'Transform {i}'))
                mermaid += f"    {trans_id}[{trans_name}]\n"
            
            # Add data stores
            for i, store in enumerate(stores[:5]):
                store_id = f"D{i}"
                store_name = str(store.get('name', f'Store {i}'))
                store_type = str(store.get('type', 'storage'))
                
                if store_type == 'database':
                    mermaid += f"    {store_id}[({store_name})]\n"
                elif store_type == 'cache':
                    mermaid += f"    {store_id}[({store_name})]\n"
                else:
                    mermaid += f"    {store_id}[{store_name}]\n"
            
            # Connect the flow
            prev_ids = [f"S{i}" for i in range(len(sources[:5]))]
            
            if transformations:
                trans_ids = [f"T{i}" for i in range(len(transformations[:5]))]
                for prev_id in prev_ids:
                    for trans_id in trans_ids:
                        mermaid += f"    {prev_id} --> {trans_id}\n"
                prev_ids = trans_ids
            
            if stores:
                store_ids = [f"D{i}" for i in range(len(stores[:5]))]
                for prev_id in prev_ids:
                    for store_id in store_ids:
                        mermaid += f"    {prev_id} --> {store_id}\n"
            
            description = f"Data flow with {len(sources)} sources, {len(transformations)} transformations, and {len(stores)} storage points."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'dataflow'
        }
    
    def _create_api_mermaid(self, api_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create API structure Mermaid diagram."""
        
        endpoints = api_analysis.get('endpoints', [])
        interfaces = api_analysis.get('interfaces', [])
        
        if not endpoints and not interfaces:
            mermaid = """graph TD
    A[Client] --> B[API Gateway]
    B --> C[Authentication]
    C --> D[Business Logic]
    D --> E[Data Access]
    E --> F[Database]"""
            
            description = "Standard API architecture with authentication and layered access."
        else:
            mermaid = "graph TD\n"
            mermaid += "    Client[Client Application]\n"
            
            # Group endpoints by method
            methods = {}
            for endpoint in endpoints[:10]:
                method = endpoint.get('method', 'GET')
                if method not in methods:
                    methods[method] = []
                methods[method].append(endpoint)
            
            # Add method groups
            for method, eps in methods.items():
                method_id = f"M_{method}"
                mermaid += f"    {method_id}[{method} Endpoints]\n"
                mermaid += f"    Client --> {method_id}\n"
                
                # Add individual endpoints
                for i, ep in enumerate(eps[:3]):  # Max 3 per method
                    ep_id = f"E_{method}_{i}"
                    ep_path = str(ep.get('path', f'endpoint_{i}'))
                    mermaid += f"    {ep_id}[{ep_path}]\n"
                    mermaid += f"    {method_id} --> {ep_id}\n"
            
            # Add interfaces
            for i, interface in enumerate(interfaces[:5]):
                int_id = f"I{i}"
                int_name = str(interface.get('name', f'Interface {i}'))
                mermaid += f"    {int_id}({int_name})\n"
                mermaid += f"    Client --> {int_id}\n"
            
            description = f"API structure with {len(endpoints)} endpoints across {len(methods)} HTTP methods."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'api'
        }
    
    def _create_ml_pipeline_mermaid(self, ml_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create ML pipeline Mermaid diagram."""
        
        models = ml_analysis.get('models', [])
        pipelines = ml_analysis.get('pipelines', [])
        
        mermaid = "flowchart TD\n"
        
        if models:
            # Data preprocessing
            mermaid += "    A[Raw Data] --> B[Data Preprocessing]\n"
            mermaid += "    B --> C[Feature Engineering]\n"
            
            # Models
            for i, model in enumerate(models[:3]):
                model_id = f"M{i}"
                model_name = str(model.get('name', f'Model {i}'))
                model_type = str(model.get('type', 'ML Model'))
                mermaid += f"    {model_id}[{model_name}<br/>{model_type}]\n"
                mermaid += f"    C --> {model_id}\n"
            
            # Evaluation and deployment
            mermaid += "    M0 --> E[Model Evaluation]\n"
            mermaid += "    E --> F[Model Deployment]\n"
            mermaid += "    F --> G[Inference API]\n"
            
            description = f"ML pipeline with {len(models)} models including data preprocessing, training, and deployment."
        else:
            mermaid += "    A[Data Input] --> B[ML Processing]\n"
            mermaid += "    B --> C[Model Training]\n"
            mermaid += "    C --> D[Model Serving]\n"
            
            description = "Basic ML pipeline structure for training and serving models."
        
        return {
            'mermaid': mermaid,
            'description': description,
            'type': 'ml_pipeline'
        }
    
    def _query_gpt4(self, prompt: str, use_gpt35: bool = False) -> str:
        """Query GPT-4.1 by default, fallback to GPT-4, and only then GPT-3.5."""
        try:
            # Use GPT-3.5-turbo for simpler analysis to save tokens and cost
            # Prefer GPT-4.1 for better reasoning and JSON adherence
            model = "gpt-3.5-turbo" if use_gpt35 else os.getenv("OPENAI_MODEL", "gpt-4.1")
            max_tokens = 1500 if use_gpt35 else 4000
            
            # Check cache first
            if self.cache_enabled:
                cache_key = self._get_cache_key(prompt, model)
                cached = self._load_from_cache(cache_key)
                if cached is not None:
                    self.logger.info(f"📦 Cache hit for model={model}, prompt_hash={cache_key[:8]}...")
                    return cached

            self.logger.info(f"🚀 Making OpenAI API call to {model}...")
            self.logger.info(f"📊 Token limit: {max_tokens}")
            
            messages = [
                {"role": "system", "content": "You are an expert software architect. Analyze code and return concise, structured JSON responses. Focus on key patterns only."},
                {"role": "user", "content": prompt}
            ]
            
            # Use OpenAI client API (v1.0+)
            # Use the new Responses API if available; fallback to chat.completions
            try:
                if hasattr(self.client, 'responses'):
                    response = self.client.responses.create(
                        model=model,
                        input=messages,
                        temperature=0.3,
                        max_output_tokens=max_tokens
                    )
                    result = response.output_text.strip()
                else:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=0.3
                    )
                    result = response.choices[0].message.content.strip()
            except Exception:
                # Fallback to chat.completions if responses API fails
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.3
                )
                result = response.choices[0].message.content.strip()
            
            self.logger.info(f"✅ Received response from {model}: {len(result)} characters")
            self.logger.info(f"📥 Response preview: {result[:200]}...")
            
            # Save to cache
            if self.cache_enabled:
                try:
                    self._save_to_cache(cache_key, result)
                    self.logger.info(f"📦 Cached response for model={model}, prompt_hash={cache_key[:8]}...")
                except Exception as e:
                    self.logger.warning(f"Failed to write cache: {e}")
            
            return result
                
        except Exception as e:
            self.logger.error(f"Error querying {model}: {e}")
            # Fallback: 4.1 -> 4 -> 3.5
            if not use_gpt35:
                if model != "gpt-4":
                    self.logger.info("Falling back to gpt-4...")
                    os.environ["OPENAI_MODEL"] = "gpt-4"
                    return self._query_gpt4(prompt, use_gpt35=False)
                self.logger.info("Falling back to gpt-3.5-turbo...")
                return self._query_gpt4(prompt, use_gpt35=True)
            return "{}"

    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Create a stable cache key for a given prompt and model."""
        # Include a version segment to allow future invalidations
        version_tag = 'ai_analysis_generator_v1'
        hasher = hashlib.sha256()
        hasher.update(version_tag.encode('utf-8'))
        hasher.update(b'|')
        hasher.update(model.encode('utf-8'))
        hasher.update(b'|')
        hasher.update(prompt.encode('utf-8'))
        return hasher.hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[str]:
        """Load a cached response if present and not expired."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if not cache_file.exists():
                return None
            # Check TTL
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime > timedelta(hours=self.cache_ttl_hours):
                # Expired
                try:
                    cache_file.unlink(missing_ok=True)
                except Exception:
                    pass
                return None
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.warning(f"Failed to read cache: {e}")
            return None

    def _save_to_cache(self, cache_key: str, content: str) -> None:
        """Persist a response content to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_basic_enhanced_analysis(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create simplified analysis when AI is not available."""
        modules = code_analysis.get('modules', [])
        classes = code_analysis.get('classes', [])
        
        return {
            'api_analysis': {
                'endpoints': [],
                'interfaces': [{'name': cls.get('name', 'Unknown'), 'type': 'class', 'purpose': 'Basic interface'} 
                             for cls in classes[:5]],
                'patterns': []
            },
            'architecture_analysis': {
                'layers': [
                    {'name': 'Application Layer', 'purpose': 'Main application logic', 'components': [m.get('name', '') for m in modules[:3]]},
                    {'name': 'Core Layer', 'purpose': 'Core functionality', 'components': [m.get('name', '') for m in modules[3:6]]}
                ],
                'patterns': [],
                'principles': []
            },
            'component_analysis': {
                'components': [{'name': m.get('name', 'Unknown'), 'type': 'module', 'purpose': 'System component'} 
                              for m in modules[:8]],
                'relationships': [],
                'communication_patterns': []
            },
            'dataflow_analysis': {'data_sources': [], 'transformations': [], 'data_stores': [], 'flow_patterns': []},
            'ml_analysis': {'models': [], 'pipelines': [], 'infrastructure': []},
            'diagrams': {'architecture': {'mermaid': 'flowchart TD\n    A[Application] --> B[Core]\n    B --> C[Data]', 'description': 'Basic system architecture', 'type': 'architecture'}},
            'metadata': {'generated_at': datetime.now().isoformat(), 'analysis_type': 'basic', 'model_used': 'none'}
        }
