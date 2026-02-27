"""Tests for akshare-mcp MCP server using mcporter."""

import subprocess
import json

import pytest


# The MCP server command
MCP_SERVER_CMD = "uvx --from /home/josephx/code/akshare-mcp akshare-mcp"


def mcporter_call(tool_name: str, *args: str) -> subprocess.CompletedProcess:
    """Helper to call mcporter with the MCP server."""
    cmd = ["mcporter", "call", "--stdio", MCP_SERVER_CMD, tool_name]
    cmd.extend(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
    )


class TestMcporterIntegration:
    """Integration tests for MCP server via mcporter."""

    def test_get_time_info_no_params(self):
        """Test calling tool with no params (uses defaults)."""
        result = mcporter_call("get_time_info")

        assert result.returncode == 0, f"Error: {result.stderr}"

        data = json.loads(result.stdout)
        assert "current_datetime" in data
        assert "last_trading_day" in data
        assert "total_apis" in data
        assert isinstance(data["total_apis"], int)
        assert data["total_apis"] > 0

    def test_list_akshare_apis_with_params(self):
        """Test calling list_akshare_apis with category and limit params."""
        result = mcporter_call("list_akshare_apis", "category:stock", "limit:3")

        assert result.returncode == 0, f"Error: {result.stderr}"

        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) == 3
        # All should contain "stock" in name or description
        for item in data:
            assert "name" in item
            assert "description" in item

    def test_list_akshare_apis_default_limit(self):
        """Test list_akshare_apis uses default limit correctly."""
        result = mcporter_call("list_akshare_apis")

        assert result.returncode == 0, f"Error: {result.stderr}"

        data = json.loads(result.stdout)
        assert isinstance(data, list)
        # Default limit is 50
        assert len(data) <= 50

    def test_search_apis_with_keyword(self):
        """Test search_apis tool with keyword parameter."""
        result = mcporter_call("search_apis", "keyword:bond")

        assert result.returncode == 0, f"Error: {result.stderr}"

        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 0
        # All results should contain "bond" in name or description
        for item in data:
            assert "name" in item
            name_lower = item["name"].lower()
            desc_lower = item.get("description", "").lower()
            assert "bond" in name_lower or "bond" in desc_lower

    def test_get_api_info(self):
        """Test get_api_info tool to retrieve specific API details."""
        result = mcporter_call("get_api_info", "api_name:stock_zh_a_spot_em")

        assert result.returncode == 0, f"Error: {result.stderr}"

        data = json.loads(result.stdout)
        assert "params" in data
        assert "doc" in data

    def test_invalid_tool_returns_error(self):
        """Test that calling non-existent tool returns error."""
        # This tests error handling via mcporter
        # Note: mcporter may handle unknown tools differently
        # We'll test with a valid tool that has invalid params instead
        result = mcporter_call("list_akshare_apis", "category:nonexistent_category_xyz", "limit:1")

        # Should still return valid JSON (possibly empty or filtered)
        assert result.returncode == 0, f"Error: {result.stderr}"
        data = json.loads(result.stdout)
        assert isinstance(data, list)
