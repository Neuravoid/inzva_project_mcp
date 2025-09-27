from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from pathlib import Path
import re
import os
from loguru import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # For type checkers only; avoids importing `mcp` at runtime during module import
    from mcp import ClientSession, StdioServerParameters

async def open_client(username: str, password: str) -> 'ClientSession':
    # Import mcp lazily to avoid importing its dependencies (pydantic, etc.) at module import time.
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except Exception as e:
        # Provide a clearer error if mcp import fails inside the container
        raise ImportError(f"Failed to import mcp package: {e}")

    # Eğer username veya password boşsa, hata ver
    if not username or not password:
        raise ValueError("MCP username and password must be provided.")

    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y", "mcp-remote", "https://mcp.turkishtechlab.com/mcp",
            "--username", username,
            "--password", password
        ],
    )

    err_log = open("mcp_errors.log", "w", encoding="utf-8")
    stdio_cm = stdio_client(server_params, errlog=err_log)
    
    try:
        logger.info("Attempting to connect to MCP server... (max 30 seconds)")
        reader, writer = await asyncio.wait_for(stdio_cm.__aenter__(), timeout=30.0)
        logger.info("Connection established with stdio server.")

    except asyncio.TimeoutError:
        logger.error("Connection to MCP server timed out after 30 seconds.")
        err_log.close()
        raise ConnectionError("MCP sunucusuna bağlanırken zaman aşımı oluştu.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during client connection: {e}")
        err_log.close()
        raise

    client_cm = ClientSession(reader, writer)
    client_session = await client_cm.__aenter__()

    await client_session.initialize()
    logger.info("Client session initialized successfully.")

    async def _close_wrapper():
        try:
            orig_close = getattr(client_session, "close", None)
            if orig_close and orig_close is not _close_wrapper:
                res = orig_close()
                if asyncio.iscoroutine(res):
                    await res
        except Exception: pass
        try: await client_cm.__aexit__(None, None, None)
        except Exception: pass
        try: await stdio_cm.__aexit__(None, None, None)
        except Exception: pass
        try: err_log.close()
        except Exception: pass

    client_session.close = _close_wrapper
    return client_session

async def get_structured_tools(session: 'ClientSession') -> list:
    tools_resp = await session.list_tools()
    langgraph_ready_tools = []
    for tool in tools_resp.tools:
        tool_definition = {
            "name": tool.name,
            "description": tool.description or "",
            "input_schema": tool.inputSchema or {},
        }
        langgraph_ready_tools.append(tool_definition)         
    return langgraph_ready_tools

async def rule_checker(arg_schema: dict, value) -> str:
    """
    Smarter rule checker that handles different data types.
    """
    schema_type = arg_schema.get("type")
    
    # Handle missing but not required values
    if value is None:
        return ""

    # --- Type Validation ---
    if schema_type == "string" and not isinstance(value, str):
        return f"value is not a string (got {type(value).__name__})"
    if schema_type == "integer" and not isinstance(value, int):
        return f"value is not an integer (got {type(value).__name__})"
    if schema_type == "array" and not isinstance(value, list):
        return f"value is not an array/list (got {type(value).__name__})"
    if schema_type == "boolean" and not isinstance(value, bool):
        return f"value is not a boolean (got {type(value).__name__})"
    if schema_type == "object" and not isinstance(value, dict):
        return f"value is not an object/dict (got {type(value).__name__})"

    # --- String Specific Rules ---
    if schema_type == "string":
        minlen = arg_schema.get("minLength")
        if minlen is not None and len(value) < int(minlen):
            return f"length {len(value)} < minLength ({minlen})"
        maxlen = arg_schema.get("maxLength")
        if maxlen is not None and len(value) > int(maxlen):
            return f"length {len(value)} > maxLength ({maxlen})"
        pattern = arg_schema.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            return f"value does not match pattern: {pattern}"
            
    # All checks passed
    return ""

async def arg_checker(tool_args: dict, input_schema: dict) -> tuple:
    """
    Validates tool arguments against the input schema using the new rule_checker.
    """
    errors = []
    props = (input_schema or {}).get("properties", {})
    required = (input_schema or {}).get("required", [])
    args = tool_args or {}

    # Check for missing required fields
    for req in required:
        if req not in args or args[req] is None:
            errors.append({"field": req, "reason": "missing required field"})

    # Validate the fields that were provided
    for name, schema in props.items():
        if name in args:
            msg = await rule_checker(schema, args[name])
            if msg:
                errors.append({"field": name, "reason": msg})

    return (len(errors) == 0, errors)

async def execute_tool_with_params(tool_name: str, tool_args: dict, session: ClientSession) -> dict:
    """
    Executes a tool and ensures the result is a JSON-serializable dictionary.
    """
    tools = await get_structured_tools(session)
    tool = next((t for t in tools if t.get("name") == tool_name), None)
    if not tool:
        return {"error": "tool_not_found", "tool": tool_name}

    schema = tool.get("input_schema", {}) or {}
    ok, errors = await arg_checker(tool_args, schema)
    if not ok:
        return {"error": "validation_error", "errors": errors}

    try:
        tool_resp = await session.call_tool(tool_name, tool_args)
    except Exception as e:
        logger.error(f"Exception during tool execution: {e}")
        return {"error": "execution_exception", "message": str(e)}

    # Check for errors in the tool's response
    if hasattr(tool_resp, "error") and tool_resp.error:
        return {"error": "execution_error", "message": str(tool_resp.error)}
    
    # FINAL FIX: Convert the complex tool response object to a simple, storable dictionary.
    # This specifically handles the 'TextContent' object that caused the crash.
    if hasattr(tool_resp, 'parts'):
        result_text = "".join(part.text for part in tool_resp.parts if hasattr(part, 'text'))
        return {"ok": True, "result": result_text}
    else:
        # Fallback for other types of responses
        return {"ok": True, "result": str(tool_resp)}