# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python package implementing document-related tools for converting and processing document formats. Tools are exposed through an MCP (Model Context Protocol) server interface for seamless integration with AI assistants. **This project is designed to work with Amazon Bedrock Mantle**.

## Setup and Development Commands

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows

# Install in development mode
uv pip install -e .

# Run the MCP server
uv run main.py

# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/test_document.py

# Run a specific test
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_docx
```

## Architecture

### MCP Server Structure

The project uses **FastMCP** from the `mcp` package to create an MCP server that exposes Python functions as tools:

- **Entry point**: `main.py` - Initializes the FastMCP server and registers tools
- **Tool modules**: `tools/` - Contains tool implementations as Python functions
- **Test suite**: `tests/` - pytest-based tests with fixtures in `tests/fixtures/`

### Tool Registration Flow

1. Tools are defined as regular Python functions in `tools/` modules
2. Functions are registered with the MCP server using `mcp.tool()` decorator
3. The server runs in stdio mode, waiting for MCP protocol messages
4. Tools become available to AI assistants through the MCP interface

## Defining MCP Tools

Tools must follow these patterns and conventions:

### Function Signature

**Always define the parameter data types when declaring functions.** Type annotations are required for all parameters and return values.

```python
from pydantic import Field

def tool_name(
    param1: str = Field(description="Detailed description of this parameter"),
    param2: int = Field(description="Explain what this parameter does")
) -> ReturnType:
    """Comprehensive docstring here"""
    # Implementation
```

### Documentation Requirements

Tool descriptions should include:

1. **One-line summary** - Brief description of what the tool does
2. **Detailed explanation** - Comprehensive explanation of functionality
3. **When to use** - Explain appropriate use cases (and when NOT to use)
4. **Usage examples** - Include expected input/output examples

Use `Field` from pydantic for parameter descriptions to ensure they are exposed through the MCP interface.

### Example Tool Structure

```python
from pydantic import Field

def add(
    a: float = Field(description="First number to add"),
    b: float = Field(description="Second number to add"),
) -> float:
    """Add two numbers together.

    Takes two numerical inputs and returns their sum. This tool handles
    integers and floating point numbers.

    When to use:
    - When you need to perform simple addition
    - When you need precise numerical calculation

    Examples:
    >>> add(2, 3)
    5.0
    >>> add(2.5, 3.5)
    6.0
    """
    return a + b
```

### Registering Tools

In `main.py`, register tools with the MCP server:

```python
from mcp.server.fastmcp import FastMCP
from tools.module_name import tool_function

mcp = FastMCP("server_name")
mcp.tool()(tool_function)

if __name__ == "__main__":
    mcp.run()
```

## Key Dependencies

- **mcp[cli]==1.27.0** - MCP server framework (FastMCP)
- **markitdown[docx,pdf]>=0.1.5** - Document conversion library
- **pydantic>=2.13.4** - Data validation and tool parameter descriptions
- **pytest>=9.0.3** - Testing framework

## Testing Conventions

- Test files live in `tests/` and follow `test_*.py` naming
- Test fixtures (sample documents) are in `tests/fixtures/`
- Current fixtures: `mcp_docs.docx` and `mcp_docs.pdf`
- Tests use class-based organization for related test cases
- Always verify fixture files exist before running conversion tests
