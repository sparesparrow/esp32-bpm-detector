# Postgres mcp-prompts Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
# Python Postgres adapter
pip install psycopg2-binary

# Or using bundled CPython
python3 scripts/ensure_bundled_python.py -m pip install psycopg2-binary
```

### 2. Start Postgres Database

**Option A: Docker Compose (Recommended)**
```bash
cd /home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts
docker-compose -f docker-compose.postgres.yml up -d
```

**Option B: Local Postgres**
```bash
# Create database
createdb mcp_prompts

# Or using psql
psql -U postgres -c "CREATE DATABASE mcp_prompts;"
```

### 3. Run Setup Script

```bash
cd /home/sparrow/projects/embedded-systems/esp32-bpm-detector
bash scripts/setup_postgres_mcp_prompts.sh
```

### 4. Update MCP Configuration

```bash
# Backup current config
cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup

# Use Postgres configuration
cp .cursor/mcp.json.postgres ~/.cursor/mcp.json
```

### 5. Restart Cursor

Restart Cursor IDE to load the new MCP configuration.

---

## Configuration Options

### Environment Variables

Set these in your shell or MCP configuration:

```bash
export STORAGE_TYPE=postgres
export POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/mcp_prompts
# Or individual variables:
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DATABASE=mcp_prompts
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
```

### MCP Configuration

Update `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-prompts": {
      "command": "npx",
      "args": ["-y", "@sparesparrow/mcp-prompts"],
      "env": {
        "STORAGE_TYPE": "postgres",
        "POSTGRES_URL": "postgresql://postgres:postgres@localhost:5432/mcp_prompts",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

---

## Testing

### Test Postgres Connection

```python
from scripts.postgres_prompts_adapter import PostgresPromptsAdapter

adapter = PostgresPromptsAdapter()
prompts = adapter.list_prompts(limit=5)
print(f"Found {len(prompts)} prompts")
adapter.close()
```

### Test MCP Integration

```python
from scripts.mcp_prompts_integration import list_prompts_mcp, get_prompt_mcp

# Should use Postgres if configured
prompts = list_prompts_mcp(tags=["esp32"])
prompt = get_prompt_mcp("code-review-assistant")
```

### Test via cursor-agent

```bash
cursor-agent --print --approve-mcps "Use mcp-prompts list_prompts limit=5"
```

---

## Migration from File Storage

### Export from File Storage

```python
import json
from pathlib import Path

prompts_dir = Path("/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts")
prompts = []

for prompt_file in prompts_dir.glob("*.json"):
    with open(prompt_file) as f:
        prompts.append(json.load(f))

# Save to file
with open("prompts_export.json", "w") as f:
    json.dump(prompts, f, indent=2)
```

### Import to Postgres

```python
from scripts.postgres_prompts_adapter import PostgresPromptsAdapter
import json

adapter = PostgresPromptsAdapter()

with open("prompts_export.json") as f:
    prompts = json.load(f)

for prompt_data in prompts:
    adapter.create_prompt(
        name=prompt_data.get("name", prompt_data.get("id")),
        description=prompt_data.get("description", ""),
        content=prompt_data.get("content", ""),
        tags=prompt_data.get("tags", []),
        category=prompt_data.get("category"),
        is_template=prompt_data.get("isTemplate", False)
    )

adapter.close()
```

---

## Troubleshooting

### Postgres Not Running

```bash
# Check if Postgres is running
pg_isready -h localhost -p 5432

# Start with Docker
docker-compose -f docker-compose.postgres.yml up -d
```

### Connection Errors

```bash
# Test connection
psql -h localhost -U postgres -d mcp_prompts -c "SELECT COUNT(*) FROM prompts;"

# Check environment variables
echo $POSTGRES_URL
```

### Schema Issues

```python
# Recreate schema
from scripts.postgres_prompts_adapter import PostgresPromptsAdapter
adapter = PostgresPromptsAdapter()
adapter._ensure_schema()
```

---

## Status

✅ **Postgres Adapter**: Implemented  
✅ **MCP Integration**: Complete  
✅ **Setup Script**: Created  
✅ **Documentation**: Complete  

**Ready for Postgres integration!** 🚀
