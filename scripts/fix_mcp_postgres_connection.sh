#!/bin/bash
# Fix MCP Postgres Connection Issues
# This script helps diagnose and fix MCP server connection problems

set -e

echo "🔍 MCP Postgres Connection Diagnostic"
echo "======================================"
echo ""

# Check if Postgres is running
echo "1. Checking Postgres connection..."
if python3 -c "
import psycopg2
import os
try:
    postgres_url = os.getenv('POSTGRES_URL', 'postgresql://postgres:postgres@localhost:5432/mcp_prompts')
    conn = psycopg2.connect(postgres_url, connect_timeout=3)
    conn.close()
    print('✅ Postgres is accessible')
    exit(0)
except Exception as e:
    print(f'❌ Postgres connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo "   ✅ Postgres is running and accessible"
    echo ""
    echo "💡 If MCP server still crashes, try:"
    echo "   1. Restart Cursor to reload MCP servers"
    echo "   2. Check MCP server logs in Cursor"
    exit 0
else
    echo "   ❌ Postgres is not accessible"
    echo ""
    echo "2. Checking for Docker Compose setup..."
    
    # Check for docker-compose file
    if [ -f "docker-compose.postgres.yml" ] || [ -f "../docker-compose.postgres.yml" ]; then
        echo "   ✅ Found docker-compose.postgres.yml"
        echo ""
        echo "3. Options to fix:"
        echo ""
        echo "   Option A: Start Postgres with Docker"
        echo "   ------------------------------------"
        echo "   docker-compose -f docker-compose.postgres.yml up -d"
        echo ""
        echo "   Option B: Switch to file storage (temporary)"
        echo "   ---------------------------------------------"
        echo "   Edit ~/.cursor/mcp.json and change:"
        echo '   "STORAGE_TYPE": "postgres"  →  "STORAGE_TYPE": "file"'
        echo ""
        echo "   Option C: Use memory storage (temporary)"
        echo "   ----------------------------------------"
        echo '   Change "STORAGE_TYPE": "memory" in ~/.cursor/mcp.json'
        echo ""
    else
        echo "   ⚠️  No docker-compose.postgres.yml found"
        echo ""
        echo "3. Options to fix:"
        echo ""
        echo "   Option A: Install and start Postgres"
        echo "   ------------------------------------"
        echo "   # Using Docker:"
        echo "   docker run -d --name mcp-postgres \\"
        echo "     -e POSTGRES_PASSWORD=postgres \\"
        echo "     -e POSTGRES_DB=mcp_prompts \\"
        echo "     -p 5432:5432 postgres:15"
        echo ""
        echo "   Option B: Switch to file storage"
        echo "   --------------------------------"
        echo "   Edit ~/.cursor/mcp.json:"
        echo '   "STORAGE_TYPE": "file"'
        echo ""
    fi
    
    echo ""
    echo "⚠️  After fixing, restart Cursor to reload MCP servers"
    exit 1
fi
