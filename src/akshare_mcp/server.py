#!/usr/bin/env python3
"""
akshare-mcp - Complete MCP server for akshare

Dynamically generates MCP tools from all akshare APIs.
"""

import inspect
import json
import logging
from datetime import datetime
from typing import Any, Callable, get_type_hints
import types

import akshare as ak
from fastmcp import FastMCP
from pydantic import Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(name="akshare-mcp")

CACHE_FILE = "/tmp/akshare_tools_cache.json"


def get_akshare_tools() -> dict[str, dict]:
    """Get cached tool definitions or generate new ones."""
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        pass

    tools = {}
    funcs = [f for f in dir(ak) if not f.startswith("_")]

    for func_name in funcs:
        func = getattr(ak, func_name)
        # Use inspect.isfunction to only include actual functions, not classes or other callables
        if not inspect.isfunction(func):
            continue

        try:
            sig = inspect.signature(func)
            params = {}

            for param_name, param in sig.parameters.items():
                param_type = "string"
                default = None

                if param.annotation != inspect.Parameter.empty:
                    anno = str(param.annotation)
                    if "int" in anno:
                        param_type = "integer"
                    elif "float" in anno:
                        param_type = "number"
                    elif "bool" in anno:
                        param_type = "boolean"
                    elif "list" in anno or "List" in anno:
                        param_type = "array"
                    elif "dict" in anno or "Dict" in anno:
                        param_type = "object"

                if param.default != inspect.Parameter.empty:
                    default = param.default

                params[param_name] = {
                    "type": param_type,
                    "default": default,
                    "required": param.default == inspect.Parameter.empty,
                }

            doc = func.__doc__ or ""
            first_line = doc.strip().split("\n")[0] if doc else ""

            tools[func_name] = {
                "params": params,
                "doc": first_line[:200] if first_line else func_name,
                "full_doc": doc[:1000] if doc else "",
            }

        except Exception as e:
            logger.debug(f"Skipping {func_name}: {e}")
            continue

    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(tools, f, indent=2, default=str)
    except Exception:
        pass

    return tools


TOOL_DEFS = get_akshare_tools()
GENERATED_TOOLS = {}


def create_tool_func(func_name: str, original_func: Callable, param_info: dict) -> Callable:
    """Create a tool function with proper signature from original akshare function."""

    # Get parameter details from TOOL_DEFS
    params = param_info.get("params", {})

    # Build the function signature with explicit parameters
    if not params:
        # No parameters - simple case
        exec_code = """def {func_name}():
    '''Tool for calling akshare.{func_name}'''
    try:
        result = original_func()
        if hasattr(result, "to_json"):
            return result.to_json(orient="records", date_format="iso") or "[]"
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e), "function": "{func_name}"}, ensure_ascii=False)
"""
        exec_code = exec_code.replace("{func_name}", func_name)
    else:
        # Build parameter list with defaults
        param_list = []
        for pname, pinfo in params.items():
            default = pinfo.get("default")
            is_required = pinfo.get("required", True)

            if default is None or default == inspect.Parameter.empty or is_required:
                # Required param - no default
                param_list.append(pname)
            else:
                # Optional param - add default
                if isinstance(default, str):
                    param_list.append(f'{pname}="{default}"')
                else:
                    param_list.append(f"{pname}={default}")

        param_str = ", ".join(param_list)

        # Build the function - call original_func with kwargs, filter None
        exec_code = f"""def {func_name}({param_str}):
    '''Tool for calling akshare.{func_name}'''
    try:
        kwargs = {{k: v for k, v in locals().items() if k != 'original_func' and v is not None}}
        result = original_func(**kwargs)
        if hasattr(result, "to_json"):
            return result.to_json(orient="records", date_format="iso") or "[]"
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        return json.dumps({{"error": str(e), "function": "{func_name}"}}, ensure_ascii=False)
"""
        exec_code = exec_code.replace("{func_name}", func_name)

    # Create the function dynamically
    local_ns = {"original_func": original_func, "json": json, "func_name": func_name}
    exec(exec_code, local_ns)
    tool_func = local_ns[func_name]

    # Set the docstring from TOOL_DEFS if available
    tool_func.__doc__ = TOOL_DEFS.get(func_name, {}).get("full_doc", f"Call akshare.{func_name}")

    return tool_func


