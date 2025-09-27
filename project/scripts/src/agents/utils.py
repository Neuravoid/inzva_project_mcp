import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from loguru import logger
from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from mcp import ClientSession


async def open_client(username: str, password: str) -> 'ClientSession':
    """
    Starts an in-container MCP client using `npx mcp-remote` via the stdio client
    and returns an initialized ClientSession.

    This function raises ValueError when credentials are missing, ConnectionError
    on timeouts, and re-raises other unexpected exceptions after logging.
    """
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
        # Increase timeout to allow for slower container startups
        logger.info("Attempting to connect to MCP server... (max 60 seconds)")
        reader, writer = await asyncio.wait_for(stdio_cm.__aenter__(), timeout=60.0)
        logger.info("Connection established with stdio server.")

        client_cm = ClientSession(reader, writer)
        client_session = await client_cm.__aenter__()

        # Allow extra time for session initialization
        logger.info("Attempting to initialize client session... (max 60 seconds)")
        await asyncio.wait_for(client_session.initialize(), timeout=60.0)
        logger.success("✅ MCP Session Initialized Successfully! Ready to chat.")
        
        async def _close_wrapper():
            await client_cm.__aexit__(None, None, None)
            await stdio_cm.__aexit__(None, None, None)
            err_log.close()

        client_session.close = _close_wrapper
        return client_session
    except asyncio.TimeoutError:
        logger.error("MCP connection timed out. The container might have network issues or the credentials might be invalid.")
        err_log.close()
        raise ConnectionError("MCP sunucusuna bağlanırken zaman aşımı oluştu.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during client connection: {e}")
        err_log.close()
        raise


async def get_structured_tools(session: 'ClientSession') -> List[Dict[str, Any]]:
    tools_resp = await session.list_tools()
    return [{"name": tool.name, "description": tool.description or "", "input_schema": tool.inputSchema or {}} for tool in tools_resp.tools]


async def execute_tool_with_params(tool_name: str, tool_args: dict, session: 'ClientSession') -> dict:
    try:
        tool_resp = await session.call_tool(tool_name, tool_args)
        if hasattr(tool_resp, "error") and tool_resp.error: return {"error": "execution_error", "message": str(tool_resp.error)}
        if hasattr(tool_resp, 'parts'): return {"ok": True, "result": "".join(part.text for part in tool_resp.parts if hasattr(part, 'text'))}
        return {"ok": True, "result": str(tool_resp)}
    except Exception as e:
        logger.error(f"Exception during tool execution: {e}")
        error_str = str(e)
        if "Invalid arguments" in error_str: return {"error": "validation_error", "message": error_str}
        return {"error": "execution_exception", "message": error_str}
