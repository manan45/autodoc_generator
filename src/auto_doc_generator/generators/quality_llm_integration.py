#!/usr/bin/env python3
"""
Quality LLM Integration - 🔬 Quality Scoring Pipeline

Integrates LLM responses for intelligent quality assessment.
Works with the existing AI analysis coordinator to provide enhanced quality insights.
"""

import json
import os
import logging
import time
import re
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Optional: OpenAI integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class QualityLLMIntegration:
    """Integrates LLM responses for intelligent quality assessment."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # LLM configuration
        ai_config = self.config.get('ai', {})
        self.openai_enabled = OPENAI_AVAILABLE and ai_config.get('enabled', True)
        self.max_retries = int(ai_config.get('retries', 3))
        self.retry_backoff_seconds = float(ai_config.get('retry_backoff_seconds', 2))
        
        # Caching configuration for LLM responses
        cache_config = ai_config.get('cache', {})
        self.cache_enabled = bool(cache_config.get('enabled', True))
        default_cache_dir = os.path.join('.cache', 'quality_llm_responses')
        self.cache_dir = Path(cache_config.get('dir', default_cache_dir))
        self.cache_ttl_hours = int(cache_config.get('ttl_hours', 24))
        
        if self.cache_enabled:
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"🔬 Quality LLM cache enabled: {self.cache_dir} (TTL: {self.cache_ttl_hours}h)")
            except Exception as e:
                self.logger.warning(f"Failed to create cache directory: {e}")
                self.cache_enabled = False
        
        if self.openai_enabled:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.client = OpenAI(api_key=api_key)
                    self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                    self.logger.info(f"🔬 Quality LLM integration initialized with model: {self.model}")
                except Exception as e:
                    self.openai_enabled = False
                    self.logger.warning(f"Failed to initialize OpenAI client: {e}")
            else:
                self.openai_enabled = False
                self.logger.warning("OpenAI API key not found, LLM quality assessment disabled")
        
        # Quality assessment prompts
        self._init_quality_prompts()
    
    def _init_quality_prompts(self):
        """Initialize quality assessment prompts."""
        self.quality_prompts = {
            'overall_assessment': """
Analyze the following code quality metrics and provide an overall assessment:

Metrics:
{metrics_summary}

Module Information:
- Path: {module_path}
- Content Preview: {content_preview}

Please provide:
1. An overall quality assessment (1-2 sentences)
2. Top 3 strengths
3. Top 3 areas for improvement
4. Priority ranking for improvements (1=highest, 3=lowest)

Format your response as JSON:
{{
  "overall_assessment": "Brief overall assessment",
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "improvement_priority": ["priority1", "priority2", "priority3"],
  "confidence": 0.85
}}

IMPORTANT: Return ONLY valid JSON with no additional text, explanations, or markdown formatting.
""",
            
            'code_review': """
Review this code module for quality issues:

Code Content:
{code_content}

Quality Metrics:
{metrics_data}

Provide a detailed code review focusing on:
1. Code structure and organization
2. Best practices adherence
3. Potential bugs or issues
4. Maintainability concerns
5. Performance considerations

Format as JSON:
{{
  "review_summary": "Overall review summary",
  "structure_analysis": "Code structure assessment",
  "best_practices": ["practice1", "practice2"],
  "potential_issues": ["issue1", "issue2"],
  "maintainability_score": 0.75,
  "performance_notes": "Performance assessment",
  "recommendations": ["rec1", "rec2", "rec3"]
}}

IMPORTANT: Return ONLY valid JSON with no additional text, explanations, or markdown formatting.
""",
            
            'pattern_analysis': """
Analyze the design patterns and architectural quality of this code:

Code Content:
{code_content}

Module Type: {module_type}
Detected Patterns: {detected_patterns}

Assess:
1. Design pattern usage appropriateness
2. SOLID principles adherence
3. Architectural quality
4. Code coupling and cohesion