def register_all_tools():
    """Register all akshare functions as MCP tools."""
    funcs = [f for f in dir(ak) if not f.startswith("_")]
    registered = 0

    for func_name in funcs:
        if func_name in GENERATED_TOOLS:
            continue

        func = getattr(ak, func_name, None)
        # Use inspect.isfunction to only include actual functions, not classes
        if not inspect.isfunction(func) or func_name.startswith("_"):
            continue

        try:
            tool_def = TOOL_DEFS.get(func_name, {})
            params = tool_def.get("params", {})

            # Build parameter defaults and annotations for the tool function
            sig_params = {}
            annotations = {}
            required_params = []

            for param_name, param_info in params.items():
                type_hint = param_info.get("type", "string")
                if type_hint == "integer":
                    type_hint = int
                elif type_hint == "number":
                    type_hint = float
                elif type_hint == "boolean":
                    type_hint = bool
                elif type_hint == "array":
                    type_hint = list
                elif type_hint == "object":
                    type_hint = dict
                else:
                    type_hint = str

                default = param_info.get("default")
                is_required = param_info.get("required", False)

                if default is None and is_required:
                    # For required params, use ... as placeholder
                    sig_params[param_name] = ...
                    required_params.append(param_name)
                else:
                    sig_params[param_name] = default
                annotations[param_name] = type_hint

            # Get the param info for the function
            param_info = tool_def

            # Create the tool function with explicit parameters
            tool_func = create_tool_func(func_name, func, param_info)

            # Use original func_name as tool name, not with replaced underscores
            # The MCP framework will handle parameter exposure automatically
            tool = mcp.tool(name=func_name)(tool_func)
            GENERATED_TOOLS[func_name] = tool
            registered += 1

        except Exception as e:
            logger.debug(f"Failed to register {func_name}: {e}")
            continue

    logger.info(f"Registered {registered} akshare tools")


register_all_tools()


@mcp.tool
def list_akshare_apis(
    category: str = Field(default="", description="Filter by category keyword"),
    limit: int = Field(default=50, description="Max number of APIs to return"),
) -> str:
    """List all available akshare APIs with descriptions."""
    all_apis = []
    for name, info in TOOL_DEFS.items():
        if (
            category
            and category.lower() not in name.lower()
            and category.lower() not in info.get("doc", "").lower()
        ):
            continue
        all_apis.append(
            {
                "name": name,
                "description": info.get("doc", ""),
                "params": list(info.get("params", {}).keys()),
            }
        )

    return json.dumps(all_apis[:limit], ensure_ascii=False, indent=2)


@mcp.tool
def get_api_info(
    api_name: str = Field(description="The akshare API function name"),
) -> str:
    """Get detailed information about a specific akshare API."""
    if api_name not in TOOL_DEFS:
        return json.dumps({"error": f"API '{api_name}' not found"}, ensure_ascii=False)

    return json.dumps(TOOL_DEFS[api_name], ensure_ascii=False, indent=2)


@mcp.tool
def search_apis(keyword: str = Field(description="Search keyword")) -> str:
    """Search akshare APIs by keyword."""
    results = []
    keyword_lower = keyword.lower()

    for name, info in TOOL_DEFS.items():
        if keyword_lower in name.lower() or keyword_lower in info.get("doc", "").lower():
            results.append({"name": name, "description": info.get("doc", "")})

    return json.dumps(results[:20], ensure_ascii=False, indent=2)


@mcp.tool
def get_time_info() -> str:
    """Get current time and trading calendar info."""
    try:
        trade_date_df = ak.tool_trade_date_hist_sina()
        trade_dates = [d for d in trade_date_df["trade_date"]]
        current_date = datetime.now().date()
        past_dates = sorted([d for d in trade_dates if d <= current_date], reverse=True)
        last_trading_day = past_dates[0].strftime("%Y-%m-%d") if past_dates else None

        return json.dumps(
            {
                "current_datetime": datetime.now().isoformat(),
                "last_trading_day": last_trading_day,
                "total_apis": len(TOOL_DEFS),
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def main():
    """Main entry point for the MCP server."""
    logger.info(f"Starting akshare-mcp with {len(TOOL_DEFS)} APIs, transport=stdio")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
