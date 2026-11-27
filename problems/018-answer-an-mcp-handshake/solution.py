def handle(request):
    """Return the JSON-RPC response dict for an MCP request."""
    request_id = request.get("id")
    method = request.get("method")

    if method == "initialize":
        result = SERVER_CAPABILITIES
    elif method == "tools/list":
        result = {"tools": TOOLS}
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    return {"jsonrpc": "2.0", "id": request_id, "result": result}
