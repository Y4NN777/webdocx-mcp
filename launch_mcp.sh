#!/bin/bash
# WebDocx MCP Server Launcher
# This script ensures the correct Python environment is used

cd /home/y4nn_777/Y7_Projects/AI_ML/webdocx-mcp
exec /home/y4nn_777/.local/bin/uv run python -m webdocx.server
    