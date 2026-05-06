# Model Context Protocol (MCP) - Complete Tutorial

## Table of Contents

- [What is MCP?](#what-is-mcp)
- [Architecture Overview](#architecture-overview)
- [Client-Server Separation](#client-server-separation)
- [Transport Mechanisms](#transport-mechanisms)
- [File Descriptors & Pipes](#file-descriptors--pipes)
- [JSON-RPC Protocol](#json-rpc-protocol)
- [Stateful vs Stateless](#stateful-vs-stateless)
- [Building an MCP Server](#building-an-mcp-server)
- [Building an MCP Client](#building-an-mcp-client)
- [MCP Inspector](#mcp-inspector)
- [Real-World Usage](#real-world-usage)
- [Project Setup](#project-setup)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)
- [Resources](#resources)
- [Summary](#summary)

## What is MCP?

Model Context Protocol (MCP) is an open protocol that standardizes how AI applications (like Claude, ChatGPT) connect to external data sources and tools.

### Key Concepts

- **Server**: Provides tools, resources, and prompts.
- **Client**: Consumes server capabilities (e.g., Claude Desktop, VS Code).
- **Transport**: How client and server communicate (stdio, HTTP, WebSocket).
- **Protocol**: JSON-RPC 2.0 format for messages.

### Why MCP?

Before MCP, each integration was custom-built:

```text
┌─────────┐   Custom API    ┌──────────┐
│ Claude │ ←──────────────→ │ Database │
└─────────┘   └──────────┘
            │ Custom API     ┌──────────┐
            └──────────────→ │ Weather │
                           └──────────┘
```

With MCP, the protocol is standardized for all integrations:

```text
┌─────────┐        ┌──────────┐
│ Claude │ ←── MCP ───→ │ Database │
└─────────┘        └──────────┘
      │
      └── MCP ───────────────→ │ Weather │
                                └──────────┘
```

## Architecture Overview

### Basic Structure

```text
┌─────────────────────────────────────────────────────────┐
│ Client Application                                      │
│ (Claude Desktop, VS Code)                              │
│                                                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │ MCP Client Library                              │    │
│  │ - Session Management                            │    │
│  │ - Protocol Handling                             │    │
│  │ - Transport Layer                               │    │
│  └──────────────────┬──────────────────────────────┘    │
│                     │                                   │
│                 Transport                            │
│             (stdio/HTTP/WebSocket)                   │
│                     │                                   │
│  ┌──────────────────▼───────────────────────────────┐    │
│  │ MCP Server Library                               │    │
│  │ - Request Handling                                │    │
│  │ - Protocol Implementation                         │    │
│  │ - Transport Layer                                 │    │
│  └──────────────────┬───────────────────────────────┘    │
│                     │                                   │
│  ┌──────────────────▼───────────────────────────────┐    │
│  │ Your Server Implementation                       │    │
│  │ - Tools (functions AI can call)                  │
│  │ - Resources (data AI can read)                   │
│  │ - Prompts (templates AI can use)                 │
│  └───────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Process Model

Each client spawns its own server instance.

```text
Claude Desktop Process     VS Code Process
┌─────────────────┐       ┌─────────────────┐
│ MCP Client      │       │ MCP Client      │
└───────┬─────────┘       └───────┬─────────┘
        │ stdio                  │ stdio
        │                       │
┌───────▼─────────┐       ┌───────▼─────────┐
│ Weather Server  │       │ Weather Server  │
│ (instance 1)    │       │ (instance 2)    │
└─────────────────┘       └─────────────────┘
```

## Client-Server Separation

### Why Not a Monolith?

Separation provides:

1. Reusability
2. Standardized protocol
3. Security & isolation
4. Language flexibility
5. Distribution model

#### Example: Same server, different clients

- Claude Desktop uses your server.
- VS Code extension uses your server.
- Custom CLI uses your server.
- Web app uses your server.

#### Standardized Protocol

Your client can connect to any MCP server.

```python
async with MCPClient(command="uv", args=["run", "weather_server.py"]):
    # Use weather tools

async with MCPClient(command="uv", args=["run", "database_server.py"]):
    # Use database tools

async with MCPClient(command="npx", args=["@modelcontextprotocol/server-github"]):
    # Use GitHub tools
```

### Security & Isolation

- Server runs in a separate process with limited permissions.
- It cannot accidentally access client memory or state.
- Easier to sandbox dangerous operations.

### Language Flexibility

- Server in Python, client in JavaScript.
- Server in Rust, client in Python.
- Mix and match implementations.

### Distribution Model

Service providers distribute pre-built servers:

```bash
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
```

You configure, not implement.

#### Real-World Example: Claude Desktop

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-api-key"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/you/Documents"]
    }
  }
}
```

## Transport Mechanisms

### 1. stdio (Standard Input/Output)

Most common for local, single-client scenarios.

```text
Client Process      Server Process
┌─────────────┐     ┌─────────────┐
│ stdin       │────▶ Read from  │
│             │     │ stdin       │
│ stdout      │◀───▶ Write to   │
└─────────────┘     └─────────────┘
```

Pros:

- Simple setup (no ports, no network config).
- Fast (direct pipes).
- Secure for local use.
- Automatic cleanup when process exits.

Cons:

- Same machine only.
- One client per server instance.

Example:

```python
import subprocess

process = subprocess.Popen(
    ["python", "server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)
```

### 2. HTTP/WebSocket

Used for remote servers or multiple clients.

```text
Client 1 ──┐
          ├──→ HTTP/WS ──→ ┌─────────────────┐
Client 2 ──┘               │ MCP Server      │
                          │ (localhost:8080)│
                          └─────────────────┘
```

Pros:

- Can be remote (different machines).
- Supports multiple clients.
- Works in browsers.

Cons:

- More complex setup.
- Higher overhead.
- Requires lifecycle management.

When to use:

- Shared resources (database connection pools).
- Rate-limited APIs.
- Browser clients.
- Remote services.

## File Descriptors & Pipes

### File Descriptors (FDs)

Every process has a file descriptor table:

```text
Process File Descriptor Table
┌────┬─────────────────┐
│ FD │ Points to       │
├────┼─────────────────┤
│ 0  │ stdin           │
│ 1  │ stdout          │
│ 2  │ stderr          │
│ 3  │ myfile.txt      │
│ 4  │ socket          │
│ 5  │ database.db     │
└────┴─────────────────┘
```

In Python:

```python
import sys
import os

sys.stdin  # File descriptor 0
sys.stdout # File descriptor 1
sys.stderr # File descriptor 2

os.read(0, 1024)
os.write(1, b"Hi")
```

### Pipes - Connecting Processes

A pipe is a unidirectional data channel between processes.

```text
Parent writes to process.stdin ↓
Data goes to kernel pipe buffer ↓
Child reads from sys.stdin ↓
Child processes and writes to sys.stdout ↓
Data goes to kernel pipe buffer ↓
Parent reads from process.stdout
```

Complete example:

```python
# server.py (Child Process)
import sys
import json

for line in sys.stdin:
    request = json.loads(line)
    result = {"response": f"Got {request['data']}"}
    sys.stdout.write(json.dumps(result) + "\n")
    sys.stdout.flush()
```

```python
# client.py (Parent Process)
import subprocess
import json

process = subprocess.Popen(
    ["python", "server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)

request = {"data": "hello"}
process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()
response = process.stdout.readline()
print(json.loads(response))
```

### What Happens in Memory

```text
Parent writes to process.stdin ↓
Data goes to kernel pipe buffer ↓
Child reads from sys.stdin ↓
Child processes and writes to sys.stdout ↓
Data goes to kernel pipe buffer ↓
Parent reads from process.stdout

Pipe Buffer (in kernel memory)
┌─────────────────────────────┐
│ {"data":"hello"}\n          │ ← Written by parent
│ {"response":"Got hello"}\n │ ← Written by child
└─────────────────────────────┘
```

## JSON-RPC Protocol

### What is JSON-RPC?

JSON-RPC stands for JSON Remote Procedure Call.

Remote means the caller invokes a procedure in another execution context. That can be:

- A different machine over a network.
- A different process on the same machine.
- A different thread within the same application.

When MCP uses stdio, it behaves like a local procedure call, but the JSON-RPC protocol remains transport-agnostic.

### JSON-RPC format

Request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "city": "San Francisco"
    }
  }
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "temperature": 72,
    "condition": "sunny"
  }
}
```

Error:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

### MCP JSON-RPC methods

- `initialize` — Handshake between client and server.
- `tools/list` — List available tools.
- `tools/call` — Execute a tool.
- `resources/list` — List available resources.
- `resources/read` — Read a resource.
- `resources/subscribe` — Subscribe to resource updates.
- `prompts/list` — List available prompts.
- `prompts/get` — Get a specific prompt.
- `sampling/createMessage` — Request an AI completion.

### stdio vs HTTP transport

#### stdio

- Transport: raw byte streams over stdin/stdout.
- Protocol: JSON-RPC messages are sent as newline-delimited JSON.
- Best for local subprocess-based servers and single-client scenarios.

Example:

```text
stdin:  {"jsonrpc":"2.0","method":"tools/list"}\n
stdout: {"jsonrpc":"2.0","result":{"tools":[...]}}\n
```

#### HTTP

- Transport: HTTP requests and responses.
- Protocol: JSON-RPC payload is carried in the request body.
- Best for remote services, browser clients, or shared servers.

Example:

```http
POST /rpc HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Content-Length: 45

{"jsonrpc":"2.0","method":"tools/list"}
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 123

{"jsonrpc":"2.0","result":{"tools":[...]}}
```

## Stateful vs Stateless

### Common misconception

- ❌ "MCP servers are stateless because each client gets its own instance."
- ✅ MCP servers are stateful during their lifetime.

Servers can maintain:

- Database connections.
- Caches.
- Session data.
- Rate limiters.

### Server lifecycle

```text
Client connects
↓
Server process starts
┌─────────────────────────────────┐
│ Server is STATEFUL here:       │
│ - DB connections open          │
│ - Caches populated             │
│ - Session state maintained     │
│ - Multiple tool calls share    │
│   the same state               │
└─────────────────────────────────┘
↓
Client disconnects
↓
Server process terminates
↓
State is lost
```

### Example: Stateful server

```python
# mcp_server.py
from mcp.server import Server
import sqlite3

class WeatherServer:
    def __init__(self):
        self.db = sqlite3.connect('weather.db')
        self.cache = {}
        self.request_count = 0

    async def get_weather(self, city: str):
        self.request_count += 1

        if city in self.cache:
            return self.cache[city]

        cursor = self.db.execute(
            "SELECT * FROM weather WHERE city=?",
            (city,),
        )
        result = cursor.fetchone()
        self.cache[city] = result
        return result

server = WeatherServer()
```

### When state matters

```python
class DBServer:
    def __init__(self):
        self.connection_pool = create_pool(size=10)

    async def query(self, sql):
        conn = await self.connection_pool.acquire()
        result = await conn.execute(sql)
        await self.connection_pool.release(conn)
        return result
```

```python
class APIServer:
    def __init__(self):
        self.rate_limiter = RateLimiter(calls=100, period=60)

    async def call_api(self, endpoint):
        await self.rate_limiter.wait()
        return await make_request(endpoint)
```

```python
class CacheServer:
    def __init__(self):
        self.cache = LRUCache(maxsize=1000)

    async def get_data(self, key):
        if key in self.cache:
            return self.cache[key]

        data = await expensive_operation(key)
        self.cache[key] = data
        return data
```

### Stateless between sessions

State does not persist across separate client sessions.

```text
Session 1: Client connects → Server starts → cache={} → Client disconnects → Server dies
Session 2: Client connects → NEW server starts → cache={} (empty again)
```

## Building an MCP Server

### Basic server structure

```python
# mcp_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

server = Server("my-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_weather",
            description="Get weather for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"],
            },
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_weather":
        city = arguments["city"]
        return [
            TextContent(
                type="text",
                text=f"Weather in {city}: Sunny, 72°F",
            )
        ]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Server with state

```python
# stateful_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import sqlite3
import asyncio

class StatefulServer:
    def __init__(self):
        self.server = Server("stateful-server")
        self.db = sqlite3.connect('data.db')
        self.cache = {}

        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)

    async def list_tools(self):
        return [
            Tool(
                name="query_db",
                description="Query the database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string"}
                    },
                    "required": ["sql"],
                },
            )
        ]

    async def call_tool(self, name: str, arguments: dict):
        if name == "query_db":
            sql = arguments["sql"]

            if sql in self.cache:
                return [TextContent(type="text", text=self.cache[sql])]

            cursor = self.db.execute(sql)
            result = cursor.fetchall()
            self.cache[sql] = str(result)
            return [TextContent(type="text", text=str(result))]

    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )

if __name__ == "__main__":
    server = StatefulServer()
    asyncio.run(server.run())
```

## Building an MCP Client

### Basic client structure

```python
# mcp_client.py
import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )

        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        read_stream, write_stream = stdio_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError("Not connected. Call connect() first.")
        return self._session

    async def list_tools(self):
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, arguments: dict):
        return await self.session().call_tool(tool_name, arguments)

    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
```

### Using the client

```python
# example_usage.py
import asyncio
import sys

async def main():
    async with MCPClient(
        command="uv",
        args=["run", "mcp_server.py"],
    ) as client:
        tools = await client.list_tools()
        print("Available tools:", tools)

        result = await client.call_tool(
            "get_weather",
            {"city": "San Francisco"},
        )
        print("Result:", result)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
```

### Manual connection

```python
client = MCPClient(command="uv", args=["run", "mcp_server.py"])

try:
    await client.connect()
    tools = await client.list_tools()
    print(tools)
finally:
    await client.cleanup()
```

## MCP Inspector

The MCP Inspector is a web-based development tool for testing and debugging MCP servers.

### Installation

```bash
npm install -g @modelcontextprotocol/inspector
```

### Running the Inspector

```bash
mcp dev mcp_server.py
```

### What it provides

- Test server tools, resources, and prompts.
- Inspect request/response messages.
- Debug server implementation.
- Validate protocol compliance.

### Typical flow

1. Start your MCP server.
2. Run `mcp dev mcp_server.py`.
3. Open the inspector in the browser.
4. Use the UI to call tools and inspect messages.

## Project Setup

### Python project structure

```text
mcp_project/
├── pyproject.toml
├── package.json
├── mcp_server.py
├── mcp_client.py
├── .env
├── .gitignore
└── README.md
```

### pyproject.toml

```toml
[project]
name = "mcp-project"
version = "0.1.0"
description = "MCP Server Implementation"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "mcp>=1.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### package.json

```json
{
  "name": "mcp-project",
  "version": "0.1.0",
  "private": true,
  "devDependencies": {
    "@modelcontextprotocol/inspector": "^0.21.2"
  }
}
```

### Installation

```bash
uv sync
npm install
```

Or install the inspector globally:

```bash
npm install -g @modelcontextprotocol/inspector
```

### .gitignore

```text
# Python
__pycache__/
*.py[cod]
.Python
*.so
*.egg
*.egg-info/
dist/
build/

# Node.js
node_modules/
package-lock.json

# Environment
.env
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
```

## Best Practices

### 1. Error handling

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "risky_operation":
            result = await perform_operation(arguments)
            return [TextContent(type="text", text=result)]
    except ValueError as e:
        return [
            TextContent(
                type="text",
                text=f"Error: Invalid input - {str(e)}",
            )
        ]
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return [
            TextContent(
                type="text",
                text="An unexpected error occurred",
            )
        ]
```

### 2. Input validation

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_user":
        if "user_id" not in arguments:
            return [
                TextContent(
                    type="text",
                    text="Error: user_id is required",
                )
            ]

        if not isinstance(arguments["user_id"], int):
            return [
                TextContent(
                    type="text",
                    text="Error: user_id must be an integer",
                )
            ]

        if arguments["user_id"] < 1:
            return [
                TextContent(
                    type="text",
                    text="Error: user_id must be positive",
                )
            ]

        return await get_user(arguments["user_id"])
```

### 3. Resource cleanup

```python
class DatabaseServer:
    def __init__(self):
        self.db = None

    async def initialize(self):
        self.db = await connect_to_database()

    async def cleanup(self):
        if self.db:
            await self.db.close()

    async def run(self):
        try:
            await self.initialize()
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    ...,
                )
        finally:
            await self.cleanup()
```

### 4. Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    logger.info(f"Tool called: {name} with args: {arguments}")
    try:
        result = await execute_tool(name, arguments)
        logger.info(f"Tool {name} succeeded")
        return result
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}", exc_info=True)
        raise
```

### 5. Testing

```python
# test_server.py
import pytest
from mcp_client import MCPClient

@pytest.mark.asyncio
async def test_get_weather_tool():
    async with MCPClient(
        command="uv",
        args=["run", "mcp_server.py"],
    ) as client:
        tools = await client.list_tools()
        assert any(t.name == "get_weather" for t in tools)

        result = await client.call_tool(
            "get_weather",
            {"city": "San Francisco"},
        )
        assert result is not None
        assert "temperature" in str(result)
```

## Common Pitfalls

### 1. Forgetting to flush stdout

```python
# Wrong
sys.stdout.write(json.dumps(response) + "\n")

# Correct
sys.stdout.write(json.dumps(response) + "\n")
sys.stdout.flush()
```

### 2. Not handling server termination

```python
# Wrong
while True:
    line = sys.stdin.readline()
    process(line)

# Correct
for line in sys.stdin:
    process(line)
```

### 3. Blocking operations

```python
# Wrong
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    result = requests.get("https://api.example.com")
    return result

# Correct
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com") as resp:
            result = await resp.json()
            return result
```

### 4. Not validating tool schemas

```python
# Wrong
Tool(
    name="get_user",
    description="Get user by ID",
    inputSchema={},
)

# Correct
Tool(
    name="get_user",
    description="Get user by ID",
    inputSchema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "User ID",
                "minimum": 1,
            }
        },
        "required": ["user_id"],
    },
)
```

## Resources

- Official MCP Specification
- MCP Documentation
- Python SDK
- TypeScript SDK
- MCP Inspector
- Official MCP Servers
- GitHub Discussions
- Discord Community

## Summary

Key takeaways:

- MCP standardizes AI-to-tool communication using JSON-RPC.
- Client-server separation enables reusability and security.
- stdio transport is simple and efficient for local, single-client scenarios.
- HTTP/WebSocket works for remote servers, browser clients, and shared services.
- Servers are stateful during their lifetime.
- Each client typically spawns its own server instance via stdio.
- Service providers distribute pre-built servers; you configure them instead of implementing them.
- MCP Inspector is helpful for development and debugging.

When to use what:

- stdio: local development, Claude Desktop, VS Code extensions.
- HTTP/WebSocket: shared resources, browser clients, remote services.
- Pre-built servers: when available (Brave, GitHub, etc.).
- Custom servers: when you need specific functionality.
 