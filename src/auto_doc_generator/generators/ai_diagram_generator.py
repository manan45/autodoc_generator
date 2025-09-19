#!/usr/bin/env python3
"""
AI Diagram Generator

Uses ChatGPT-4 to generate comprehensive architecture diagrams from code analysis.
Generates logical architecture, physical architecture, and detailed module interaction diagrams.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import openai
from datetime import datetime


class AIDiagramGenerator:
    """Generates AI-powered architecture and module diagrams from code analysis."""
    
    def __init__(self, output_dir: str = "docs/diagrams", config: Dict[str, Any] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Set up OpenAI client
        self.api_key = self.config.get('ai', {}).get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.logger.warning("OpenAI API key not found. AI diagram generation will be skipped.")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_all_ai_diagrams(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all AI-powered diagrams from code analysis."""
        if not self.client:
            self.logger.warning("OpenAI client not available. Falling back to basic diagram generation.")
            return self._generate_fallback_diagrams(code_analysis, ai_analysis)
        
        diagrams = {}
        
        try:
            # 1. Logical Architecture Diagram
            diagrams['logical_architecture'] = self.generate_logical_architecture(code_analysis, ai_analysis)
            
            # 2. Physical Architecture Diagram  
            diagrams['physical_architecture'] = self.generate_physical_architecture(code_analysis, ai_analysis)
            
            # 3. Module Interaction Diagrams (one per major module)
            diagrams['module_diagrams'] = self.generate_module_interaction_diagrams(code_analysis)
            
            # 4. Data Flow Architecture
            diagrams['data_flow_architecture'] = self.generate_data_flow_architecture(code_analysis, ai_analysis)
            
            # 5. Component Communication Diagram
            diagrams['component_communication'] = self.generate_component_communication_diagram(code_analysis)
            
        except Exception as e:
            self.logger.error(f"Error generating AI diagrams: {e}")
            diagrams = self._generate_fallback_diagrams(code_analysis, ai_analysis)
        
        return diagrams
    
    def generate_logical_architecture(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate logical architecture diagram showing system components and relationships."""
        self.logger.info("Generating logical architecture diagram with AI...")
        
        # Prepare context for AI
        context = self._prepare_architecture_context(code_analysis, ai_analysis)
        
        prompt = f"""
Based on the following code analysis, generate a comprehensive logical architecture diagram in Mermaid syntax.
The diagram should show:
1. Main system layers (presentation, business logic, data access, etc.)
2. Key components and their responsibilities
3. Inter-component relationships and dependencies
4. Data flow between components
5. External integrations and interfaces

Focus on logical separation of concerns rather than physical deployment.

Code Analysis Context:
{json.dumps(context, indent=2)}

Generate a Mermaid flowchart diagram that clearly represents the logical architecture.
Include proper styling and grouping. Return ONLY the Mermaid syntax, no other text.
"""
        
        mermaid_diagram = self._query_gpt4(prompt)
        
        # Also generate a detailed description
        description_prompt = f"""
Based on the same code analysis, provide a detailed description of the logical architecture.
Explain each layer, component responsibilities, and key relationships.
Format as markdown with clear sections and bullet points.

{json.dumps(context, indent=2)}
"""
        
        description = self._query_gpt4(description_prompt)
        
        return {
            'mermaid': mermaid_diagram,
            'description': description,
            'type': 'logical_architecture',
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_physical_architecture(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate physical architecture diagram showing deployment and infrastructure."""
        self.logger.info("Generating physical architecture diagram with AI...")
        
        # Prepare context for AI
        context = self._prepare_architecture_context(code_analysis, ai_analysis)
        
        prompt = f"""
Based on the following code analysis, generate a physical architecture diagram in Mermaid syntax.
The diagram should show:
1. Deployment environments (development, staging, production)
2. Server/container deployment topology
3. Database and storage systems
4. Network connections and protocols
5. Load balancers, caches, and infrastructure components
6. External services and APIs
7. Security boundaries and access controls

Focus on how the system is deployed and runs in production.

Code Analysis Context:
{json.dumps(context, indent=2)}

Generate a Mermaid C4 or deployment diagram that represents the physical architecture.
Include proper styling and clear component boundaries. Return ONLY the Mermaid syntax.
"""
        
        mermaid_diagram = self._query_gpt4(prompt)
        
        # Generate deployment description
        description_prompt = f"""
Provide a detailed description of the physical/deployment architecture.
Include information about:
- Runtime environments and requirements
- Deployment patterns and strategies
- Infrastructure components and their roles
- Scalability and reliability considerations
- Security architecture

Format as markdown with clear sections.
"""
        
        description = self._query_gpt4(description_prompt)
        
        return {
            'mermaid': mermaid_diagram,
            'description': description,
            'type': 'physical_architecture',
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_module_interaction_diagrams(self, code_analysis: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Generate detailed diagrams for each major module showing component interactions."""
        self.logger.info("Generating module interaction diagrams with AI...")
        
        module_diagrams = {}
        modules = code_analysis.get('modules', [])
        
        # Group modules by package/directory for better organization
        module_groups = self._group_modules_by_package(modules)
        
        for package_name, package_modules in module_groups.items():
            if len(package_modules) < 2:  # Skip packages with only one module
                continue
            
            # Prepare context for this module group
            context = {
                'package_name': package_name,
                'modules': package_modules,
                'functions': [func for module in package_modules for func in module.get('functions', [])],
                'classes': [cls for module in package_modules for cls in module.get('classes', [])],
                'dependencies': code_analysis.get('dependencies', {})
            }
            
            prompt = f"""
Based on the following module analysis, generate a detailed interaction diagram in Mermaid syntax.
The diagram should show:
1. Each module as a distinct component
2. Classes within modules and their key methods
3. Function calls and data flow between modules
4. Dependencies and import relationships
5. Data transformations and processing flow

Focus on how these modules work together to achieve functionality.

Module Group: {package_name}
Context:
{json.dumps(context, indent=2)}

Generate a Mermaid flowchart or class diagram showing module interactions.
Return ONLY the Mermaid syntax.
"""
            
            mermaid_diagram = self._query_gpt4(prompt)
            
            # Generate module description
            description_prompt = f"""
Describe how the modules in the {package_name} package interact.
Explain:
- The purpose of each module
- Key interactions and data flow
- Dependencies between modules
- Main functions and classes

Format as markdown.
"""
            
            description = self._query_gpt4(description_prompt)
            
            module_diagrams[package_name] = {
                'mermaid': mermaid_diagram,
                'description': description,
                'type': 'module_interaction',
                'modules': [m['name'] for m in package_modules],
                'generated_at': datetime.now().isoformat()
            }
        
        return module_diagrams
    
    def generate_data_flow_architecture(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate data flow architecture diagram showing how data moves through the system."""
        self.logger.info("Generating data flow architecture diagram with AI...")
        
        # Extract data flow information
        data_flow = code_analysis.get('data_flow', {})
        ai_components = ai_analysis.get('pipelines', [])
        
        context = {
            'data_flow': data_flow,
            'ai_pipelines': ai_components,
            'entry_points': data_flow.get('entry_points', []),
            'transformations': data_flow.get('transformations', []),
            'output_points': data_flow.get('output_points', [])
        }
        
        prompt = f"""
Generate a data flow architecture diagram in Mermaid syntax showing:
1. Data sources and inputs
2. Processing stages and transformations
3. Decision points and branching logic
4. Output destinations and formats
5. Data storage and persistence layers
6. AI/ML pipeline data flows (if present)

Context:
{json.dumps(context, indent=2)}

Generate a Mermaid flowchart focusing on data movement and processing.
Return ONLY the Mermaid syntax.
"""
        
        mermaid_diagram = self._query_gpt4(prompt)
        
        description_prompt = f"""
Describe the data flow architecture of the system.
Explain how data enters, gets processed, transformed, and exits the system.
Include any AI/ML data pipelines and their role in the overall flow.

Format as markdown.
"""
        
        description = self._query_gpt4(description_prompt)
        
        return {
            'mermaid': mermaid_diagram,
            'description': description,
            'type': 'data_flow_architecture',
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_component_communication_diagram(self, code_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate component communication diagram showing inter-component messaging."""
        self.logger.info("Generating component communication diagram with AI...")
        
        dependencies = code_analysis.get('dependencies', {})
        functions = code_analysis.get('functions', [])
        
        context = {
            'internal_dependencies': dependencies.get('internal_dependencies', []),
            'external_dependencies': dependencies.get('external_dependencies', []),
            'communication_patterns': self._analyze_communication_patterns(functions)
        }
        
        prompt = f"""
Generate a component communication diagram in Mermaid syntax showing:
1. Communication protocols and interfaces
2. Message passing between components
3. Event-driven interactions
4. API calls and responses
5. Synchronous vs asynchronous communication
6. Error handling and fallback mechanisms

Context:
{json.dumps(context, indent=2)}

Generate a Mermaid sequence diagram or communication diagram.
Return ONLY the Mermaid syntax.
"""
        
        mermaid_diagram = self._query_gpt4(prompt)
        
        description_prompt = f"""
Describe the component communication patterns in the system.
Explain how components interact, what protocols they use, and how errors are handled.

Format as markdown.
"""
        
        description = self._query_gpt4(description_prompt)
        
        return {
            'mermaid': mermaid_diagram,
            'description': description,
            'type': 'component_communication',
            'generated_at': datetime.now().isoformat()
        }
    
    def save_diagrams(self, diagrams: Dict[str, Any]) -> None:
        """Save all generated diagrams to files."""
        for diagram_type, diagram_data in diagrams.items():
            if isinstance(diagram_data, dict) and 'mermaid' in diagram_data:
                # Single diagram
                self._save_single_diagram(diagram_type, diagram_data)
            elif isinstance(diagram_data, dict):
                # Multiple diagrams (like module_diagrams)
                for sub_name, sub_diagram in diagram_data.items():
                    self._save_single_diagram(f"{diagram_type}_{sub_name}", sub_diagram)
    
    def _save_single_diagram(self, name: str, diagram_data: Dict[str, str]) -> None:
        """Save a single diagram and its description."""
        # Save Mermaid diagram
        mermaid_file = self.output_dir / f"{name}.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(diagram_data.get('mermaid', ''))
        
        # Save description
        desc_file = self.output_dir / f"{name}_description.md"
        with open(desc_file, 'w', encoding='utf-8') as f:
            f.write(diagram_data.get('description', ''))
        
        # Save metadata
        metadata_file = self.output_dir / f"{name}_metadata.json"
        metadata = {k: v for k, v in diagram_data.items() if k not in ['mermaid', 'description']}
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def _query_gpt4(self, prompt: str) -> str:
        """Query GPT-4 with the given prompt and return the response."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert software architect and diagram designer. Generate clear, accurate, and well-structured diagrams based on code analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error querying GPT-4: {e}")
            return "Error generating diagram with AI"
    
    def _prepare_architecture_context(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context information for architecture diagram generation."""
        return {
            'overview': code_analysis.get('overview', {}),
            'modules': code_analysis.get('modules', [])[:10],  # Top 10 modules
            'architecture': code_analysis.get('architecture', {}),
            'dependencies': code_analysis.get('dependencies', {}),
            'ai_components': {
                'frameworks': ai_analysis.get('frameworks_detected', []),
                'models': ai_analysis.get('ml_models', []),
                'pipelines': ai_analysis.get('pipelines', [])[:5]  # Top 5 pipelines
            },
            'complexity_summary': code_analysis.get('complexity', {}).get('summary', {})
        }
    
    def _group_modules_by_package(self, modules: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group modules by their package/directory structure."""
        groups = {}
        
        for module in modules:
            # Extract package name from file path
            file_path = module.get('file', '')
            if not file_path:
                continue
            
            path_parts = Path(file_path).parts
            if len(path_parts) > 1:
                package_name = path_parts[-2]  # Parent directory
            else:
                package_name = 'root'
            
            if package_name not in groups:
                groups[package_name] = []
            groups[package_name].append(module)
        
        return groups
    
    def _analyze_communication_patterns(self, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze communication patterns from function analysis."""
        patterns = []
        
        for func in functions[:20]:  # Analyze top 20 functions
            if 'calls' in func:
                for call in func.get('calls', []):
                    patterns.append({
                        'caller': func.get('name', 'Unknown'),
                        'callee': call,
                        'module': func.get('module', 'Unknown')
                    })
        
        return patterns
    
    def _generate_fallback_diagrams(self, code_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic diagrams when AI is not available."""
        self.logger.info("Generating fallback diagrams...")
        
        return {
            'logical_architecture': {
                'mermaid': self._generate_basic_mermaid_architecture(code_analysis),
                'description': "Basic architecture diagram generated without AI assistance.",
                'type': 'logical_architecture',
                'generated_at': datetime.now().isoformat()
            },
            'physical_architecture': {
                'mermaid': self._generate_basic_mermaid_deployment(code_analysis),
                'description': "Basic deployment diagram generated without AI assistance.",
                'type': 'physical_architecture', 
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def _generate_basic_mermaid_architecture(self, code_analysis: Dict[str, Any]) -> str:
        """Generate a basic Mermaid architecture diagram."""
        modules = code_analysis.get('modules', [])[:10]
        
        mermaid = "flowchart TD\n"
        mermaid += "    subgraph Application\n"
        
        for i, module in enumerate(modules):
            module_name = module.get('name', f'Module{i}').replace('.', '_')
            mermaid += f"        {module_name}[{module.get('name', f'Module {i}')}]\n"
        
        mermaid += "    end\n"
        
        # Add basic connections
        for i in range(len(modules) - 1):
            mod1 = modules[i].get('name', f'Module{i}').replace('.', '_')
            mod2 = modules[i+1].get('name', f'Module{i+1}').replace('.', '_')
            mermaid += f"    {mod1} --> {mod2}\n"
        
        return mermaid
    
    def _generate_basic_mermaid_deployment(self, code_analysis: Dict[str, Any]) -> str:
        """Generate a basic Mermaid deployment diagram."""
        return """graph TD
    subgraph Production Environment
        LB[Load Balancer]
        APP[Application Server]
        DB[Database]
        CACHE[Cache Layer]
    end
    
    subgraph Development Environment
        DEV_APP[Dev Application]
        DEV_DB[Dev Database]
    end
    
    LB --> APP
    APP --> DB
    APP --> CACHE
    DEV_APP --> DEV_DB
"""
