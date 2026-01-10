# Postgres mcp-prompts Integration

## Overview

This project now supports **Postgres storage** for mcp-prompts, providing a robust, scalable backend for prompt management. This enables:

1. **Centralized Storage**: All prompts in a shared Postgres database
2. **Team Collaboration**: Multiple developers can access the same prompts
3. **Version Control**: Database-level versioning and history
4. **Performance**: Fast queries with proper indexing
5. **Scalability**: Handle thousands of prompts efficiently

---

## Configuration

### MCP Server Configuration

Update `~/.cursor/mcp.json` to use Postgres storage:

```json
{
  "mcpServers": {
    "mcp-prompts": {
      "command": "npx",
      "args": ["-y", "@sparesparrow/mcp-prompts"],
      "env": {
        "STORAGE_TYPE": "postgres",
        "POSTGRES_URL": "postgresql://postgres:postgres@localhost:5432/mcp_prompts",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DATABASE": "mcp_prompts",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

### Environment Variables

Set these environment variables for Postgres connection:

```bash
export STORAGE_TYPE=postgres
export POSTGRES_URL=postgresql://user:password@host:port/database
# Or individual variables:
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DATABASE=mcp_prompts
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
```

---

## Database Setup

### Using Docker Compose

```bash
cd /home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts
docker-compose -f docker-compose.postgres.yml up -d
```

This starts:
- Postgres database on port 5432
- mcp-prompts server with Postgres storage on port 3003

### Manual Setup

```bash
# Create database
createdb mcp_prompts

# Or using psql
psql -U postgres -c "CREATE DATABASE mcp_prompts;"
```

The schema will be automatically created on first connection.

---

## Python Integration

### Postgres Adapter

**File**: `scripts/postgres_prompts_adapter.py`

Provides direct Python access to Postgres storage:

```python
from postgres_prompts_adapter import PostgresPromptsAdapter

# Initialize adapter
adapter = PostgresPromptsAdapter(
    host="localhost",
    port=5432,
    database="mcp_prompts",
    user="postgres",
    password="postgres"
)

# List prompts
prompts = adapter.list_prompts(tags=["esp32"], limit=10)

# Get prompt
prompt = adapter.get_prompt("code-review-assistant", arguments={"platform": "esp32"})

# Create prompt
adapter.create_prompt(
    name="esp32-bpm-review",
    description="ESP32 BPM detector code review",
    content="Review ESP32 firmware...",
    tags=["esp32", "bpm", "code-review"],
    category="embedded"
)

# Update prompt
adapter.update_prompt("esp32-bpm-review", {
    "content": "Updated review instructions...",
    "tags": ["esp32", "bpm", "code-review", "updated"]
})
```

### Automatic Detection

The `mcp_prompts_integration.py` automatically detects and uses Postgres if available:

```python
from mcp_prompts_integration import list_prompts_mcp, get_prompt_mcp

# Automatically uses Postgres if configured, falls back to MCP tools
prompts = list_prompts_mcp(tags=["esp32"])
prompt = get_prompt_mcp("code-review-assistant")
```

---

## Database Schema

The adapter automatically creates this schema:

```sql
CREATE TABLE prompts (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    description TEXT,
    is_template BOOLEAN DEFAULT FALSE,
    tags TEXT[],
    variables JSONB,
    category VARCHAR(255),
    metadata JSONB,
    version VARCHAR(50) DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_prompts_tags ON prompts USING GIN(tags);
CREATE INDEX idx_prompts_category ON prompts(category);
CREATE INDEX idx_prompts_search ON prompts USING GIN(to_tsvector('english', name || ' ' || COALESCE(description, '')));
```

---

## Migration from File Storage

### Option 1: Export/Import Script

```python
from postgres_prompts_adapter import PostgresPromptsAdapter
import json
from pathlib import Path

# Load prompts from file storage
prompts_dir = Path("/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts")
adapter = PostgresPromptsAdapter()

for prompt_file in prompts_dir.glob("*.json"):
    with open(prompt_file) as f:
        prompt_data = json.load(f)
        adapter.create_prompt(
            name=prompt_data.get("name", prompt_data.get("id")),
            description=prompt_data.get("description", ""),
            content=prompt_data.get("content", ""),
            tags=prompt_data.get("tags", []),
            category=prompt_data.get("category"),
            is_template=prompt_data.get("isTemplate", False)
        )
```

### Option 2: Use mcp-prompts CLI

```bash
# Export from file storage
mcp-prompts export --output prompts.json

# Import to Postgres (if supported)
mcp-prompts import --input prompts.json --storage postgres
```

---

## Dependencies

### Python

```bash
pip install psycopg2-binary
```

### Node.js

The mcp-prompts server already includes Postgres support (via KeyV).

---

## Usage in Learning Loop

The learning loop workflow automatically uses Postgres if configured:

```python
from mcp_prompts_integration import discover_relevant_prompts, get_prompt_mcp

# Automatically uses Postgres backend
prompts = discover_relevant_prompts("code-review", {"platform": "esp32"})
prompt = get_prompt_mcp("code-review-assistant", {"platform": "esp32"})
```

---

## Benefits

1. **Centralized**: Single source of truth for all prompts
2. **Team Access**: Multiple developers can use the same prompts
3. **Performance**: Fast queries with proper indexing
4. **Scalability**: Handle large numbers of prompts
5. **Backup**: Easy database backups
6. **History**: Track prompt changes over time

---

## Troubleshooting

### Connection Issues

```bash
# Test Postgres connection
psql -U postgres -d mcp_prompts -c "SELECT COUNT(*) FROM prompts;"

# Check environment variables
echo $POSTGRES_URL
echo $POSTGRES_HOST
```

### Schema Issues

```python
# Recreate schema
adapter = PostgresPromptsAdapter()
adapter._ensure_schema()  # Will create tables if missing
```

### Performance Issues

```sql
-- Check indexes
SELECT * FROM pg_indexes WHERE tablename = 'prompts';

-- Analyze table
ANALYZE prompts;
```

---

## Status

✅ **Postgres Adapter**: Implemented  
✅ **Automatic Detection**: Working  
✅ **Schema Creation**: Automatic  
✅ **Integration**: Complete  
✅ **Documentation**: Complete  

**Postgres integration ready for use!** 🚀

---

**Last Updated**: 2026-01-01  
**Version**: 1.0.0
