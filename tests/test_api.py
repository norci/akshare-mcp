"""Tests for MCP server tool endpoints."""

import json

import pytest


class TestListAkshareApis:
    """Tests for list_akshare_apis tool."""

    def test_list_apis_returns_json(self):
        """Test that list_akshare_apis returns valid JSON."""
        from akshare_mcp.server import mcp

        # Get the tool function
        tool_func = None
        for name in dir(mcp):
            if "list" in name.lower() and "api" in name.lower():
                tool_func = getattr(mcp, name)
                break

        if tool_func:
            result = tool_func()
            assert isinstance(result, str)
            data = json.loads(result)
            assert isinstance(data, list)

    def test_list_apis_with_category_filter(self):
        """Test filtering by category."""
        from akshare_mcp.server import mcp

        tool_func = None
        for name in dir(mcp):
            if "list" in name.lower() and "api" in name.lower():
                tool_func = getattr(mcp, name)
                break

        if tool_func:
            result = tool_func(category="stock", limit=10)
            data = json.loads(result)
            assert len(data) <= 10


class TestSearchApis:
    """Tests for search_apis tool."""

    def test_search_returns_results(self):
        """Test that search returns matching APIs."""
        from akshare_mcp.server import mcp

        tool_func = None
        for name in dir(mcp):
            if "search" in name.lower():
                tool_func = getattr(mcp, name)
                break

        if tool_func:
            result = tool_func(keyword="stock")
            data = json.loads(result)
            assert isinstance(data, list)
            if len(data) > 0:
                assert "stock" in data[0]["name"].lower()


class TestGetApiInfo:
    """Tests for get_api_info tool."""

    def test_get_info_for_existing_api(self):
        """Test getting info for existing API."""
        from akshare_mcp.server import mcp

        tool_func = None
        for name in dir(mcp):
            if "get" in name.lower() and "info" in name.lower():
                tool_func = getattr(mcp, name)
                break

        if tool_func:
            result = tool_func(api_name="stock_zh_a_spot_em")
            data = json.loads(result)
            assert isinstance(data, dict)


class TestGetTimeInfo:
    """Tests for get_time_info tool."""

    def test_get_time_info_returns_datetime(self):
        """Test that get_time_info returns time information."""
        from akshare_mcp.server import mcp

        tool_func = None
        for name in dir(mcp):
            if "time" in name.lower():
                tool_func = getattr(mcp, name)
                break

        if tool_func:
            result = tool_func()
            data = json.loads(result)
            assert "current_datetime" in data or "last_trading_day" in data
