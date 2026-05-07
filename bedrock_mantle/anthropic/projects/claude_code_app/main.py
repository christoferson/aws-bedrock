from mcp.server.fastmcp import FastMCP
from tools.math import add
from tools.document import document_path_to_markdown
from tools.converter import unit_converter

mcp = FastMCP("docs")

mcp.tool()(add)
mcp.tool()(document_path_to_markdown)
mcp.tool()(unit_converter)

if __name__ == "__main__":
    mcp.run()
