#!/usr/bin/env python3
"""
Test Postgres MCP Integration
Tests the integration between mcp-prompts Postgres storage and Postgres MCP server.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sparetools_utils import setup_logging
from postgres_prompts_adapter import get_postgres_adapter
from postgres_mcp_integration import get_postgres_mcp_integration
from template_utils import (
    extract_template_variables,
    substitute_template_variables,
    get_template_info,
    validate_template_variables
)

logger = setup_logging(__name__)

def test_template_utilities():
    """Test template utility functions."""
    print("\n" + "="*70)
    print("Testing Template Utilities")
    print("="*70)
    
    # Test 1: Extract variables
    content = "Review {{platform}} code in {{code_path}} using {{language}}"
    vars = extract_template_variables(content)
    print(f"\n✅ Extract Variables:")
    print(f"   Content: {content}")
    print(f"   Variables: {vars}")
    assert vars == ["platform", "code_path", "language"]
    
    # Test 2: Substitute variables
    result = substitute_template_variables(
        content,
        {"platform": "esp32", "code_path": "src/", "language": "cpp"}
    )
    print(f"\n✅ Substitute Variables:")
    print(f"   Result: {result}")
    assert "esp32" in result and "src/" in result and "cpp" in result
    
    # Test 3: Get template info
    info = get_template_info(content)
    print(f"\n✅ Template Info:")
    print(f"   Is Template: {info['is_template']}")
    print(f"   Variables: {info['variables']}")
    print(f"   Count: {info['variable_count']}")
    assert info['is_template'] == True
    
    # Test 4: Validate variables
    validation = validate_template_variables(
        content,
        {"platform": "esp32", "code_path": "src/"}
    )
    print(f"\n✅ Variable Validation:")
    print(f"   Valid: {validation['valid']}")
    print(f"   Missing: {validation['missing']}")
    assert validation['missing'] == ["language"]
    
    print("\n✅ All template utility tests passed!")

def test_postgres_adapter():
    """Test Postgres adapter connection."""
    print("\n" + "="*70)
    print("Testing Postgres Adapter")
    print("="*70)
    
    adapter = get_postgres_adapter()
    
    if adapter:
        print("\n✅ Postgres adapter created successfully")
        
        # Test connection
        if adapter.connect():
            print("✅ Connected to Postgres database")
            
            # Test schema
            adapter._ensure_schema()
            print("✅ Database schema ensured")
            
            # Test list prompts
            prompts = adapter.list_prompts(limit=5)
            print(f"✅ Listed {len(prompts)} prompts from database")
            
            adapter.disconnect()
            print("✅ Disconnected from database")
        else:
            print("❌ Failed to connect to Postgres database")
            print("   Make sure Postgres is running:")
            print("   docker-compose -f docker-compose.postgres.yml up -d")
    else:
        print("⚠️  Postgres adapter not available")
        print("   Install psycopg2: pip install psycopg2-binary")
        print("   Or start Postgres: docker-compose -f docker-compose.postgres.yml up -d")

def test_postgres_mcp_integration():
    """Test Postgres MCP integration."""
    print("\n" + "="*70)
    print("Testing Postgres MCP Integration")
    print("="*70)
    
    integration = get_postgres_mcp_integration()
    
    if integration:
        print("\n✅ Postgres MCP integration created successfully")
        
        # Test statistics
        stats = integration.get_prompt_stats()
        if stats:
            print(f"✅ Retrieved prompt statistics:")
            print(f"   Total: {stats.get('total', 0)}")
            print(f"   Templates: {stats.get('templates', 0)}")
            print(f"   Regular: {stats.get('regular', 0)}")
        
        # Test advanced search
        prompts = integration.search_prompts_advanced(limit=5)
        print(f"✅ Advanced search returned {len(prompts)} prompts")
    else:
        print("⚠️  Postgres MCP integration not available")
        print("   Ensure Postgres adapter is working first")

def test_mcp_configuration():
    """Test MCP server configuration."""
    print("\n" + "="*70)
    print("Testing MCP Configuration")
    print("="*70)
    
    import subprocess
    
    # Test mcp-prompts server
    try:
        result = subprocess.run(
            ["cursor-agent", "mcp", "list-tools", "mcp-prompts"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ mcp-prompts MCP server accessible")
        else:
            print("⚠️  mcp-prompts MCP server not accessible")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not test mcp-prompts server: {e}")
    
    # Test Postgres MCP server
    try:
        result = subprocess.run(
            ["cursor-agent", "mcp", "list-tools", "postgres"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Postgres MCP server accessible")
        else:
            print("⚠️  Postgres MCP server not accessible")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not test Postgres MCP server: {e}")

def main():
    """Run all tests."""
    print("="*70)
    print("Postgres MCP Integration Test Suite")
    print("="*70)
    
    # Test template utilities (always available)
    test_template_utilities()
    
    # Test Postgres adapter (requires Postgres running)
    test_postgres_adapter()
    
    # Test Postgres MCP integration
    test_postgres_mcp_integration()
    
    # Test MCP configuration
    test_mcp_configuration()
    
    print("\n" + "="*70)
    print("Test Suite Complete")
    print("="*70)
    print("\nNext Steps:")
    print("1. Start Postgres: docker-compose -f docker-compose.postgres.yml up -d")
    print("2. Install psycopg2: pip install psycopg2-binary")
    print("3. Verify MCP config: cat ~/.cursor/mcp.json")
    print("4. Test with cursor-agent: cursor-agent mcp list-tools mcp-prompts")

if __name__ == "__main__":
    main()
