#!/usr/bin/env python3
"""
Check if Postgres is available and can be connected to.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def main():
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Get connection string from environment
        import os
        postgres_url = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/mcp_prompts")
        
        print(f"Testing Postgres connection...")
        print(f"URL: {postgres_url.split('@')[0]}@***")  # Hide password
        
        try:
            conn = psycopg2.connect(postgres_url, connect_timeout=3)
            conn.close()
            print("✅ Postgres is available and accessible")
            print("   MCP server should be able to connect")
            return 0
        except psycopg2.OperationalError as e:
            print(f"❌ Postgres connection failed: {e}")
            print("\n💡 Solutions:")
            print("   1. Start Postgres:")
            print("      docker-compose -f docker-compose.postgres.yml up -d")
            print("   2. Or switch to file storage in ~/.cursor/mcp.json:")
            print('      "STORAGE_TYPE": "file"')
            return 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return 1
            
    except ImportError:
        print("⚠️  psycopg2 not installed")
        print("   Install with: pip install psycopg2-binary")
        return 1

if __name__ == "__main__":
    sys.exit(main())
