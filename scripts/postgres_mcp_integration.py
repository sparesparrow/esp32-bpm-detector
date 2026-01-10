#!/usr/bin/env python3
"""
Postgres MCP Server Integration
Combines mcp-prompts Postgres storage with Postgres MCP server for direct database access.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sparetools_utils import setup_logging
from postgres_prompts_adapter import PostgresPromptsAdapter, get_postgres_adapter

logger = setup_logging(__name__)

class PostgresMCPIntegration:
    """Integration between Postgres MCP server and mcp-prompts Postgres storage."""
    
    def __init__(self, postgres_adapter: PostgresPromptsAdapter = None):
        """
        Initialize Postgres MCP integration.
        
        Args:
            postgres_adapter: Postgres adapter instance (auto-created if None)
        """
        self.adapter = postgres_adapter or get_postgres_adapter()
        if not self.adapter:
            logger.warning("Postgres adapter not available")
    
    def execute_query(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query via Postgres MCP server or direct adapter.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        if not self.adapter:
            logger.error("Postgres adapter not available")
            return []
        
        try:
            self.adapter._ensure_connected()
            with self.adapter.conn.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Fetch results
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in results]
                else:
                    # For INSERT/UPDATE/DELETE
                    self.adapter.conn.commit()
                    return [{"affected_rows": cursor.rowcount}]
                    
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            if self.adapter.conn:
                self.adapter.conn.rollback()
            return []
    
    def get_prompt_stats(self) -> Dict[str, Any]:
        """Get statistics about prompts in Postgres."""
        if not self.adapter:
            return {}
        
        try:
            stats_query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE is_template = TRUE) as templates,
                    COUNT(*) FILTER (WHERE is_template = FALSE) as regular,
                    COUNT(DISTINCT category) as categories,
                    COUNT(DISTINCT jsonb_array_elements_text(tags)) as unique_tags
                FROM prompts
            """
            
            results = self.execute_query(stats_query)
            if results:
                return results[0]
            return {}
            
        except Exception as e:
            logger.error(f"Error getting prompt stats: {e}")
            return {}
    
    def search_prompts_advanced(
        self,
        search_text: str = None,
        tags: List[str] = None,
        category: str = None,
        is_template: bool = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Advanced prompt search using SQL.
        
        Args:
            search_text: Text to search in name, content, description
            tags: Filter by tags
            category: Filter by category
            is_template: Filter by template status
            limit: Maximum results
            
        Returns:
            List of matching prompts
        """
        if not self.adapter:
            return []
        
        try:
            query = "SELECT * FROM prompts WHERE 1=1"
            params = []
            
            if search_text:
                query += " AND (name ILIKE %s OR content ILIKE %s OR description ILIKE %s)"
                pattern = f"%{search_text}%"
                params.extend([pattern, pattern, pattern])
            
            if tags:
                for tag in tags:
                    query += " AND tags::jsonb @> %s::jsonb"
                    import json
                    params.append(json.dumps([tag]))
            
            if category:
                query += " AND category = %s"
                params.append(category)
            
            if is_template is not None:
                query += " AND is_template = %s"
                params.append(is_template)
            
            query += " ORDER BY updated_at DESC LIMIT %s"
            params.append(limit)
            
            return self.execute_query(query, params)
            
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return []
    
    def migrate_prompts_from_file(self, prompts_dir: str) -> int:
        """
        Migrate prompts from file storage to Postgres.
        
        Args:
            prompts_dir: Directory containing prompt JSON files
            
        Returns:
            Number of prompts migrated
        """
        if not self.adapter:
            logger.error("Postgres adapter not available")
            return 0
        
        import json
        from pathlib import Path
        
        prompts_path = Path(prompts_dir)
        if not prompts_path.exists():
            logger.error(f"Prompts directory not found: {prompts_dir}")
            return 0
        
        migrated = 0
        
        # Find all JSON prompt files
        for prompt_file in prompts_path.glob("*.json"):
            if prompt_file.name == "index.json":
                continue
            
            try:
                with open(prompt_file, 'r') as f:
                    prompt_data = json.load(f)
                
                # Check if prompt already exists
                existing = self.adapter.get_prompt(prompt_data.get('name') or prompt_data.get('id'))
                if existing:
                    logger.debug(f"Prompt already exists: {prompt_data.get('name')}")
                    continue
                
                # Create prompt in Postgres
                success = self.adapter.create_prompt(
                    name=prompt_data.get('name', prompt_file.stem),
                    description=prompt_data.get('description', ''),
                    content=prompt_data.get('content', ''),
                    tags=prompt_data.get('tags', []),
                    category=prompt_data.get('category', 'general'),
                    is_template=prompt_data.get('isTemplate', False)
                )
                
                if success:
                    migrated += 1
                    logger.info(f"Migrated prompt: {prompt_data.get('name')}")
                    
            except Exception as e:
                logger.error(f"Error migrating {prompt_file}: {e}")
        
        logger.info(f"Migrated {migrated} prompts to Postgres")
        return migrated

def get_postgres_mcp_integration() -> Optional[PostgresMCPIntegration]:
    """Get Postgres MCP integration instance."""
    adapter = get_postgres_adapter()
    if adapter:
        return PostgresMCPIntegration(adapter)
    return None
