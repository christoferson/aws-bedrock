# MCP Chat

MCP Chat is a command-line interface application that enables interactive chat capabilities with AI models through the Anthropic API. The application supports document retrieval, command-based prompts, and extensible tool integrations via the MCP (Model Control Protocol) architecture.

## Prerequisites

- Python 3.9+
- Anthropic API Key

## Setup

### Step 1: Configure the environment variables

1. Create or edit the `.env` file in the project root and verify that the following variables are set correctly:

```
ANTHROPIC_API_KEY=""  # Enter your Anthropic API secret key
```

### Step 2: Install dependencies

#### Option 1: Setup with uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

1. Install uv, if not already installed:

```bash
pip install uv
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv pip install -e .
```

4. Run the project

```bash
uv run main.py
```

#### Option 2: Setup without uv

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
```

3. Run the project

```bash
python main.py
```

## Usage

### Basic Interaction

Simply type your message and press Enter to chat with the model.

### Document Retrieval

Use the @ symbol followed by a document ID to include document content in your query:

```
> Tell me about @deposition.md
```

### Commands

Use the / prefix to execute commands defined in the MCP server:

```
> /summarize deposition.md
```

Commands will auto-complete when you press Tab.

## Development

### Adding New Documents

Edit the `mcp_server.py` file to add new documents to the `docs` dictionary.

### Implementing MCP Features

To fully implement the MCP features:

1. Complete the TODOs in `mcp_server.py`
2. Implement the missing functionality in `mcp_client.py`

### Linting and Typing Check

There are no lint or type checks implemented.



## MCP Server Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is a web-based development tool that helps you test and debug your Model Context Protocol servers. It provides an interactive interface to:

- Test server tools, resources, and prompts
- Inspect request/response messages in real-time
- Debug your MCP server implementation
- Validate protocol compliance

### Prerequisites

The inspector is a Node.js package that needs to be installed separately:

```bash
npm install -g @modelcontextprotocol/inspector
```

### Running the Inspector

Start the inspector with your MCP server:

```bash
mcp dev mcp_server.py
```

This will launch a proxy server and open the inspector in your browser:

```
Starting MCP inspector...
⚙️ Proxy server listening on localhost:6277
🔑 Session token: 36ed0045db15a9d2ab17b3a4250ac2cd8afe1cdd326047a55d2acad5fed23e28
   Use this token to authenticate requests or set DANGEROUSLY_OMIT_AUTH=true to disable auth

🚀 MCP Inspector is up and running at:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=36ed0045db15a9d2ab17b3a4250ac2cd8afe1cdd326047a55d2acad5fed23e28

🌐 Opening browser...
```

The inspector will automatically open in your default browser with authentication handled via the URL token.

### Learn More

- [MCP Inspector Documentation](https://modelcontextprotocol.io/docs/tools/inspector)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)