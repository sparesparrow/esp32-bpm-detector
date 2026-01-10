#!/usr/bin/env python3
"""
Postgres Prompts Adapter
Direct database access adapter for mcp-prompts Postgres storage.

This adapter provides direct access to the Postgres database used by mcp-prompts,
allowing Python scripts to interact with prompts without going through MCP.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sparetools_utils import setup_logging

logger = setup_logging(__name__)

# Try to import psycopg2
POSTGRES_AVAILABLE = False
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    logger.warning("psycopg2 not installed. Install with: pip install psycopg2-binary")
    POSTGRES_AVAILABLE = False

class PostgresPromptsAdapter:
    """Adapter for accessing mcp-prompts Postgres storage directly."""
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        database: str = None,
        user: str = None,
        password: str = None,
        database_url: str = None
    ):
        """
        Initialize Postgres adapter.
        
        Args:
            host: Postgres host (default: from env or localhost)
            port: Postgres port (default: from env or 5432)
            database: Database name (default: from env or mcp_prompts)
            user: Database user (default: from env or postgres)
            password: Database password (default: from env or postgres)
            database_url: Full database URL (overrides individual params)
        """
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 not available. Install with: pip install psycopg2-binary")
        
        # Get connection parameters
        # Check for POSTGRES_URL first (full connection string)
        database_url = database_url or os.getenv("POSTGRES_URL")
        if database_url:
            self.conn_string = database_url
        else:
            host = host or os.getenv("POSTGRES_HOST", "localhost")
            port = port or int(os.getenv("POSTGRES_PORT", "5432"))
            database = database or os.getenv("POSTGRES_DATABASE", "mcp_prompts")
            user = user or os.getenv("POSTGRES_USER", "postgres")
            password = password or os.getenv("POSTGRES_PASSWORD", "postgres")
            
            # Construct connection string with proper URL encoding
            from urllib.parse import quote_plus
            password_encoded = quote_plus(password) if password else ""
            self.conn_string = f"postgresql://{user}:{password_encoded}@{host}:{port}/{database}"
        
        self.conn = None
        logger.info(f"Initialized Postgres adapter for database: {database or 'from URL'}")
        # Don't connect on initialization - use lazy connection
        # This prevents crashes if Postgres is unavailable
    
    def connect(self, retry_count: int = 1):
        """Establish database connection with retry logic."""
        for attempt in range(retry_count):
            try:
                # Try connection string first, fall back to individual parameters
                try:
                    self.conn = psycopg2.connect(
                        self.conn_string,
                        connect_timeout=5  # 5 second timeout
                    )
                except Exception as e1:
                    # Parse connection string and use individual parameters
                    from urllib.parse import urlparse, unquote
                    parsed = urlparse(self.conn_string)
                    
                    # Decode password if URL encoded
                    password = unquote(parsed.password) if parsed.password else "postgres"
                    
                    self.conn = psycopg2.connect(
                        host=parsed.hostname or "localhost",
                        port=parsed.port or 5432,
                        database=parsed.path.lstrip('/') or "mcp_prompts",
                        user=parsed.username or "postgres",
                        password=password,
                        connect_timeout=5
                    )
                
                # Ensure schema exists after successful connection
                self._ensure_schema()
                logger.debug("Connected to Postgres database")
                return True
            except psycopg2.OperationalError as e:
                if attempt < retry_count - 1:
                    logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")
                    import time
                    time.sleep(0.5)  # Brief delay before retry
                else:
                    logger.error(f"Failed to connect to Postgres after {retry_count} attempts: {e}")
                    return False
            except Exception as e:
                logger.error(f"Failed to connect to Postgres: {e}")
                return False
        
        return False
    
    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.debug("Disconnected from Postgres database")
    
    def _ensure_connected(self):
        """Ensure database connection is established."""
        # Check if connection exists and is open
        if self.conn:
            try:
                # Try a simple query to check if connection is alive
                with self.conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
            except (psycopg2.InterfaceError, psycopg2.OperationalError):
                # Connection is dead, close it
                try:
                    self.conn.close()
                except:
                    pass
                self.conn = None
        
        # Connect if needed
        if not self.conn:
            if not self.connect():
                raise ConnectionError("Failed to connect to Postgres database")
    
    def _ensure_schema(self):
        """Ensure database schema exists."""
        self._ensure_connected()
        
        try:
            with self.conn.cursor() as cursor:
                # Create prompts table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS prompts (
                        id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        content TEXT NOT NULL,
                        description TEXT,
                        is_template BOOLEAN DEFAULT FALSE,
                        tags JSONB,
                        variables JSONB,
                        category VARCHAR(255),
                        metadata JSONB,
                        version INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts USING GIN(tags)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_prompts_name ON prompts(name)
                """)
                
                self.conn.commit()
                logger.debug("Database schema ensured")
        except Exception as e:
            logger.error(f"Failed to ensure schema: {e}")
            if self.conn:
                self.conn.rollback()
    
    def list_prompts(
        self,
        tags: List[str] = None,
        category: str = None,
        search: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List prompts from Postgres database.
        
        Args:
            tags: Filter by tags
            category: Filter by category
            search: Search query
            limit: Maximum results
            
        Returns:
            List of prompt dictionaries
        """
        self._ensure_connected()
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Build query
                query = "SELECT * FROM prompts WHERE 1=1"
                params = []
                
                if tags:
                    # Filter by tags (assuming tags are stored as JSON array)
                    for tag in tags:
                        query += " AND tags::jsonb @> %s::jsonb"
                        params.append(json.dumps([tag]))
                
                if category:
                    query += " AND category = %s"
                    params.append(category)
                
                if search:
                    query += " AND (name ILIKE %s OR content ILIKE %s OR description ILIKE %s)"
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern, search_pattern])
                
                query += " ORDER BY updated_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                # Convert to list of dicts
                prompts = [dict(row) for row in results]
                
                logger.debug(f"Listed {len(prompts)} prompts from Postgres")
                return prompts
                
        except Exception as e:
            logger.error(f"Error listing prompts from Postgres: {e}")
            return []
    
    def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Get a prompt from Postgres database.
        
        Args:
            name: Prompt name/ID
            arguments: Template variables (for template hydration)
            
        Returns:
            Prompt dictionary or None if not found
        """
        self._ensure_connected()
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Try by name first, then by ID
                cursor.execute(
                    "SELECT * FROM prompts WHERE name = %s OR id = %s ORDER BY version DESC LIMIT 1",
                    (name, name)
                )
                result = cursor.fetchone()
                
                if not result:
                    logger.warning(f"Prompt not found: {name}")
                    return None
                
                prompt = dict(result)
                
                # Apply template variables if provided
                if arguments:
                    content = prompt.get('content', '')
                    
                    # Import template utilities
                    from template_utils import substitute_template_variables, extract_template_variables, get_template_info
                    
                    # Check if this is a template (has {{variables}})
                    template_info = get_template_info(content)
                    if template_info['is_template']:
                        # Substitute variables using proper handlebars syntax
                        content = substitute_template_variables(content, arguments)
                        prompt['content'] = content
                        prompt['is_template'] = True
                        prompt['template_variables'] = template_info['variables']
                        prompt['substituted_variables'] = list(arguments.keys())
                        logger.debug(f"Substituted template variables: {list(arguments.keys())}")
                    elif prompt.get('is_template'):
                        # Legacy: if marked as template, still try substitution
                        content = substitute_template_variables(content, arguments)
                        prompt['content'] = content
                
                logger.debug(f"Retrieved prompt: {name}")
                return prompt
                
        except Exception as e:
            logger.error(f"Error getting prompt from Postgres: {e}")
            return None
    
    def create_prompt(
        self,
        name: str,
        description: str,
        content: str,
        tags: List[str] = None,
        category: str = None,
        is_template: bool = False
    ) -> bool:
        """
        Create a new prompt in Postgres database.
        
        Args:
            name: Prompt name
            description: Prompt description
            content: Prompt content
            tags: List of tags
            category: Category
            is_template: Whether prompt is a template
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connected()
        
        try:
            with self.conn.cursor() as cursor:
                # Import template utilities to auto-detect templates
                from template_utils import get_template_info, extract_template_variables
                
                # Auto-detect if template (has {{variables}})
                template_info = get_template_info(content)
                is_template = is_template or template_info['is_template']
                template_vars = template_info['variables']
                
                # Generate ID
                import uuid
                prompt_id = str(uuid.uuid4())
                
                # Store variables as JSONB
                variables_json = json.dumps(template_vars) if template_vars else None
                
                # Insert prompt
                cursor.execute(
                    """
                    INSERT INTO prompts (id, name, description, content, tags, category, is_template, variables, version, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, NOW(), NOW())
                    """,
                    (
                        prompt_id,
                        name,
                        description,
                        content,
                        json.dumps(tags or []),
                        category or 'general',
                        is_template,
                        variables_json
                    )
                )
                
                self.conn.commit()
                logger.info(f"Created prompt in Postgres: {name} ({prompt_id})")
                return True
                
        except Exception as e:
            logger.error(f"Error creating prompt in Postgres: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def update_prompt(self, name: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing prompt in Postgres database.
        
        Args:
            name: Prompt name/ID
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connected()
        
        try:
            with self.conn.cursor() as cursor:
                # Get current version
                cursor.execute(
                    "SELECT version FROM prompts WHERE name = %s OR id = %s ORDER BY version DESC LIMIT 1",
                    (name, name)
                )
                result = cursor.fetchone()
                
                if not result:
                    logger.warning(f"Prompt not found for update: {name}")
                    return False
                
                current_version = result[0]
                new_version = current_version + 1
                
                # Build update query
                set_clauses = []
                params = []
                
                for key, value in updates.items():
                    if key == 'tags' and isinstance(value, list):
                        set_clauses.append(f"{key} = %s::jsonb")
                        params.append(json.dumps(value))
                    elif key == 'metadata' and isinstance(value, dict):
                        set_clauses.append(f"{key} = %s::jsonb")
                        params.append(json.dumps(value))
                    elif key == 'variables' and isinstance(value, (list, dict)):
                        set_clauses.append(f"{key} = %s::jsonb")
                        params.append(json.dumps(value))
                    else:
                        set_clauses.append(f"{key} = %s")
                        params.append(value)
                
                set_clauses.append("version = %s")
                params.append(new_version)
                
                set_clauses.append("updated_at = NOW()")
                
                params.append(name)  # For WHERE clause
                params.append(name)  # For WHERE clause
                
                query = f"""
                    UPDATE prompts 
                    SET {', '.join(set_clauses)}
                    WHERE (name = %s OR id = %s) AND version = {current_version}
                """
                
                cursor.execute(query, params)
                self.conn.commit()
                
                logger.info(f"Updated prompt in Postgres: {name} (v{new_version})")
                return True
                
        except Exception as e:
            logger.error(f"Error updating prompt in Postgres: {e}")
            if self.conn:
                self.conn.rollback()
            return False

def get_postgres_adapter() -> Optional[PostgresPromptsAdapter]:
    """
    Get Postgres adapter instance using environment variables or config.
    
    Returns:
        PostgresPromptsAdapter instance or None if not available
    """
    if not POSTGRES_AVAILABLE:
        logger.debug("Postgres adapter not available (psycopg2 not installed)")
        return None
    
    try:
        # Try to get database URL from environment
        database_url = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
        
        if database_url:
            adapter = PostgresPromptsAdapter(database_url=database_url)
        else:
            # Use individual parameters
            adapter = PostgresPromptsAdapter(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432")),
                database=os.getenv("POSTGRES_DATABASE", "mcp_prompts"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres")
            )
        
        # Don't test connection here - use lazy connection
        # This prevents crashes if Postgres is unavailable
        # Connection will be tested on first use
        return adapter
            
    except Exception as e:
        logger.warning(f"Failed to create Postgres adapter: {e}")
        return None
