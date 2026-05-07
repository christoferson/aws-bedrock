# Claude Code MCP Integration Guide

## Quick Start

```bash
# 1. Navigate to project directory
cd bedrock_mantle/anthropic/projects/claude_code_app

# 2. Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# 3. IMPORTANT: Keep the virtual environment activated!
# The MCP server needs the venv to be active to access the tools

# 4. The project already has .mcp.json configured!
# Verify it's recognized:
claude mcp get local-docs
# Should show: Scope: Project config (shared via .mcp.json)

# 5. Start a FRESH Claude Code session (with venv activated)
# IMPORTANT: MCP servers are loaded on session start
# If you're already in a Claude Code session, exit first with /exit
claude

# 6. Test the MCP tools
# Then ask: "Convert 100 celsius to fahrenheit using the unit converter tool"
```

**Critical Notes**:
- ⚠️ **MUST activate the virtual environment** before starting Claude Code! The MCP server runs `uv run main.py` which needs access to the installed packages
- The `.mcp.json` file is included in this repository, so the MCP server named `local-docs` is automatically configured
- **MCP servers are loaded when Claude Code starts** - if you modified `.mcp.json` during an active session, you must exit and restart Claude Code for it to take effect
- Always start Claude Code from this project directory (with venv activated) so it can find `.mcp.json` and dependencies

## Overview

This document explains how to integrate our custom MCP (Model Context Protocol) server with Claude Code and test the implemented tools.

### What is MCP?

MCP (Model Context Protocol) is Anthropic's protocol for connecting AI assistants to external tools and data sources. It allows Claude to interact with custom tools through a standardized interface.

### What We Built

We've implemented an MCP server with the following tools:

1. **add** - Basic arithmetic addition tool
   - Adds two numbers together
   - Demonstrates simple function-to-tool conversion

2. **document_path_to_markdown** - Document conversion tool
   - Converts PDF and DOCX files to markdown format
   - Reads files from disk and processes them
   - Uses the `markitdown` library for conversion

3. **unit_converter** - Unit conversion tool
   - Converts between different units of measurement
   - Supports: Temperature, Length, Weight/Mass, Volume
   - Includes unit aliases and case-insensitive input
   - 20+ supported units across 4 categories

### Implementation Architecture

```
claude_code_app/
├── main.py                    # MCP server entry point (FastMCP)
├── tools/
│   ├── math.py               # add() tool
│   ├── document.py           # document_path_to_markdown() tool
│   └── converter.py          # unit_converter() tool
└── tests/
    ├── test_document.py      # Document tool tests
    └── test_converter.py     # Converter tool tests (30 tests)
```

**Key Pattern**: Tools are regular Python functions decorated with `mcp.tool()` and use `pydantic.Field` for parameter descriptions.

## Integration with Claude Code

### Step 1: Configure MCP Server in Claude Code

Claude Code needs to know about your MCP server through an MCP configuration. The server needs a **name** (an identifier you choose) and details about how to run it.

**About the Server Name**: We use `local-docs` as the name for our MCP server. You can choose any name you like - it's just an identifier that Claude Code uses to reference this specific MCP server. Common patterns are descriptive names like `local-docs`, `my-tools`, `project-mcp`, etc.

#### Option A: Project-Specific Configuration (Recommended)

**This project already includes `.mcp.json`, so the MCP server is pre-configured!** The sections below explain how it was set up.

You can configure the MCP server for this project in two ways:

**Method 1: Using Claude CLI Command**

```bash
# Add MCP server with project scope
claude mcp add -s project local-docs -- uv run main.py
```

**Command Breakdown**:
- `claude mcp add` - Command to add a new MCP server
- `-s project` - Scope flag: adds to `.mcp.json` in the current directory (project-specific)
  - Other options: `-s local` (default, goes to `~/.claude.json`), `-s user` (user-level config)
- `local-docs` - The name/identifier for this MCP server (you can use any name)
- `--` - Separator indicating everything after this is the command to run
- `uv run main.py` - The actual command that starts the MCP server

**Method 2: Manually Create `.mcp.json` File**

