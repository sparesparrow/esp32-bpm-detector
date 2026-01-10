#!/bin/bash
# Setup script for Postgres mcp-prompts integration

set -e

echo "🔧 Setting up Postgres mcp-prompts integration"
echo "================================================"

# Check if Postgres is running
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "⚠ Postgres is not running. Starting with Docker..."
    
    # Try to start Postgres via Docker Compose
    if [ -f "/home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts/docker-compose.postgres.yml" ]; then
        cd /home/sparrow/projects/ai-mcp-monorepo/packages/mcp-prompts
        docker-compose -f docker-compose.postgres.yml up -d
        echo "✅ Postgres started via Docker Compose"
    else
        echo "❌ Postgres not running and Docker Compose file not found"
        echo "Please start Postgres manually or install Docker Compose"
        exit 1
    fi
fi

# Wait for Postgres to be ready
echo "⏳ Waiting for Postgres to be ready..."
for i in {1..30}; do
    if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        echo "✅ Postgres is ready"
        break
    fi
    sleep 1
done

# Create database if it doesn't exist
echo "📦 Creating database if needed..."
psql -h localhost -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'mcp_prompts'" | grep -q 1 || \
    psql -h localhost -U postgres -c "CREATE DATABASE mcp_prompts;"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install psycopg2-binary || echo "⚠ psycopg2-binary installation failed (may already be installed)"

# Test connection
echo "🧪 Testing Postgres connection..."
python3 << 'EOF'
import sys
sys.path.insert(0, 'scripts')
from postgres_prompts_adapter import PostgresPromptsAdapter

try:
    adapter = PostgresPromptsAdapter()
    print("✅ Postgres connection successful")
    adapter.close()
except Exception as e:
    print(f"❌ Postgres connection failed: {e}")
    sys.exit(1)
EOF

echo ""
echo "================================================"
echo "✅ Postgres mcp-prompts setup complete!"
echo ""
echo "Next steps:"
echo "1. Update ~/.cursor/mcp.json with Postgres configuration"
echo "2. Restart Cursor to load new MCP configuration"
echo "3. Test with: python3 scripts/mcp_prompts_integration.py"
