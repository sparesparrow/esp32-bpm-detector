# MCP Connection Troubleshooting Guide

## Problem: "Connection closed" Error

If you see this error:
```
Error (unhandledRejection): MCP error -32000: Connection closed
```

This means the mcp-prompts server is crashing on startup, usually because Postgres is unavailable.

---

## Quick Fix

### Option 1: Start Postgres (Recommended)

```bash
# If you have docker-compose.postgres.yml
docker-compose -f docker-compose.postgres.yml up -d

# Or using Docker directly
docker run -d --name mcp-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=mcp_prompts \
  -p 5432:5432 postgres:15
```

Then restart Cursor.

### Option 2: Switch to File Storage (Temporary)

Edit `~/.cursor/mcp.json` and change:

```json
{
  "mcpServers": {
    "mcp-prompts": {
      "env": {
        "STORAGE_TYPE": "file",  // Changed from "postgres"
        "PROMPTS_DIR": "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/data/prompts"
        // Remove POSTGRES_* variables
      }
    }
  }
}
```

Then restart Cursor.

### Option 3: Use Memory Storage (Temporary)

```json
{
  "mcpServers": {
    "mcp-prompts": {
      "env": {
        "STORAGE_TYPE": "memory"
        // Remove POSTGRES_* variables
      }
    }
  }
}
```

---

## Diagnostic Script

Run the diagnostic script:

```bash
./scripts/fix_mcp_postgres_connection.sh
```

This will:
1. Check if Postgres is accessible
2. Provide specific fix instructions
3. Show available options

---

## Root Cause

The mcp-prompts Node.js server tries to connect to Postgres on startup. If Postgres is unavailable, the server crashes, causing the MCP connection to close.

**Why this happens:**
- MCP servers are started by Cursor on startup
- If Postgres isn't running, the server fails to initialize
- The connection closes before operations can fall back

---

## Solutions

### Long-term: Make Server Resilient

The mcp-prompts server should handle Postgres failures gracefully, but currently it doesn't. Until that's fixed:

1. **Always have Postgres running** when using Postgres storage
2. **Use file storage** if Postgres isn't needed
3. **Monitor Postgres** to ensure it stays running

### Short-term: Use Fallback Storage

1. **File Storage**: Works without Postgres, persists to disk
2. **Memory Storage**: Fast but loses data on restart
3. **Postgres**: Best for production, requires running database

---

## Verification

After fixing, verify the connection:

```bash
# Check Postgres
python3 scripts/check_postgres_connection.py

# Test MCP prompt retrieval
python3 -c "
from scripts.mcp_prompts_integration import get_prompt_mcp
prompt = get_prompt_mcp('code-review-assistant')
print('✅ MCP connection working' if prompt else '❌ Still failing')
"
```

---

## Related Files

- `~/.cursor/mcp.json` - MCP server configuration
- `scripts/fix_mcp_postgres_connection.sh` - Diagnostic script
- `scripts/check_postgres_connection.py` - Connection checker
- `.cursor/mcp.json.fallback` - File storage fallback config

---

**Last Updated**: 2026-01-01
