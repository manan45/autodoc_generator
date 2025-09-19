#!/usr/bin/env python3
"""
AI Analysis Coordinator

Coordinates AI-enhanced code analysis using modular components:
- AIPromptBuilder for intelligent prompt construction
- DiagramFactory for hierarchical diagram generation  
- CodeMemorySystem for context enhancement and local code database integration
- OpenAI API integration with caching and fallback models

This is the main orchestrator that replaces the monolithic ai_analysis_generator.py
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import openai
from datetime import datetime, timedelta
import hashlib

from .ai_prompt_builder import AIPromptBuilder
from .diagram_factory import DiagramFactory
from .code_memory_system import CodeMemorySystem

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not available, environment variables will still work
    pass


class AIAnalysisCoordinator:
    """Coordinates AI-enhanced code analysis using modular components."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.prompt_builder = AIPromptBuilder(config)
        self.diagram_factory = DiagramFactory()
        self.memory_system = CodeMemorySystem(config)
        
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
        
        # Store current analysis in memory system
        project_path = code_analysis.get('repository_path', '.')
        session_id = self.memory_system.store_analysis_session(project_path, code_analysis, ai_analysis)
        
        enhanced_analysis = {}
        
        try:
            # 1. API Analysis
            self.logger.info("Analyzing API endpoints and interfaces...")
            enhanced_analysis['api_analysis'] = self._analyze_api_endpoints(code_analysis, project_path)
            
            # 2. Architecture Analysis
            self.logger.info("Analyzing system architecture patterns...")
            enhanced_analysis['architecture_analysis'] = self._analyze_architecture_patterns(code_analysis, project_path)
            
            # 3. Component Analysis
            self.logger.info("Analyzing component relationships...")
            enhanced_analysis['component_analysis'] = self._analyze_component_relationships(code_analysis, project_path)
            
            # 4. Data Flow Analysis
            self.logger.info("Analyzing data flow patterns...")
            enhanced_analysis['dataflow_analysis'] = self._analyze_data_flow_patterns(code_analysis, project_path)
            
            # 5. ML Pipeline Analysis
            self.logger.info("Analyzing ML pipelines and modules...")
            enhanced_analysis['ml_analysis'] = self._analyze_ml_components(code_analysis, ai_analysis, project_path)
            
            # 6. Generate Mermaid Diagrams
            self.logger.info("Generating comprehensive hierarchical diagrams...")
            enhanced_analysis['diagrams'] = self.diagram_factory.create_all_diagrams(enhanced_analysis)
            
            # Add metadata
            enhanced_analysis['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'analysis_type': 'ai_enhanced',
                'model_used': os.getenv("OPENAI_MODEL", "gpt-4.1"),
                'session_id': session_id,
                'memory_stats': self.memory_system.get_memory_stats()
            }
            
            # Store enhanced insights in memory
            self._store_insights_in_memory(enhanced_analysis, project_path)
            
        except Exception as e:
            self.logger.error(f"Error during AI analysis: {e}")
            self.logger.warning("Using basic analysis without AI enhancement")
            enhanced_analysis = self._create_basic_enhanced_analysis(code_analysis, ai_analysis)
        
        return enhanced_analysis
    
    def _analyze_api_endpoints(self, code_analysis: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Analyze API endpoints and interfaces using AI with memory enhancement."""
        
        self.logger.info("🔍 Starting API endpoint analysis...")
        
        # Build enhanced prompt with memory context
        base_prompt = self.prompt_builder.build_api_analysis_prompt(code_analysis)
        enhanced_prompt = self.memory_system.enhance_prompt_with_context(
            base_prompt, project_path, 'api_analysis'
        )
        
        self.logger.info("📤 SENDING API ANALYSIS PROMPT:")
        self.logger.info("=" * 50)
        self.logger.info(enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt)
        self.logger.info("=" * 50)
        
        response = self._query_openai(enhanced_prompt, use_gpt35=False)
        return self._parse_json_response(response, "API analysis", {
            "endpoints": [], "interfaces": [], "patterns": []
        })
    
    def _analyze_architecture_patterns(self, code_analysis: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Analyze system architecture patterns using AI with memory enhancement."""
        
        base_prompt = self.prompt_builder.build_architecture_analysis_prompt(code_analysis)
        enhanced_prompt = self.memory_system.enhance_prompt_with_context(
            base_prompt, project_path, 'architecture_analysis'
        )
        
        response = self._query_openai(enhanced_prompt, use_gpt35=False)
        return self._parse_json_response(response, "Architecture analysis", {
            "layers": [], "patterns": [], "principles": []
        })
    
    def _analyze_component_relationships(self, code_analysis: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Analyze component relationships and interactions using AI with memory enhancement."""
        
        base_prompt = self.prompt_builder.build_component_analysis_prompt(code_analysis)
        enhanced_prompt = self.memory_system.enhance_prompt_with_context(
            base_prompt, project_path, 'component_analysis'
        )
        
        response = self._query_openai(enhanced_prompt, use_gpt35=False)
        return self._parse_json_response(response, "Component analysis", {
            "components": [], "relationships": [], "communication_patterns": []
        })
    
    def _analyze_data_flow_patterns(self, code_analysis: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Analyze data flow patterns using AI with memory enhancement."""
        
        base_prompt = self.prompt_builder.build_dataflow_analysis_prompt(code_analysis)
        enhanced_prompt = self.memory_system.enhance_prompt_with_context(
            base_prompt, project_path, 'dataflow_analysis'
        )
        
        response = self._query_openai(enhanced_prompt, use_gpt35=False)
        return self._parse_json_response(response, "Data flow analysis", {
            "data_sources": [], "transformations": [], "data_stores": [], "flow_patterns": []
        })
    
    def _analyze_ml_components(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Analyze ML pipelines and components using AI with memory enhancement."""
        
        base_prompt = self.prompt_builder.build_ml_analysis_prompt(code_analysis, ai_analysis)
        enhanced_prompt = self.memory_system.enhance_prompt_with_context(
            base_prompt, project_path, 'ml_analysis'
        )
        
        response = self._query_openai(enhanced_prompt, use_gpt35=False)
        return self._parse_json_response(response, "ML analysis", {
            "models": [], "pipelines": [], "infrastructure": []
        })
    
    def _query_openai(self, prompt: str, use_gpt35: bool = False) -> str:
        """Query OpenAI with the given prompt and return the response."""
        try:
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
            
            # Use the OpenAI client API (v1.0+)
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
                    return self._query_openai(prompt, use_gpt35=False)
                self.logger.info("Falling back to gpt-3.5-turbo...")
                return self._query_openai(prompt, use_gpt35=True)
            return "{}"
    
    def _parse_json_response(self, response: str, analysis_type: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON response from OpenAI with error handling."""
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
            self.logger.error(f"Failed to parse {analysis_type} JSON")
            self.logger.error(f"Raw response: {response[:200]}...")
            return fallback
    
    def _store_insights_in_memory(self, enhanced_analysis: Dict[str, Any], project_path: str) -> None:
        """Store analysis insights in memory system for future reference."""
        
        try:
            # Store key insights for each analysis type
            for analysis_type, data in enhanced_analysis.items():
                if isinstance(data, dict) and analysis_type != 'metadata':
                    key = f"{project_path}_{analysis_type}"
                    content = json.dumps(data, indent=2)
                    self.memory_system.store_context_memory(
                        key, content, analysis_type, relevance_score=0.9
                    )
            
            self.logger.debug("Stored analysis insights in memory system")
            
        except Exception as e:
            self.logger.error(f"Failed to store insights in memory: {e}")
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Create a stable cache key for a given prompt and model."""
        # Include a version segment to allow future invalidations
        version_tag = 'ai_analysis_coordinator_v1'
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
        
        basic_analysis = {
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
            'metadata': {'generated_at': datetime.now().isoformat(), 'analysis_type': 'basic', 'model_used': 'none'}
        }
        
        # Generate diagrams even for basic analysis
        basic_analysis['diagrams'] = self.diagram_factory.create_all_diagrams(basic_analysis)
        
        return basic_analysis
