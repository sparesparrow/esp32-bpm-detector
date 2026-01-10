# Postgres MCP Integration Guide

## Overview

This project integrates **mcp-prompts with Postgres storage** combined with **Postgres MCP server** for comprehensive database access and prompt management.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Postgres MCP Integration                    │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ mcp-prompts   │   │ Postgres MCP  │   │ Postgres     │
│ MCP Server    │   │ Server       │   │ Adapter      │
│ (Postgres)    │   │ (Direct SQL) │   │ (Python)     │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Postgres DB   │
                    │  mcp_prompts   │
                    └────────────────┘
```

---

## Configuration

### MCP Configuration (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "mcp-prompts": {
      "command": "node",
      "args": [
        "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/dist/mcp-server-standalone.js"
      ],
      "env": {
        "MODE": "mcp",
        "STORAGE_TYPE": "postgres",
        "POSTGRES_URL": "postgresql://postgres:postgres@localhost:5432/mcp_prompts",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DATABASE": "mcp_prompts",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "LOG_LEVEL": "info"
      }
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://postgres:postgres@localhost:5432/mcp_prompts"
      ],
      "env": {
        "POSTGRES_URL": "postgresql://postgres:postgres@localhost:5432/mcp_prompts"
      }
    }
  }
}
```

---

## Database Setup

### 1. Start Postgres Database

```bash
# Using Docker Compose (from mcp-prompts project)
cd /home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts
docker-compose -f docker-compose.postgres.yml up -d

# Or manually
docker run -d \
  --name mcp-prompts-postgres \
  -e POSTGRES_DB=mcp_prompts \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine
```

### 2. Schema Creation

The Postgres adapter automatically creates the schema on first connection:

```sql
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
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category);
CREATE INDEX IF NOT EXISTS idx_prompts_name ON prompts(name);
```

---

## Usage

### Method 1: mcp-prompts MCP Server (Postgres Storage)

```python
from mcp_prompts_integration import list_prompts_mcp, get_prompt_mcp

# List prompts (uses Postgres via mcp-prompts server)
prompts = list_prompts_mcp(tags=["esp32", "embedded"], limit=10)

# Get prompt with template variables
prompt = get_prompt_mcp(
    "code-review-assistant",
    arguments={"platform": "esp32", "language": "cpp"}
)
```

### Method 2: Postgres MCP Server (Direct SQL)

```bash
# Use cursor-agent with Postgres MCP server
cursor-agent --print --approve-mcps \
  "Use postgres MCP server to query: SELECT * FROM prompts WHERE category = 'embedded' LIMIT 10"
```

### Method 3: Direct Postgres Adapter (Python)

```python
from postgres_prompts_adapter import get_postgres_adapter

adapter = get_postgres_adapter()
if adapter:
    # List prompts
    prompts = adapter.list_prompts(tags=["esp32"], limit=10)
    
    # Get prompt
    prompt = adapter.get_prompt("code-review-assistant", {"platform": "esp32"})
    
    # Create prompt
    adapter.create_prompt(
        name="esp32-specialized-review",
        description="ESP32-specific code review",
        content="Review ESP32 code...",
        tags=["esp32", "embedded"],
        category="embedded"
    )
```

### Method 4: Postgres MCP Integration (Combined)

```python
from postgres_mcp_integration import get_postgres_mcp_integration

integration = get_postgres_mcp_integration()
if integration:
    # Advanced search
    prompts = integration.search_prompts_advanced(
        search_text="ESP32",
        tags=["embedded"],
        is_template=True,
        limit=10
    )
    
    # Get statistics
    stats = integration.get_prompt_stats()
    
    # Execute custom SQL
    results = integration.execute_query(
        "SELECT category, COUNT(*) as count FROM prompts GROUP BY category"
    )
```

---

## Integration Priority

The system tries methods in this order:

1. **Postgres MCP Server** - Direct SQL queries via MCP
2. **Postgres Adapter (Direct)** - Python direct database access
3. **mcp-prompts MCP Server** - MCP tools with Postgres storage
4. **Fallback** - File-based or memory storage

---

## Template Variable Handling

### Automatic Template Detection

```python
from template_utils import get_template_info, substitute_template_variables

content = "Review {{platform}} code in {{code_path}}"
info = get_template_info(content)
# Returns: {
#   "is_template": True,
#   "variables": ["platform", "code_path"],
#   "has_defaults": False
# }

# Substitute variables
result = substitute_template_variables(
    content,
    {"platform": "esp32", "code_path": "src/"}
)
# Returns: "Review esp32 code in src/"
```

### Variable Validation

```python
from template_utils import validate_template_variables

validation = validate_template_variables(
    "Hello {{name}}, count: {{count}}",
    {"name": "World"}
)
# Returns: {
#   "valid": False,
#   "missing": ["count"],
#   "extra": [],
#   "required": ["name", "count"],
#   "provided": ["name"]
# }
```

---

## Migration from File Storage

```python
from postgres_mcp_integration import get_postgres_mcp_integration

integration = get_postgres_mcp_integration()
if integration:
    # Migrate prompts from file storage to Postgres
    migrated = integration.migrate_prompts_from_file(
        "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
    )
    print(f"Migrated {migrated} prompts to Postgres")
```

---

## Testing

### Test Postgres Connection

```python
from postgres_prompts_adapter import get_postgres_adapter

adapter = get_postgres_adapter()
if adapter:
    print("✅ Postgres adapter connected")
    adapter.disconnect()
else:
    print("❌ Postgres adapter not available")
```

### Test MCP Servers

```bash
# Test mcp-prompts server
cursor-agent mcp list-tools mcp-prompts

# Test Postgres MCP server
cursor-agent mcp list-tools postgres
```

### Test Template Utilities

```python
from scripts.template_utils import (
    extract_template_variables,
    substitute_template_variables,
    get_template_info,
    validate_template_variables
)

# Test extraction
vars = extract_template_variables("Hello {{name}}")
assert vars == ["name"]

# Test substitution
result = substitute_template_variables("Hello {{name}}", {"name": "World"})
assert result == "Hello World"

# Test validation
validation = validate_template_variables("{{a}} {{b}}", {"a": "1"})
assert validation["missing"] == ["b"]
```

---

## Dependencies

### Python Packages

```bash
pip install psycopg2-binary
```

### Node.js Packages

```bash
# Postgres MCP server (installed via npx)
npx -y @modelcontextprotocol/server-postgres

# mcp-prompts (already installed)
npm list -g @sparesparrow/mcp-prompts
```

### Database

```bash
# Postgres 15+ recommended
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_DB=mcp_prompts \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  postgres:15-alpine
```

---

## Benefits

1. **Unified Storage**: All prompts in Postgres database
2. **Direct SQL Access**: Query prompts with SQL via Postgres MCP server
3. **Python Integration**: Direct database access for scripts
4. **Template Support**: Automatic template variable detection and substitution
5. **Migration Tools**: Easy migration from file storage
6. **Performance**: Indexed queries for fast searches

---

## Status

✅ **Postgres Adapter**: Implemented  
✅ **Postgres MCP Integration**: Implemented  
✅ **Template Utilities**: Implemented  
✅ **MCP Configuration**: Updated  
✅ **Schema Auto-Creation**: Implemented  
✅ **Migration Tools**: Available  

**Postgres MCP integration is ready for use!** 🚀

---

**Last Updated**: 2026-01-01  
**Version**: 1.0.0