Create a `.mcp.json` file in the project directory with the following contents:

```json
{
  "mcpServers": {
    "local-docs": {
      "command": "uv",
      "args": ["run", "main.py"]
    }
  }
}
```

**Configuration Breakdown**:
- `"local-docs"` - The server name (matches what you'd use in CLI)
- `"command": "uv"` - The base command to execute
- `"args": ["run", "main.py"]` - Arguments passed to the command

**Benefits of Project-Specific Configuration**:
- Configuration is committed to version control (`.mcp.json` should be in git)
- Only active when working in this project directory
- Team members get the same MCP setup automatically when they clone
- No global pollution of your Claude Code config

**Verify the configuration**:
```bash
# Check if the server is configured
claude mcp get local-docs

# Or try listing (note: project-scoped servers may not always show in list)
claude mcp list
```

You should see the server details when using `get`. The output will show:
```
local-docs:
  Scope: Project config (shared via .mcp.json)
  Status: ✗ Failed to connect
```

**Note**: The "Failed to connect" status for stdio servers during health checks is normal and doesn't affect functionality. The server will work correctly when Claude Code actually uses it in a session.

**Known Issue**: `claude mcp list` may not always display project-scoped (`.mcp.json`) servers, but `claude mcp get <name>` will show them. The server will still work in Claude Code sessions.

#### Option B: Local/Global Configuration

If you want the MCP server available globally across all projects:

```bash
# Default scope is 'local' - adds to ~/.claude.json
claude mcp add local-docs -- uv run main.py

# Explicitly specify local scope
claude mcp add -s local local-docs -- uv run main.py
```

**Difference from Project Configuration**:
- Writes to `~/.claude.json` instead of `.mcp.json`
- Available in all directories, not just this project
- Not shared via version control
- Useful for personal tools you use across many projects

#### Option C: Manual Configuration

Edit your Claude Code settings file (typically `~/.claude/config.json` or project-specific `.claude/settings.json`):

```json
{
  "mcpServers": {
    "local-docs": {
      "command": "uv",
      "args": ["run", "main.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

Or specify a relative path from your workspace root:

```json
{
  "mcpServers": {
    "local-docs": {
      "command": "uv",
      "args": ["run", "main.py"],
      "cwd": "bedrock_mantle/anthropic/projects/claude_code_app"
    }
  }
}
```

### Step 2: Verify MCP Server Works

Test that the MCP server starts correctly:

```bash
# From the project directory
uv run main.py
```

The server should start without errors and wait for stdio input. Press `Ctrl+C` to stop.

### Step 3: Start Claude Code with MCP Support

```bash
# Start Claude Code in this directory
claude

# The MCP server will automatically connect when Claude Code starts
```

### Step 4: Verify MCP Server Connection

You can verify the MCP server is running with:

```bash
# List all configured MCP servers and their status
claude mcp list

# Get detailed information about your server
claude mcp get local-docs
```

### Step 5: Test Tools Are Available

In a Claude Code session, ask:

```
What MCP tools are available from the local-docs server?
```

Or simply try using a tool:

```
Use the add tool to calculate 25 + 17
```

Claude should have access to the three tools: `add`, `document_path_to_markdown`, and `unit_converter`.

## Testing the MCP Integration

### Test 1: Basic Math Tool

```
Use the add tool to calculate 42 + 58
```

**Expected Response**: Claude will use the `add` tool and return `100.0`

### Test 2: Unit Converter Tool

```
Convert 100 celsius to fahrenheit using the unit converter tool
```

**Expected Response**: Claude will use the `unit_converter` tool and return `212.0`

**More unit converter tests:**
```
Convert 5 miles to kilometers
Convert 150 pounds to kilograms  
Convert 2 gallons to liters
Convert 100 meters to feet
```

### Test 3: Document Conversion Tool

First, verify the test fixtures exist:
```bash
ls tests/fixtures/
# Should show: mcp_docs.docx  mcp_docs.pdf
```

Then ask Claude:
```
Use the document_path_to_markdown tool to convert tests/fixtures/mcp_docs.pdf to markdown
```

**Expected Response**: Claude will read the PDF and return its markdown-formatted content.

**Alternative test with DOCX:**
```
Convert the file at tests/fixtures/mcp_docs.docx to markdown
```

## Troubleshooting

### Issue: Claude Code Not Using MCP Tools

**Symptom**: Claude explains what MCP is instead of actually using the tool. Example response: "To use this tool, you would need to start the MCP server..."

**Root Cause**: MCP servers are loaded when the Claude Code session starts. If you added/modified `.mcp.json` during an active session, it won't be detected.

**Solution**:
1. **Exit the current Claude Code session completely** (type `/exit` or Ctrl+C)
2. **Start a fresh Claude Code session**:
   ```bash
   claude
   ```
3. The MCP server will be loaded automatically on startup
4. Try the tool again: "Use the add tool to calculate 42 + 58"

**Alternative**: If you're already in a session and don't want to exit, you may be able to reload MCP servers with `/mcp reload` (if available in your version).

### Issue: MCP Server Not Found

**Symptom**: Claude Code says tools are not available or MCP server cannot be found

**Solutions**:
1. ⚠️ **CRITICAL: Activate the virtual environment BEFORE starting Claude Code**:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   claude
   ```
2. Verify `.mcp.json` exists: `ls -la .mcp.json`
3. Check the configuration: `claude mcp get local-docs`
4. Ensure you're in the correct directory (where `.mcp.json` is located)
5. Ensure `uv` is in your PATH: `which uv` or `where uv`
6. Verify the virtual environment exists: `ls .venv`
7. Make sure you started Claude Code from this directory with venv activated

### Issue: Tools Not Showing Up

**Symptom**: MCP server starts but tools aren't available

**Solutions**:
1. Check `main.py` has all tools registered
2. Verify imports are correct
3. Look for Python syntax errors: `uv run python -m py_compile tools/*.py`

### Issue: Tool Execution Fails

**Symptom**: Tool is called but returns an error

**Solutions**:
1. Run the unit tests: `uv run pytest tests/test_converter.py -v`
2. Test the function directly in Python:
   ```bash
   uv run python
   >>> from tools.converter import unit_converter
   >>> unit_converter(100, "celsius", "fahrenheit")
   212.0
   ```

### Issue: Document Tool DLL Error (Windows)

**Symptom**: `ImportError: DLL load failed` with onnxruntime

**Note**: This is a known Windows-specific issue with the `markitdown` dependency. The document conversion tool may not work in Windows environments due to onnxruntime DLL loading issues. The tool works correctly on Linux/Mac.

**Workaround**: Focus testing on `add` and `unit_converter` tools which don't have this dependency.

## Debugging MCP Communication

To see MCP protocol messages for debugging:

```bash
# Run with debug logging
export MCP_DEBUG=1
uv run main.py
```

Or in Claude Code settings, add:
```json
{
  "mcpServers": {
    "local-docs": {
      "command": "uv",
      "args": ["run", "main.py"],
      "env": {
        "MCP_DEBUG": "1"
      }
    }
  }
}
```

## Adding New Tools

To add a new tool to this MCP server:

1. **Create the tool function** in `tools/` directory
2. **Use type annotations** and `pydantic.Field` for parameters
3. **Write comprehensive docstring** (see CLAUDE.md)
4. **Register in main.py**: `mcp.tool()(your_function)`
5. **Write tests** in `tests/`
6. **Reload MCP** in Claude Code: `/mcp reload`

Example:
```python
# tools/example.py
from pydantic import Field

def multiply(
    a: float = Field(description="First number"),
    b: float = Field(description="Second number")
) -> float:
    """Multiply two numbers together."""
    return a * b

# main.py
from tools.example import multiply
mcp.tool()(multiply)
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/anthropics/fastmcp)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- Project CLAUDE.md - Tool development guidelines

## Summary

You now have a working MCP server with three tools integrated into Claude Code:
- ✅ Mathematical operations (`add`)
- ✅ Unit conversions (`unit_converter`) - 30 tests passing
- ✅ Document conversion (`document_path_to_markdown`)

The tools follow MCP best practices and can be extended with additional functionality as needed.
