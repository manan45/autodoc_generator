#!/usr/bin/env python3
"""
Code Memory System

Integrates with local code databases (like Cursor's) and provides enhanced context
for LLM prompts. Supports vector embeddings, semantic search, and persistent memory.
"""

import json
import os
import sqlite3
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import hashlib
import numpy as np

# Optional: Vector embeddings for semantic search
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None


class CodeMemorySystem:
    """Enhanced memory system for code analysis with local database integration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Memory configuration
        memory_config = self.config.get('memory', {})
        self.memory_dir = Path(memory_config.get('dir', '.cache/memory'))
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Database paths
        self.code_db_path = self.memory_dir / 'code_analysis.db'
        self.context_db_path = self.memory_dir / 'context_memory.db'
        
        # Vector embeddings
        self.embeddings_enabled = memory_config.get('embeddings_enabled', EMBEDDINGS_AVAILABLE)
        if self.embeddings_enabled and EMBEDDINGS_AVAILABLE:
            model_name = memory_config.get('embedding_model', 'all-MiniLM-L6-v2')
            try:
                self.embedding_model = SentenceTransformer(model_name)
                self.logger.info(f"Loaded embedding model: {model_name}")
            except Exception as e:
                self.logger.warning(f"Failed to load embedding model: {e}")
                self.embeddings_enabled = False
        else:
            self.embeddings_enabled = False
        
        # Initialize databases
        self._init_databases()
    
    def _init_databases(self):
        """Initialize SQLite databases for code analysis and context memory."""
        
        # Code analysis database
        with sqlite3.connect(self.code_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS code_files (
                    id INTEGER PRIMARY KEY,
                    file_path TEXT UNIQUE,
                    content TEXT,
                    ast_data TEXT,
                    functions TEXT,
                    classes TEXT,
                    complexity_score REAL,
                    last_modified TIMESTAMP,
                    embedding BLOB
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS code_relationships (
                    id INTEGER PRIMARY KEY,
                    source_file TEXT,
                    target_file TEXT,
                    relationship_type TEXT,
                    strength REAL,
                    last_updated TIMESTAMP
                )
            ''')
        
        # Context memory database
        with sqlite3.connect(self.context_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT UNIQUE,
                    project_path TEXT,
                    analysis_data TEXT,
                    ai_insights TEXT,
                    created_at TIMESTAMP,
                    last_accessed TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS context_memory (
                    id INTEGER PRIMARY KEY,
                    context_key TEXT,
                    context_type TEXT,
                    content TEXT,
                    embedding BLOB,
                    relevance_score REAL,
                    created_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            ''')
    
    def store_code_analysis(self, file_path: str, analysis_data: Dict[str, Any]) -> None:
        """Store code analysis results in the local database."""
        
        try:
            # Generate embedding if enabled
            embedding_blob = None
            if self.embeddings_enabled:
                content = analysis_data.get('content', '')
                if content:
                    embedding = self.embedding_model.encode(content)
                    embedding_blob = pickle.dumps(embedding)
            
            with sqlite3.connect(self.code_db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO code_files 
                    (file_path, content, ast_data, functions, classes, complexity_score, last_modified, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_path,
                    analysis_data.get('content', ''),
                    json.dumps(analysis_data.get('ast_data', {})),
                    json.dumps(analysis_data.get('functions', [])),
                    json.dumps(analysis_data.get('classes', [])),
                    analysis_data.get('complexity_score', 0.0),
                    datetime.now(),
                    embedding_blob
                ))
            
            self.logger.debug(f"Stored code analysis for: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to store code analysis for {file_path}: {e}")
    
    def get_similar_code(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar code using semantic search."""
        
        if not self.embeddings_enabled:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Retrieve all embeddings from database
            with sqlite3.connect(self.code_db_path) as conn:
                cursor = conn.execute('SELECT file_path, content, embedding FROM code_files WHERE embedding IS NOT NULL')
                results = []
                
                for row in cursor.fetchall():
                    file_path, content, embedding_blob = row
                    if embedding_blob:
                        stored_embedding = pickle.loads(embedding_blob)
                        
                        # Calculate cosine similarity
                        similarity = np.dot(query_embedding, stored_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                        )
                        
                        results.append({
                            'file_path': file_path,
                            'content': content[:500],  # Truncate for display
                            'similarity': float(similarity)
                        })
                
                # Sort by similarity and return top results
                results.sort(key=lambda x: x['similarity'], reverse=True)
                return results[:limit]
                
        except Exception as e:
            self.logger.error(f"Failed to find similar code: {e}")
            return []
    
    def store_analysis_session(self, project_path: str, code_analysis: Dict[str, Any], 
                             ai_insights: Dict[str, Any] = None) -> str:
        """Store complete analysis session for future reference."""
        
        session_id = hashlib.md5(f"{project_path}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        try:
            with sqlite3.connect(self.context_db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO analysis_sessions 
                    (session_id, project_path, analysis_data, ai_insights, created_at, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    project_path,
                    json.dumps(code_analysis),
                    json.dumps(ai_insights or {}),
                    datetime.now(),
                    datetime.now()
                ))
            
            self.logger.info(f"Stored analysis session: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis session: {e}")
            return ""
    
    def get_previous_analysis(self, project_path: str, days_back: int = 7) -> Optional[Dict[str, Any]]:
        """Retrieve previous analysis for the same project."""
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            with sqlite3.connect(self.context_db_path) as conn:
                cursor = conn.execute('''
                    SELECT analysis_data, ai_insights, created_at 
                    FROM analysis_sessions 
                    WHERE project_path = ? AND created_at > ?
                    ORDER BY created_at DESC LIMIT 1
                ''', (project_path, cutoff_date))
                
                row = cursor.fetchone()
                if row:
                    analysis_data, ai_insights, created_at = row
                    return {
                        'code_analysis': json.loads(analysis_data),
                        'ai_insights': json.loads(ai_insights),
                        'created_at': created_at
                    }
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve previous analysis: {e}")
        
        return None
    
    def enhance_prompt_with_context(self, prompt: str, project_path: str, 
                                  context_type: str = 'general') -> str:
        """Enhance LLM prompt with relevant context from memory."""
        
        try:
            # Get similar code examples
            similar_code = self.get_similar_code(prompt, limit=3)
            
            # Get previous analysis insights
            previous_analysis = self.get_previous_analysis(project_path)
            
            # Build enhanced context
            context_parts = []
            
            if similar_code:
                context_parts.append("## Similar Code Examples:")
                for i, code in enumerate(similar_code[:2], 1):  # Limit to 2 examples
                    context_parts.append(f"{i}. {code['file_path']} (similarity: {code['similarity']:.2f})")
                    context_parts.append(f"   {code['content'][:200]}...")
            
            if previous_analysis:
                context_parts.append("## Previous Analysis Insights:")
                prev_insights = previous_analysis.get('ai_insights', {})
                if prev_insights.get('architecture_analysis'):
                    arch = prev_insights['architecture_analysis']
                    if arch.get('patterns'):
                        patterns = [p.get('name', '') for p in arch['patterns'][:3]]
                        context_parts.append(f"   - Architecture patterns: {', '.join(patterns)}")
                
                if prev_insights.get('api_analysis'):
                    api = prev_insights['api_analysis']
                    if api.get('endpoints'):
                        endpoint_count = len(api['endpoints'])
                        context_parts.append(f"   - API endpoints detected: {endpoint_count}")
            
            # Combine context with original prompt
            if context_parts:
                enhanced_prompt = f"""CONTEXT (from code memory):
{chr(10).join(context_parts)}

ANALYSIS REQUEST:
{prompt}"""
                return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"Failed to enhance prompt with context: {e}")
        
        return prompt
    
    def store_context_memory(self, key: str, content: str, context_type: str = 'general',
                           relevance_score: float = 1.0) -> None:
        """Store contextual information for future use."""
        
        try:
            # Generate embedding if enabled
            embedding_blob = None
            if self.embeddings_enabled:
                embedding = self.embedding_model.encode(content)
                embedding_blob = pickle.dumps(embedding)
            
            with sqlite3.connect(self.context_db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO context_memory 
                    (context_key, context_type, content, embedding, relevance_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    key,
                    context_type,
                    content,
                    embedding_blob,
                    relevance_score,
                    datetime.now()
                ))
            
            self.logger.debug(f"Stored context memory: {key}")
            
        except Exception as e:
            self.logger.error(f"Failed to store context memory: {e}")
    
    def get_relevant_context(self, query: str, context_type: str = None, 
                           limit: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant context based on semantic similarity."""
        
        if not self.embeddings_enabled:
            return []
        
        try:
            query_embedding = self.embedding_model.encode(query)
            
            # Build SQL query
            sql = 'SELECT context_key, content, context_type, relevance_score, embedding FROM context_memory'
            params = []
            
            if context_type:
                sql += ' WHERE context_type = ?'
                params.append(context_type)
            
            with sqlite3.connect(self.context_db_path) as conn:
                cursor = conn.execute(sql, params)
                results = []
                
                for row in cursor.fetchall():
                    key, content, ctx_type, relevance, embedding_blob = row
                    if embedding_blob:
                        stored_embedding = pickle.loads(embedding_blob)
                        
                        # Calculate similarity
                        similarity = np.dot(query_embedding, stored_embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                        )
                        
                        results.append({
                            'key': key,
                            'content': content,
                            'context_type': ctx_type,
                            'relevance_score': relevance,
                            'similarity': float(similarity)
                        })
                
                # Sort by combined score (similarity * relevance)
                results.sort(key=lambda x: x['similarity'] * x['relevance_score'], reverse=True)
                return results[:limit]
                
        except Exception as e:
            self.logger.error(f"Failed to get relevant context: {e}")
            return []
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """Clean up old data from memory databases."""
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean code analysis database
            with sqlite3.connect(self.code_db_path) as conn:
                deleted_files = conn.execute(
                    'DELETE FROM code_files WHERE last_modified < ?', 
                    (cutoff_date,)
                ).rowcount
                
                deleted_relationships = conn.execute(
                    'DELETE FROM code_relationships WHERE last_updated < ?',
                    (cutoff_date,)
                ).rowcount
            
            # Clean context memory database
            with sqlite3.connect(self.context_db_path) as conn:
                deleted_sessions = conn.execute(
                    'DELETE FROM analysis_sessions WHERE created_at < ?',
                    (cutoff_date,)
                ).rowcount
                
                deleted_context = conn.execute(
                    'DELETE FROM context_memory WHERE created_at < ?',
                    (cutoff_date,)
                ).rowcount
            
            self.logger.info(f"Cleaned up old data: {deleted_files} files, {deleted_relationships} relationships, "
                           f"{deleted_sessions} sessions, {deleted_context} context entries")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get statistics about stored memory data."""
        
        stats = {}
        
        try:
            # Code database stats
            with sqlite3.connect(self.code_db_path) as conn:
                stats['total_files'] = conn.execute('SELECT COUNT(*) FROM code_files').fetchone()[0]
                stats['total_relationships'] = conn.execute('SELECT COUNT(*) FROM code_relationships').fetchone()[0]
            
            # Context database stats
            with sqlite3.connect(self.context_db_path) as conn:
                stats['total_sessions'] = conn.execute('SELECT COUNT(*) FROM analysis_sessions').fetchone()[0]
                stats['total_context_entries'] = conn.execute('SELECT COUNT(*) FROM context_memory').fetchone()[0]
            
            # File system stats
            stats['memory_dir_size_mb'] = sum(
                f.stat().st_size for f in self.memory_dir.rglob('*') if f.is_file()
            ) / (1024 * 1024)
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
        
        return stats
