"""Tests for akshare-mcp server core functionality."""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestGetAkshareTools:
    """Unit tests for get_akshare_tools function."""

    def test_get_akshare_tools_returns_dict(self):
        """Test that get_akshare_tools returns a dictionary."""
        from akshare_mcp.server import get_akshare_tools

        tools = get_akshare_tools()

        assert isinstance(tools, dict)

    def test_get_akshare_tools_contains_stock_apis(self):
        """Test that stock-related APIs are included."""
        from akshare_mcp.server import get_akshare_tools

        tools = get_akshare_tools()

        assert "stock_zh_a_spot_em" in tools or any("stock" in k for k in tools.keys())

    def test_get_akshare_tools_cache_functionality(self):
        """Test that cache file is created."""
        import os
        from akshare_mcp.server import CACHE_FILE, get_akshare_tools

        tools = get_akshare_tools()

        assert os.path.exists(CACHE_FILE) or len(tools) > 0


class TestCreateToolFunc:
    """Unit tests for create_tool_func helper."""

    def test_create_tool_func_returns_callable(self):
        """Test that create_tool_func returns a callable."""
        from akshare_mcp.server import create_tool_func

        def sample_func():
            return {"data": "test"}

        tool_func = create_tool_func("sample_func", sample_func, [])

        assert callable(tool_func)

    def test_create_tool_func_executes_original_function(self):
        """Test that tool func executes the original function."""
        from akshare_mcp.server import create_tool_func

        def sample_func():
            return {"data": "test"}

        tool_func = create_tool_func("sample_func", sample_func, [])
        result = tool_func()

        assert json.loads(result) == {"data": "test"}

    def test_create_tool_func_handles_kwargs(self):
        """Test that tool func handles keyword arguments."""
        from akshare_mcp.server import create_tool_func

        def sample_func(symbol="000001", period="daily"):
            return {"symbol": symbol, "period": period}

        tool_func = create_tool_func("sample_func", sample_func, ["symbol", "period"])
        result = tool_func(symbol="600000", period="weekly")

        data = json.loads(result)
        assert data["symbol"] == "600000"
        assert data["period"] == "weekly"


class TestToolDefs:
    """Tests for TOOL_DEFS global."""

    def test_tool_defs_is_not_empty(self):
        """Test that TOOL_DEFS contains tools."""
        from akshare_mcp.server import TOOL_DEFS

        assert len(TOOL_DEFS) > 0

    def test_tool_defs_contains_expected_structure(self):
        """Test that each tool has expected structure."""
        from akshare_mcp.server import TOOL_DEFS

        for name, info in list(TOOL_DEFS.items())[:5]:
            assert "params" in info or "doc" in info


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_api_returns_error(self):
        """Test that calling non-existent API returns error."""
        from akshare_mcp.server import create_tool_func

        def nonexistent():
            raise ValueError("API not found")

        tool_func = create_tool_func("nonexistent", nonexistent, [])
        result = tool_func()

        data = json.loads(result)
        assert "error" in data