Format as JSON:
{{
  "pattern_assessment": "Overall pattern usage assessment",
  "solid_principles": {{
    "single_responsibility": 0.8,
    "open_closed": 0.7,
    "liskov_substitution": 0.9,
    "interface_segregation": 0.6,
    "dependency_inversion": 0.8
  }},
  "coupling_analysis": "Coupling assessment",
  "cohesion_analysis": "Cohesion assessment",
  "architectural_notes": "Architecture quality notes"
}}

IMPORTANT: Return ONLY valid JSON with no additional text, explanations, or markdown formatting.
""",
            
            'security_assessment': """
Assess the security quality of this code:

Code Content:
{code_content}

Security Metrics:
{security_metrics}

Analyze:
1. Security vulnerabilities
2. Input validation
3. Error handling security
4. Data protection practices

Format as JSON:
{{
  "security_score": 0.85,
  "vulnerabilities": ["vuln1", "vuln2"],
  "security_strengths": ["strength1", "strength2"],
  "security_recommendations": ["rec1", "rec2"],
  "risk_level": "low|medium|high|critical"
}}

IMPORTANT: Return ONLY valid JSON with no additional text, explanations, or markdown formatting.
"""
        }
    
    def enhance_quality_assessment(self, module_path: str, quality_metrics: Dict[str, Any], 
                                 content: str = "", module_type: str = "module", 
                                 enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance quality assessment with LLM insights.
        
        Args:
            module_path: Path to the module
            quality_metrics: Quality metrics from QualityAnalyzer
            content: Module content for analysis
            module_type: Type of module (e.g., 'api', 'service', 'utility')
            enhanced_analysis: Enhanced AI analysis results with architectural insights
            
        Returns:
            Enhanced quality assessment with LLM insights
        """
        if not self.openai_enabled:
            return self._generate_fallback_assessment(quality_metrics)
        
        try:
            # Perform comprehensive quality assessment in a single API call to reduce costs and latency
            enhanced_assessment = self._get_comprehensive_quality_assessment(
                module_path, quality_metrics, content, module_type, enhanced_analysis
            )
            
            # Add metadata
            enhanced_assessment['llm_metadata'] = {
                'model_used': self.model,
                'analysis_timestamp': datetime.now().isoformat(),
                'content_analyzed': len(content) > 0,
                'assessments_performed': list(enhanced_assessment.keys()),
                'cache_stats': self.get_cache_stats()
            }
            
            return enhanced_assessment
            
        except Exception as e:
            self.logger.error(f"Error in LLM quality assessment: {e}")
            return self._generate_fallback_assessment(quality_metrics)
    
    def _get_comprehensive_quality_assessment(self, module_path: str, quality_metrics: Dict[str, Any], 
                                            content: str, module_type: str, enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive quality assessment in a single API call to reduce costs."""
        
        # Prepare metrics summary and context
        metrics_summary = self._format_metrics_for_llm(quality_metrics)
        content_preview = content[:2000] + "..." if len(content) > 2000 else content
        ai_context = self._format_ai_context_for_llm(module_path, enhanced_analysis)
        security_metrics = quality_metrics.get('security', {})
        
        # Build comprehensive prompt
        comprehensive_prompt = f"""
Analyze the following module and provide a comprehensive quality assessment covering all aspects below.

Module Information:
- Path: {module_path}
- Type: {module_type}
- Content Size: {len(content)} characters

Quality Metrics:
{metrics_summary}

Code Content:
{content_preview}

{f"Additional AI Analysis Context: {ai_context}" if ai_context else ""}

{f"Security Metrics: {json.dumps(security_metrics.get('details', {}))}" if security_metrics else ""}

Please provide a comprehensive JSON response with ALL of the following sections:

1. Overall Assessment - Brief overall quality assessment, strengths, weaknesses, and improvement priorities
2. Code Review - Structure, best practices, potential issues, and maintainability 
3. Pattern Analysis - Design patterns, SOLID principles, coupling, and cohesion
4. Security Assessment - Security vulnerabilities, input validation, and risk level

Format your response as JSON with these exact keys:
{{
  "overall_assessment": "Brief overall assessment",
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "improvement_priority": ["priority1", "priority2", "priority3"],
  "confidence": 0.85,
  "code_review": {{
    "review_summary": "Overall review summary",
    "structure_analysis": "Code structure assessment",
    "best_practices": ["practice1", "practice2"],
    "potential_issues": ["issue1", "issue2"],
    "maintainability_score": 0.75,
    "performance_notes": "Performance assessment",
    "recommendations": ["rec1", "rec2", "rec3"]
  }},
  "pattern_analysis": {{
    "pattern_assessment": "Overall pattern usage assessment",
    "solid_principles": {{
      "single_responsibility": 0.8,
      "open_closed": 0.7,
      "liskov_substitution": 0.9,
      "interface_segregation": 0.6,
      "dependency_inversion": 0.8
    }},
    "coupling_analysis": "Coupling assessment",
    "cohesion_analysis": "Cohesion assessment",
    "architectural_notes": "Architecture quality notes"
  }},
  "security_assessment": {{
    "security_score": 0.85,
    "vulnerabilities": ["vuln1", "vuln2"],
    "security_strengths": ["strength1", "strength2"],
    "security_recommendations": ["rec1", "rec2"],
    "risk_level": "low|medium|high|critical"
  }}
}}

IMPORTANT: Return ONLY valid JSON with no additional text, explanations, or markdown formatting.
"""
        
        try:
            response = self._call_openai(comprehensive_prompt)
            result = self._parse_json_response(response)
            
            # Validate that all required sections exist
            required_sections = ['overall_assessment', 'strengths', 'weaknesses', 'improvement_priority']
            if not all(key in result for key in required_sections):
                self.logger.warning("Comprehensive assessment missing required keys, using fallback")
                return self._fallback_to_individual_assessments(module_path, quality_metrics, content, module_type, enhanced_analysis)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Comprehensive quality assessment failed: {e}")
            self.logger.info("Falling back to individual assessment methods...")
            return self._fallback_to_individual_assessments(module_path, quality_metrics, content, module_type, enhanced_analysis)
    
    def _fallback_to_individual_assessments(self, module_path: str, quality_metrics: Dict[str, Any], 
                                          content: str, module_type: str, enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback to individual assessment methods if comprehensive assessment fails."""
        self.logger.info("Using individual assessment methods as fallback...")
        
        enhanced_assessment = {}
        
        # 1. Overall Quality Assessment
        try:
            overall_assessment = self._get_overall_assessment(
                module_path, quality_metrics, content, enhanced_analysis
            )
            enhanced_assessment.update(overall_assessment)
        except Exception as e:
            self.logger.error(f"Overall assessment fallback failed: {e}")
            fallback_assessment = self._generate_fallback_assessment(quality_metrics)
            enhanced_assessment.update(fallback_assessment)
        
        # 2. Detailed Code Review (if content available and not too large)
        if content and len(content) < 5000:  # Limit content size for LLM
            try:
                code_review = self._get_code_review(content, quality_metrics)
                enhanced_assessment['code_review'] = code_review
            except Exception as e:
                self.logger.error(f"Code review fallback failed: {e}")
                enhanced_assessment['code_review'] = {"review_summary": "Code review unavailable due to processing error"}
        
        # 3. Pattern Analysis
        if content:
            try:
                pattern_analysis = self._get_pattern_analysis(content, module_type, quality_metrics)
                enhanced_assessment['pattern_analysis'] = pattern_analysis
            except Exception as e:
                self.logger.error(f"Pattern analysis fallback failed: {e}")
                enhanced_assessment['pattern_analysis'] = self._generate_fallback_pattern_analysis({})
        
        # 4. Security Assessment
        security_metrics = quality_metrics.get('security', {})
        if security_metrics and content:
            try:
                security_assessment = self._get_security_assessment(content, security_metrics)
                enhanced_assessment['security_assessment'] = security_assessment
            except Exception as e:
                self.logger.error(f"Security assessment fallback failed: {e}")
                enhanced_assessment['security_assessment'] = {"security_score": 0.5, "risk_level": "unknown"}
        
        return enhanced_assessment
    
    def _get_overall_assessment(self, module_path: str, quality_metrics: Dict[str, Any], 
                              content: str, enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get overall quality assessment from LLM."""
        
        # Prepare metrics summary
        metrics_summary = self._format_metrics_for_llm(quality_metrics)
        content_preview = content[:500] + "..." if len(content) > 500 else content
        
        # Add enhanced AI analysis context
        ai_context = self._format_ai_context_for_llm(module_path, enhanced_analysis)
        
        prompt = self.quality_prompts['overall_assessment'].format(
            metrics_summary=metrics_summary,
            module_path=module_path,
            content_preview=content_preview
        )
        
        # Append AI context if available
        if ai_context:
            prompt += f"\n\nAdditional AI Analysis Context:\n{ai_context}\n\nConsider this architectural and component analysis in your quality assessment."
        
        try:
            response = self._call_openai(prompt)
            assessment = self._parse_json_response(response)
            
            # Validate response structure
            required_keys = ['overall_assessment', 'strengths', 'weaknesses', 'improvement_priority']
            if all(key in assessment for key in required_keys):
                return assessment
            else:
                self.logger.warning("LLM response missing required keys, using fallback")
                return self._generate_fallback_overall_assessment(quality_metrics)
                
        except Exception as e:
            self.logger.error(f"Error in overall assessment: {e}")
            return self._generate_fallback_overall_assessment(quality_metrics)
    
    def _get_code_review(self, content: str, quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed code review from LLM."""
        
        metrics_data = json.dumps({k: v.get('score', 0) for k, v in quality_metrics.items()})
        
        prompt = self.quality_prompts['code_review'].format(
            code_content=content[:3000],  # Limit content size
            metrics_data=metrics_data
        )
        
        try:
            response = self._call_openai(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            self.logger.error(f"Error in code review: {e}")
            return {"review_summary": "Code review unavailable due to processing error"}
    
    def _get_pattern_analysis(self, content: str, module_type: str, 
                            quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get design pattern analysis from LLM."""
        
        detected_patterns = quality_metrics.get('design_patterns', {}).get('details', {}).get('pattern_matches', {})
        
        prompt = self.quality_prompts['pattern_analysis'].format(
            code_content=content[:2000],  # Limit content size
            module_type=module_type,
            detected_patterns=json.dumps(detected_patterns)
        )
        
        try:
            response = self._call_openai(prompt)
            if not response or not response.strip():
                self.logger.warning("Empty response from OpenAI for pattern analysis")
                return self._generate_fallback_pattern_analysis(detected_patterns)
            
            parsed_response = self._parse_json_response(response)
            if not parsed_response or not isinstance(parsed_response, dict):
                self.logger.warning("Invalid JSON response for pattern analysis, using fallback")
                return self._generate_fallback_pattern_analysis(detected_patterns)
            
            return parsed_response
        except Exception as e:
            self.logger.error(f"Error in pattern analysis: {e}")
            return self._generate_fallback_pattern_analysis(detected_patterns)
    
    def _generate_fallback_pattern_analysis(self, detected_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback pattern analysis when LLM fails."""
        pattern_count = len(detected_patterns) if detected_patterns else 0
        return {
            "pattern_assessment": f"Static analysis detected {pattern_count} design patterns. LLM analysis unavailable.",
            "patterns_found": list(detected_patterns.keys()) if detected_patterns else [],
            "recommendations": [
                "Review code structure for better pattern implementation",
                "Consider applying SOLID principles",
                "Evaluate if current patterns fit the use case"
            ] if pattern_count > 0 else ["Consider implementing design patterns for better code structure"]
        }
    
    def _get_security_assessment(self, content: str, security_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get security assessment from LLM."""
        
        prompt = self.quality_prompts['security_assessment'].format(
            code_content=content[:2000],  # Limit content size
            security_metrics=json.dumps(security_metrics.get('details', {}))
        )
        
        try:
            response = self._call_openai(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            self.logger.error(f"Error in security assessment: {e}")
            return {"security_score": 0.5, "risk_level": "unknown"}
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with caching, retries and backoff for transient errors."""
        if not getattr(self, 'client', None):
            raise RuntimeError("OpenAI client not initialized")

        # Check cache first
        cache_key = self._get_cache_key(prompt)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response

        last_exception: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a senior software engineer and code quality expert. Always respond with ONLY valid JSON format - no explanations, no markdown, no additional text. Your response must be parseable by json.loads()."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3,
                    timeout=30
                )
                content = (response.choices[0].message.content or "").strip()
                if not content:
                    raise ValueError("Empty response content from OpenAI")
                
                # Cache the successful response
                self._cache_response(cache_key, content)
                return content
                
            except Exception as e:
                last_exception = e
                message = str(e).lower()
                is_retryable = any(term in message for term in [
                    "429", "500", "502", "503", "504", "timeout", "temporarily unavailable", "service unavailable", "rate limit"
                ])
                if attempt < self.max_retries - 1 and is_retryable:
                    delay = self.retry_backoff_seconds * (2 ** attempt)
                    self.logger.warning(f"OpenAI call failed (attempt {attempt + 1}/{self.max_retries}). Retrying in {delay:.1f}s: {e}")
                    time.sleep(delay)
                    continue
                self.logger.error(f"OpenAI API call failed (non-retryable or max attempts reached): {e}")
                break
        raise last_exception if last_exception else RuntimeError("OpenAI call failed without exception detail")
    
    def _get_cache_key(self, prompt: str, model: str = None) -> str:
        """Generate cache key for a prompt."""
        model = model or self.model
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if available and not expired."""
        if not self.cache_enabled:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            expiry_time = cached_time + timedelta(hours=self.cache_ttl_hours)
            
            if datetime.now() > expiry_time:
                cache_file.unlink()  # Remove expired cache
                return None
            
            self.logger.debug(f"Using cached quality LLM response: {cache_key[:8]}...")
            return cache_data['response']
            
        except Exception as e:
            self.logger.warning(f"Error reading cache file {cache_key}: {e}")
            return None
    
    def _cache_response(self, cache_key: str, response: str) -> None:
        """Cache LLM response."""
        if not self.cache_enabled:
            return
        
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            cache_data = {
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'model': self.model
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
                
            self.logger.debug(f"Cached quality LLM response: {cache_key[:8]}...")
            
        except Exception as e:
            self.logger.warning(f"Error caching response {cache_key}: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache_enabled:
            return {'cache_enabled': False}
        
        try:
            cache_files = list(self.cache_dir.glob('*.json'))
            total_files = len(cache_files)
            
            # Count expired files
            expired_files = 0
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    cached_time = datetime.fromisoformat(cache_data['timestamp'])
                    expiry_time = cached_time + timedelta(hours=self.cache_ttl_hours)
                    if datetime.now() > expiry_time:
                        expired_files += 1
                except Exception:
                    expired_files += 1  # Count corrupted files as expired
            
            return {
                'cache_enabled': True,
                'cache_dir': str(self.cache_dir),
                'total_cached_responses': total_files,
                'expired_responses': expired_files,
                'valid_responses': total_files - expired_files,
                'cache_ttl_hours': self.cache_ttl_hours
            }
        except Exception as e:
            self.logger.warning(f"Error getting cache stats: {e}")
            return {'cache_enabled': True, 'error': str(e)}

    def _parse_json_response(self, text: str) -> Any:
        """Parse JSON from LLM text response with robust recovery for various formats."""
        if not text or not text.strip():
            self.logger.warning("Empty text received for JSON parsing")
            return {}
        
        text = text.strip()
        
        # First attempt: direct JSON parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            self.logger.warning(f"Initial JSON parsing failed: {e}")
        
        # Second attempt: Remove markdown code fences if present
        cleaned = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text, flags=re.MULTILINE)
        if cleaned != text:
            try:
                return json.loads(cleaned.strip())
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse after removing markdown fences")
        
        # Third attempt: Extract JSON object between first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse extracted JSON block")
        
        # Fourth attempt: Look for JSON after common prefixes
        json_prefixes = [
            "Here's the JSON response:",
            "Here is the JSON:",
            "JSON response:",
            "Response:",
            "```json",
            "The analysis results:",
            "Analysis:"
        ]
        
        for prefix in json_prefixes:
            if prefix in text.lower():
                # Find text after the prefix
                prefix_pos = text.lower().find(prefix.lower())
                after_prefix = text[prefix_pos + len(prefix):].strip()
                
                # Try to parse what comes after the prefix
                try:
                    return json.loads(after_prefix)
                except json.JSONDecodeError:
                    # Try to find JSON object after prefix
                    start = after_prefix.find("{")
                    end = after_prefix.rfind("}")
                    if start != -1 and end != -1 and end > start:
                        candidate = after_prefix[start:end + 1]
                        try:
                            return json.loads(candidate)
                        except json.JSONDecodeError:
                            continue
        
        # Fifth attempt: Try to extract multiple JSON objects and take the first valid one
        json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
        for obj in json_objects:
            try:
                return json.loads(obj)
            except json.JSONDecodeError:
                continue
        
        # Return empty dict as fallback instead of raising
        self.logger.error(f"All JSON parsing attempts failed for text: {text[:200]}...")
        return {}
    
    def _format_metrics_for_llm(self, quality_metrics: Dict[str, Any]) -> str:
        """Format quality metrics for LLM consumption."""
        
        formatted_metrics = []
        
        for metric_name, metric_data in quality_metrics.items():
            if isinstance(metric_data, dict):
                score = metric_data.get('score', 0)
                weight = metric_data.get('weight', 0)
                description = metric_data.get('description', '')
                
                formatted_metrics.append(f"- {metric_name.title()}: {score:.2f} (weight: {weight:.1%}) - {description}")
        
        return "\n".join(formatted_metrics)
    
    def _format_ai_context_for_llm(self, module_path: str, enhanced_analysis: Dict[str, Any]) -> str:
        """Format enhanced AI analysis context for LLM consumption."""
        if not enhanced_analysis:
            return ""
        
        context_parts = []
        
        # API Analysis
        api_analysis = enhanced_analysis.get('api_analysis', {})
        if api_analysis.get('endpoints'):
            endpoints = api_analysis['endpoints'][:3]  # Limit to first 3
            endpoint_paths = []
            for ep in endpoints:
                if isinstance(ep, dict):
                    endpoint_paths.append(ep.get('path', '') or ep.get('endpoint', '') or str(ep))
                else:
                    endpoint_paths.append(str(ep))
            context_parts.append(f"API Endpoints: {', '.join(endpoint_paths)}")
        
        # Architecture Analysis
        arch_analysis = enhanced_analysis.get('architecture_analysis', {})
        if arch_analysis.get('patterns'):
            patterns = arch_analysis['patterns'][:3]  # Limit to first 3
            pattern_strs = [str(p) for p in patterns]
            context_parts.append(f"Architecture Patterns: {', '.join(pattern_strs)}")
        
        # Component Analysis
        component_analysis = enhanced_analysis.get('component_analysis', {})
        if component_analysis.get('components'):
            components_data = component_analysis['components']
            if isinstance(components_data, dict):
                components = list(components_data.keys())[:3]  # Limit to first 3
            elif isinstance(components_data, list):
                components = components_data[:3]  # Limit to first 3
            else:
                components = [str(components_data)]
            component_strs = [str(c) for c in components]
            context_parts.append(f"Key Components: {', '.join(component_strs)}")
        
        # ML Analysis
        ml_analysis = enhanced_analysis.get('ml_analysis', {})
        if ml_analysis.get('models'):
            models = []
            for m in ml_analysis['models'][:2]:  # Limit to first 2
                if isinstance(m, dict):
                    models.append(m.get('name', '') or str(m))
                else:
                    models.append(str(m))
            context_parts.append(f"ML Models: {', '.join(models)}")
        
        return " | ".join(context_parts) if context_parts else ""
    
    def _generate_fallback_assessment(self, quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback assessment when LLM is not available."""
        
        overall_score = sum(m.get('score', 0) * m.get('weight', 0) 
                          for m in quality_metrics.values() if isinstance(m, dict))
        
        # Determine assessment based on scores
        if overall_score >= 0.8:
            assessment = "This module demonstrates high code quality with strong adherence to best practices."
            strengths = ["High overall quality score", "Good metric performance", "Well-structured code"]
        elif overall_score >= 0.6:
            assessment = "This module shows good code quality with some areas for improvement."
            strengths = ["Decent overall quality", "Some strong metrics", "Generally well-organized"]
        else:
            assessment = "This module has significant quality issues that need attention."
            strengths = ["Potential for improvement", "Basic functionality present"]
        
        # Identify weaknesses based on low-scoring metrics
        weaknesses = []
        improvement_priority = []
        
        for metric_name, metric_data in quality_metrics.items():
            if isinstance(metric_data, dict):
                score = metric_data.get('score', 0)
                if score < 0.5:
                    weaknesses.append(f"Low {metric_name.replace('_', ' ')} score")
                    improvement_priority.append(metric_name.replace('_', ' ').title())
        
        if not weaknesses:
            weaknesses = ["Minor optimization opportunities"]
        
        if not improvement_priority:
            improvement_priority = ["Code documentation", "Test coverage", "Complexity reduction"]
        
        return {
            'overall_assessment': assessment,
            'strengths': strengths[:3],
            'weaknesses': weaknesses[:3],
            'improvement_priority': improvement_priority[:3],
            'confidence': 0.7,
            'source': 'fallback_analysis'
        }
    
    def _generate_fallback_overall_assessment(self, quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback overall assessment."""
        return self._generate_fallback_assessment(quality_metrics)
    
    def analyze_quality_trends(self, historical_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze quality trends over time using LLM.
        
        Args:
            historical_assessments: List of historical quality assessments
            
        Returns:
            Trend analysis and predictions
        """
        if not self.openai_enabled or not historical_assessments:
            return self._generate_fallback_trends(historical_assessments)
        
        # Prepare trend data for LLM analysis
        trend_data = []
        for assessment in historical_assessments[-10:]:  # Last 10 assessments
            trend_data.append({
                'timestamp': assessment.get('timestamp', ''),
                'average_score': assessment.get('overview', {}).get('average_quality_score', 0),
                'total_modules': assessment.get('overview', {}).get('total_modules', 0)
            })
        
        prompt = f"""
Analyze these quality trends over time:

Historical Data:
{json.dumps(trend_data, indent=2)}

Provide:
1. Overall trend direction (improving/declining/stable)
2. Key observations about quality changes
3. Predictions for future quality
4. Recommended actions

Format as JSON:
{{
  "trend_direction": "improving|declining|stable",
  "trend_strength": 0.75,
  "key_observations": ["obs1", "obs2", "obs3"],
  "predictions": {{
    "next_period_score": 0.85,
    "confidence": 0.8,
    "factors": ["factor1", "factor2"]
  }},
  "recommended_actions": ["action1", "action2"]
}}

IMPORTANT: Return ONLY valid JSON with no additional text, explanations, or markdown formatting.
"""
        
        try:
            response = self._call_openai(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")
            return self._generate_fallback_trends(historical_assessments)
    
    def _generate_fallback_trends(self, historical_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback trend analysis."""
        
        if len(historical_assessments) < 2:
            return {
                'trend_direction': 'insufficient_data',
                'key_observations': ['Not enough historical data for trend analysis'],
                'recommended_actions': ['Continue monitoring quality metrics over time']
            }
        
        # Simple trend calculation
        scores = [a.get('overview', {}).get('average_quality_score', 0) for a in historical_assessments]
        recent_scores = scores[-3:] if len(scores) >= 3 else scores
        earlier_scores = scores[:-3] if len(scores) >= 6 else scores[:-len(recent_scores)]
        
        if earlier_scores:
            recent_avg = sum(recent_scores) / len(recent_scores)
            earlier_avg = sum(earlier_scores) / len(earlier_scores)
            
            if recent_avg > earlier_avg + 0.05:
                trend_direction = 'improving'
            elif recent_avg < earlier_avg - 0.05:
                trend_direction = 'declining'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'stable'
        
        return {
            'trend_direction': trend_direction,
            'trend_strength': 0.6,
            'key_observations': [f'Quality trend appears to be {trend_direction}'],
            'predictions': {
                'next_period_score': recent_scores[-1] if recent_scores else 0.5,
                'confidence': 0.6
            },
            'recommended_actions': ['Continue regular quality monitoring']
        }
    
    def generate_quality_insights(self, quality_analysis: Dict[str, Any], 
                                enhanced_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate high-level quality insights across the entire codebase.
        
        Args:
            quality_analysis: Complete quality analysis results
            enhanced_analysis: Enhanced AI analysis with architectural insights
            
        Returns:
            High-level insights and recommendations
        """
        if not self.openai_enabled:
            return self._generate_fallback_insights(quality_analysis)
        
        overview = quality_analysis.get('overview', {})
        distribution = quality_analysis.get('quality_distribution', {})
        
        # Add enhanced analysis context for global insights
        global_ai_context = ""
        if enhanced_analysis:
            arch_patterns = enhanced_analysis.get('architecture_analysis', {}).get('patterns', [])
            api_count = len(enhanced_analysis.get('api_analysis', {}).get('endpoints', []))
            ml_models = len(enhanced_analysis.get('ml_analysis', {}).get('models', []))
            components_data = enhanced_analysis.get('component_analysis', {}).get('components', {})
            if isinstance(components_data, dict):
                components = len(components_data)
            elif isinstance(components_data, list):
                components = len(components_data)
            else:
                components = 0
            
            global_ai_context = f"""

Enhanced AI Analysis Context:
- Architecture Patterns: {', '.join([str(p) for p in arch_patterns[:5]]) if arch_patterns else 'None detected'}
- API Endpoints: {api_count}
- ML Models: {ml_models}
- Components: {components}"""
        
        prompt = f"""
Analyze this codebase quality summary and provide strategic insights:

Quality Overview:
{json.dumps(overview, indent=2)}

Quality Distribution:
{json.dumps(distribution, indent=2)}{global_ai_context}

Provide strategic insights:
1. Overall codebase health assessment
2. Critical areas requiring immediate attention
3. Long-term quality strategy recommendations
4. Resource allocation suggestions

Format as JSON:
{{
  "health_assessment": "Overall codebase health summary",
  "health_score": 0.75,
  "critical_areas": ["area1", "area2"],
  "strategic_recommendations": ["rec1", "rec2", "rec3"],
  "resource_allocation": {{
    "immediate_focus": ["focus1", "focus2"],
    "long_term_investments": ["investment1", "investment2"]
  }},
  "success_metrics": ["metric1", "metric2"]
}}

IMPORTANT: Return ONLY valid JSON with no additional text, explanations, or markdown formatting.
"""
        
        try:
            response = self._call_openai(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            self.logger.error(f"Error generating quality insights: {e}")
            return self._generate_fallback_insights(quality_analysis)
    
    def _generate_fallback_insights(self, quality_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback quality insights."""
        
        overview = quality_analysis.get('overview', {})
        avg_score = overview.get('average_quality_score', 0.5)
        
        if avg_score >= 0.8:
            health_assessment = "Codebase shows excellent quality with strong engineering practices."
            critical_areas = ["Maintain current standards", "Consider advanced optimizations"]
        elif avg_score >= 0.6:
            health_assessment = "Codebase has good quality with room for targeted improvements."
            critical_areas = ["Focus on lowest-scoring modules", "Improve documentation coverage"]
        else:
            health_assessment = "Codebase requires significant quality improvements across multiple areas."
            critical_areas = ["Address complexity issues", "Improve test coverage", "Enhance documentation"]
        
        return {
            'health_assessment': health_assessment,
            'health_score': avg_score,
            'critical_areas': critical_areas,
            'strategic_recommendations': [
                "Implement regular quality monitoring",
                "Establish quality gates in CI/CD",
                "Provide team training on best practices"
            ],
            'resource_allocation': {
                'immediate_focus': critical_areas[:2],
                'long_term_investments': ["Automated quality tools", "Code review processes"]
            },
            'success_metrics': ["Average quality score improvement", "Reduction in critical issues"]
        }
