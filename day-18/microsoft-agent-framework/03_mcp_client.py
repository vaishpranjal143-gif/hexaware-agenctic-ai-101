import sys
from pathlib import Path
from agent_framework import MCPStdioTool
from _maf import POLICY, banner, get_client, run

banner("MAF - File 03 - MCP Client + MCP Server")

SERVER = str(Path(__file__).resolve().parent / "_mcp_server.py")

async def main():
    orders = MCPStdioTool(name="hex-orders",
                          command=sys.executable, args=[SERVER])

    async with orders:
        print("WHAT THE SERVER EXPOSED AS MCP (We did not write this list)")
        for tool in orders.functions:
            print(f" {tool.name}: {tool.description}")
        print()

        agent = get_client().as_agent(
            name="support",
            tools=[orders],
            instructions=f"You are Hex Retail suppoert. {POLICY} Use the tools.")
        result = await agent.run("Is order HX-90455 returnable?")
        print(f"THE AGENT SAID        : {result.text}")

run(main())